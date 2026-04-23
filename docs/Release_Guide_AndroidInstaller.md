# 软件发布与打包指南 (Release & Packaging Guide)

如果您希望将此 Python 开发的「APK安装工具」发布给团队其他成员，或者在没有 Python 环境的电脑上直接运行，建议将其打包为 **独立的 `.exe` 可执行文件**。

---

## 1. 准备打包环境

我们使用 Python 社区最常用的打包工具 `PyInstaller`。

1. **安装 PyInstaller**:
   打开终端并运行：
   ```cmd
   pip install pyinstaller
   ```

2. **验证环境**:
   确保您的项目目录结构完整，核心逻辑和 UI 组件都在对应的文件夹下。

---

## 2. 执行打包指令

在项目根目录 `e:\AI\Little-Tyrant` 下执行以下打包命令：

```cmd
pyinstaller --noconsole --onefile --name "LittleTyrantInstaller" --icon=NONE main.py
```

### **参数说明：**
- `--noconsole` (或 `-w`): 启动程序时不显示黑色的命令行窗口（GUI 程序必备）。
- `--onefile` (或 `-F`): 将所有依赖项、图片及代码压缩成一个单一的 `.exe` 文件，方便分发。
- `--name "LittleTyrantInstaller"`: 指定生成的可执行文件名。
- `main.py`: 指定主入口程序。

---

## 3. 获取发布产物

打包过程结束后，您的项目目录下会多出几个文件夹：
- **`dist/`**: **【核心】** 里面存放着您最终生成的 `LittleTyrantInstaller.exe`。
- `build/`: 存放打包过程中的临时文件，打包成功后可删除。
- `LittleTyrantInstaller.spec`: 打包配置文件，若后续需要定制（如添加外部资源），可修改此文件。

**发布方式**: 
您只需要将 `dist/` 文件夹下的 `LittleTyrantInstaller.exe` 发送给其他同事即可。对方机器**无需安装 Python** 也能直接双击运行。

---

## 4. 常见注意事项 (Tips)

1. **杀毒软件报毒**: 
   由于 `PyInstaller` 打包后的 `.exe` 没有数字签名，部分杀毒软件可能会拦截。建议分发时提醒用户“允许运行”或“添加信任”。
   
2. **多平台打包**: 
   - 在 Windows 上打包生成的是 `.exe`。
   - 如果需要 macOS 版本，必须在 macOS 环境下安装 PyInstaller 重复上述过程（生成的是 .app 或 Unix 可执行文件）。

3. **包含 ADB 工具**:
   如果对方电脑没有安装并配置 ADB 环境变量，该工具将无法工作。建议在发布时，将 `adb.exe` 及其关联的两个 `.dll` 文件随 `.exe` 一起放在同一个文件夹里发给用户，并在代码或文档中说明。
