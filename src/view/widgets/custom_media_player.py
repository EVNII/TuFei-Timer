from collections import deque
import time
from qfluentwidgets.multimedia import MediaPlayer
from PySide6.QtMultimedia import QMediaMetaData
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtGui import QPainter, Qt

class CustomMediaPlayer(MediaPlayer):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.similarity = None

    def setVideoOutput(self, output: QGraphicsVideoItem):
        super().setVideoOutput(output)
        self.injectCustomLogic(output)

    def injectCustomLogic(self, output: QGraphicsVideoItem):
        original_paint = output.paint

        def custom_paint(painter, option, widget=None):
            original_paint(painter, option, widget)
            self.modifyFrame(painter)

        output.paint = custom_paint

    def modifyFrame(self, painter: QPainter):
        frame_rate = self.metaData().value(QMediaMetaData.Key.VideoFrameRate)
        currentFrame = self.getCurrentFrameNumber()
        totalFrame = int(self.metaData().value(QMediaMetaData.Key.Duration) * frame_rate / 1000) + 1

        # 绘制 FPS
        painter.setPen(Qt.red)
        painter.setFont(painter.font())
        painter.drawText(10, 10, f"Current Frame: {currentFrame}/{totalFrame}")

        if not self.similarity:
            return

        if self.similarity[currentFrame - 1]:
            if self.similarity[currentFrame - 1] > 0.93:
                painter.setPen(Qt.green)
            painter.drawText(10, 20, f"Similarity: {100 * self.similarity[currentFrame-1]:.2f}%")
        else:
            painter.drawText(10, 20, f"Similarity: Not Calculated yet!")

    def getCurrentFrameNumber(self):
        position = self.position()
        frame_rate = self.metaData().value(QMediaMetaData.Key.VideoFrameRate)
        return int(position * frame_rate / 1000) + 1