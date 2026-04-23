# 故障排查与 Debug 调试手册 (Debug & Troubleshooting Manual)

当您在进行「APK安装工具」的手动测试过程中遇到非预期行为时，请按照本手册进行分层定位和调试。

---

## 1. 环境自检层 (Environment Layer)

### 1.1 Python/PyQt5 无法启动
- **现象**: 运行 `python main.py` 无任何反应或报错 `ModuleNotFoundError`。
- **Debug 步骤**:
  1. **检查 Python 版本**: 确保是 3.8+ 版本：`python --version`。
  2. **验证依赖库**: 执行 `pip list` 检查列表中是否有 `PyQt5`。
  3. **强制覆盖安装**: 如果 PyQt5 损坏，尝试 `pip install --force-reinstall PyQt5`。

### 1.2 ADB 命令无效
- **现象**: 报错 `adb 不是内部或外部命令`。
- **Debug 步骤**:
  1. **环境变量**: 检查系统 `Path` 是否包含 `platform-tools` 目录。
  2. **版本冲突**: 输入 `adb version`。建议使用 Google 官方最新 adb 版本（31及以上）。
  3. **端口占用**: 若 adb-server 无法启动，尝试 `adb kill-server` 后再 `adb devices` 指令重置。

---

## 2. 硬件连接层 (HARDWARE Connectivity Layer)

### 2.1 刷新设备列表为空
- **现象**: 手机已插入但工具内“刷新”不出。
- **Debug 步骤**:
  1. **终端二次验证**: 关闭工具，在 CMD 运行 `adb devices`。
  2. **状态检查**: 
     - 如果显示 `unauthorized`：请解锁手机，在弹出的窗口点击“允许 USB 调试”。
     - 如果显示 `offline`：重新拔插或手动启用开发者模式中的“撤销 USB 调试授权”。
  3. **驱动问题**: 检查设备管理器，确认是否存在 `Android Composite ADB Interface` 驱动。

---

## 3. 安装逻辑层 (Installation Logic Layer)

### 3.1 点击安装无反应 (UI假死监测)
- **现象**: 点击按钮后 UI 变灰，但日志不滚动，进度条不走。
- **Debug 步骤**:
  1. **查看控制台**: 观察启动工具的控制台窗口（CMD）是否有 Python 崩溃栈输出。
  2. **路径转义**: 检查 APK 文件路径是否包含及其罕见的特殊字符（如引号）。
  3. **进程自查**: 打开任务管理器，确认是否存在正在运行的 `adb.exe`。如果文件过大（如 2G+），推包过程可能需要几十秒，请耐心等待日志跳出 `Performing Streamed Install`。

### 3.2 常见的 ADB 报错 (Log Mapping)
通过工具底部的日志区域，您可以快速定位以下问题：
- **`INSTALL_FAILED_INSUFFICIENT_STORAGE`**: 手机存储空间不足。
- **`INSTALL_FAILED_UPDATE_INCOMPATIBLE`**: 手机已存在同包名应用但签名不一致，请手动卸载旧版后重装。
- **`INSTALL_FAILED_VERSION_DOWNGRADE`**: 尝试安装比手机当前版本更低的版本，无法直接覆盖，需先卸载。
- **`INSTALL_PARSE_FAILED_NOT_APK`**: 假冒的 APK 文件名或文件已损坏。

---

## 4. 开发者进阶 Debug (Advanced Debug)

如果您需要直接修改并调试代码逻辑，可以使用以下方式：

1. **启用详细日志**: 
   在 `core/worker_thread.py` 中，可以将 `subprocess.Popen` 的参数临时修改，移除 `startupinfo` 或手动打印 `process.args` 以查看工具发出的原始指令。
   
2. **测试脚本回归**:
   随时运行项目根目录下的 `test_runner.py`。该脚本绕过了 GUI，直接测试底层 `adb_manager` 的逻辑：
   ```cmd
   python test_runner.py
   ```
   如果测试脚本通过而 GUI 报错，则问题锁定在 `ui/tabs/android_tab.py` 的信号绑定上；反之，则是底层环境或 ADB 层面的问题。
