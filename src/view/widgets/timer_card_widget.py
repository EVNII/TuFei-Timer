from skimage.color import rgb2gray
from utility.ssim_optimizer import SSIMOptimizer
from math import floor

from time import time
import cv2
import numpy as np

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from PySide6.QtGui import  QImage, QRegion
from PySide6.QtCore import Qt, QRect, QTimer

from qfluentwidgets import CardWidget, CaptionLabel, DisplayLabel, ToolButton, FluentIcon, ImageLabel, PrimaryToolButton, setCustomStyleSheet

class TimerCardWidget(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.status = "NOT_START"
        # "TIMING"
        # "PAUSE"


        self.startTime = None
        self.elapsed_time = 0
        self.elapsed_tp_time = 0
        self.current_tp_time = 0
        self.startTpTime = None

        self.isTp = False

        self.lastTpTime = None

        self.mainVBoxLayout = QVBoxLayout(self)
        

        self.comparedImage_day = ImageLabel("./assets/images/loading_daytime.png")
        self.comparedImage_day.scaledToWidth(self.width())
        self.comparedImage_day.setBorderRadius(2, 2, 2, 2)

        self.comparedImage_night = ImageLabel("./assets/images/loading_night.png")
        self.comparedImage_night.scaledToWidth(self.width())
        self.comparedImage_night.setBorderRadius(2, 2, 2, 2)

        self.similarityLabel_day = CaptionLabel("相似度: 0.00%", self)
        self.similarityLabel_night = CaptionLabel("相似度: 0.00%", self)

        self.timeLabel = DisplayLabel(self.format_time(0), self)

        self.tpTimeLabel = CaptionLabel('传送时间： '+ self.format_time(0), self)

        self.buttonsLayout = QHBoxLayout()

        self.startAndPauseButton = PrimaryToolButton(FluentIcon.PLAY)
        self.startAndPauseButton.clicked.connect(self.onStartAndPauseButtonClick)
        self.startAndPauseButton.setFixedSize(64,64)
        qss = 'PrimaryToolButton{border-radius: 32px}'
        setCustomStyleSheet(self.startAndPauseButton, qss, qss)

        self.stopButton = ToolButton(FluentIcon.SYNC)
        self.stopButton.clicked.connect(self.onStopButtonClick)
        self.stopButton.setFixedSize(48,48)
        qss = 'ToolButton{border-radius: 24px;}'
        setCustomStyleSheet(self.stopButton, qss, qss)


        sp_retain = self.stopButton.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.stopButton.setSizePolicy(sp_retain)

        self.stopButton.setVisible(False)

        self.buttonsLayout.addStretch(1)
        self.buttonsLayout.addWidget(self.startAndPauseButton, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.buttonsLayout.addWidget(self.stopButton, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.mainVBoxLayout.addWidget(self.comparedImage_day, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.mainVBoxLayout.addWidget(self.similarityLabel_day, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.mainVBoxLayout.addWidget(self.comparedImage_night, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.mainVBoxLayout.addWidget(self.similarityLabel_night, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.mainVBoxLayout.addWidget(self.timeLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.mainVBoxLayout.addWidget(self.tpTimeLabel, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        self.mainVBoxLayout.addLayout(self.buttonsLayout, 0)
        self.mainVBoxLayout.addStretch(1)

        self.setLayout(self.mainVBoxLayout)

        self.compared_target_image_day = rgb2gray(cv2.cvtColor(cv2.imread('./assets/images/loading_daytime.png'), cv2.COLOR_BGR2RGB))
        self.compared_target_image_day = (self.compared_target_image_day * 255).astype(np.uint8)

        self.ssimOpt_day = SSIMOptimizer(self.compared_target_image_day)

        self.compared_target_image_night = rgb2gray(cv2.cvtColor(cv2.imread('./assets/images/loading_night.png'), cv2.COLOR_BGR2RGB))
        self.compared_target_image_night = (self.compared_target_image_night * 255).astype(np.uint8)

        self.ssimOpt_night = SSIMOptimizer(self.compared_target_image_night)

        h, w = self.compared_target_image_day.shape
        ch = 1
        bytes_per_line = ch * w
        # self.comparedImage_day.setImage(QImage(self.compared_target_image_day.data, w, h, bytes_per_line, QImage.Format_Grayscale8))
        self.comparedImage_day.scaledToWidth(300)
        self.comparedImage_day.setBorderRadius(2, 2, 2, 2)

        # self.comparedImage_night.setImage(QImage(self.compared_target_image_night.data, w, h, bytes_per_line, QImage.Format_Grayscale8))
        self.comparedImage_night.scaledToWidth(300)
        self.comparedImage_night.setBorderRadius(2, 2, 2, 2)

        self.hwnd = -1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.timer.start()

    def compareWithImage(self, img: any) -> tuple[float, float]:
        simlarity_day = self.ssimOpt_day.structural_similarity(img, data_range=img.max() - img.min())
        simlarity_night = self.ssimOpt_night.structural_similarity(img, data_range=img.max() - img.min())

        simlarity = max(simlarity_day, simlarity_night)

        self.timeLabel.setTextColor('black')
        if self.status == "TIMING":
            if self.isTp == True:
                if simlarity > 0.95:
                    self.current_tp_time = self.elapsed_tp_time + (time() - self.startTpTime)
                    self.timeLabel.setTextColor('red')
                else:
                    self.elapsed_tp_time = self.elapsed_tp_time + (time() - self.startTpTime)
                    self.isTp = False
                    self.current_tp_time = self.elapsed_tp_time
                    self.timeLabel.setTextColor('black')
            elif self.isTp == False:
                if simlarity > 0.95:
                    self.startTpTime = time()
                    self.isTp = True
                    self.timeLabel.setTextColor('red')
                else:
                    pass

        return (simlarity_day, simlarity_night)

    def setSimilarity(self, simlarities) -> None:
        simlarity_day, simlarity_night = simlarities
        self.similarityLabel_day.setText("相似度: " + str(round(100 * simlarity_day, 2)) + "%")
        self.similarityLabel_night.setText("相似度: " + str(round(100 * simlarity_night, 2)) + "%")

    def onStartAndPauseButtonClick(self):
        if self.status == "NOT_START":
            self.startTime = time()
            self.status = "TIMING"
            self.startAndPauseButton.setIcon(FluentIcon.PAUSE)
        elif self.status == "TIMING":
            self.elapsed_time = self.elapsed_time + (time() - self.startTime)
            self.status = "PAUSE"
            self.startAndPauseButton.setIcon(FluentIcon.PLAY)

            self.stopButton.setVisible(True)

        elif self.status == "PAUSE":
            self.startTime = time()
            self.status = "TIMING"
            self.startAndPauseButton.setIcon(FluentIcon.PAUSE)
            self.stopButton.setVisible(False)

    def onStopButtonClick(self):
        if self.status == "NOT_START":
            pass
        elif self.status == "TIMING":
            pass
        elif self.status == "PAUSE":
            self.elapsed_time = 0
            self.elapsed_tp_time = 0
            self.current_tp_time = 0
            self.tpTimeLabel.setText('传送时间： '+ self.format_time(0))
            self.timeLabel.setText(self.format_time(0))
            self.status = "NOT_START"
            self.stopButton.setVisible(False)
            self.startAndPauseButton.setIcon(FluentIcon.PLAY)

    def format_time(self, seconds):
        minutes = floor(seconds / 60)
        seconds = floor(seconds % 60)
        return "{:02}:{:02}".format(minutes, seconds)
    
    def update_timer(self):
        if self.status == "TIMING":
            currentTime = self.elapsed_time + (time() - self.startTime) - self.current_tp_time 
            self.timeLabel.setText(self.format_time(currentTime))

            self.tpTimeLabel.setText('传送时间： '+ self.format_time(self.current_tp_time))

