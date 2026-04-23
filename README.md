# Little-Tyrant: Android APK 安装工具

一款基于 Python & PyQt5 开发的桌面端可视化 APK 安装工具。旨在简化 Android 应用的日常安装流程，提供跨平台支持并具备自动化的 CI/CD 发布能力。

## 核心功能
- **可视化设备管理**: 自动识别并下拉选择多台连接的 ADB 设备。
- **智能文件系统扫描**: 自动过滤目标目录下的所有 `.apk` 文件。
- **异步多线程安装**: 安装过程 UI 不卡顿，实时打印 ADB 终端日志。
- **进度反馈**: 提供视觉进度反馈及成功的弹窗提示。
- **跨平台 CI/CD**: 自动打包 Windows (.exe) 以及 macOS (Intel/Silicon) 双版本。

## 目录结构
- `/core`: 包含 ADB 管理及多线程逻辑。
- `/ui`: 包含 PyQt5 界面组件。
- `/docs`: 包含全套开发与测试文档（PRD, Tech Design, QA, Release, Debug）。
- `.github/workflows`: 自动化构建与发布流水线。

## 开发与文档
详细的开发文档已同步至本项目的 `docs/` 目录中，包括：
1. [产品需求文档 (PRD)](./docs/PM_PRD_AndroidInstaller.md)
2. [技术设计文档 (Tech Design)](./docs/Tech_Design_AndroidInstaller.md)
3. [测试用例与报告](./docs/QA_TestReport_AndroidInstaller.md)
4. [发布与打包指南](./docs/Release_Guide_AndroidInstaller.md)
5. [故障排除手册](./docs/Debug_Manual_AndroidInstaller.md)
