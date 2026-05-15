from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QComboBox, QLabel, 
                             QListWidget, QStackedWidget, QFrame)
from PyQt5.QtCore import Qt
from core.adb_manager import AdbManager
from ui.tabs.android_pages.install_page import InstallPage
from ui.tabs.android_pages.explorer_page import ExplorerPage
from core.worker_thread import DeviceInfoWorker

class AndroidTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.hw_worker = None
        self.device_combo.currentTextChanged.connect(self.on_device_changed)
        self.refresh_devices()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # 1. Top Bar: Device Selection (Shared across pages)
        top_bar = QFrame()
        top_bar.setFrameShape(QFrame.StyledPanel)
        top_layout = QHBoxLayout(top_bar)
        
        device_label = QLabel("选择设备:")
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(250)
        self.refresh_btn = QPushButton("刷新设备")
        self.refresh_btn.clicked.connect(self.refresh_devices)
        
        self.hw_info_label = QLabel("硬件信息: 待加载")
        self.hw_info_label.setStyleSheet("color: #565f89; margin-left: 20px;")
        
        top_layout.addWidget(device_label)
        top_layout.addWidget(self.device_combo)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.hw_info_label)
        top_layout.addStretch()
        
        main_layout.addWidget(top_bar)
        
        # 2. Middle Area: Sidebar + Stacked Widget
        content_layout = QHBoxLayout()
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                color: white;
                border: none;
                font-size: 14px;
                padding-top: 10px;
            }
            QListWidget::item {
                height: 40px;
                padding-left: 10px;
            }
            QListWidget::item:selected {
                background-color: #34495e;
                border-left: 4px solid #3498db;
            }
        """)
        self.sidebar.addItem("安装应用")
        self.sidebar.addItem("数据资源管理器")
        self.sidebar.currentRowChanged.connect(self.on_nav_changed)
        
        # Pages Container
        self.pages_container = QStackedWidget()
        
        # Add Pages
        self.install_page = InstallPage(self)
        self.explorer_page = ExplorerPage(self)
        
        self.pages_container.addWidget(self.install_page)
        self.pages_container.addWidget(self.explorer_page)
        
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.pages_container)
        
        main_layout.addLayout(content_layout)
        
        # Select first item
        self.sidebar.setCurrentRow(0)
        
    def refresh_devices(self):
        self.device_combo.clear()
        devices = AdbManager.get_connected_devices()
        if devices:
            self.device_combo.addItems(devices)
        else:
            self.device_combo.addItem("未检测到设备")
            
    def get_current_device(self):
        return self.device_combo.currentText()
        
    def set_sidebar_enabled(self, enabled):
        self.sidebar.setEnabled(enabled)
        self.device_combo.setEnabled(enabled)
        self.refresh_btn.setEnabled(enabled)
        
    def on_nav_changed(self, index):
        self.pages_container.setCurrentIndex(index)
        if index == 1: # Explorer page
            self.explorer_page.load_packages()

    def on_device_changed(self, text):
        if not text or text == "未检测到设备":
            self.hw_info_label.setText("硬件信息: 未检测到设备")
            self.hw_info_label.setStyleSheet("color: #565f89; margin-left: 20px;")
            return
            
        self.hw_info_label.setText("硬件信息: 提取中...")
        self.hw_info_label.setStyleSheet("color: #c0caf5; margin-left: 20px;")
        
        if self.hw_worker and self.hw_worker.isRunning():
            self.hw_worker.terminate()
            
        self.hw_worker = DeviceInfoWorker(text)
        self.hw_worker.finished_signal.connect(self.on_hw_info_ready)
        self.hw_worker.start()
        
    def on_hw_info_ready(self, info):
        text = f"📱 {info.get('model', 'Unknown')} | ⚙️ {info.get('platform', 'Unknown')} | 🎮 {info.get('gpu', 'Unknown')} ({info.get('opengl', 'Unknown')})"
        self.hw_info_label.setText(text)
        self.hw_info_label.setStyleSheet("color: #00ffcc; font-weight: bold; margin-left: 20px;")
