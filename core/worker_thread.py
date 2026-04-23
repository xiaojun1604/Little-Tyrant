import subprocess
import os
from PyQt5.QtCore import QThread, pyqtSignal

class InstallWorker(QThread):
    # Signals to communicate with the main UI thread
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str) # success, message
    
    def __init__(self, device_id, apk_path):
        super().__init__()
        self.device_id = device_id
        self.apk_path = apk_path
        
    def run(self):
        self.log_signal.emit(f"开始向设备 {self.device_id} 安装应用...")
        self.log_signal.emit(f"APK文件: {self.apk_path}")
        
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            # Run adb install
            process = subprocess.Popen(
                ['adb', '-s', self.device_id, 'install', '-r', self.apk_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=startupinfo,
                text=True,
                encoding='utf-8',
                errors='replace' # Handle encoding issues gracefully
            )
            
            # Read output line by line
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.log_signal.emit(line.strip())
            
            return_code = process.wait()
            
            if return_code == 0:
                self.log_signal.emit("安装成功完成！")
                self.finished_signal.emit(True, "Success")
            else:
                self.log_signal.emit(f"安装失败，退出码: {return_code}")
                self.finished_signal.emit(False, f"Failed with code {return_code}")
                
        except Exception as e:
            self.log_signal.emit(f"执行异常: {str(e)}")
            self.finished_signal.emit(False, str(e))
