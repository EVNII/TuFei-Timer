from src.utility.windows import get_windows_frames

from time import time
from typing import Optional

import numpy as np
import cv2

from PySide6.QtCore import QThread, Signal
from queue import Queue

class CaptureWindowThread(QThread):
    image_captured = Signal(np.ndarray)

    def __init__(self, frameQueues: Queue):
        super().__init__()
        self.hwnd: Optional[int] = None
        self.running: bool = False

        self.frameQueues = frameQueues

    def run(self) -> None:
        if self.hwnd is None:
            self.running = False
            return

        self.running = True
        t = time()
        
        frame_generator = get_windows_frames(self.hwnd)
        while self.running:
            try:
                img = next(frame_generator)

                im_mono = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                
                if self.frameQueues.full():
                    self.frameQueues.get()

                
                self.frameQueues.put(im_mono)
                self.image_captured.emit(img)
            except RuntimeError as e:
                print(e)
                self.running = False
            except StopIteration:
                break

    def stop(self) -> None:
        self.running = False
        self.wait()

    def setHwnd(self, hwnd: int) -> bool:
        if self.running:
            return False
        
        self.hwnd = hwnd
        return True

        
