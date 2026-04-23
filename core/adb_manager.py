import subprocess
import os

class AdbManager:
    @staticmethod
    def get_connected_devices():
        """Returns a list of connected ADB device IDs."""
        try:
            # We use startupinfo to hide the console window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            output = subprocess.check_output(
                ['adb', 'devices'], 
                startupinfo=startupinfo,
                encoding='utf-8', 
                errors='ignore'
            )
            
            devices = []
            lines = output.strip().split('\n')
            for line in lines[1:]:  # skip the first line "List of devices attached"
                parts = line.split()
                if len(parts) == 2 and parts[1] == 'device':
                    devices.append(parts[0])
            return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []
            
    @staticmethod
    def list_apks_in_directory(directory_path):
        """Returns a list of .apk files in the given directory."""
        if not directory_path or not os.path.isdir(directory_path):
            return []
        
        apks = []
        for file in os.listdir(directory_path):
            if file.lower().endswith('.apk'):
                apks.append(file)
        return apks
