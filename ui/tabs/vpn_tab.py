from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, 
                             QListWidgetItem, QMessageBox, QComboBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from core.vpn_manager import VpnManager

class VpnWorker(QThread):
    finished = pyqtSignal(bool, str)
    
    def __init__(self, action, vpn_name, enable_split=None):
        super().__init__()
        self.action = action
        self.vpn_name = vpn_name
        self.enable_split = enable_split
        
    def run(self):
        if self.action == 'connect':
            success, msg = VpnManager.connect(self.vpn_name)
        elif self.action == 'disconnect':
            success, msg = VpnManager.disconnect(self.vpn_name)
        elif self.action == 'set_split':
            success, msg = VpnManager.set_split_tunneling(self.vpn_name, self.enable_split)
        elif self.action == 'reconnect_with_split':
            VpnManager.disconnect(self.vpn_name)
            success, msg = VpnManager.set_split_tunneling(self.vpn_name, self.enable_split)
            if success:
                success, msg = VpnManager.connect(self.vpn_name)
        self.finished.emit(success, msg)

class VpnTab(QWidget):
    def __init__(self):
        super().__init__()
        self.vpns = []
        self.connected_vpn = None
        self.split_tunneling_map = {}
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
        
        # Global Switch Controls
        self.default_vpn_combo = QComboBox()
        self.default_vpn_combo.setMinimumWidth(150)
        self.default_vpn_combo.setToolTip("默认要连接的 VPN")
        
        self.global_switch_btn = QPushButton("一键连接")
        self.global_switch_btn.setMinimumHeight(30)
        self.global_switch_btn.setStyleSheet("background-color: #3b4261; color: #a9b1d6; font-weight: bold;")
        self.global_switch_btn.clicked.connect(self.toggle_global_vpn)
        
        self.refresh_btn = QPushButton("刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_list)
        
        self.settings_btn = QPushButton("⚙️ 系统 VPN 设置")
        self.settings_btn.clicked.connect(VpnManager.open_windows_settings)
        
        toolbar.addWidget(QLabel("默认 VPN:"))
        toolbar.addWidget(self.default_vpn_combo)
        toolbar.addWidget(self.global_switch_btn)
        toolbar.addSpacing(20)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.settings_btn)
        
        main_layout.addLayout(toolbar)
        
        # VPN List
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)
        
    def refresh_list(self):
        self.vpns = VpnManager.get_all_vpns()
        self.split_tunneling_map = VpnManager.get_all_vpn_split_tunneling()
        self.connected_vpn = VpnManager.get_connected_vpn()
        self.update_combo_box()
        self.render_list()
        self.update_global_switch_ui()
        
    def update_combo_box(self):
        current_text = self.default_vpn_combo.currentText()
        self.default_vpn_combo.blockSignals(True)
        self.default_vpn_combo.clear()
        if self.vpns:
            self.default_vpn_combo.addItems(self.vpns)
            # Try to restore previous selection
            index = self.default_vpn_combo.findText(current_text)
            if index >= 0:
                self.default_vpn_combo.setCurrentIndex(index)
        self.default_vpn_combo.blockSignals(False)
        
    def update_global_switch_ui(self):
        if self.connected_vpn:
            self.global_switch_btn.setText("全部断开")
            self.global_switch_btn.setStyleSheet("background-color: #f77a7a; color: #1a1b26; font-weight: bold;")
        else:
            self.global_switch_btn.setText("一键连接")
            self.global_switch_btn.setStyleSheet("background-color: #7aa2f7; color: #1a1b26; font-weight: bold;")
            
        # Disable controls if no VPNs available
        has_vpns = len(self.vpns) > 0
        self.default_vpn_combo.setEnabled(has_vpns)
        self.global_switch_btn.setEnabled(has_vpns)
        
    def poll_status(self):
        if self.worker and self.worker.isRunning():
            return
            
        current = VpnManager.get_connected_vpn()
        if current != self.connected_vpn:
            self.connected_vpn = current
            self.render_list()
            self.update_global_switch_ui()

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
            
            # Split Tunneling (Global Mode) CheckBox
            # True means SplitTunneling is enabled -> Not Global
            # False means SplitTunneling is disabled -> Global
            is_global = not self.split_tunneling_map.get(vpn, True)
            global_cb = QCheckBox("全局模式")
            global_cb.setToolTip("开启后，所有网络流量都会经过该 VPN")
            global_cb.setChecked(is_global)
            global_cb.setStyleSheet("margin-right: 20px;")
            global_cb.clicked.connect(lambda checked, v=vpn: self.on_global_cb_clicked(v, checked))
            
            btn = QPushButton("断开" if is_connected else "连接")
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(80)
            if is_connected:
                btn.setStyleSheet("background-color: #f77a7a; color: #1a1b26;")
            
            btn.clicked.connect(lambda checked, v=vpn, connected=is_connected: self.toggle_vpn(v, connected))
            
            layout.addWidget(name_label)
            layout.addStretch()
            layout.addWidget(global_cb)
            layout.addWidget(status_label)
            layout.addWidget(btn)
            
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            
    def on_global_cb_clicked(self, vpn_name, is_global):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "警告", "正在执行操作，请稍候...")
            self.refresh_list()
            return
            
        enable_split = not is_global
        
        if vpn_name == self.connected_vpn:
            reply = QMessageBox.question(self, "确认", 
                                         "更改全局模式需要重新连接 VPN 才能生效。是否立即重连？",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.worker = VpnWorker('reconnect_with_split', vpn_name, enable_split)
                self.worker.finished.connect(self.on_worker_finished)
                self.worker.start()
                self.list_widget.setEnabled(False)
                self.global_switch_btn.setEnabled(False)
            else:
                self.refresh_list() # Revert checkbox
        else:
            self.worker = VpnWorker('set_split', vpn_name, enable_split)
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()
            self.list_widget.setEnabled(False)
            self.global_switch_btn.setEnabled(False)

    def toggle_vpn(self, vpn_name, is_connected):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "警告", "正在执行操作，请稍候...")
            return
            
        action = 'disconnect' if is_connected else 'connect'
        
        self.worker = VpnWorker(action, vpn_name)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()
        
        self.list_widget.setEnabled(False)
        self.global_switch_btn.setEnabled(False)
        
    def toggle_global_vpn(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "警告", "正在执行操作，请稍候...")
            return
            
        if self.connected_vpn:
            # We are connected, so disconnect the current one
            action = 'disconnect'
            vpn_name = self.connected_vpn
        else:
            # We are not connected, connect the default one
            action = 'connect'
            vpn_name = self.default_vpn_combo.currentText()
            if not vpn_name:
                QMessageBox.warning(self, "警告", "未找到可用的 VPN 配置。")
                return
                
        self.worker = VpnWorker(action, vpn_name)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()
        
        self.list_widget.setEnabled(False)
        self.global_switch_btn.setEnabled(False)
        
    def on_worker_finished(self, success, msg):
        self.list_widget.setEnabled(True)
        self.update_global_switch_ui() # re-enables switch btn based on vpns count
        if not success:
            QMessageBox.critical(self, "操作失败", msg)
        self.refresh_list()
