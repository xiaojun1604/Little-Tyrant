# 技术实现文档 (Tech Design) - Android 设备硬件信息模块 v1.0

## 1. 技术架构选型
基于现有的 `core/adb_manager.py` 进行功能扩充。利用 Python 标准库 `subprocess` 触发 `adb shell` 隐藏式命令执行，通过正则提取关键信息字符串。

## 2. 核心数据层 (`core/adb_manager.py`)

新增静态方法 `get_device_hardware_info(device_id: str) -> dict`:
- **返回数据结构**：
  ```python
  {
      "model": "Pixel 6",          # 手机型号
      "platform": "gs101",         # SoC 型号
      "gpu": "ARM, Mali-G78",      # GPU 型号
      "opengl": "OpenGL ES 3.2"    # OpenGL 版本
  }
  ```

### 2.1 硬件提取逻辑
- **获取设备基础型号**：
  执行 `adb -s {device_id} shell getprop ro.product.model` -> 返回 `Pixel 6` 等。
- **获取芯片平台**：
  执行 `adb -s {device_id} shell getprop ro.board.platform` -> 返回 `gs101` 或 `taro` 等。如果为空，尝试降级使用 `ro.hardware`。
- **获取 GPU 与 OpenGL 版本**：
  执行 `adb -s {device_id} shell dumpsys SurfaceFlinger`。
  由于输出文本巨大，使用 Python 处理输出文本流，按行查找包含 `GLES:` 的行。
  *样例：`GLES: ARM, Mali-G78, OpenGL ES 3.2 v1.r32p1...`*
  *正则/分割策略*：以逗号 `,` 为分隔符拆解。第一段+第二段作为 GPU 名称，第三段作为 OpenGL 版本，滤除后面冗余的驱动哈希值。

## 3. UI 视图层 (`ui/tabs/android_tab.py`)

在 `AndroidTab` 中已有的设备选择器（Device ComboBox）附近，植入一个新的极简信息展示面板。

### 3.1 视图结构修改
- 在设备选择下拉框的右侧或者正下方，加入一个 `QWidget` 作为“硬件信息卡片”。
- 卡片内部使用网格布局 (`QGridLayout`) 或横向标签 (`QHBoxLayout`) 展示属性名（深灰）和属性值（高亮蓝）。
- 为了应对文本长度变化，标签需要支持自动缩略或具有固定最大宽度。

### 3.2 异步加载防假死 (`core/worker_thread.py`)
- `dumpsys SurfaceFlinger` 是一个相对耗时的调用（可能需要 0.5 - 1.5 秒）。
- 若在设备列表 `currentIndexChanged` 信号中同步调用，会导致下拉框卡顿。
- **解决方案**：复用或新建一个继承自 `QThread` 的 `DeviceInfoWorker`，当用户切换设备时：
  1. UI 信息面板立刻清空，显示“Loading GPU info...”。
  2. 启动 Worker 传入新的 `device_id`。
  3. Worker 获取到数据后通过 `pyqtSignal` 传回主线程。
  4. 主线程解包 Dict 并将数值渲染至 QLabel 即可。
