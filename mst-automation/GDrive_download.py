import os
from pathlib import Path
import shutil

from gdrivedl import donwload_gdrive

BASE_DIR = Path(__file__).resolve().parent
g_drives={
    "y2/CC5067_Smart_Data_Discovery": "https://drive.google.com/drive/folders/1ElYESqIdhbCNiOstE0y8h7qWHoo5MamH",
}

out_dir=BASE_DIR/'mst'
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)


def parse_path(path):
    path_str=str(path)
    path_str='_'.join(path_str.strip().split())
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        path_str = path_str.replace(char, '_')
    return path_str

# run
for mod,url in g_drives.items():
    donwload_gdrive(url, str(out_dir)+'/'+mod)

# arrange files
for mod in g_drives:
    break
    path=str(out_dir)+'/'+mod+'_GDRIVE'
    for f in os.listdir(path):
        full_file_path = os.path.join(path, f)

        if os.path.isfile(full_file_path):
            prefix = f[:2]

            if prefix.isdigit() and int(prefix) < 100:
                folder_path = os.path.join(path, prefix)

                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                shutil.move(full_file_path, os.path.join(folder_path, f))

