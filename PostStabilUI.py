from distutils.dep_util import newer_pairwise
from pydoc import doc
import sys
from xml.etree.ElementTree import tostring
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *

import cv2
import os
import json
import numpy as np
from datetime import datetime
import subprocess
import math

import signal
import time



ui = uic.loadUiType("PostStabilUI.ui")[0]

class MyWindow(QMainWindow, ui):

    def __init__(self, parent =None):
        super(MyWindow,self).__init__(parent)
        
        self.setupUi(self)
        self.setWindowTitle(" 4DReplay - Post Stabilize")
        
        
        self.file = ""
        self.json_file = ""
        self.fps = 30
        self.vWid = 1920
        self.vHei = 1080
        self.json_data = []
        self.startFrame = 0
        self.roi_left = 0
        self.roi_top = 0
        self.roi_width = 0
        self.roi_height = 0
        self.selected  = ""
        self.idx = 0
        self.position = 0
        self.startF = 0
        self.endF = 0
        self.newIdx = 0

        self.ShowList()
        self.pb_import.clicked.connect(self.Open)
        self.pb_json.clicked.connect(self.openJson)
   
        self.view = CView(self)
        self.lay.addWidget(self.view)
    
        self.pb_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pb_play.clicked.connect(self.play)
        self.pb_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pb_pause.clicked.connect(self.view.pause)
        self.pb_stop.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.pb_stop.clicked.connect(self.view.stop)
        self.pb_reload.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.pb_reload.clicked.connect(self.ShowList)
        self.pb_start.clicked.connect(self.saveStart)
        self.pb_end.clicked.connect(self.saveEnd)
        self.pb_saves.clicked.connect(self.saveNewSwipe)
         
        self.pb_draw.clicked.connect(self.drawROI)
        #self.pb_ok.clicked.connect(self.saveROI)
        self.pb_savej.clicked.connect(self.saveNewJson)
        self.pb_stabil.clicked.connect(self.calcStabil)
        self.pb_frame.clicked.connect(self.calcStabilFrame)
        self.pb_json2.clicked.connect(self.openJsonFolder)
   
        self.status.addItem("> Please import Video file(.mp4) or Select Json file. ")
        #self.status.setAlternatingRowColors(True)
        self.status.setDragEnabled(True)
        self.index_list.itemClicked.connect(self.saveROI)

       
        self.video_slider.sliderMoved.connect(self.view.setPosition)
        self.video_slider.sliderMoved.connect(self.positionChanged)
        self.view.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.view.mediaPlayer.durationChanged.connect(self.durationChanged)
        
        #delete frame
        self.pb_save.clicked.connect(self.saveFrame)
        self.pb_clear.clicked.connect(self.clearFrame)
        self.frame = 0
        self.delete_frame = []
        
        self.checkDraw = False
      

    def Open(self):
        #self.index_list.clear()
        file_name,_ = QFileDialog.getOpenFileName(self,
                            "Open Video File",'','Videos (*.mp4)')
        if file_name != "":
            self.file = file_name
            self.status.addItem("Opend video file : "+str(self.file))
            self.play()
            cap = cv2.VideoCapture(self.file)
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.view.fps = self.fps
            self.vWid = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.vHei = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
            self.status.addItem("Size : "+str(self.vWid)+" , "+ str(self.vHei)+ "   fps : "+ str(self.fps))

            self.filename.setText(self.file)
            self.status.addItem("> Please import Json file(.json)")
            
            self.spinBox.setValue(0)
        
    def openJson(self):
        self.index_list.clear()
        file_name,_ = QFileDialog.getOpenFileName(self,"Open JSON file",'','Json file (*.json)')    
        if file_name != "":
            self.json_file = file_name
            self.status.addItem("Opend json file : "+str(self.json_file))
            self.ParseJson()
            self.status.scrollToBottom()
            self.jsonname.setText(self.json_file)
            self.index_list.setCurrentRow(0)
        
    def openJsonFolder(self):
        dirName = QFileDialog.getExistingDirectory(self, self.tr("Open Folder ", "./"))
        
        if dirName != "":
            self.listwidget.clear()
            filelist = os.listdir(dirName)
            
            for file in filelist:
                if os.path.splitext(file)[1]=='.json':
                    self.listwidget.addItem(file)
        
        
    def ShowList(self):
        self.listwidget.clear()
        filelist = os.listdir(os.getcwd())
        
        for file in filelist:
            if os.path.splitext(file)[1]=='.json':
                self.listwidget.addItem(file)
            
    def play(self):
        if(self.file==''):
            self.status.addItem("> Open file, first!")
        else:
            self.view.play(self.file)

    def positionChanged(self, position):
        self.video_slider.setValue(position)
        self.frame = math.trunc(self.view.frame)
        position = ((self.frame)*1000)/self.fps  #position is (ms)
        #self.view.setStartFrame(position)
        self.lb_frame.setText("frame: " + str(self.frame))
    
    def durationChanged(self, duration):
        self.video_slider.setRange(0,duration)


    #draw event        
    def drawROI(self):
        if self.json_file!='' and self.file!='':
            self.checkDraw = True
            if self.startFrame==0:
                self.status.addItem("[warning] Check Json file. ")
            
            self.view.clearROI()
            self.idx  = self.index_list.row(self.index_list.currentItem())
            self.startFrame = self.json_data['swipeperiod'][self.idx]['start']
            print(self.index_list.row(self.index_list.currentItem()))
            
            
            #self.fps = 15
            print("fps : "+str(self.fps))
            position = ((self.startFrame)*1000)/self.fps  #position is (ms)
            self.view.setStartFrame(position)
            self.lb_frame.setText("frame: " + str(self.startFrame))
    
        else:
            self.status.addItem("[Warning] Import Video and Json file !")
            self.status.scrollToBottom()     
        
    def saveFrame(self):
        self.delete_frame.append(self.frame)
        self.delete_frame.sort()
        self.lb_delete.setText(str(self.delete_frame))
     
    def clearFrame(self):
        self.delete_frame = []
        self.lb_delete.setText(str(self.delete_frame))   
        
        
    def saveROI(self):
        self.roi_left = self.view.start.x()*self.view.ratio
        self.roi_top = self.view.start.y()*self.view.ratio
        self.roi_width =(self.view.end.x()-self.view.start.x())*self.view.ratio
        self.roi_height = (self.view.end.y()-self.view.start.y())*self.view.ratio
        
        self.json_data['swipeperiod'][self.idx]['roi_left'] = self.roi_left
        self.json_data['swipeperiod'][self.idx]['roi_top'] = self.roi_top
        self.json_data['swipeperiod'][self.idx]['roi_width'] = self.roi_width
        self.json_data['swipeperiod'][self.idx]['roi_height'] = self.roi_height
                   
        self.json_data['input'] = self.file

        self.status.addItem("Saved "+str(self.idx))
        self.status.addItem("   left , top    :  {0} , {1}".format(self.roi_left,self.roi_top))    
        self.status.addItem("   width, height :  {0} , {1}".format(self.roi_width, self.roi_height))
        self.status.scrollToBottom()  
        

    def saveNewSwipe(self):
        #self.index_list.clear()
        self.newIdx = self.spinBox.value()
        # if self.newIdx == 0:
        #     self.json_data['swipeperiod'] = []
        self.json_data['swipeperiod'][self.newIdx]['start'] = self.startF
        self.json_data['swipeperiod'][self.newIdx]['end'] = self.endF
        
        self.status.addItem("   new start frame: "+str(self.startF)+"     new end frame: "+str(self.endF)+"        index : "+str(self.newIdx))
        self.status.scrollToBottom()
        
        self.spinBox.setValue(self.spinBox.value()+1)

    
    def saveNewJson(self):
        try:
            if self.delete_frame:
                self.json_data['delete_frame'] = self.delete_frame
      
            self.saveROI()
            
            self.json_data['input'] = self.file
            self.json_data['output'] = os.path.splitext(self.file)[0]+str('_stabil.mp4')
            
            
            
            json_data = self.json_data
            data = json.dumps(json_data,indent=4)
            dir = os.getcwd()
            base = os.path.basename(self.file)
            fname = os.path.splitext(base)[0]
            uniq = 1
            newjson = dir +"/"+ fname + str("_stabil.json")
            while os.path.exists(newjson):
                newjson = dir +"/"+ fname + str("_stabil(%d).json") % (uniq)
                uniq+=1
           
            file = open(newjson,'w')
            #file = open(FileSave,'w')      
            file.write(data)
            file.close()
             
            self.status.addItem("%s file was saved. " % newjson)       
            self.status.scrollToBottom() 
            addfile = os.path.basename(newjson)
            
            newItem = QListWidgetItem()
            newItem.setText(addfile)
            print(addfile)
            self.listwidget.insertItem(0, newItem)
            self.listwidget.setCurrentRow(0)
        

        except:
            self.status.addItem("[warning] Check the JSON file. (json file name = video file name)")
            self.status.scrollToBottom()
            
    def ParseJson(self):
        try:
            file = open(self.json_file)
            json_data = json.load(file)
            self.json_data = json_data
            sf = []
            swipe=''
            
            for i in range(len(json_data['swipeperiod'])):
                self.index_list.addItem("Swipe "+str(i+1))
                self.status.scrollToBottom()
                self.startFrame = json_data['swipeperiod'][i]['start']
                swipe_end = json_data['swipeperiod'][i]['end']
                self.status.addItem("   start frame: "+str(self.startFrame)+"      end frame: "+str(swipe_end)+"        index : "+str(i))
                
                self.status.scrollToBottom()
            self.status.addItem("> Click Draw button and draw ROI")
        except:
            self.status.addItem("[warning] Check the JSON file. (json file name = video file name)")
            self.status.scrollToBottom()
    

    def calcStabil(self):
        
        try :
            selected = self.listwidget.currentItem().text()
            file = open(selected)
            json_data = json.load(file)
            print(selected)
   
            try:
                subprocess.run("CMd/CMd.exe "+selected)
                self.status.addItem("Stabil Done    : "+ str(json_data['output']))
                self.status.scrollToBottom()
                   
            except:
                self.status.addItem("Stabil Failed.")
                self.status.scrollToBottom()
        except:
            self.status.addItem("[Warning] Please Select the New Json file")
            self.status.scrollToBottom() 
            
    def calcStabilFrame(self):
        try :
            selected = self.listwidget.currentItem().text()
            file = open(selected)
            json_data = json.load(file)
            print(selected)
            try:
                subprocess.run("CMd/CMd_c.exe "+selected)
                self.status.addItem("Stabil Done (crop ver)    : "+ str(json_data['output']))
                self.status.scrollToBottom()
            except:
                self.status.addItem("Stabil Failed.")
                self.status.scrollToBottom()
        except:
            self.status.addItem("[Warning] Please Select the New Json file")
            self.status.scrollToBottom() 
  
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print("space bar")
            if self.view.mediaPlayer.state() ==QMediaPlayer.PlayingState:
                self.view.mediaPlayer.pause()
            else:
                self.view.mediaPlayer.play()
        if event.key() == Qt.Key_F:
            self.view.frame += 1
            position = ((self.view.frame)*1000)/self.fps
            self.view.mediaPlayer.setPosition(position)
        if event.key() == Qt.Key_D:
            self.view.frame -= 1
            position = ((self.view.frame)*1000)/self.fps
            self.view.mediaPlayer.setPosition(position)    
            
    def saveStart(self):
        self.startF = self.frame
        self.lb_start.setText(str(self.startF))
        
    def saveEnd(self):
        self.endF = self.frame
        self.lb_end.setText(str(self.endF))
             
                
