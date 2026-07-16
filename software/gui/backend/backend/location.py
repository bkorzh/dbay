from pathlib import Path
import os
import sys


# BASE_DIR = Path(__file__).resolve().parent

if getattr(sys, 'frozen', False):
    # inside a PyInstaller bundle
    BASE_DIR = sys._MEIPASS

else:
    # normal Python execution
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    


DATA_DIR = os.path.join(BASE_DIR, "config")
WEB_DIR = os.path.join(BASE_DIR, "compiled_frontend")
MODULE_DIR = os.path.join(BASE_DIR, "modules")


def _user_data_dir(app_name: str = "dbay") -> str:
    # Writable per-user location for persisted state. BASE_DIR is inside the
    # PyInstaller bundle when frozen, so it can't be used for the database.
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home())))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
    directory = base / app_name
    directory.mkdir(parents=True, exist_ok=True)
    return str(directory)


PERSIST_DIR = _user_data_dir()




# BASE_DIR = os.path.dirname(os.path.realpath(__file__))
