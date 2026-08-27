import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_as_admin():
    """Re-run the script with admin privileges if not already elevated."""
    if sys.platform == 'win32':
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

def kill_edge_processes():
    """Terminate all Edge-related processes."""
    edge_processes = [
        "msedge.exe",
        "MicrosoftEdge.exe",
        "MicrosoftEdgeCP.exe",
        "MicrosoftEdgeSH.exe",
        "setup.exe"
    ]
    
    for proc in edge_processes:
        try:
            subprocess.run(["taskkill", "/F", "/IM", proc], capture_output=True)
            print(f"Killed process: {proc}")
        except:
            pass

def remove_edge_directories():
    """Remove Edge installation directories."""
    edge_paths = [
        Path(os.environ.get("PROGRAMFILES(x86)", r"C:\Program Files (x86)")) / "Microsoft" / "Edge",
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Microsoft" / "Edge",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge",
        Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Microsoft Edge",
        Path.home() / "AppData" / "Local" / "Microsoft" / "Edge",
        Path.home() / "AppData" / "Roaming" / "Microsoft" / "Edge",
        Path(r"C:\Windows\SystemApps\Microsoft.MicrosoftEdge_8wekyb3d8bbwe"),
        Path(r"C:\Windows\SystemApps\Microsoft.MicrosoftEdgeDevToolsClient_8wekyb3d8bbwe"),
    ]
    
    for path in edge_paths:
        if path.exists():
            try:
                shutil.rmtree(path, ignore_errors=True)
                print(f"Removed: {path}")
            except Exception as e:
                print(f"Failed to remove {path}: {e}")

def remove_edge_registry():
    """Remove Edge registry entries."""
    reg_keys = [
        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge",
        r"HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge",
        r"HKLM\SOFTWARE\Microsoft\EdgeUpdate",
        r"HKCU\Software\Microsoft\Edge",
    ]
    
    for key in reg_keys:
        try:
            subprocess.run(["reg", "delete", key, "/f"], capture_output=True)
            print(f"Removed registry key: {key}")
        except:
            pass

def block_edge_reinstall():
    """Block Edge from reinstalling via Windows Update."""
    try:
        # Create registry key to prevent Edge reinstall
        subprocess.run([
            "reg", "add", 
            r"HKLM\SOFTWARE\Microsoft\EdgeUpdate", 
            "/v", "DoNotUpdateToEdgeWithChromium", 
            "/t", "REG_DWORD", "/d", "1", "/f"
        ], capture_output=True)
        
        # Block Edge update service
        subprocess.run(["sc", "config", "edgeupdate", "start=", "disabled"], capture_output=True)
        subprocess.run(["sc", "config", "MicrosoftEdgeElevationService", "start=", "disabled"], capture_output=True)
        subprocess.run(["sc", "stop", "edgeupdate"], capture_output=True)
        
        print("Blocked Edge reinstallation")
    except Exception as e:
        print(f"Failed to block reinstall: {e}")

def remove_edge_tasks():
    """Remove scheduled tasks related to Edge."""
    tasks = [
        "MicrosoftEdgeUpdateTaskMachineCore",
        "MicrosoftEdgeUpdateTaskMachineUA",
    ]
    
    for task in tasks:
        try:
            subprocess.run(["schtasks", "/delete", "/tn", task, "/f"], capture_output=True)
            print(f"Removed task: {task}")
        except:
            pass

def main():
    print("Microsoft Edge Removal Tool")
    print("=" * 40)
    
    run_as_admin()
    kill_edge_processes()
    remove_edge_directories()
    remove_edge_registry()
    block_edge_reinstall()
    remove_edge_tasks()
    
    print("\nEdge removal complete. Restart recommended.")

if __name__ == "__main__":
    main()