import subprocess
import os
import re

class VpnManager:
    @staticmethod
    def get_all_vpns():
        """Reads pbk files to get a list of all configured VPN names."""
        vpns = set()
        
        appdata = os.environ.get('APPDATA')
        programdata = os.environ.get('PROGRAMDATA')
        
        paths_to_check = []
        if appdata:
            paths_to_check.append(os.path.join(appdata, "Microsoft", "Network", "Connections", "Pbk", "rasphone.pbk"))
        if programdata:
            paths_to_check.append(os.path.join(programdata, "Microsoft", "Network", "Connections", "Pbk", "rasphone.pbk"))
            
        pattern = re.compile(r"^\[(.*)\]$")
        
        for pbk_path in paths_to_check:
            if os.path.exists(pbk_path):
                try:
                    with open(pbk_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            match = pattern.match(line.strip())
                            if match:
                                vpns.add(match.group(1))
                except Exception as e:
                    print(f"Error reading {pbk_path}: {e}")
                    
        return sorted(list(vpns))

    @staticmethod
    def get_connected_vpn():
        """Returns the name of the connected VPN, or None if no VPN is connected."""
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            output = subprocess.check_output(['rasdial'], startupinfo=startupinfo, encoding='gbk', errors='ignore')
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            
            if len(lines) >= 2 and ("已连接" in lines[0] or "Connected" in lines[0]):
                return lines[1]
                
            return None
        except Exception as e:
            print(f"Error checking connected VPN: {e}")
            return None

    @staticmethod
    def connect(vpn_name):
        """Connects to the specified VPN."""
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            subprocess.check_call(['rasdial', vpn_name], startupinfo=startupinfo)
            return True, "连接成功"
        except subprocess.CalledProcessError as e:
            return False, f"连接失败 (错误码: {e.returncode})。请确保您在系统中保存了账密。"
        except Exception as e:
            return False, f"连接异常: {str(e)}"

    @staticmethod
    def disconnect(vpn_name):
        """Disconnects the specified VPN."""
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            subprocess.check_call(['rasdial', vpn_name, '/DISCONNECT'], startupinfo=startupinfo)
            return True, "断开成功"
        except Exception as e:
            return False, f"断开异常: {str(e)}"

    @staticmethod
    def open_windows_settings():
        """Opens Windows VPN settings."""
        try:
            os.startfile("ms-settings:network-vpn")
        except Exception as e:
            print(f"Failed to open settings: {e}")
