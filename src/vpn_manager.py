import subprocess
import psutil

def disconnect():
    try:
        subprocess.run('nordvpn -d', shell=True, check=True, cwd=r"C:\Program Files\NordVPN")
    except subprocess.CalledProcessError:
        pass


def connect():
    try:
        subprocess.run('nordvpn -c -g "United States"', shell=True, check=True, cwd=r"C:\Program Files\NordVPN")
    except subprocess.CalledProcessError:
        pass


def is_nordvpn_running():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == 'NordVPN.exe':
            return True
    return False
