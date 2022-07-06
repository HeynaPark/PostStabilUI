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


ui = uic.loadUiType("PostStabilUI.ui")[0]

class MyWindow(QMainWindow, ui):

    def __init__(self, parent =None):
        super(MyWindow,self).__init__(parent)
        
        self.setupUi(self)
        self.setWindowTitle("Post Stabilization Program")
   
        self.file = ""
        self.json_file = ""
        self.fps = 30
        self.json_data = []
        self.startFrame = 0
        self.roi_left = 0
        self.roi_top = 0
        self.roi_width = 0
        self.roi_height = 0
        self.selected  = ""
        self.idx = 0

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
         
        self.pb_draw.clicked.connect(self.drawROI)
        self.pb_ok.clicked.connect(self.saveROI)
        self.pb_send.clicked.connect(self.send)
        self.pb_stabil.clicked.connect(self.calcStabil)
        
        self.status.addItem(">>Please import Video file(.mp4), first")
        self.status.setAlternatingRowColors(True)
        self.status.setDragEnabled(True)
       
        self.video_slider.sliderMoved.connect(self.view.setPosition)
        self.video_slider.sliderMoved.connect(self.view.setPosition)
        self.view.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.view.mediaPlayer.durationChanged.connect(self.durationChanged)

    def Open(self):
        #self.index_list.clear()

        file_name,_ = QFileDialog.getOpenFileName(self,
                            "Open Video File",'','Videos (*.mp4)')
        self.file = file_name
        self.status.addItem("Opend video file : "+str(self.file))
        self.play()
        # if self.file!='':
        #     self.json_file = os.path.splitext(file_name)[0]+'.json'
        #     self.status.addItem("Opend json file : "+str(self.json_file))
        #     self.ParseJson()
        #     self.status.scrollToBottom()
        # else:
        #     self.status.addItem("[Warning] json file was not opend.")
        self.filename.setText(self.file)
        self.status.addItem(">>Please import Json file(.json)")
        
    def openJson(self):
        self.index_list.clear()
        file_name,_ = QFileDialog.getOpenFileName(self,"Open JSON file",'','Json file (*.json)')    
        self.json_file = file_name
        self.status.addItem("Opend json file : "+str(self.json_file))
        self.ParseJson()
        self.status.scrollToBottom()
        self.jsonname.setText(self.json_file)
        
        
    def ShowList(self):
        self.listwidget.clear()
        dir = QApplication.applicationDirPath()
        filelist = os.listdir(os.getcwd())
        
        for file in filelist:
            if os.path.splitext(file)[1]=='.json':
                self.listwidget.addItem(file)
            
    def play(self):
        if(self.file==''):
            self.status.addItem("Open file, first!")
        else:
            self.view.play(self.file)

    def positionChanged(self, position):
        self.video_slider.setValue(position)
    
    def durationChanged(self, duration):
        self.video_slider.setRange(0,duration)

    def mouseReleaseEvent(self, event):
        self.status.scrollToBottom()

    #draw event        
    def drawROI(self):
        if self.json_file!='' and self.file!='':
            if self.startFrame==0:
                self.status.addItem("[warning] Check Json file. ")

            self.view.clearROI()
            self.idx  = self.index_list.row(self.index_list.currentItem())
            self.startFrame = self.json_data['swipeperiod'][self.idx]['start']
            print(self.index_list.row(self.index_list.currentItem()))
            
            cap = cv2.VideoCapture(self.file)
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            #self.fps = 15
            print("fps : "+str(self.fps))
            position = ((self.startFrame)*1000)/self.fps  #position is (ms)
            self.view.drawROI(position)

        else:
            self.status.addItem("[Warning] Import Video and Json file !")
            self.status.scrollToBottom()     
        
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
            #jname = os.path.basename(self.json_file)
            #self.json_data['output'] = os.path.splitext(self.file)[0]+"+"+os.path.splitext(jname)[0]+str("%02d")+str('_stabil_output.mp4')
            
            self.status.addItem("Saved "+str(self.index_list.currentItem().text()))
            self.status.addItem("   left , top    :  {0} , {1}".format(self.roi_left,self.roi_top))    
            self.status.addItem("   width, height :  {0} , {1}".format(self.roi_width, self.roi_height))
            self.status.scrollToBottom()  
        
    def send(self):
        self.roi_left = self.view.start.x()*self.view.ratio
        self.roi_top = self.view.start.y()*self.view.ratio
        self.roi_width =(self.view.end.x()-self.view.start.x())*self.view.ratio
        self.roi_height = (self.view.end.y()-self.view.start.y())*self.view.ratio 
        self.status.scrollToBottom()
        self.saveNewJson()   
        self.ShowList()

    def saveNewJson(self):
        try:
            FileSave, _=QFileDialog.getSaveFileName(self, ' Save json file',  '.json')
            base = os.path.basename(FileSave)
            fname = os.path.splitext(base)[0]
            self.json_data['output'] = os.path.splitext(self.file)[0]+"+"+fname+str('_stabil_output.mp4')
            json_data = self.json_data
            data = json.dumps(json_data,indent=4)
 
            file = open(FileSave,'w')
            file.write(data)
            file.close()
            
            self.status.addItem("New JSON file was saved. ")
            self.status.scrollToBottom() 
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
        except:
            self.status.addItem("[warning] Check the JSON file. (json file name = video file name)")
            self.status.scrollToBottom()
    
    def calcStabil(self):
        try :
            selected = self.listwidget.currentItem().text()
            print(selected)
            try:
                subprocess.run("CMd.exe "+selected)
                self.status.addItem("Stabil Done.")
                self.status.scrollToBottom()
            except:
                self.status.addItem("Stabil Failed.")
                self.status.scrollToBottom()
        except:
            self.status.addItem("[Warning] Please Select the New Json file")
            self.status.scrollToBottom() 
  
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
        self.file = ""
        self.position = QPointF()
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
       # self.mediaPlayer.durationChanged.connect(self.durationChanged)
    
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:       
            self.start = event.pos()
            self.end = event.pos()
 
    def mouseMoveEvent(self, event):
        self.position = event.pos()
        
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
        txt = "Position : {0} , {1} ".format(event.x(),event.y())
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
        print(self.ratio)
        
        #self.mediaPlayer.play()
        self.fitInView(self.gScene.sceneRect(),Qt.KeepAspectRatio)
        # if self.first:
        #     video = QMediaContent((QUrl.fromLocalFile(file)))             
        #     self.mediaPlayer.setVideoOutput(self.videoitem)
        #     self.setScene(self.gScene)
        #     self.mediaPlayer.setMedia(video)

        #     self.mediaPlayer.play()   
        #     #self.first = False

        #     vid = cv2.VideoCapture(file)
        #     self.vid_wid = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            
        #     self.ratio = self.vid_wid/self.new_w
        #     print(self.ratio)
        # else:
        #     self.mediaPlayer.play()
        #     self.fitInView(self.gScene.sceneRect(),Qt.KeepAspectRatio)

    
    def pause(self):
        self.mediaPlayer.pause() 
        
    def stop(self):
        self.mediaPlayer.stop()
        self.videoitem.setPos(0,0)
        self.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.fitInView(self.gScene.sceneRect(),Qt.KeepAspectRatio)
    def setPosition(self,position): 
        self.mediaPlayer.setPosition(position)    
      
        
    def drawROI(self,position):
        self.mediaPlayer.setPosition(position)
        self.pause()
        
    def clearROI(self):
        if len(self.items)>0:
            self.gScene.removeItem(self.items[-1])
            del(self.items[-1])
    
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def mediaStateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            pass
    
        
    def showEvent(self, event):
        if not event.spontaneous():
            print('show event')
          

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.showMaximized()
    myWindow.show()
    app.exec_()
    