import requests
import json
import os
import re
from pathlib import Path
from time import sleep
from random import randint

from dateutil import parser
import pytz
npt_tz = pytz.timezone('Asia/Kathmandu')

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
    #sleep(randint(10, 60))
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
                print(dwnfiledir)
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
    
    r=requests.get("https://api.mysecondteacher.com.np/api/classroom-subjects",headers=header)
    if r.status_code==401:
        print('Invalid token')
        return
    subjects=r.json()['result']
    for sub in subjects:
        subid=sub["subjectId"]
        subname=sub["subjectName"]
        download_dir=out_dir/parse_path(year)/parse_path(subname)
        # ignore y2_sem1 subjects for y2_sem2
        if parse_path(year)=='y2' and parse_path(subname) in ['CC5051_Database','CS4051_Fundamentals_of_Computing','CT4005_Computer_Hardware_&_Software_Architectures','CS5053_Cloud_Computing_and_the_Internet_of_Things','CT5052_Network_Operating_Systems']: continue
        # ignore y2_sem2 subjects for y3
        if parse_path(year)=='y3' and parse_path(subname) in ['CC5067_Smart_Data_Discovery','CS5002_Software_Engineering','CS5054_Advanced_Programming_and_Technologies','CS5071_Professional_and_Ethical_Issues']: continue
        mkdir(download_dir)
            
        classes=requests.get("https://api.mysecondteacher.com.np/api/subject/"+str(subid)+"/class-detail",headers=header).json()['result']
        for clas in classes:
            classid=clas["classId"]
            classname=clas["className"]
            # ignore sem1 assessments for y2_sem2
            if parse_path(year)=='y2' and parse_path(subname)=='Assessment' and parse_path(classname) in ['CC5051NP_Databases_Assessment_AU_24','CS5053NP_Cloud_Computing_and_the_Internet_of_Things_Assessment_AU_24','CT5052NP_Network_Operating_Systems_Assessment_AU_24']: continue
            # ignore y2_sem2 assessments for y3
            if parse_path(year)=='y3' and parse_path(subname)=='Assessment' and parse_path(classname) in ['CC5067NP_Smart_Data_Discovery_Assessment_SP_25','CS5071NP_Professional_and_Ethical_Issues_Assessment_SP_25','CS5002NP_Software_Engineering_Assessment_SP_25','CS5054NP_Advanced_Programming_and_Technologies_Assessment_SP_25']: continue
            print(subname+'-->'+classname)
            download_dir=out_dir/parse_path(year)/parse_path(subname)/parse_path(classname)
            mkdir(download_dir)

            # attempt to get assignments:
            assignments = requests.get("https://api.mysecondteacher.com.np/api/v2/student-assignment-status?classId="+str(classid),headers=header).json()['result']
            for ass in assignments['data']:
                print(f"Assignent: {ass['title']} --> {classname}")
                aid = ass ['assignmentId']
                assignment_dir=download_dir/"Assignments"
                if not os.path.exists(assignment_dir):
                    os.mkdir(assignment_dir)

                fol_name = f"{ass['title']} _ {aid}"
                ass_fol_path = os.path.join(assignment_dir, fol_name)
                if not os.path.exists(ass_fol_path):
                    os.mkdir(ass_fol_path)

                dt = parser.isoparse(ass['deadline'])
                if dt.tzinfo is None: dt = dt.replace(tzinfo=pytz.UTC)
                dt_npt = dt.astimezone(npt_tz)
                deadline = dt_npt.strftime('%d %b %-I%p')

                for fol in os.listdir(assignment_dir):
                    full_path = os.path.join(assignment_dir, fol)
                    if os.path.isdir(full_path) and fol.endswith(aid):
                        if fol!=fol_name: os.rename(fol, fol_name)
                        for fls in os.listdir(ass_fol_path):
                            files_in_ass = os.path.join(full_path, fls)
                            if os.path.isfile(files_in_ass) and files_in_ass.startswith('dl__') and files_in_ass.endswith('.html'):
                                os.remove(files_in_ass)
      
                with open(os.path.join(ass_fol_path, f"dl__{deadline}.html"),'w',encoding="utf-8") as f:
                    f.write(ass['description'])

                submssion_detail=requests.get("https://api.mysecondteacher.com.np/api/v2/student-submission/"+aid,headers=header).json()['result']
                suffix=f"?Key-Pair-Id={submssion_detail['signedCookie']['keyPairId']['value']}&Signature={submssion_detail['signedCookie']['signature']['value']}&Policy={submssion_detail['signedCookie']['policy']['value']}"
                suffix = {
                    'Key-Pair-Id': submssion_detail['signedCookie']['keyPairId']['value'].strip(),
                    'Signature': submssion_detail['signedCookie']['signature']['value'].strip(),
                    'Policy': submssion_detail['signedCookie']['policy']['value'].strip()
                }
                for ass_attch in submssion_detail['links']:
                    adwnlink = "https://app.mysecondteacher.com.np"+ass_attch['name'].strip()
                    with open('/home/prabesh/t/mst/url.txt', 'w') as f: f.write(adwnlink)
                    print(f"DEBUG - Length of URL: {len(adwnlink)}") 
                    adwnflnme = ass_attch['label']

                    if not ass_attch['type']=="FILE":
                        with open(os.path.join(ass_fol_path, f"{adwnflnme}.url"),'w',encoding="utf-8") as f:
                            f.write("[InternetShortcut]\nURL="+adwnlink)
                        continue 

                    adwnfilepath=os.path.join(ass_fol_path, adwnflnme)
                    # print(adwnfilepath)
                    if os.path.exists(adwnfilepath):
                        if os.stat(adwnfilepath).st_size==ass_attch["size"]: 
                            print("--------------")
                            continue
                    with open(adwnfilepath,'wb') as f:
                        r=requests.get(adwnlink, params=suffix) # , headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
                        print(r.url)
                        f.write(r.content)
                        print(f"Status Code: {r.status_code}")
                        print(f"Request Headers: {r.request.headers}")  # See what you sent
                        print(f"Response Headers: {r.headers}")          # See what the server said
                        sys.exit()

            #teachers=requests.get("https://api.mysecondteacher.com.np/api/classes/"+str(classid)+"/teachers",headers=header).json()['result']                
            #for teacher in teachers:
            #    teacherid=teacher["teacherId"]
            #    contents=requests.get("https://api.mysecondteacher.com.np/api/users/content?teacherId="+str(teacherid)+"&classId="+str(classid)+"&userId=0&folderParentId=0&pageNumber=1&pageSize=1000",headers=header).json()['result']
            #    recursive_lookup(contents, download_dir, classid, teacherid)
# run
for year in json_data:
    if year==".env": continue
    fetch_files_folders(year)
