from utility.capture_window_thread import CaptureWindowThread

from time import time

from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer

from qfluentwidgets import CardWidget

class ScreenDisplayGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hwnd = -1
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        #self.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.capture_thread = None
        self.lastFrameUpdate = time()

    def start(self, hwnd):
        if self.capture_thread:
            self.capture_thread.stop()
        
        self.hwnd = hwnd
        self.capture_thread = CaptureWindowThread(self.hwnd)
        self.capture_thread.image_captured.connect(self.update_image)

        self.capture_thread.start()


    def update_image(self, img):
        h, w, ch = img.shape
        #h, w = img.shape
        #ch = 1
        bytes_per_line = ch * w
        #qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.pixmap_item.setPixmap(pixmap)
        self.setSceneRect(0, 0, w, h)
        self.adjust_view()
        currentTime = time()
        self.lastFrameUpdate = currentTime

    def adjust_view(self):
        view_width = self.viewport().width()
        view_height = self.viewport().height()
        scene_width = self.scene.width()
        scene_height = self.scene.height()

        width_ratio = view_width / scene_width
        height_ratio = view_height / scene_height
        scale_factor = min(width_ratio, height_ratio)

        self.resetTransform()
        self.scale(scale_factor, scale_factor)


class ScreenDisplayWidget(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vBoxlayout = QVBoxLayout()

        self.graphics_view = ScreenDisplayGraphicsView()
        self.graphics_view.setFixedSize(self.width(), self.height())
        self.vBoxlayout.addWidget(self.graphics_view, 0, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.vBoxlayout)

        self.hwnd = -1

    def _resizeEvent(self, event):
        super().resizeEvent(event)

        margin = 12
        height = self.height()
        width = self.width()

        aspect_ratio = height / width

        if(aspect_ratio > 16/9):
            frame_width = width - 2 * margin
            frame_height = frame_width * 9 / 16
        else:
            frame_height = height - 2 * margin
            frame_width = frame_height * 16 / 9

        
        frame_height = self.height() - 2 * margin
        frame_width = frame_height * 16/9

        self.graphics_view.setFixedSize(frame_width, frame_height)

    def get_graphic_view(self):
        return self.graphics_view