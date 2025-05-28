from pathlib import Path
import zipfile
import rarfile
import subprocess

def password_protected(file_path: str):
    ext = Path(file_path).suffix

    if ext == ".zip":
        return check_zip(file_path)
    elif ext == ".rar":
        return check_rar(file_path)
    elif ext == ".7z":
        return check_7z(file_path)
    elif ext in [".tar", ".gz", ".bz2"]:
        return False
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def check_zip(file_path: str):
    with zipfile.ZipFile(file_path) as zf:
        for zinfo in zf.infolist():
            if zinfo.flag_bits & 0x1:
                return True
        return False
    
def check_rar(file_path: str):
    with rarfile.RarFile(file_path) as rf:
        return rf.needs_password()
    
def check_7z(file_path: str):
    result = subprocess.run(["7z", "t", file_path], capture_output=True, text=True)
    return "Enter password" in result.stderr
