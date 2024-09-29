# */15 * * * * nohup python3 -u /root/discord/mst.py > /root/discord/mst.log 2>&1 &
import requests
import json
import os
from pathlib import Path
from datetime import datetime
from lxml import html
import re


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
        if notif['seen']: continue
        msg=notif['title']
        urldata=json.loads(notif['payload'])
        if notif['type']=='TEACHINGRESOURCES':
            url=f'https://app.mysecondteacher.com.np/classroom/subject/{urldata["SubjectId"]}/class/{urldata["ClassRoomId"]}/content'
            msg=f"[{msg}]({url})"
        elif notif['type']=='ASSIGNMENTLATER' or notif['type']=='ASSIGNMENTCREATE' or notif['type']=='ASSIGNMENT' or notif['type']=='ASSIGNMENTREMINDER':
            url=f'https://app.mysecondteacher.com.np/classroom/subject/{urldata["SubjectId"]}/class/{urldata["ClassRoomId"]}/assignments/{urldata["AssignmentId"]}'
            msg=f"[{msg}]({url})"
            deadline_request=requests.get(f"https://api.mysecondteacher.com.np/api/v2/student-submission/{urldata['AssignmentId']}",headers=header)
            if deadline_request.status_code==200:
                try:
                    deadline=deadline_request.json()['result']['deadline']
                    msg=f'🚩 [<t:{int(datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%SZ").timestamp())}:R>] ' +msg
                except:
                    msg='🚩 '+msg
            else:
                msg='🚩 '+msg
        elif notif['type']=="ANNOUNCEMENT" or notif['type']=="ANNOUNCEMENTLATER":
            url=f"https://app.mysecondteacher.com.np/#dashboard-notice-board"
            try:
                r=requests.get("https://api.mysecondteacher.com.np/api/v2/ongoing-announcements-student?recordPerPage=1&pageNumber=1",headers=header).json()
                announcement_item=r['result']['items'][0]
                announcement_text=re.sub(r'(https?://[^\s]+)', r'<\1>',html.fromstring(announcement_item['message']).text_content())
                announcement_creator=announcement_item['creatorName']
                links=[]
                l=f=0
                for item in announcement_item['announcementFiles']:
                    if item['fileType']=='link':
                        l+=1
                        links.append(f"[Link-{l}](<{item['fileTitle']}>)")
                    else:
                        f+=1
                        links.append(f"[File-{f}](<{item['fileUrl']}>)")
                msg=f"📢 {announcement_text}\n{' | '.join(links)}\n- {announcement_creator} | [View on mst]({url})"
            except:
                msg=f"📢 [{msg}]({url})"
        elif notif['type']=="ASSIGNMENTDELETE": pass
        else:
            msg=msg+'\n`'+notif['payload']+'`'
        send(json_data[year]["webhook"], msg)
        requests.put(f"{notification_url}/{notif['id']}/seen",headers=header)


# run
for year in json_data:
    fetch_notification(year)
