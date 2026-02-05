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
WEB_DIR = os.path.join(BASE_DIR, "dbay_control")
MODULE_DIR = os.path.join(BASE_DIR, "modules")




# BASE_DIR = os.path.dirname(os.path.realpath(__file__))
