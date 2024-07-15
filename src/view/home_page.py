from utility.windows import Window, get_windows_bytitle
from utility.run_sync_function_in_executor import run_sync_function_in_executor
from utility.capture_window_thread import CaptureWindowThread
from utility.compare_thread import CompareThread

from view.widgets.screen_display_widget import ScreenDisplayWidget
from view.widgets.timer_card_widget import TimerCardWidget

import asyncio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QWidgetAction
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from qfluentwidgets import ToolButton, FluentIcon, ComboBox, ToolTipFilter, ToolTipPosition

class HomePage(QFrame):
    windowsList : list[Window] = []
    currentWindow : int | None = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        

        self.mainHBoxLayout = QHBoxLayout()
        self.leftVBoxLayout = QVBoxLayout()

        self.selectWindowsHBoxLayout = QHBoxLayout()

        self.gameDisplayWidget = ScreenDisplayWidget()
        
        self.windowsComboBox = ComboBox()
        self.windowsComboBox.setPlaceholderText('请选择原神窗口')
        self.windowsComboBox.setCurrentIndex(-1)
        self.windowsComboBox.setFixedWidth(256)

        self.updateWindowsAction = QWidgetAction(self)
        self.updateWindowsAction.setStatusTip("刷新窗口选项")
        self.updateWindowsAction.triggered.connect(self.onUpdateWindows)

        self.connectWindowsAction = QWidgetAction(self)
        self.connectWindowsAction.setStatusTip("连接窗口")
        self.connectWindowsAction.triggered.connect(self.onConnectWindows)

        self.updateWindowsButton = ToolButton(FluentIcon.UPDATE)
        self.updateWindowsButton.setToolTip('刷新窗口选项')
        self.updateWindowsButton.installEventFilter(ToolTipFilter(self.updateWindowsButton, showDelay=300, position=ToolTipPosition.TOP))
        self.updateWindowsButton.clicked.connect(self.updateWindowsAction.trigger)

        self.connectWindowsButton = ToolButton(FluentIcon.CONNECT)
        self.connectWindowsButton.setToolTip('连接窗口')
        self.connectWindowsButton.installEventFilter(ToolTipFilter(self.connectWindowsButton, showDelay=300, position=ToolTipPosition.TOP))
        self.connectWindowsButton.clicked.connect(self.connectWindowsAction.trigger)

        self.selectWindowsHBoxLayout.addWidget(self.windowsComboBox, 0, Qt.AlignmentFlag.AlignLeft)
        self.selectWindowsHBoxLayout.addWidget(self.updateWindowsButton, 0, Qt.AlignmentFlag.AlignLeft)
        self.selectWindowsHBoxLayout.addWidget(self.connectWindowsButton, 1, Qt.AlignmentFlag.AlignLeft)

        self.leftVBoxLayout.addWidget(self.gameDisplayWidget)
        self.leftVBoxLayout.addLayout(self.selectWindowsHBoxLayout)

        self.timerCard = TimerCardWidget(self)

        self.mainHBoxLayout.addLayout(self.leftVBoxLayout)
        self.mainHBoxLayout.addWidget(self.timerCard)
        
        self.setLayout(self.mainHBoxLayout)

        self.compare_thread = CompareThread(self.timerCard.compareWithImage)
        self.compare_thread.simularity.connect(self.timerCard.setSimilarity)

        self.capture_thread = CaptureWindowThread(self.compare_thread.frame_queue)
        self.capture_thread.image_captured.connect(self.gameDisplayWidget.graphics_view.update_image)

        self.setObjectName('HomePage')

    def onUpdateWindows(self):
        asyncio.ensure_future(self.onUpdateWindowsAsync())


    async def onUpdateWindowsAsync(self):
        HomePage.windowsList = await run_sync_function_in_executor(get_windows_bytitle, "原神")

        self.windowsComboBox.clear()
        self.windowsComboBox.addItems([w.title for w in HomePage.windowsList])
        self.windowsComboBox.update()

    def onConnectWindows(self):
        self.capture_thread.stop()
        hwnd = HomePage.windowsList[self.windowsComboBox.currentIndex()].hwnd
        HomePage.currentWindow = hwnd
        print("Connect to: " + str(hwnd))

        self.compare_thread.start()

        self.capture_thread.setHwnd(hwnd)
        self.capture_thread.start()