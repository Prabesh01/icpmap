# */15 * * * * nohup python3 -u /root/discord/mst.py > /root/discord/mst.log 2>&1 &
import requests
import json
import os
from pathlib import Path
import datetime as dt
from datetime import datetime
from lxml import html
import re
from time import sleep

tz_NP = dt.timezone(dt.timedelta(hours=5, minutes=45))  # NEPAL TIMEZONE

BASE_DIR = Path(__file__).resolve().parent

login_url='https://api.mysecondteacher.com.np/api/TokenAuth/Authenticate'
notification_url='https://api.mysecondteacher.com.np/api/UserNotifications/user-notifications'
creds_file=BASE_DIR/'mst_creds.json'
header={
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept-Language': 'en',
    }
tg_message_recrod_file = BASE_DIR/"tg_message_record.json"


def log_err(msg):
    file=BASE_DIR/f"{msg}.err"
    if os.path.exists(file): return False
    else:
        with open(file,"w") as f: f.write("")
        return True


def no_err(msg):
    file=BASE_DIR/f"{msg}.err"
    if os.path.exists(file): os.remove(file)


def send(hook,msg):
    requests.post(hook, data={'content':msg})


def read_json():
    if os.path.exists(creds_file):
        with open(creds_file) as f:
            return json.load(f)
    else:
        return {}
json_data=read_json()

# record of announcement url and corresponding message id sent to tg topics
def read_tg_records():
    if not tg_message_recrod_file.exists():
        return {}
    with open(tg_message_recrod_file, "r") as f:
        data = json.load(f)
    return data
tg_records = read_tg_records()

def write_tg_records(data):
    with open(tg_message_recrod_file, "w") as f:
        json.dump(data, f, indent=4)


#captcha-bypass
def getCaptchaToken():
    r=requests.post("https://api.capsolver.com/createTask",json={"clientKey":json_data['.env']['fcb_key'],"task":{"type":"ReCaptchaV3TaskProxyLess","websiteURL":"https://app.mysecondteacher.com.np/","websiteKey":"6LeuUMonAAAAABv-aLjhx_JTT7utsNhCwSPcBb5m"}})
    if r.status_code!=200: return False
    taskid=r.json()['taskId']
    i=0
    while True:
        i+=1
        sleep(10)
        r=requests.post("https://api.capsolver.com/getTaskResult",json={"clientKey":json_data['.env']['fcb_key'],"taskId":taskid})
        if r.status_code!=200: return False
        if i>=10: return False
        if r.json()['status']!='ready': continue
        return r.json()['solution']['gRecaptchaResponse']


