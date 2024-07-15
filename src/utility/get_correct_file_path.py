import os
import sys

def get_correct_file_path(filename: str):
    try:
        if os.path.exists(os.path.join(os.path.dirname(__file__), "../../" + filename)):
            return os.path.join(os.path.dirname(__file__), "../../" + filename)
        else:
            return os.path.join(os.path.dirname(sys.argv[0]), filename)
    except NameError:
        return os.path.join(os.path.dirname(sys.argv[0]), filename)
    