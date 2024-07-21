from PySide6.QtCore import QThread, Signal
from queue import Queue
from typing import Callable
from time import sleep
import cv2
import ffmpeg
import numpy as np
from src.utility.get_correct_file_path import get_correct_file_path
from src.utility.fast_ssim import SSIM
#from fast_ssim.ssim import SSIM
from skimage.color import rgb2gray
import numpy as np

class CompareVideoThread(QThread):
    simularities = Signal(object)
    currentProgress = Signal(int)

    def __init__(self, videPath):
        super().__init__()

        self.videoPath = videPath
        self.isRunning = True
        self.simularitiesList = []
        self.ffmpeg_path = get_correct_file_path('bin/ffmpeg.exe')
        self.ffmpeg_probe_path = get_correct_file_path('bin/ffprobe.exe')

        self.compared_target_image_day = rgb2gray(cv2.cvtColor(cv2.imread(get_correct_file_path('assets/images/loading_daytime.png')), cv2.COLOR_BGR2RGB))
        self.compared_target_image_day = (self.compared_target_image_day * 255).astype(np.uint8)
        self.compared_target_image_night = rgb2gray(cv2.cvtColor(cv2.imread(get_correct_file_path('assets/images/loading_night.png')), cv2.COLOR_BGR2RGB))
        self.compared_target_image_night = (self.compared_target_image_night * 255).astype(np.uint8)

        self.process = None

    def run(self):
        probe = ffmpeg.probe(self.videoPath, cmd=self.ffmpeg_probe_path)
        total_frame_count = int(probe['streams'][0]['nb_frames'])
        print("Totoal Frames: ", total_frame_count)
        self.simularitiesList = [None] * total_frame_count 
        self.simularities.emit(self.simularitiesList)

        self.process = (
            ffmpeg
            .input(self.videoPath)
            .output('pipe:', format='rawvideo', pix_fmt='gray', s='1280x720')
            .run_async(pipe_stdout=True, pipe_stderr=True, cmd=self.ffmpeg_path)
        )

        frame_number = 0
        frame_size = 1280 * 720
        while not self.isInterruptionRequested():
            in_bytes = self.process.stdout.read(frame_size)
            if not in_bytes:
                break
            frame = np.frombuffer(in_bytes, np.uint8).reshape([720, 1280, 1])
            result = max(SSIM(frame, self.compared_target_image_day), SSIM(frame, self.compared_target_image_night))
            self.simularitiesList[frame_number] = result
            self.simularities.emit(self.simularitiesList)
            self.currentProgress.emit(int(1000 * (1+frame_number)/total_frame_count))
            frame_number += 1
        self.process.stdout.close()
        self.process = None