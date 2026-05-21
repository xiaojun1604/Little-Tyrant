# 技术实现文档 (Tech Design) - Windows VPN 管理器 v1.0

## 1. 技术栈选型
基于 Python 标准库 `subprocess` 和 `os` 直接调用 Windows 的原生命令行工具来实现功能，无需引入第三方 C++ 扩展或厚重的网络库。
主要利用：
- `rasdial`: 用于建立连接、断开连接和检查当前活动连接。
- `.pbk` (电话簿) 文件解析: 用于获取系统中已配置的所有 VPN 名称。
- `ms-settings:network-vpn`: 用于唤起 Windows UWP 设置。

## 2. 核心逻辑层 (`core/vpn_manager.py`)

创建一个静态管理器类 `VpnManager`，封装以下方法：

### 2.1 `get_all_vpns() -> list[str]`
- **实现原理**：Windows 的 VPN 配置通常保存在两个路径下的 `rasphone.pbk` 文件中：
  1. 系统级：`%PROGRAMDATA%\Microsoft\Network\Connections\Pbk\rasphone.pbk`
  2. 用户级：`%APPDATA%\Microsoft\Network\Connections\Pbk\rasphone.pbk`
- **解析逻辑**：按行读取这两个文件，匹配以 `[` 开头并以 `]` 结尾的行（例如 `[v.corp.sdo.com]`），即可提取出所有的 VPN 连接名称并去重返回。

### 2.2 `get_connected_vpn() -> str | None`
- **实现原理**：通过 `subprocess.check_output(['rasdial'], encoding='gbk')` (需注意本地系统默认编码通常为 GBK) 获取输出。
- **解析逻辑**：如果输出包含“已连接”，则下一行通常就是当前连接的 VPN 名称。如果输出为“没有连接”，则返回 `None`。

### 2.3 `connect(vpn_name: str) -> tuple[bool, str]`
- **实现原理**：执行 `rasdial "{vpn_name}"`。
- **注意**：这种调用方式假定用户已经在系统中勾选了“记住我的登录信息”。如果 rasdial 挂起或提示需要账户密码，应捕获异常并返回错误信息提示用户前往系统设置补全凭据。

### 2.4 `disconnect(vpn_name: str) -> bool`
- **实现原理**：执行 `rasdial "{vpn_name}" /DISCONNECT`。检测返回码或输出确认断开成功。

### 2.5 `get_split_tunneling(vpn_name: str) -> bool`
- **实现原理**：通过 PowerShell 执行 `(Get-VpnConnection -Name "{vpn_name}").SplitTunneling`，获取当前的拆分隧道状态。
- **注意**：返回 `False` 意味着开启了“全局模式”（不拆分），返回 `True` 意味着是路由模式。由于涉及到 PowerShell 调用，批量查询可能耗时，建议在 `Worker` 或后台线程中执行。

### 2.6 `set_split_tunneling(vpn_name: str, enable_split: bool) -> bool`
- **实现原理**：通过 PowerShell 执行 `Set-VpnConnection -Name "{vpn_name}" -SplitTunneling $True` 或 `$False` 来修改配置。

### 2.7 `open_windows_settings()`
- **实现原理**：调用 `os.startfile("ms-settings:network-vpn")`。

## 3. UI 表现层 (`ui/tabs/vpn_tab.py`)

### 3.1 视图结构
- 继承自 `QWidget`，作为 `MainWindow` QTabWidget 的一个新标签。
- 顶部是一个 `QHBoxLayout` 的工具栏，包含：
  - “默认 VPN” 下拉框 (`QComboBox`)：在有多个 VPN 时可用。
  - “全局连接/断开” 按钮 (`QPushButton`)：作为全局开关。
  - “刷新列表” 和 “系统设置” 按钮。
- 中部使用一个 `QScrollArea` 加 `QVBoxLayout`（或直接使用定制的 `QListWidget`）来渲染每条 VPN 记录。
- **单条 VPN 记录布局**：包含 VPN 名称标签、状态指示灯、“全局模式” 复选框 (`QCheckBox`)、连接/断开按钮。

### 3.2 状态同步与定时器
- **定时器轮询**：为了保证状态与系统同步，初始化一个 `QTimer`，每 3 秒触发一次静默的 `get_connected_vpn()` 检查。
- 如果检测到当前连接的 VPN 发生改变（对比上次记录的值），则自动刷新 UI 上的状态指示灯、单条记录的按钮文字（连接/断开），以及顶部全局开关的状态和文本。

### 3.3 异步交互优化 (防界面假死)
- `rasdial` 拨号在网络不佳时可能阻塞数秒钟。
- **方案**：UI 线程不应被直接阻塞。建议使用 `QThread` 加 `pyqtSignal` 的方式去执行 `VpnManager.connect()`，期间界面显示“连接中...”，避免触发“程序未响应”。
