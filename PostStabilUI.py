from distutils.dep_util import newer_pairwise
from pydoc import doc
import sys
from xml.etree.ElementTree import tostring
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
#from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
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
        self.json_new_data =[]
        self.startFrame = 0
        self.start = QPointF()
        self.end = QPointF()
        self.items = []
        self.roi_left = 0
        self.roi_top = 0
        self.roi_width = 0
        self.roi_height = 0


        self.ShowList()
        
        self.pb_import.clicked.connect(self.Open)
   

        self.view = CView(self)
        self.lay.addWidget(self.view)
    

        self.pb_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pb_play.clicked.connect(self.view.play)

        self.pb_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pb_pause.clicked.connect(self.view.pause)

        self.pb_stop.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.pb_stop.clicked.connect(self.view.stop)
        
        self.video_slider.sliderMoved.connect(self.view.setPosition)
        
        self.pb_draw.clicked.connect(self.drawROI)
        self.pb_delete.clicked.connect(self.clearROI)
        self.pb_delete.clicked.connect(self.view.clearROI)
        self.pb_send.clicked.connect(self.send)
        self.pb_stabil.clicked.connect(self.calcStabil)
        
        self.status.addItem("Import Video file(.mp4) ====> click [Video Import]")
        self.status.setAlternatingRowColors(True)
        self.status.setDragEnabled(True)
        
   

    def Open(self):
        
        self.index_list.clear()
        
        file_name,_ = QFileDialog.getOpenFileName(self,
                            "Open Video File",'','"Videos (*.mp4)')
        self.file = file_name
        
        if self.file!='':
            self.json_file = os.path.splitext(file_name)[0]+'.json'
            self.view.play(self.file)
            self.ParseJson()
  
        self.filename.setText(self.file)
        self.status.addItem("[File]  "+ self.file)   
       
        
    def ShowList(self):
        self.listwidget.clear()
        dir = QApplication.applicationDirPath()
        filelist = os.listdir(os.getcwd())
        
        for file in filelist:
            if os.path.splitext(file)[1]=='.json':
                self.listwidget.addItem(file)
            

    def PositionChanged(self,position):
        self.video_slider.setValue(position)
    

    
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            
            self.start = event.pos()
            self.end = event.pos()
            self.lb_pos.setText(self.view.txt)
        
 
    
    def mouseMoveEvent(self, event):

        
        if event.buttons() == Qt.LeftButton:
            self.end = event.pos()
            
            if len(self.items)>0:
                # self.gScene.removeItem(self.items[-1])
                del(self.items[-1])
                
            rect = QRectF(self.start, self.end)
            pen = QPen(Qt.green)
            green20 = QColor(Qt.green)
            green20.setAlphaF(0.2)
            brush = QBrush(green20)
   
    def mouseReleaseEvent(self, event):
        self.status.scrollToBottom()

    
    #draw event        
    def drawROI(self):
        if self.file!='':
            if self.startFrame==0:
                print("[warning] Check Json file. ")
            position = self.fps*self.startFrame
            self.view.drawROI(position)
            #self.view.viewFrame(self.file)
        else:
            self.status.addItem("Select Video First !")
            self.status.scrollToBottom()
      #  self.rectitem = QGraphicsRectItem(self.videoitem)
        
    def clearROI(self):
        if self.file!='':
            pass
        else:
            self.status.addItem("Select Video First !")
            self.status.scrollToBottom()
        

        
    def send(self):
       # if self.file != '':
        self.roi_left = self.view.start.x()*self.view.ratio
        self.roi_top = self.view.start.y()*self.view.ratio
        self.roi_width =(self.view.end.x()-self.view.start.x())*self.view.ratio
        self.roi_height = (self.view.end.y()-self.view.start.y())*self.view.ratio
        self.status.addItem(" left , top    : {0},{1}".format(self.roi_left,self.roi_top))    
        self.status.addItem(" width, height : {0},{1}".format(self.roi_width, self.roi_height))    
        self.status.scrollToBottom()
        self.saveNewJson()
        
        self.ShowList()
        # else:
        #     self.status.addItem("Select Video First !")
        #     self.status.scrollToBottom()
       
    def saveNewJson(self):
        try:
            json_data = self.json_data
            for i in range(len(json_data['swipeperiod'])):
                json_data['swipeperiod'][i]['roi_left'] = self.roi_left
                json_data['swipeperiod'][i]['roi_top'] = self.roi_top
                json_data['swipeperiod'][i]['roi_width'] = self.roi_width
                json_data['swipeperiod'][i]['roi_height'] = self.roi_height
            
            data = json.dumps(json_data,indent=4)
        
            
            
            FileSave, _=QFileDialog.getSaveFileName(self, ' Save json file',  '.json')
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
            
            for i in range(len(json_data['swipeperiod'])):
                self.index_list.addItem("Swipe "+str(i+1))
                self.status.addItem("start frame is "+str(self.startFrame)+"    index : "+str(i))
                self.status.scrollToBottom()
                self.startFrame = json_data['swipeperiod'][i]['start']
            print(self.startFrame)
            
        except:
            self.status.addItem("[warning] Check the JSON file. (json file name = video file name)")
            self.status.scrollToBottom()
    
    def calcStabil(self):
        
        try :
            selected = self.listwidget.currentItem().text()
            try:
                subprocess.run("CMd.exe "+selected)
                self.status.addItem("Stabil Done.")
            except:
                self.status.addItem("Stabil Failed.")
        except:
            self.status.addItem("Please Select the New Json file")

    
    def RoiClear(self):
        pass 

    def paintEvent(self,event):
        pass


    
        
