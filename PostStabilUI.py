from pydoc import doc
import sys
from xml.etree.ElementTree import tostring
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem

import cv2
import os
import json
import numpy as np
from datetime import datetime

import gc


ui = uic.loadUiType("PostStabilUI.ui")[0]

class MyWindow(QMainWindow, ui):

    def __init__(self, parent =None):
        super(MyWindow,self).__init__(parent)
        
        self.setupUi(self)
        self.setWindowTitle("Post Stabilization Program")
   
        self.file = None
        self.fps = 30
        self.json_data = []
        self.startFrame = 0
        self.start = QPointF()
        self.end = QPointF()
   


        self.ShowList()
        
        self.pb_import.clicked.connect(self.Open)
     
       
    
        # self.video_slider.sliderMoved.connect(self.SetPosition)
        
       
        
          # self.graphicsView = QGraphicsView(self.scene)
    #     self.scene = QGraphicsScene(self)
    #     # self.scene.setSceneRect(self.graphicsView.sceneRect())
        
    #     #self.scene.setSceneRect(0,0,960,540)
    #    # self.graphicsView.resize(1600,900)
    #     # self.graphicsView.setSceneRect(0,0,960,540)
    #     self.graphicsView.setScene(self.scene)
        
    #   #  self.scene.setSceneRect(self.graphicsView.mapFromScene())
        
    #     self.sceneRect = self.graphicsView.sceneRect()
    #     print(self.sceneRect.getRect())
    
        
      
        #self.graphicsView.setFixedSize(960,540)
        #self.graphicsView.setSceneRect(0,0,960,540)
        self.view = CView(self)
        self.lay.addWidget(self.view)
        
       
        # self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.graphicsView.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        
      #  self.graphicsView.fitInView(self.scene.sceneRect(),Qt::KeepAspectRatio)
        
        # self.videoitem = QGraphicsVideoItem()
        
        # self.rectitem = QGraphicsRectItem(self.videoitem)
        self.items = []
       
        
        #self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        # self.mediaPlayer = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        # self.mediaPlayer.stateChanged.connect(self.MediaStateChanged)
        # self.mediaPlayer.positionChanged.connect(self.PositionChanged)
        # self.mediaPlayer.durationChanged.connect(self.DurationChanged)
        # self.scene.addItem(self.videoitem)
       
        
       # self.mediaPlayer.setVideoOutput(self.videoitem)
        
        self.pb_draw.clicked.connect(self.RoiDraw)
        self.pb_delete.clicked.connect(self.RoiClear)
        self.pb_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pb_play.clicked.connect(self.view.play)

        self.pb_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pb_pause.clicked.connect(self.view.pause)

        self.pb_stop.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.pb_stop.clicked.connect(self.view.stop)
        self.lb_pos.setText(str(self.view.position))

    
     
   

    def Open(self):
        
        self.index_list.clear()
        
        file_name,_ = QFileDialog.getOpenFileName(self,
                            "Open Video File",'','"Videos (*.mp4)')
        self.file = file_name
        
        if self.file!='':
            json_file = os.path.splitext(file_name)[0]+'.json'
            print(json_file)
            self.ParseJson(json_file)
            self.view.play(self.file)
            # self.mediaPlayer.setVideoOutput(self.videoitem)
            # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.file)))
        
            # self.mediaPlayer.play()
            
            # testRect = self.scene.itemsBoundingRect()
            # print("testRect",testRect)
            # self.scene.setSceneRect(0,0,160,90)
           
           # self.graphicsView.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)
            #self.graphicsView.fitInView(self.videoitem,Qt.KeepAspectRatio)
            # print(self.videoitem.size())
            #self.graphicsView.fitInView(self.videoitem,Qt.KeepAspectRatio)
        # self.scene.setSceneRect(0,0,480,270)
        # rect = QRectF(self.rect())
        # rect.adjust(0,0,-2,-2)
        # self.scene.setSceneRect(rect)
        
        
        # self.graphicsView.fitInView(self.graphicsView.viewport.rect(),Qt.KeepAspectRatio)
        # self.graphicsView.centerOn(0,0)
        # print(self.scene.sceneRect())
        self.filename.setText(self.file)   
       
        # print(self.graphicsView.viewport().width())
        
      #  self.Preview()
       # self.Play()
        
    def ShowList(self):
        dir = QApplication.applicationDirPath()
        filelist = os.listdir(os.getcwd())
        for file in filelist:
            self.listwidget.addItem(file)
            
        
    # def Preview(self):
    #     if self.file!='':
            
    #         self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.file)))
            
    #         self.mediaPlayer.setVideoOutput(self.videoitem)
    #         self.graphicsView.fitInView(self.videoitem, Qt.KeepAspectRatio)
            
           
        
    #     self.mediaPlayer.play()
     

    # def Play(self):
    #     # self.graphicsView.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)
    #     if self.mediaPlayer.mediaChanged:
    #         # self.graphicsView.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)
    #         pass
    #     if self.file!='':
            
    #         self.mediaPlayer.play()
    
    # def Pause(self):
    #     self.mediaPlayer.pause()
        
    # def Stop(self):
    #     self.mediaPlayer.stop()
        
        
    # def SetPosition(self, position):
    #     self.mediaPlayer.setPosition(position)
        
    # def PositionChanged(self,position):
    #     self.video_slider.setValue(position)
    
    # def DurationChanged(self, duration):
    #     self.video_slider.setRange(0,duration)
        
    # def MediaStateChanged(self, state):
    #     if state == QMediaPlayer.PlayingState:
    #         pass
            # self.graphicsView.fitInView(self.videoitem,Qt.KeepAspectRatio)
        
    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Space:
    #         print("space")
    #         if self.mediaPlayer.state() ==QMediaPlayer.PlayingState:
    #             self.mediaPlayer.pause()
    #         else:
    #             self.mediaPlayer.play()
    
    
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            
            self.start = event.pos()
            self.end = event.pos()
        
    #     self.start[0], self.start[1] = event.localPos().x(), event.y()
    #     print("start", self.start)
      
            
    #   #  self.rectitem.clear()
    #     #gc.collect()
        
    #     width = self.end[0]-self.start[0]
    #     height = self.end[1]-self.start[1]
        

       # self.scene.removeItem(self.rectitem)
       
   
    
    def mouseMoveEvent(self, event):
       # print(self.graphicsView.mapToScene(event.pos()))
        # self.end[0], self.end[1] = event.x(), event.y()
        # self.update()
        # txt = "Position : {0} , {1} ".format(event.x(),event.y())
        # self.lb_pos.setText(txt)
        if event.buttons() == Qt.LeftButton:
            self.end = event.pos()
            
            if len(self.items)>0:
                # self.scene.removeItem(self.items[-1])
                del(self.items[-1])
                
            rect = QRectF(self.start, self.end)
            pen = QPen(Qt.green)
            green20 = QColor(Qt.green)
            green20.setAlphaF(0.2)
            brush = QBrush(green20)
            # self.items.append(self.scene.addRect(rect,pen,brush))
           
    def mouseReleaseEvent(self, event):
        # self.end[0], self.end[1] = event.x(), event.y()
        # print("end", self.end)
        # self.update()
        if event.buttons() == Qt.LeftButton:
            self.items.clear()
            rect = QRect(self.start, self.end)
            pen = QPen(Qt.green)
            green20 = QColor(Qt.green)
            green20.setAlphaF(0.2)
            brush = QBrush(green20)
            # self.scene.addRect(rect,pen,brush)
        
    
    #draw event        
    def RoiDraw(self):
        self.Pause()
        position = self.fps*self.startFrame
        self.mediaPlayer.setPosition(position)
      #  self.rectitem = QGraphicsRectItem(self.videoitem)
        
        
    #     palette = QPalette(self.palette())
    #   #  self.drawlb.setAutoFillBackground(True)
    #     palette.setColor(palette.Background, Qt.transparent)
    #     self.drawlb.setPalette(palette)
    #     self.drawlb.setAlignment(Qt.AlignCenter)
        #self.drawlb.setGeometry(self.viewer.x(),self.viewer.y(),self.viewer.width(),self.viewer.height())
        #self.drawlb.setGeometry(500,500,700,700)
    
       
        #self.drawlb.setStyleSheet("background-color: blue")
    
        #self.drawlb.setGeometry(1,1,1000,1000)
        
        #self.drawlb = QLabel('draw',self)

        print(self.viewer.x())
        print(self.viewer.y())
        
        
        
    def RoiClear(self):
        # self.scene.removeItem(self.rectitem)
        pass 
        #self.drawlb.setGeometry(self.viewer.)
       # self.CreateMarker()
       
    def paintEvent(self,event):
        pass
        # width = self.end[0]-self.start[0]
        # height = self.end[1]-self.start[1]
        
        # self.rectitem.setRect(self.start[0],self.start[1],width,height)
      #  self.rectitem.setBrush(QBrush(Qt.green))
        # self.rectitem.setPen(Qt.green)
        
        # self.rectitem = QGraphicsRectItem(QRectF(self.start[0],self.start[1],100,100),self.videoitem)
        # self.rectitem.setBrush(QBrush(Qt.green))
        # self.rectitem.setPen(Qt.red)
        
        # self.drawlb.setGeometry(self.start[0],self.start[1],self.end[0]-self.start[0],self.end[1]-self.start[1])
        # self.drawlb.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.drawlb.raise_()
        
       
        
    #     pixmap = QPixmap(self.drawlb.size())
    #    # pixmap = QPixmap(500,500)
    #     pixmap.fill(Qt.transparent)
    #     paint = QPainter(pixmap)
    #     brush = QBrush(QColor(40,240,150))
    #     paint.setBrush(brush)
    #     paint.drawRect(self.start[0],self.start[1],width,height)
    #     paint.end()
       # self.drawlb.setPixmap(pixmap)
      
        
        # paint = QPainter()
        # paint.begin(self)
        # brush = QBrush(QColor(40,240,150))
        # paint.setBrush(brush)
        # paint.drawRect(self.start[0],self.start[1],width,height)
        # paint.end()
        

  

    # def CreateMarker(self):
    #     bookmark = self(self.video_slider.value(),self)
    #     bookmark.show()
    
    
    def ParseJson(self, jsonfile):
        file = open(jsonfile)
        json_data = json.load(file)
        
        for i in range(len(json_data['swipeperiod'])):
            print(i)
            self.startFrame = json_data['swipeperiod'][i]['start']
            self.index_list.addItem("Swipe "+str(i+1))
        print(self.startFrame)
    
    
        
