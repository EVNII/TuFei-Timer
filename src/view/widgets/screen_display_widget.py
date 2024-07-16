from src.utility.capture_window_thread import CaptureWindowThread

from time import time

from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QBrush, QPainter, QColor
from PySide6.QtCore import Qt, QSizeF

from qfluentwidgets import CardWidget

class ScreenDisplayGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hwnd = -1
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        qimg = QImage(1280, 720, QImage.Format_RGB32)
        qimg.fill(QColor(255, 255, 255))
        pixmap = QPixmap.fromImage(qimg)
        self.pixmap_item.setPixmap(pixmap)
        self.setSceneRect(0, 0, 1280, 720)
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

        self.capture_thread = None
        self.lastFrameUpdate = time()

        self.setStyleSheet("background: transparent")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def start(self, hwnd):
        if self.capture_thread:
            self.capture_thread.stop()
        self.hwnd = hwnd


    def update_image(self, img):
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.pixmap_item.setPixmap(pixmap)
        currentTime = time()
        self.lastFrameUpdate = currentTime

class ScreenDisplayWidget(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vBoxlayout = QVBoxLayout()

        self.graphics_view = ScreenDisplayGraphicsView()
        self.vBoxlayout.addWidget(self.graphics_view, 0, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.vBoxlayout)

        self.hwnd = -1

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.graphics_view.setGeometry(0, 0, self.width(), self.height())
        self.graphics_view.fitInView(self.graphics_view.pixmap_item, Qt.KeepAspectRatio)