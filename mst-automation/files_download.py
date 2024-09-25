import requests
import json
import os
import re
from pathlib import Path
from time import sleep
from random import randint

BASE_DIR = Path(__file__).resolve().parent

login_url='https://api.mysecondteacher.com.np/api/TokenAuth/Authenticate'
creds_file=BASE_DIR/'mst_creds.json'
out_dir=BASE_DIR/'mst'
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)

header={
    'Accept-Language': 'en',
    'Platform': 'web-app',
    'Referer': 'https://app.mysecondteacher.com.np/',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
    }


def read_json():
    if os.path.exists(creds_file):
        with open(creds_file) as f:
            return json.load(f)
    else:
        return {}
json_data=read_json()


def resub(txt):
    return re.sub(r'[^\w]', ' ', txt)


def parse_path(path):
    path_str=str(path)
    path_str='_'.join(path_str.strip().split())
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        path_str = path_str.replace(char, '_')
    return path_str


def mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def downloadFile(path, itemid, classid):
    sleep(randint(10, 60))
    r=requests.get("https://api.mysecondteacher.com.np/api/users/content/generate-link?resourceId="+str(itemid)+"&classId="+str(classid),headers=header)
    dwnurl=r.json()['result']['resourceContentUrl']
    if not os.path.exists(path):
        with open(path,'wb') as f:
            r=requests.get(dwnurl)
            f.write(r.content)


def recursive_lookup(contents, download_dir, classid, teacherid):
    for item in contents["items"]:
        folddir=download_dir/parse_path(item["displayName"])
        if item["url"]==None:
            mkdir(folddir)
            contentz=requests.get("https://api.mysecondteacher.com.np/api/users/content?teacherId="+str(teacherid)+"&classId="+str(classid)+"&userId=0&folderParentId="+str(item["id"])+"&pageNumber=1&pageSize=1000",headers=header).json()['result']
            recursive_lookup(contentz, folddir, classid, teacherid)
        else:
            ext=item["fileExtension"]
            if ext:
                dwnfiledir=str(folddir)+"."+parse_path(ext)
                if os.path.exists(dwnfiledir):
                    if os.stat(dwnfiledir).st_size==item["fileSizeInt"]: continue                        
                downloadFile(dwnfiledir,item["id"],classid)
            else:
                dwnfiledir=str(folddir)+".url"
                with open(dwnfiledir,'w',encoding="utf-8") as f:
                    f.write("[InternetShortcut]\nURL="+item["url"])


#fetch files and folders
def fetch_files_folders(year):
    header['Authorization']= f'Bearer {json_data[year]["token"]}'
    download_dir=out_dir/parse_path(year)
    mkdir(download_dir)
    
    subjects=requests.get("https://api.mysecondteacher.com.np/api/classroom-subjects",headers=header).json()['result']
    for sub in subjects:
        subid=sub["subjectId"]
        subname=sub["subjectName"]
        download_dir=out_dir/parse_path(year)/parse_path(subname)
        mkdir(download_dir)
            
        classes=requests.get("https://api.mysecondteacher.com.np/api/subject/"+str(subid)+"/class-detail",headers=header).json()['result']
        for clas in classes:
            classid=clas["classId"]
            classname=clas["className"]
            print(subname+'-->'+classname)
            download_dir=out_dir/parse_path(year)/parse_path(subname)/parse_path(classname)
            mkdir(download_dir)

            teachers=requests.get("https://api.mysecondteacher.com.np/api/classes/"+str(classid)+"/teachers",headers=header).json()['result']                
            for teacher in teachers:
                teacherid=teacher["teacherId"]
                contents=requests.get("https://api.mysecondteacher.com.np/api/users/content?teacherId="+str(teacherid)+"&classId="+str(classid)+"&userId=0&folderParentId=0&pageNumber=1&pageSize=1000",headers=header).json()['result']
                recursive_lookup(contents, download_dir, classid, teacherid)
# run
for year in json_data:
    fetch_files_folders(year)
