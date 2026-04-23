# GitHub Actions 自动化发布指南 (Auto-Release Guide)

是的，GitHub 完全可以实现自动化打包并发布多平台安装包。通过配置 **GitHub Actions**，您可以实现“只要推送到某个版本标签（如 `v1.0`），就自动生成 Windows 和 macOS 的安装包并同步创建 GitHub Release”。

---

## 1. 自动化流程说明

我已经为您配置好了工作流文件：`.github/workflows/release.yml`。其逻辑如下：
1. **触发条件**: 当您向 GitHub 仓库推送一个以 `v` 开头的标签（例如 `git tag v1.0.0` && `git push origin v1.0.0`）时，或者手动在 Actions 页面点击运行时触发。
2. **多环境构建**: 
   - 自动启动一个 **Windows** 云虚拟机进行打包生成 `.exe`。
   - 自动启动一个 **macOS** 云虚拟机进行打包生成 Mac 版可执行文件。
3. **自动发布**: 将两个平台的产物汇总并自动创建一个 GitHub Release，作为附件供下载。

---

## 2. 如何使用

### 第一步：将代码推送到 GitHub
确保您本地的所有修改（包括刚生成的 `.github` 目录）都已提交并推送到您的仓库：
```cmd
git add .
git commit -m "Add GitHub Actions auto-release workflow"
git push origin main
```

### 第二步：创建并推送版本标签
当您准备发布新版本时，在本地终端执行：
```cmd
git tag v1.0.0
git push origin v1.0.0
```

### 第三步：查看进度
1. 打开您的 GitHub 项目网页。
2. 点击顶部导航栏的 **Actions** 选项卡。
3. 您会看到一个名为 `Build and Release` 的工作流正在运行。
4. 运行结束后，点击项目右侧的 **Releases** 区域，即可看到生成的安装包。

---

## 3. 注意事项 (Important)

1. **GitHub Token 权限**: 默认情况下工作流有权限创建 Release。如果执行失败，请检查仓库设置：`Settings -> Actions -> General -> Workflow permissions` 确保勾选了 `Read and write permissions`。
2. **额外资源**: 如果您的工具将来需要集成特定的图片或数据文件，需要修改 `release.yml` 中的 `pyinstaller` 打包参数（例如使用 `--add-data`）。
3. **ADB 依赖**: 指南中提到的打包产物不包含 ADB 动态库。建议通过 `docs/Release_Guide_AndroidInstaller.md` 中提到的方式，将 ADB 工具手动随包分发。
