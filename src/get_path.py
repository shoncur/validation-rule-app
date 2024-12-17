import sys
import os

def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(sys.argv[0])

    return os.path.join(base_path, relative_path)