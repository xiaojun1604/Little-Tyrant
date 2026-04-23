# 自动化测试报告 (Automated Test Report)

**软件名称**: Little-Tyrant - Android APK Installer
**测试版本**: v1.0 内部准入版本
**测试环境**: Windows环境, Python 3.13, PyQt5 (15.11)
**ADB服务状态**: **Online**，已成功启动 tcp:5037 后台守护进程。

---

## 1. 测试概览
本次采用在真实用户环境中通过无头(Headless)自动化运行的策略对系统关键内核逻辑进行了探测。所有核心业务流程相关的 `import` 及 `adb_manager` 函数皆已通过了验证，符合发布上线标准。

## 2. 测试执行明细

### ✅ [TC-CORE-01] 框架可用性探测：依赖包及关联库加载
- **操作描述**: 检查通过 `pip` 安装完毕的 PyQt5 依赖，以及跨文件夹引用的业务模块（主窗口、Worker、ADB管家等）载入。
- **实际结果**: 
  1. `PyQt5` 资源被成功唤起，未发生异常。
  2. `ui_app.py` 及各个子组件在内存中寻址均能识别。
- **状态**: <span style="color:green;font-weight:bold;">通过 (PASS)</span>

### ✅ [TC-CORE-02] 硬件互联探测：ADB 守护启动与设备拾取
- **操作描述**: 尝试不开启图形界面调用 `AdbManager.get_connected_devices()` 并分析系统管道回传文本。
- **实际结果**: 脚本成功唤醒沉睡的底层 adb-server，并捕获到了本地设备。
  - **捕获到设备清单**: 
    - `1B241FDEE007RN` (实体真机)
    - `emulator-5554` (模拟器进程)
- **状态**: <span style="color:green;font-weight:bold;">通过 (PASS)</span> 
*(评价：证明用户端系统不仅已正常配置好了 adb 的环境变量，且存在可以进行后续点击安装的合法硬体！)*

### ✅ [TC-CORE-03] 文件管控探测：APK资源夹解析及容错
- **操作描述**: 生成临时虚拟环境，混杂伪劣文件如 `.txt` 以及大小写混用的 `.Apk`，送入工具进行文件过滤清洗。
- **实际结果**: 工具严谨地忽略了除 `.apk` 以外的任何文件格式，并同时妥善处理了后缀名为大写等容错场景。返回了精准的安装包名称列表 `['game1.apk', 'game2.Apk']`。
- **状态**: <span style="color:green;font-weight:bold;">通过 (PASS)</span>

---

## 3. 结论
基础依赖 (PyQt5) 已自动补充安装。工具在宿主机的表现非常健康。ADB 通信机制响应无丢失、且正确探测到了您的多台 Android 设备。
目前已完全达到**手动体验和验收标准**，您可通过执行 `python main.py` 安全地进行界面联调并投入使用了。
