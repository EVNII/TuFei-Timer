from PySide6.QtCore import QThread, Signal
from queue import Queue
from typing import Callable
from time import sleep

class CompareThread(QThread):
    simularity = Signal(object)

    def __init__(self, compareFunc: Callable[[any], tuple[float, float]]):
        super().__init__()

        self.frame_queue = Queue(maxsize=8)
        self.compareFunc = compareFunc

    def run(self):
        while True:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                processed_frame = self.compareFunc(frame)
                self.simularity.emit(processed_frame)
            else:
                sleep(0.01)