class CView(QGraphicsView):
    
    def __init__(self, parent):
        
        super(CView,self).__init__(parent)
        self.gScene = QGraphicsScene(self)
    
        self.new_w = 1280
        self.new_h = 720
        self.ratio = 0
        self.vid_wid =0
        self.vid_hei = 0
        
        self.setAlignment(Qt.AlignTop|Qt.AlignLeft)

        self.items = []
        self.start = QPointF()
        self.end = QPointF()
        self.startPos = []
        self.endPos = []
        
        self.file = ""
        self.point = QPointF()
        self.txt = ""
        self.first = True

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setRenderHint(QPainter.HighQualityAntialiasing)  
        self.mediaPlayer = QMediaPlayer(self, QMediaPlayer.VideoSurface)
    
        self.videoitem = QGraphicsVideoItem() 
        self.videoitem.setPos(0,0)
        self.videoitem.setSize(QSizeF(self.new_w,self.new_h))
        self.videoitem.setFlag(QGraphicsVideoItem.ItemIsMovable)
        self.rectitem = QGraphicsRectItem(self.videoitem)

        self.setScene(self.gScene)
        self.gScene.addItem(self.videoitem)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        
        line = QLineF(self.gScene.width()/2,0,self.gScene.width()/2,self.gScene.height())
        line2 = QLineF(0,self.gScene.height()/2,self.gScene.width(),self.gScene.height()/2)
        pen = QPen(Qt.black)

        self.items.append(self.gScene.addLine(line,pen))  
        self.items.append(self.gScene.addLine(line2,pen))  
        
        #delete frame
        self.fps = 0
        self.frame = 0
        
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:       
            self.start = event.pos()
            self.end = event.pos()
            
 
    def mouseMoveEvent(self, event):
        self.point = event.pos()
        
        if event.buttons() == Qt.LeftButton:
            self.end = event.pos()          
            if len(self.items)>0:
                self.gScene.removeItem(self.items[-1])
                del(self.items[-1])          
            rect = QRectF(self.start, self.end)
            pen = QPen(Qt.green)
            green20 = QColor(Qt.green)
            green20.setAlphaF(0.2)
            brush = QBrush(green20)
            self.items.append(self.gScene.addRect(rect,pen,brush))     
        
    def mousePos(self, event, ui):
        txt = "Point : {0} , {1} ".format(event.x(),event.y())
        ui.setText(txt)   
    
    def mouseReleaseEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.items.clear()
            rect = QRect(self.start, self.end)
            pen = QPen(Qt.green)
            green20 = QColor(Qt.green)
            green20.setAlphaF(0.2)
            brush = QBrush(green20)
            self.gScene.addRect(rect,pen,brush)
            
            txt = "start : {0} , end : {1} ".format(self.start,self.end)
            print(txt)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print("space")
            if self.mediaPlayer.state() ==QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()
            else:
                self.mediaPlayer.play()
            
    def play(self, file):
        self.file = file  
        video = QMediaContent((QUrl.fromLocalFile(file)))             
        self.mediaPlayer.setVideoOutput(self.videoitem)
        self.setScene(self.gScene)
        self.mediaPlayer.setMedia(video)
        self.mediaPlayer.play()   
        
        vid = cv2.VideoCapture(file)
        self.vid_wid = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.ratio = self.vid_wid/self.new_w
 
        self.fitInView(self.gScene.sceneRect(),Qt.KeepAspectRatio)
 
    def pause(self):
        self.mediaPlayer.pause() 
        
    def stop(self):
        self.mediaPlayer.stop()
        self.videoitem.setPos(0,0)
        self.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.fitInView(self.gScene.sceneRect(),Qt.KeepAspectRatio)
    
    # def setPosition(self,position): 
    #     self.mediaPlayer.setPosition(position)    
      
        
    def setStartFrame(self,position):
        self.mediaPlayer.setPosition(position)
        self.pause()
        
    def clearROI(self):
        if len(self.items)>0:
            self.gScene.removeItem(self.items[-1])
            del(self.items[-1])
    
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)
        ##
        frame = position * self.fps /1000
        self.frame = frame
        #print(" frame : "+str(frame))
        
    # def posToFrame(self, frame):

    #     frame = self.fps * self.mediaPlayer.getPosition() / 1000
        

    def mediaStateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            pass
    
        
    def showEvent(self, event):
        if not event.spontaneous():
            print('show event')
          

CSS = """
        video_slider::handle::horizontal{
            background: red;
            border: 1px solid #565a5e;
            width: 24px;
            height: 8px;
        }
        
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_icon = QIcon("logo.png")
    app.setWindowIcon(app_icon)
    #app.setStyleSheet(CSS)
    myWindow = MyWindow()
    myWindow.move(0,0)
    myWindow.showMaximized()
    myWindow.show()
    app.exec_()
    