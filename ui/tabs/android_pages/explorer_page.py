import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QListWidget, 
                             QTextEdit, QLabel, QSplitter, 
                             QFileDialog, QMessageBox, QShortcut)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence
from core.adb_manager import AdbManager

class ExplorerPage(QWidget):
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.current_package = None
        self.current_remote_path = ""
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        
        # --- Left: Package List ---
        pkg_container = QWidget()
        pkg_layout = QVBoxLayout(pkg_container)
        pkg_layout.setContentsMargins(0, 0, 5, 0)
        
        pkg_layout.addWidget(QLabel("搜索应用:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入包名筛选...")
        self.search_input.textChanged.connect(self.filter_packages)
        pkg_layout.addWidget(self.search_input)
        
        self.pkg_list = QListWidget()
        self.pkg_list.currentRowChanged.connect(self.on_package_selected)
        pkg_layout.addWidget(self.pkg_list)
        
        self.refresh_pkgs_btn = QPushButton("刷新应用列表")
        self.refresh_pkgs_btn.clicked.connect(self.load_packages)
        pkg_layout.addWidget(self.refresh_pkgs_btn)
        
        splitter.addWidget(pkg_container)
        
        # --- Center: File Browser ---
        file_container = QWidget()
        file_layout = QVBoxLayout(file_container)
        file_layout.setContentsMargins(5, 0, 5, 0)
        
        self.path_label = QLabel("路径: 请先选择应用")
        self.path_label.setStyleSheet("font-weight: bold; color: #34495e;")
        self.path_label.setWordWrap(True)
        file_layout.addWidget(self.path_label)
        
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("返回上级")
        self.back_btn.clicked.connect(self.navigate_up)
        self.copy_btn = QPushButton("复制到本地 (Ctrl+C)")
        self.copy_btn.clicked.connect(self.copy_to_local)
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.copy_btn)
        file_layout.addLayout(nav_layout)
        
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_list.itemSelectionChanged.connect(self.on_file_selected)
        file_layout.addWidget(self.file_list)
        
        splitter.addWidget(file_container)
        
        # --- Right: Preview ---
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(5, 0, 0, 0)
        
        preview_layout.addWidget(QLabel("文件预览 (文本格式/前50KB):"))
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("background-color: #fafafa; font-family: 'Consolas', monospace;")
        preview_layout.addWidget(self.preview_text)
        
        splitter.addWidget(preview_container)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 2)
        
        main_layout.addWidget(splitter)
        
        # Shortcuts
        self.shortcut_copy = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut_copy.activated.connect(self.copy_to_local)
        
    def load_packages(self):
        device_id = self.parent_tab.get_current_device()
        if not device_id or device_id == "未检测到设备":
            self.pkg_list.clear()
            return
            
        packages = AdbManager.get_installed_packages(device_id)
        self.pkg_list.clear()
        self.pkg_list.addItems(packages)
        
    def filter_packages(self, text):
        for i in range(self.pkg_list.count()):
            item = self.pkg_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
            
    def on_package_selected(self, index):
        if index < 0: return
        self.current_package = self.pkg_list.item(index).text()
        self.current_remote_path = f"/sdcard/Android/data/{self.current_package}"
        self.load_remote_files()
        
    def load_remote_files(self):
        device_id = self.parent_tab.get_current_device()
        self.path_label.setText(f"路径: {self.current_remote_path}")
        self.file_list.clear()
        self.preview_text.clear()
        
        items = AdbManager.list_remote_files(device_id, self.current_remote_path)
        if items:
            self.file_list.addItems(items)
        else:
            self.file_list.addItem("(空目录或无权限访问)")
            
    def on_file_double_clicked(self, item):
        name = item.text()
        if name.endswith("/"):
            self.current_remote_path = os.path.join(self.current_remote_path, name[:-1]).replace("\\", "/")
            self.load_remote_files()
            
    def navigate_up(self):
        if not self.current_package: return
        base_path = f"/sdcard/Android/data/{self.current_package}"
        if self.current_remote_path == base_path:
            return
        self.current_remote_path = os.path.dirname(self.current_remote_path).replace("\\", "/")
        self.load_remote_files()
        
    def on_file_selected(self):
        selected = self.file_list.selectedItems()
        if not selected: return
        name = selected[0].text()
        
        if not name.endswith("/") and name != "(空目录或无权限访问)":
            device_id = self.parent_tab.get_current_device()
            full_path = os.path.join(self.current_remote_path, name).replace("\\", "/")
            content = AdbManager.read_remote_file(device_id, full_path)
            self.preview_text.setText(content)
        else:
            self.preview_text.clear()
            
    def copy_to_local(self):
        selected = self.file_list.selectedItems()
        if not selected: return
        name = selected[0].text()
        if name == "(空目录或无权限访问)": return
        
        # For folders, we need to handle them differently or just pull recursive
        # Let's support both
        clean_name = name.rstrip("/")
        remote_full_path = os.path.join(self.current_remote_path, clean_name).replace("\\", "/")
        
        local_path = QFileDialog.getSaveFileName(self, "保存到本地", clean_name)[0]
        if local_path:
            device_id = self.parent_tab.get_current_device()
            success = AdbManager.pull_file(device_id, remote_full_path, local_path)
            if success:
                QMessageBox.information(self, "成功", f"文件已成功复制到:\n{local_path}")
            else:
                QMessageBox.critical(self, "失败", "复制失败，请检查设备连接或权限。")
