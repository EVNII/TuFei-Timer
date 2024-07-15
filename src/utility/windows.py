from dataclasses import dataclass
import win32gui
import win32ui
import ctypes.wintypes
from ctypes import windll
from PIL import Image
import cv2
import numpy as np
from ctypes import windll
import win32gui
import win32ui
import win32con

@dataclass
class Window:
    hwnd: int
    title: str

def get_windows_bytitle(expected_title: str, exact : bool = False) -> list[Window]:
    def window_callback(hwnd: int, windows: list[Window]) -> None:
        title = win32gui.GetWindowText(hwnd)
        if title:
            windows.append(Window(hwnd = hwnd, title = win32gui.GetWindowText(hwnd)))
    windows: list[Window] = []
    win32gui.EnumWindows(window_callback, windows)
    if expected_title == '':
        return windows

    if exact:
        return [w for w in windows if w.title == expected_title]
    else:
        return [w for w in windows if w.title in expected_title]
    
from contextlib import contextmanager



def get_windows_frames(hWnd):
    def get_window_rect(hwnd):
        try:
            f = ctypes.windll.dwmapi.DwmGetWindowAttribute
        except WindowsError:
            f = None
        if f:
            rect = ctypes.wintypes.RECT()
            DWMWA_EXTENDED_FRAME_BOUNDS = 9
            f(ctypes.wintypes.HWND(hwnd),
            ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
            ctypes.byref(rect),
            ctypes.sizeof(rect))
            return rect.left, rect.top, rect.right, rect.bottom
    left, top, right, bot = get_window_rect(hWnd)
    width = right - left
    height = bot - top

    hWndDC = win32gui.GetWindowDC(hWnd)
    mfcDC = win32ui.CreateDCFromHandle(hWndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    try:
        while True:
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
            signedIntsArray = saveBitMap.GetBitmapBits(True)

            im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
            im_opencv.shape = (height, width, 4)
        
            im_opencv = cv2.resize(im_opencv, (1280, 720), interpolation=cv2.INTER_LINEAR)
            im_opencv = cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2RGB)
            yield im_opencv
    finally:
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hWnd, hWndDC)
        print("Resources have been released")