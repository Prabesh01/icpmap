from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def get_basedir():
    return BASE_DIR