#login
def login(mst_email,mst_pass):
    reCaptchaToken=getCaptchaToken()
    if not reCaptchaToken: return None
    r=requests.post(login_url,json={'userNameOrEmailAddress':mst_email,'password':mst_pass,'rememberClient':False,'reCaptchaToken':reCaptchaToken}, headers=header)
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
        if log_err('login'):
            send(json_data[year]['webhook'], 'mst login err!')
        return token
    else:
        no_err("login")
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
        # send(json_data[year]["webhook"],'mst notification fetch err!')
        return
    if not notifs: return
    # send unseen notifications and mark them as seen
    for notif in notifs:
        msg=notif['title']
        urldata=json.loads(notif['payload'])
        # skip to another notification if notification is seen
        # unless..
        # it is a assignment notification and
        # we have to edit telegram message
        if notif['seen']:
            if notif['type'] not in ['ASSIGNMENTLATER', 'ASSIGNMENTCREATE']: continue
            elif urldata['AssignmentId'] not in tg_records.keys(): continue
        if notif['type']=='TEACHINGRESOURCES':
            url=f'https://app.mysecondteacher.com.np/classroom/subject/{urldata["SubjectId"]}/class/{urldata["ClassRoomId"]}/content'
            msg=f"[{msg}]({url})"
        elif notif['type']=='ASSIGNMENTLATER' or notif['type']=='ASSIGNMENTCREATE' or notif['type']=='ASSIGNMENT' or notif['type']=='ASSIGNMENTREMINDER':
            url=f'https://app.mysecondteacher.com.np/classroom/subject/{urldata["SubjectId"]}/class/{urldata["ClassRoomId"]}/assignments/{urldata["AssignmentId"]}'
            msg=f"[{msg}]({url})"
            deadline_request=requests.get(f"https://api.mysecondteacher.com.np/api/v2/student-submission/{urldata['AssignmentId']}",headers=header)
            deadline = None
            if deadline_request.status_code==200:
                try:
                    deadline=deadline_request.json()['result']['deadline']
                    msg=f'🚩 [<t:{int(datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%SZ").timestamp())}:R>] ' +msg
                except:
                    msg='🚩 '+msg
            else:
                msg='🚩 '+msg

            # do telegram stuff if configured and we have assignment deadline
            if 'tg_bot_token' in json_data[year].keys() and deadline:
                tg_bot_token=json_data[year]['tg_bot_token']
                tg_group_id=json_data[year]['tg_group_id']
                tg_topic_id=json_data[year]['tg_topic_id']
                time_left = None
                # check if assignment is expired
                deadline_dt = datetime.strptime(deadline,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).astimezone(tz_NP)
                if deadline_dt > datetime.now(tz=tz_NP):
                    # calcualte remaining time in days, hours and minutes
                    time_left = deadline_dt - datetime.now(tz=tz_NP)
                    days, seconds = time_left.days, time_left.seconds
                    hours = seconds // 3600
                    seconds %= 3600
                    minutes = seconds // 60
                    seconds %= 60
                    deadline_str=deadline_dt.strftime("%a, %-d %B %-I:%M %p")
                    title = notif['title'].replace('You have an assignment ', '')
                    tg_msg = f"🚩 ({days}d {hours}h {minutes}m left)\n📅 {deadline_str}\n\n<a href='{url}'>{title}</a>"

                # check if message is already sent
                if urldata['AssignmentId'] in tg_records.keys():
                    # if assignment is expired, delete the message and remove it from records
                    if not time_left:
                        tg_delete_msg_url = f"https://api.telegram.org/bot{tg_bot_token}/deleteMessage?\
chat_id=-100{tg_group_id}&\
message_id={tg_records[urldata['AssignmentId']]}"
                        hya=requests.get(tg_delete_msg_url)
                        if hya.status_code==400:
                            print("Coudlnt delete the message. Attempting to edit the message instead")
                            tg_redact_msg_url = f"https://api.telegram.org/bot{tg_bot_token}/editMessageText?\
chat_id=-100{tg_group_id}&\
message_id={tg_records[urldata['AssignmentId']]}&\
parse_mode=HTML&\
text=."
                            requests.get(tg_redact_msg_url)
                        del tg_records[urldata['AssignmentId']]
                        write_tg_records(tg_records)
                    else:
                        # else edit the message and update remaining time
                        tg_edit_msg_url = f"https://api.telegram.org/bot{tg_bot_token}/editMessageText?\
chat_id=-100{tg_group_id}&\
message_id={tg_records[urldata['AssignmentId']]}&\
parse_mode=HTML&\
text="
                        requests.get(tg_edit_msg_url+tg_msg)
                elif time_left:
                    # send new message and record its message id
                    tg_send_msg_url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage?\
chat_id=-100{tg_group_id}&\
message_thread_id={tg_topic_id}&\
parse_mode=HTML&\
text="
                    response = requests.post(tg_send_msg_url+tg_msg).json()
                    tg_records[urldata['AssignmentId']]=response['result']['message_id']
                    write_tg_records(tg_records)
            # if message isn't new, no need to send message to discord.
            if notif['seen']: continue
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
                        links.append(f"[File-{f}](<https://nepal-assets-apollo.mysecondteacher.com{item['fileUrl']}>)")
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
    if year=='.env': continue
    fetch_notification(year)
