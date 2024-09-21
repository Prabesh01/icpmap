import requests
import json
import os
import re
from pathlib import Path
from time import sleep
from random import randint

BASE_DIR = Path(__file__).resolve().parent

login_url='https://api.mysecondteacher.com.np/api/TokenAuth/Authenticate'
notification_url='https://api.mysecondteacher.com.np/api/UserNotifications/user-notifications'
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

def downloadFile(path, itemid, classid):
    sleep(randint(10, 60))
    r=requests.get("https://api.mysecondteacher.com.np/api/users/content/generate-link?resourceId="+str(itemid)+"&classId="+str(classid),headers=header)
    dwnurl=r.json()['result']
    if not os.path.exists(path):
        with open(path,'wb') as f:
            r=requests.get(dwnurl)
            f.write(r.content)

def recursive_lookup(contents, download_dir, classid, teacherid):
    for item in contents["items"]:
        folddir=download_dir/resub(item["displayName"])
        if item["url"]==None:
            if not os.path.exists(folddir):
                os.mkdir(folddir)
            contentz=requests.get("https://api.mysecondteacher.com.np/api/users/content?teacherId="+str(teacherid)+"&classId="+str(classid)+"&userId=0&folderParentId="+str(item["id"])+"&pageNumber=1&pageSize=1000",headers=header).json()['result']
            recursive_lookup(contentz, folddir, classid, teacherid)
        else:
            try:
                dwnfiledir=str(folddir)+"."+item["fileExtension"]
                if os.path.exists(dwnfiledir):
                    if os.stat(dwnfiledir).st_size==item["fileSizeInt"]: continue                        
                downloadFile(dwnfiledir,item["id"],classid)
            except:
                dwnfiledir=str(folddir)+".url"
                with open(dwnfiledir,'w',encoding="utf-8") as f:
                    f.write("[InternetShortcut]\nURL="+item["url"])
    
#download files
def download_files(year):
    header['Authorization']= f'Bearer {json_data[year]["token"]}'
    download_dir=out_dir/year
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
    
    subjects=requests.get("https://api.mysecondteacher.com.np/api/classroom-subjects",headers=header).json()['result']
    for sub in subjects:
        subid=sub["subjectId"]
        subname=sub["subjectName"]
        download_dir=out_dir/year/subname
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)
            
        classes=requests.get("https://api.mysecondteacher.com.np/api/subject/"+str(subid)+"/class-detail",headers=header).json()['result']
        for clas in classes:
            classid=clas["classId"]
            classname=clas["className"]
            print(subname+'-->'+classname)
            download_dir=out_dir/year/subname/classname
            if not os.path.exists(download_dir):
                os.mkdir(download_dir)

            teachers=requests.get("https://api.mysecondteacher.com.np/api/classes/"+str(classid)+"/teachers",headers=header).json()['result']                
            for teacher in teachers:
                teacherid=teacher["teacherId"]
                contents=requests.get("https://api.mysecondteacher.com.np/api/users/content?teacherId="+str(teacherid)+"&classId="+str(classid)+"&userId=0&folderParentId=0&pageNumber=1&pageSize=1000",headers=header).json()['result']
                recursive_lookup(contents, download_dir, classid, teacherid)
# run
for year in json_data:
    download_files(year)