class CView(QGraphicsView):
    
    def __init__(self, parent):
        
        super(CView,self).__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
         
        self.items = []
        self.start = QPointF()
        self.end = QPointF()
        self.file = None
        self.position = QPointF()
 
        self.setRenderHint(QPainter.HighQualityAntialiasing)
        
        self.mediaPlayer = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.videoitem = QGraphicsVideoItem() 
        self.rectitem = QGraphicsRectItem(self.videoitem)
        self.scene.addItem(self.videoitem)
        self.parent().pb_play.clicked.connect(self.play)
        # self.mediaPlayer.stateChanged.connect(self.MediaStateChanged)
        # self.mediaPlayer.positionChanged.connect(self.PositionChanged)
        # self.mediaPlayer.durationChanged.connect(self.DurationChanged)
        
    def moveEvent(self, e):
        rect = QRectF(self.rect())
        rect.adjust(0,0,-2,-2)
 
        self.scene.setSceneRect(rect)
        
        
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            
            self.start = event.pos()
            self.end = event.pos()
    
    def mouseMoveEvent(self, event):
        self.position = event.pos()
        
        if event.buttons() == Qt.LeftButton:
            self.end = event.pos()
            
            if len(self.items)>0:
                self.scene.removeItem(self.items[-1])
                del(self.items[-1])
                
            rect = QRectF(self.start, self.end)
            pen = QPen(Qt.green)
            green20 = QColor(Qt.green)
            green20.setAlphaF(0.2)
            brush = QBrush(green20)
            self.items.append(self.scene.addRect(rect,pen,brush))
            
            
        
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
            self.scene.addRect(rect,pen,brush)
             
    def play(self, file):
        
        if file!='':
            self.mediaPlayer.setVideoOutput(self.videoitem)
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
            self.mediaPlayer.play()
        
    
    def pause(self):
        self.mediaPlayer.pause()
        
    def stop(self):
        self.mediaPlayer.stop()
