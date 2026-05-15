from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, 
                             QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from core.vpn_manager import VpnManager

class VpnWorker(QThread):
    finished = pyqtSignal(bool, str)
    
    def __init__(self, action, vpn_name):
        super().__init__()
        self.action = action
        self.vpn_name = vpn_name
        
    def run(self):
        if self.action == 'connect':
            success, msg = VpnManager.connect(self.vpn_name)
        else:
            success, msg = VpnManager.disconnect(self.vpn_name)
        self.finished.emit(success, msg)

class VpnTab(QWidget):
    def __init__(self):
        super().__init__()
        self.vpns = []
        self.connected_vpn = None
        self.worker = None
        self.init_ui()
        
        # Timer for polling VPN status
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_status)
        self.timer.start(3000)
        
        self.refresh_list()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Top toolbar
        toolbar = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_list)
        
        self.settings_btn = QPushButton("⚙️ 系统 VPN 设置")
        self.settings_btn.clicked.connect(VpnManager.open_windows_settings)
        
        toolbar.addWidget(self.refresh_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.settings_btn)
        
        main_layout.addLayout(toolbar)
        
        # VPN List
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)
        
    def refresh_list(self):
        self.vpns = VpnManager.get_all_vpns()
        self.connected_vpn = VpnManager.get_connected_vpn()
        self.render_list()
        
    def poll_status(self):
        if self.worker and self.worker.isRunning():
            return
            
        current = VpnManager.get_connected_vpn()
        if current != self.connected_vpn:
            self.connected_vpn = current
            self.render_list()

    def render_list(self):
        self.list_widget.clear()
        
        if not self.vpns:
            self.list_widget.addItem("未找到系统 VPN 配置")
            return
            
        for vpn in self.vpns:
            item = QListWidgetItem()
            
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(10, 5, 10, 5)
            
            is_connected = (vpn == self.connected_vpn)
            status_text = "🟢 已连接" if is_connected else "⚪ 未连接"
            status_color = "#00ffcc" if is_connected else "#565f89"
            
            name_label = QLabel(vpn)
            name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
            
            status_label = QLabel(status_text)
            status_label.setStyleSheet(f"color: {status_color}; font-weight: bold; margin-right: 20px;")
            
            btn = QPushButton("断开" if is_connected else "连接")
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(80)
            if is_connected:
                btn.setStyleSheet("background-color: #f77a7a; color: #1a1b26;")
            
            btn.clicked.connect(lambda checked, v=vpn, connected=is_connected: self.toggle_vpn(v, connected))
            
            layout.addWidget(name_label)
            layout.addStretch()
            layout.addWidget(status_label)
            layout.addWidget(btn)
            
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            
    def toggle_vpn(self, vpn_name, is_connected):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "警告", "正在执行操作，请稍候...")
            return
            
        action = 'disconnect' if is_connected else 'connect'
        
        self.worker = VpnWorker(action, vpn_name)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()
        
        self.list_widget.setEnabled(False)
        
    def on_worker_finished(self, success, msg):
        self.list_widget.setEnabled(True)
        if not success:
            QMessageBox.critical(self, "操作失败", msg)
        self.refresh_list()
