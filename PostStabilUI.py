from pydoc import doc
import sys
from xml.etree.ElementTree import tostring
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

import cv2
import os
import json
import numpy as np
from datetime import datetime

ui = uic.loadUiType("PostStabilUI.ui")[0]

class MyWindow(QMainWindow, ui):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        
        self.file = None
        self.fps = 30
        self.json_data = []
        self.startFrame = 0
        
        
        
        self.ShowList()
        
        self.pb_import.clicked.connect(self.Open)
     
        self.pb_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pb_play.clicked.connect(self.Play)

        self.pb_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pb_pause.clicked.connect(self.Pause)

        self.pb_stop.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.pb_stop.clicked.connect(self.Stop)
    
        self.video_slider.sliderMoved.connect(self.SetPosition)
        
       
        
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.viewer)
        self.mediaPlayer.stateChanged.connect(self.MediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.PositionChanged)
        self.mediaPlayer.durationChanged.connect(self.DurationChanged)
        
        self.pb_draw.clicked.connect(self.RoiDraw)




    def Open(self):
        
        file_name,_ = QFileDialog.getOpenFileName(self,
                            "Open Video File",'','"Videos (*.mp4)')
        self.file = file_name
        
        json_file = os.path.splitext(file_name)[0]+'.json'
        print(json_file)
        self.ParseJson(json_file)
       
        self.filename.setText(self.file)    
        self.Preview()
        
    def ShowList(self):
        dir = QApplication.applicationDirPath()
        filelist = os.listdir(os.getcwd())
        for file in filelist:
            self.listwidget.addItem(file)
            
        
    def Preview(self):
        if self.file!='':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.file)))
        
        self.mediaPlayer.play()

    def Play(self):
        self.mediaPlayer.play()
    
    def Pause(self):
        self.mediaPlayer.pause()
        
    def Stop(self):
        self.mediaPlayer.stop()
        
        
    def SetPosition(self, position):
        self.mediaPlayer.setPosition(position)
        
    def PositionChanged(self,position):
        self.video_slider.setValue(position)
    
    def DurationChanged(self, duration):
        self.video_slider.setRange(0,duration)
        
    def MediaStateChanged(self, state):
        pass
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print("space")
            if self.mediaPlayer.state() ==QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()
            else:
                self.mediaPlayer.play()
            
    def RoiDraw(self):
        self.Pause()
        position = self.fps*self.startFrame
        self.mediaPlayer.setPosition(position)
        self.CreateMarker()

    def CreateMarker(self):
        bookmark = self(self.video_slider.value(),self)
        bookmark.show()
    
    def ParseJson(self, jsonfile):
        file = open(jsonfile)
        json_data = json.load(file)
        
        for i in range(len(json_data['swipeperiod'])):
            print(i)
            self.startFrame = json_data['swipeperiod'][i]['start']
            self.index_list.addItem("Swipe "+str(i+1))
        print(self.startFrame)
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.showMaximized()
    myWindow.show()
    app.exec_()