class CView(QGraphicsView):
    
    def __init__(self, parent):
        
        super(CView,self).__init__(parent)
        self.gScene = QGraphicsScene(self)
        # self.gScene.setSceneRect(0,0,self.parent().videoWidget.width(),self.parent().videoWidget.height())
        # pimg = QPixmap("frame.png")
        
        self.new_w = 1280
        self.new_h = 720
        self.ratio = 0
        self.vid_wid =0
        self.vid_hei = 0
        
        # self.scaled_img = pimg.scaled(QSize(1280,720),Qt.KeepAspectRatio)
        #self.gScene.addPixmap(scaled_img)
        
        self.setAlignment(Qt.AlignTop|Qt.AlignLeft)
    #    print(self.gScene.sceneRect().width())
    
        self.items = []
        self.start = QPointF()
        self.end = QPointF()
        self.file = ""
        self.position = QPointF()
        self.txt = ""
        self.first = True
 
        self.setRenderHint(QPainter.HighQualityAntialiasing)
        
        self.mediaPlayer = QMediaPlayer(self, QMediaPlayer.VideoSurface)
    #    self.videoWidget = QVideoWidget()
        
       
        self.videoitem = QGraphicsVideoItem() 
        self.videoitem.setPos(0,0)
        self.videoitem.setSize(QSizeF(self.new_w,self.new_h))
        self.rectitem = QGraphicsRectItem(self.videoitem)
        self.setScene(self.gScene)
        self.gScene.addItem(self.videoitem)
        self.parent().pb_play.clicked.connect(self.play)
        self.mediaPlayer.positionChanged.connect(self.setPosition)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)

    
    # def viewFrame(self, file):
    #     cap = cv2.VideoCapture(file)
    #     fps = cap.get(cv2.CAP_PROP_FPS)
    #     sleep_ms = int(np.round((1/fps)*500))
        
    #     self.gScene.addPixmap(file)    
        
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            
            self.start = event.pos()
            self.end = event.pos()
            txt = "(left, top) : {0} , {1} ".format(self.start.x(),self.start.y())
            print(txt)
            

    
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
        if file!=False:
            if self.first:
                video = QMediaContent((QUrl.fromLocalFile(file)))   
                
                self.mediaPlayer.setVideoOutput(self.videoitem)
                self.setScene(self.gScene)
                #self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
                self.mediaPlayer.setMedia(video)
            
            # self.fitInView(self.parent().videoWidget.rect(),Qt.KeepAspectRatio)
                self.mediaPlayer.play()   
                self.first = False

                vid = cv2.VideoCapture(file)
                self.vid_wid = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                
                self.ratio = self.vid_wid/self.new_w
                print(self.ratio)
            else:
                self.mediaPlayer.play()
                self.fitInView(self.gScene.sceneRect(),Qt.KeepAspectRatio)
        else:
            pass
    
    def pause(self):
        self.mediaPlayer.pause() 
        
    def stop(self):
        self.mediaPlayer.stop()
        
    def setPosition(self,position): 
        self.mediaPlayer.setPosition(position)    
      
        
    def drawROI(self,position):
        self.mediaPlayer.setPosition(position)
        self.pause()
        
    def clearROI(self):
        if len(self.items)>0:
            self.gScene.removeItem(self.items[-1])
            del(self.items[-1])

    def mediaStateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            pass

    def updateView(self):
        pass
        # scene = self.scene()

        # r = scene.sceneRect()
        # print('rect :{0} {1} {2} {3}' .format(r.x(), r.y(), r.width(), r.height()))

   
        
    def showEvent(self, event):
        if not event.spontaneous():
            print('show event')
            self.updateView()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.showMaximized()
    myWindow.show()
    app.exec_()