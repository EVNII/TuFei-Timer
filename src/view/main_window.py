from src.view.widget import Widget
from src.view.home_page import HomePage
from src.view.video_play_page import VideoPlayPage
from src.utility.get_correct_file_path import get_correct_file_path

from PySide6.QtCore import QSize, QEventLoop, QTimer
from PySide6.QtGui import QIcon
from qfluentwidgets import NavigationItemPosition, FluentWindow, SplashScreen
from qfluentwidgets import FluentIcon as FIF

class MainWindow(FluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()
        self.initWindow()
        
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(256, 256))

        self.show()
        
        loop = QEventLoop(self)
        QTimer.singleShot(2500, loop.quit)
        loop.exec()
        self.homeInterface = HomePage(self)
        self.videoPlayInterface = VideoPlayPage(self)
        self.settingInterface = Widget('Setting Interface', self)
        self.initNavigation()

        self.splashScreen.finish()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.addSubInterface(self.videoPlayInterface, FIF.VIDEO, '视频')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(1280, 720)
        # self.setFixedSize(1280, 720)
        self.setWindowIcon(QIcon(get_correct_file_path('assets/images/logo.png')))
        self.setWindowTitle('土肥杯计时器')