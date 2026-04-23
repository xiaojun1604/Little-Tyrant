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
        try:
            for file in os.listdir(directory_path):
                if file.lower().endswith('.apk'):
                    apks.append(file)
        except Exception:
            pass
        return apks

    @staticmethod
    def get_installed_packages(device_id, filter_text=""):
        """Returns a list of installed package names on the device."""
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            # Use -3 to list only third-party apps by default if needed, 
            # but usually we want all or user apps.
            output = subprocess.check_output(
                ['adb', '-s', device_id, 'shell', 'pm', 'list', 'packages', '-3'],
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='ignore'
            )
            
            packages = []
            for line in output.strip().split('\n'):
                if line.startswith('package:'):
                    pkg = line.replace('package:', '').strip()
                    if not filter_text or filter_text.lower() in pkg.lower():
                        packages.append(pkg)
            return sorted(packages)
        except Exception as e:
            print(f"Error listing packages: {e}")
            return []

    @staticmethod
    def list_remote_files(device_id, remote_path):
        """Lists files and directories at the given remote path."""
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            # -F adds / to directories
            output = subprocess.check_output(
                ['adb', '-s', device_id, 'shell', 'ls', '-F', remote_path],
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='ignore'
            )
            
            items = []
            for line in output.strip().split('\n'):
                line = line.strip()
                if line:
                    items.append(line)
            return sorted(items)
        except Exception:
            return []

    @staticmethod
    def read_remote_file(device_id, remote_path, max_bytes=50000):
        """Reads the content of a remote file as text."""
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            # We use head to prevent loading massive files into memory
            output = subprocess.check_output(
                ['adb', '-s', device_id, 'shell', 'cat', remote_path, '|', 'head', '-c', str(max_bytes)],
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='replace' # Handle binary or encoding issues
            )
            return output
        except Exception as e:
            return f"无法读取文件内容: {str(e)}"

    @staticmethod
    def pull_file(device_id, remote_path, local_path):
        """Copies a file from the device to the local system."""
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.check_call(
                ['adb', '-s', device_id, 'pull', remote_path, local_path],
                startupinfo=startupinfo
            )
            return True
        except Exception:
            return False
