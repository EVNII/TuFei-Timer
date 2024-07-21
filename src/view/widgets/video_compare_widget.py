from src.utility.comopare_video_thread import CompareVideoThread
from src.utility.ssim_optimizer import SSIMOptimizer
from src.utility.get_correct_file_path import get_correct_file_path
from src.view.widgets.custom_media_player import CustomMediaPlayer
from PySide6.QtCore import QUrl, QTime

from math import floor
from time import time

import cv2

from skimage.color import rgb2gray
import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect, QHBoxLayout, QVBoxLayout, QGridLayout
from PySide6.QtGui import QPainter, QColor
from qfluentwidgets import ProgressBar, DisplayLabel, CompactTimeEdit, BodyLabel, PushButton
from qfluentwidgets.multimedia import VideoWidget
from PySide6.QtMultimedia import QMediaMetaData

class VideoCompareDetailPanelWidget(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.mainVBoxLayout = QVBoxLayout(self)

        self.timeSettingGridLayout = QGridLayout()

        self.startTimeEdit = CompactTimeEdit()
        self.startTimeEdit.setDisplayFormat("mm:ss")

        self.endTimeEdit = CompactTimeEdit()
        self.endTimeEdit.setDisplayFormat("mm:ss")

        #self.timeSettingGridLayout.addWidget(BodyLabel("入点"), 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        #self.timeSettingGridLayout.addWidget(self.startTimeEdit, 1, 0)

        self.timeSettingGridLayout.setColumnStretch(0,3)
        self.timeSettingGridLayout.setColumnStretch(1,1)
        self.timeSettingGridLayout.setColumnStretch(2,3)

        self.timeSettingGridLayout.setRowStretch(0, 1)
        self.timeSettingGridLayout.setRowStretch(1, 1)
        self.timeSettingGridLayout.setRowStretch(2, 1)

        #self.timeSettingGridLayout.addWidget(BodyLabel("出点"), 0, 2, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        #self.timeSettingGridLayout.addWidget(self.endTimeEdit, 1, 2)

        self.computingButton = PushButton("计算")
        self.timeSettingGridLayout.addWidget(self.computingButton, 2, 2, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        #self.computingResultLayout

        self.mainVBoxLayout.addLayout(self.timeSettingGridLayout, 3)

        self.progressBar = ProgressBar()
        self.progressBar.setRange(0, 1000)

        self.mainVBoxLayout.addWidget(self.progressBar)
        self.mainVBoxLayout.addWidget(BodyLabel("统计结果："))
        self.totalTime = BodyLabel("有效时长: 00:00/00:00")
        self.mainVBoxLayout.addWidget(self.totalTime)

        self.mainVBoxLayout.addStretch(10)
        self.setLayout(self.mainVBoxLayout)

        self.videoPath = None
        self.compareVideoThread = None

        self.computingButton.clicked.connect(self.onComputingButtonCliecked)


    def onComputingButtonCliecked(self):
        if self.compareVideoThread:
            self.compareVideoThread.requestInterruption()
        self.compareVideoThread = CompareVideoThread(self.videoPath)
        self.compareVideoThread.currentProgress.connect(self.progressBar.setValue)
        self.compareVideoThread.start()

        self.compareVideoThread.simularities.connect(self.parent.onSimilarityListUpdated)
        self.compareVideoThread.simularities.connect(self.onSimilarityListUpdated)

    
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)


        painter.setBrush(QColor(248, 248, 248))
        painter.setPen(QColor(0, 0, 0, 10))

        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)

    def onSimilarityListUpdated(self, similarities):
        totalTime = QTime(0, 0, 0)
        effectiveTime = QTime(0, 0, 0)
        frame_time = (1 / self.parent.customPlayer.metaData().value(QMediaMetaData.Key.VideoFrameRate))

        calculatedFrame = sum([1 for _ in similarities if _ != None])
        noTpFrame = sum([s < 0.92 for s in similarities if s != None])
        totalTime = totalTime.addSecs(calculatedFrame * frame_time)
        effectiveTime = effectiveTime.addSecs(noTpFrame * frame_time)

        self.totalTime.setText(f"有效时长: {effectiveTime.toString("mm:ss")}/{totalTime.toString("mm:ss")}")
        self.totalTime.update()


class VideoCompareWidget(VideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.detailPanel = VideoCompareDetailPanelWidget(self)

        self.customPlayer = CustomMediaPlayer(self.playBar)
        self.playBar.playButton.clicked.disconnect()
        self.playBar.setMediaPlayer(self.customPlayer)
        self.customPlayer.setVideoOutput(self.videoItem)

        

    def onSimilarityListUpdated(self, similarities):
        self.customPlayer.similarity = similarities

    def setVideo(self, video_path):
        video_url = QUrl.fromLocalFile(video_path)
        super().setVideo(video_url)
        self.detailPanel.videoPath = video_path


    def resizeEvent(self, e):
        super().resizeEvent(e)

        detialPanelMargin = 32

        self.detailPanel.move(detialPanelMargin + self.width() * 0.6, detialPanelMargin)
        self.detailPanel.setFixedSize(self.width() * 0.4 - 2 * detialPanelMargin, self.height() - self.playBar.height() - 2 * detialPanelMargin)