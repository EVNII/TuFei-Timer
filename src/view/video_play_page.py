from src.view.widgets.video_compare_widget import VideoCompareWidget

from PySide6.QtWidgets import QFrame, QHBoxLayout, QFileDialog
from PySide6.QtCore import QUrl
from qfluentwidgets import PushButton, FluentIcon


class VideoPlayPage(QFrame):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setObjectName('VideoPlayPage')

        self.mainHBoxLayout = QHBoxLayout(self)

        self.selectFileButton = PushButton(FluentIcon.VIDEO, '打开视频')
        self.selectFileButton.setFixedSize(180, 38)
        self.selectFileButton.clicked.connect(self.open_dialog)

        self.videoPlayer = VideoCompareWidget(self)

        self.videoPlayer.setVisible(False)

        self.mainHBoxLayout.addWidget(self.videoPlayer)
        self.mainHBoxLayout.addWidget(self.selectFileButton)
        self.setLayout(self.mainHBoxLayout)

        self.video_path = None

    def setVideo(self, video_path:str):
        self.video_path = video_path
        video_url = QUrl.fromLocalFile(self.video_path)
        self.videoPlayer.setVideo(video_url)

    def open_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov *.mkv)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.video_path = selected_files[0]
                self.videoPlayer.setVideo(self.video_path)
                self.selectFileButton.setVisible(False)
                self.videoPlayer.setVisible(True)
    