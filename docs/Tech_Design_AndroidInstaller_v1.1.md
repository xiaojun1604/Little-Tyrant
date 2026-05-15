# 技术设计文档 (Tech Design) - v1.1.0 架构升级

## 1. UI 架构重构
为了实现侧边栏功能，我们将对 `AndroidTab` 类进行重构。

- **导航控制**: 使用 `QListWidget` 或自定义的 `QPushButtonGroup` 作为左侧 SideBar。
- **视图展示**: 使用 `QStackedWidget` 作为右侧的内容承载器。
- **页面解耦**: 将原本在 `AndroidTab` 里的 UI 代码抽离到两个独立的子类：
  - `AndroidInstallPage`: 负责 APK 安装。
  - `AndroidDataPullPage`: 负责数据同步。

## 2. 模块划分更新
```text
ui/tabs/
├── android_tab.py         # 聚合类，维护 SideBar 和 QStackedWidget
├── android_pages/         # 新增目录
│   ├── __init__.py
│   ├── install_page.py    # 迁移后的安装逻辑
│   ├── data_pull_page.py  # 新增的数据同步界面逻辑
```

## 3. 核心功能实现方案：应用数据资源管理器 (Data Explorer)
### 3.1. 应用列表获取与搜索 (Package Discovery)
- **获取列表**: 通过 `adb shell pm list packages -3` (获取三方应用) 或全部包名。
- **搜索优化**: 使用 `QSortFilterProxyModel` 或简单的 `QLineEdit` 信号配合列表过滤实现毫秒级搜索响应。

### 3.2. 远程文件浏览 (Remote File Browsing)
- **逻辑模型**: 选中包名后，后台执行 `adb shell ls -F /sdcard/Android/data/{package_name}/` 获取首层目录。
- **动态加载**: 为了性能，采用“点击展开”加载模式，仅在展开文件夹时拉取其下层内容。

### 3.3. 文件操作逻辑
- **复制与导出 (ADB Pull)**: 
  - 使用 `QClipboard` 模拟粘贴板逻辑，或直接在选中时缓存路径。
  - 支持 `Ctrl+C` 快捷键捕获，触发 `adb pull {remote_path} {temp_or_target_local_path}`。
- **上传与替换 (ADB Push)**:
  - 提供上传按钮或支持文件拖拽到目录视图。底层触发 `adb push {local_path} {remote_path}` 操作，实现文件上传或同名覆盖替换。
- **文本预览与编辑**:
  - 小型文件直接通过 `adb shell cat {remote_path}` 读取流并展示在可编辑的 `QTextEdit` 中。
  - 增加“保存”按钮。用户修改并保存时，将 `QTextEdit` 的文本写入本地临时文件，再通过 `adb push {temp_local_path} {remote_path}` 推送到设备覆盖原文件，最后清理临时文件。
  - 对于二进制或超大文件，增加安全截断或二进制检测逻辑，避免界面卡死，并禁用编辑功能。

## 4. 迁移与开发 SOP
1. **基础重构**: 完成 `QStackedWidget` 侧边栏框架。
2. **迁移功能**: 将 APK 安装逻辑移入 `install_page.py`。
3. **开发 Explorer**: 
   - 实现包名异步加载与搜索框逻辑。
   - 实现文件列表渲染。
   - 实现 `adb shell cat` 预览、`adb pull` 复制导出、文件 `adb push` 上传替换及文本编辑保存逻辑。
4. **集成测试**: 验证文件传输的完整性及编码（UTF-8）显示正确性。
