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

    @staticmethod
    def _get_pbk_paths():
        appdata = os.environ.get('APPDATA')
        programdata = os.environ.get('PROGRAMDATA')
        
        paths = []
        if appdata:
            paths.append(os.path.join(appdata, "Microsoft", "Network", "Connections", "Pbk", "rasphone.pbk"))
        if programdata:
            paths.append(os.path.join(programdata, "Microsoft", "Network", "Connections", "Pbk", "rasphone.pbk"))
        return paths

    @staticmethod
    def get_all_vpn_split_tunneling() -> dict:
        """Returns a dict mapping VPN names to their SplitTunneling status (True/False).
        True = Split Tunneling enabled (Routing Mode, IpPrioritizeRemote=0)
        False = Split Tunneling disabled (Global Mode, IpPrioritizeRemote=1)
        """
        result = {}
        pattern_section = re.compile(r"^\[(.*)\]$")
        pattern_ip = re.compile(r"^IpPrioritizeRemote=(\d)")
        
        for pbk_path in VpnManager._get_pbk_paths():
            if os.path.exists(pbk_path):
                try:
                    with open(pbk_path, 'r', encoding='utf-8', errors='ignore') as f:
                        current_vpn = None
                        for line in f:
                            line = line.strip()
                            match_sec = pattern_section.match(line)
                            if match_sec:
                                current_vpn = match_sec.group(1)
                                continue
                                
                            if current_vpn:
                                match_ip = pattern_ip.match(line)
                                if match_ip:
                                    val = match_ip.group(1)
                                    # IpPrioritizeRemote=1 means Global Mode (SplitTunneling = False)
                                    # IpPrioritizeRemote=0 means Routing Mode (SplitTunneling = True)
                                    result[current_vpn] = (val == '0')
                                    current_vpn = None # Wait for next section
                except Exception as e:
                    print(f"Error reading {pbk_path} for split tunneling: {e}")
                    
        return result

    @staticmethod
    def set_split_tunneling(vpn_name: str, enable_split: bool) -> tuple[bool, str]:
        """Sets SplitTunneling for the specified VPN by modifying the .pbk file."""
        target_val = '0' if enable_split else '1'
        pattern_section = re.compile(r"^\[(.*)\]$")
        
        for pbk_path in VpnManager._get_pbk_paths():
            if not os.path.exists(pbk_path):
                continue
                
            try:
                with open(pbk_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                found_vpn = False
                modified = False
                in_target_section = False
                
                for i, line in enumerate(lines):
                    match_sec = pattern_section.match(line.strip())
                    if match_sec:
                        if match_sec.group(1) == vpn_name:
                            in_target_section = True
                            found_vpn = True
                        else:
                            in_target_section = False
                        continue
                        
                    if in_target_section and line.strip().startswith("IpPrioritizeRemote="):
                        lines[i] = f"IpPrioritizeRemote={target_val}\n"
                        modified = True
                        break # Found and modified, no need to continue parsing
                        
                if found_vpn and modified:
                    with open(pbk_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    return True, "设置成功"
                    
            except Exception as e:
                return False, f"修改配置文件失败: {str(e)}"
                
        return False, "未找到对应的 VPN 配置文件"
