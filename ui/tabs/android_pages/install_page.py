import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QComboBox, QLabel, 
                             QFileDialog, QListWidget, QTextEdit, 
                             QProgressBar, QMessageBox)
from core.adb_manager import AdbManager
from core.worker_thread import InstallWorker

class InstallPage(QWidget):
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab # To access shared data like current device
        self.current_directory = ""
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. Directory and File Selection
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("当前目录: 尚未选择")
        self.select_dir_btn = QPushButton("选择目录")
        self.select_dir_btn.clicked.connect(self.select_directory)
        
        dir_layout.addWidget(self.select_dir_btn)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addStretch()
        layout.addLayout(dir_layout)
        
        # APK List
        self.apk_list = QListWidget()
        layout.addWidget(QLabel("选择安装包 (.apk):"))
        layout.addWidget(self.apk_list)
        
        # 2. Install Button and Progress
        install_layout = QHBoxLayout()
        self.install_btn = QPushButton("开始安装")
        self.install_btn.setMinimumHeight(40)
        self.install_btn.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.install_btn.clicked.connect(self.start_installation)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        
        install_layout.addWidget(self.install_btn)
        layout.addLayout(install_layout)
        layout.addWidget(self.progress_bar)
        
        # 3. Log Area
        layout.addWidget(QLabel("安装日志:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #f0f0f0; font-family: monospace;")
        layout.addWidget(self.log_text)
        
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择包含 APK 的目录")
        if directory:
            self.current_directory = directory
            self.dir_label.setText(f"当前目录: {self.current_directory}")
            self.refresh_apk_list()
            
    def refresh_apk_list(self):
        self.apk_list.clear()
        apks = AdbManager.list_apks_in_directory(self.current_directory)
        if apks:
            self.apk_list.addItems(apks)
        else:
            self.apk_list.addItem("该目录下没有找到 .apk 文件")
            
    def append_log(self, text):
        self.log_text.append(text)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
            
    def start_installation(self):
        device_id = self.parent_tab.get_current_device()
        if not device_id or device_id == "未检测到设备":
            QMessageBox.warning(self, "警告", "请先在顶部选择有效设备。")
            return
            
        selected_items = self.apk_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请在列表中选择一个要安装的 APK 文件。")
            return
            
        apk_name = selected_items[0].text()
        if apk_name == "该目录下没有找到 .apk 文件":
            return
            
        apk_path = os.path.join(self.current_directory, apk_name)
        
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.log_text.clear()
        
        self.worker = InstallWorker(device_id, apk_path)
        self.worker.log_signal.connect(self.append_log)
        self.worker.finished_signal.connect(self.on_installation_finished)
        self.worker.start()
        
    def set_ui_enabled(self, enabled):
        self.select_dir_btn.setEnabled(enabled)
        self.apk_list.setEnabled(enabled)
        self.install_btn.setEnabled(enabled)
        self.parent_tab.set_sidebar_enabled(enabled)
        
    def on_installation_finished(self, success, message):
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        self.worker = None
        if success:
            QMessageBox.information(self, "成功", "应用安装成功！")
        else:
            QMessageBox.critical(self, "失败", f"应用安装失败！\n\n原因: {message}")