# class Overlay(QWidget):
#     def __init__(self, parent = None):
#         QWidget.__init__(self, parent)
#         palette = QPalette(self.palette())
#         palette.setColor(palette.Background, Qt.transparent)
#         self.setPalette(palette)
        
#         self.start = [0,0]
#         self.end = [0,0]
        
#         self.drawlb = QLabel('-0-',self)
#         self.drawlb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        
#     def paintEvent(self,event):
#         width = self.end[0]-self.start[0]
#         height = self.end[1]-self.start[1]
        
#         paint = QPainter()
#         paint.begin(self)
#         brush = QBrush(QColor(40,240,150))
#         paint.setBrush(brush)
#         paint.drawRect(self.start[0],self.start[1],width,height)
#         paint.end()    
        
#         print(self.start)
        
#     def mousePressEvent(self, event):
#         self.start[0], self.start[1] = event.pos().x(), event.pos().y()
#         print("start", self.start)
        
#     def mouseMoveEvent(self, event):
#         self.end[0], self.end[1] = event.pos().x(), event.pos().y()
#         self.update()
    
#     def mouseReleaseEvent(self, event):
#         self.end[0], self.end[1] = event.pos().x(), event.pos().y()
#         print("end", self.end)
#         self.update() 
        
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.showMaximized()
    myWindow.show()
    app.exec_()