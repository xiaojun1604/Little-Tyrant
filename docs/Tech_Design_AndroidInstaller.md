# 技术设计与架构文档 (Tech Design)

## 1. 技术栈选型
- **开发语言**：Python 3.8+ (保证跨平台性，丰富的基础库)。
- **GUI 框架选型界定**：推荐使用 **PyQt5** (或 PySide2/PySide6)。
  - **理由**：该框架对多标签页 (`QTabWidget`) 的支持极其规范，且拥有原生级的文件选择对话框 (`QFileDialog`)。最关键的是，其完善的`信号与槽机制 (Signals and Slots)`非常利于实现多线程中执行命令行时的 UI 异步刷新（处理安装日志）。
- **底层通信**：使用 Python 内置库 `subprocess` 调用 ADB 命令，无须引入过重的三方库。

## 2. 软件架构设计模式
基于“界面与逻辑分离”的原则进行模块化设计。

**推荐的模块划分设计：**
```text
Little-Tyrant/
├── core/
│   ├── __init__.py
│   ├── adb_manager.py     # 底层接口层：负责封装所有的 adb 命令调用如 devices, install
│   ├── worker_thread.py   # 线程逻辑层：继承 QThread，用于在后台执行安装任务而不阻塞 UI
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # UI主框架层：加载 QTabWidget 等最外层结构
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── android_tab.py # UI业务层：专处理 Android Tab 标签下的所有视觉交互和绑定
├── main.py                # 应用主入口文件
└── requirements.txt       # 依赖文件
```

## 3. 关键疑难点与解决方案
### 3.1. 避免安装过程中的 UI 线程“假死”
- **痛点**：执行 `adb install` 命令属于同步阻塞型 I/O，特别是游戏大包（1GB+）安装时耗时可达数分钟，若直接在 UI 线程执行会导致应用无响应（Not Responding）。
- **解决方案**：
  1. 通过集成 `QtCore.QThread` 将 `adb install` 命令下发到子线程中。
  2. 子线程通过 `subprocess.Popen` 时指定 `stdout=subprocess.PIPE` 与 `stderr=subprocess.STDOUT`，并持续 `readline()` 读取。
  3. 通过 `pyqtSignal(str)` 将读取到的日志行以信号发送给主线程。
  4. 主 UI 线程监听此信号，将日志行展示到 `QTextEdit` 中。

### 3.2. 安装进度条 (Progress Bar) 的模拟
- **痛点**：`adb install` 默认只在极少数阶段抛出具体的进度数字，较难实现精准的百分比进度预估。
- **解决方案**：
  在不使用较复杂 ADB 源码二次开发的前提下，我们将进度条设定为“跑马灯/不确定状态（Indeterminate）”模式，或通过日志特征（如 `Performing Streamed Install` -> `Success`）提供几个核心阶段跃进式的进度反馈（如 0% -> 30% -> 100%）。

### 3.3. 中文路径与编码问题
- **痛点**：Windows 系统下的终端可能出现中文字符串调用导致的 GBK 报错。
- **解决方案**：`subprocess` 调用时设置参数 `encoding='utf-8'` 或者系统的默认终端编码（根据操作系统适配）；通过 PyQt 的 `QFileDialog` 明确传递给 `adb_manager` 最原本的绝对路径进行安装。

## 4. 后续开发流程 (SOP)
1. **环境准备**：配置 `requirements.txt` 及对应的 Virtual Environment。
2. **基建代码**：实现 `adb_manager.py` 获取设备信息、实现安装包扫描函数。
3. **UI骨架搭建**：建立含 Android Tab 的主应用程序视窗（`main_window.py`）。
4. **绑定与联调**：使用槽函数连接子线程和 UI，打印日志验证功能。
5. **发布打包**：使用 `PyInstaller -w -F main.py` 将工具打包成单个独立的可执行文件（.exe），供普通用户免安装环境直接使用。
