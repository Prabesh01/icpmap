import requests
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

login_url='https://api.mysecondteacher.com.np/api/TokenAuth/Authenticate'
notification_url='https://api.mysecondteacher.com.np/api/UserNotifications/user-notifications'
creds_file=BASE_DIR/'mst_creds.json'
header={
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept-Language': 'en',
    }


def send(hook,msg):
    requests.post(hook, data={'content':msg})


def read_json():
    if os.path.exists(creds_file):
        with open(creds_file) as f:
            return json.load(f)
    else:
        return {}
json_data=read_json()


#login
def login(mst_email,mst_pass):
    r=requests.post(login_url,json={'userNameOrEmailAddress':mst_email,'password':mst_pass,'rememberClient':False})
    try:
        access_token=r.json()['result']['accessToken']
        return access_token
    except:
        return None


# refresh token
def write_token(year):
    global json_data
    token=login(json_data[year]['user'],json_data[year]['pass'])
    if not token:
        send(json_data[year]['webhook'], 'mst login err!')
        return token
    else:
        with open(creds_file,'w') as f:
            json_data[year]['token']=token
            json.dump(json_data,f)
    return token


#fetch notifications
def fetch_notification(year):
    header['Authorization']= f'Bearer {json_data[year]["token"]}'
    notifs=[]
    try:
        r=requests.get(notification_url,headers=header)
        if r.status_code==401:
            token=write_token(year)
            if not token: return
            fetch_notification(year)
        notifs=r.json()['result']
    except Exception as e:
        send(json_data[year]["webhook"],'mst notification fetch err!')
        return
    if not notifs: return
    # send unseen notifications and mark them as seen
    for notif in notifs:
        unmatched=assignment=announcement=False
        if notif['seen']: continue
        msg=notif['title']
        urldata=json.loads(notif['payload'])
        if notif['type']=='TEACHINGRESOURCES':
            url=f'https://app.mysecondteacher.com.np/subjects/{urldata["SubjectId"]}/classroom/{urldata["ClassRoomId"]}/content'
        elif notif['type']=='ASSIGNMENTLATER' or notif['type']=='ASSIGNMENTCREATE' or notif['type']=='ASSIGNMENT' or notif['type']=='ASSIGNMENTREMINDER':
            assignment=True
            url=f'https://app.mysecondteacher.com.np/classroom/subject/{urldata["SubjectId"]}/class/{urldata["ClassRoomId"]}/assignments/{urldata["AssignmentId"]}'
        elif notif['type']=="ANNOUNCEMENT":
            announcement=True
            url=f"https://app.mysecondteacher.com.np/#dashboard-notice-board"
        else:
            unmatched=True
        if unmatched: 
            msg=msg+'\n`'+notif['payload']+'`'
        else:
            msg=f"[{'🚩 ' if assignment else ''}{'📢  ' if announcement else ''}{msg}]({url})"
        send(json_data[year]["webhook"], msg)
        requests.put(f"{notification_url}/{notif['id']}/seen",headers=header)


# run
for year in json_data:
    fetch_notification(year)
