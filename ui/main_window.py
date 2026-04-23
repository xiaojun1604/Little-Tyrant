from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from ui.tabs.android_tab import AndroidTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Little Tyrant - APK Installer")
        self.resize(800, 600)
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Android Tab
        self.android_tab = AndroidTab()
        self.tabs.addTab(self.android_tab, "Android 工具")
        
        # Placeholder for iOS Tab
        self.ios_tab = QWidget()
        ios_layout = QVBoxLayout(self.ios_tab)
        ios_layout.addWidget(QLabel("iOS 工具预留页面（待开发）"))
        self.tabs.addTab(self.ios_tab, "iOS 工具")
