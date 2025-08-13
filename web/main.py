import os
from pathlib import Path
import requests
import json
import flask
from functools import wraps
import urllib.parse
import uuid
from dotenv import load_dotenv
import google_auth_oauthlib.flow
from datetime import datetime, timedelta
import pytz
tz_NP = pytz.timezone('Asia/Kathmandu')

BASE_DIR = Path(__file__).resolve().parent.parent

app = flask.Flask(__name__)
app.secret_key = jwt_secret = str(uuid.uuid4())
@app.after_request
def gnu_terry_pratchett(resp):
    resp.headers.add("X-Clacks-Overhead", "GNU Binit Ghimire")
    return resp

@app.get('/static/<path:filepath>')
def vendors(filepath):
    return flask.send_from_directory('static/', filepath)

##############################################################
                        # MAP/CAL
##############################################################
data_file=BASE_DIR / "data/data.json"

weekdays=["SUN","MON","TUE","WED","THU","FRI","SAT"]

# parse_data_file
with open(data_file) as f:
    data = json.load(f)

classwise_calendar = {}
daywise_classes = {"SAT":[]}
teachers=data["teachers"]
sections=data["sections"]
rooms=data["rooms"]
cal_ids=data.get("cal_ids",{})

for c in data["classes"]:
    for s in c["sections"]:
        day=c["day"]
        c_key = c["class"]+ ' - '+ s
        c_data=[c["module"], c["room"], c["stime"]]
        if not c_key in classwise_calendar:
            classwise_calendar[c_key]=[[],[],[],[],[],[],[]]
        classwise_calendar[c_key][weekdays.index(day)].append(c_data)

    d_key=c["day"]
    c.pop("day")
    c.pop("sections")
    c.pop("code")
    c.pop("module")
    if not d_key in daywise_classes:
        daywise_classes[d_key]=[c]
    else:
        daywise_classes[d_key].append(c)
del data


def calculate_time_difference(reference_time, check_time):
  time_delta = timedelta(hours=abs(check_time.hour - reference_time.hour),
                         minutes=abs(check_time.minute - reference_time.minute),
                         seconds=abs(check_time.second - reference_time.second))

  return time_delta

def empty(day=None,check_time=None,teach=None):
    empty_rooms_list=rooms[:]
    taken_rooms_list={}
    empty_rooms={}
    taken_rooms={}
    if not day:day=weekdays[datetime.today().weekday()]
    if check_time: check_time=datetime.strptime(check_time,"%I:%M %p").time()
    else: check_time=datetime.now().time()
    teach_return=None, None
    teach_return_dict=[]
    for classe in daywise_classes[day]:
        start_time = datetime.strptime(classe["stime"], "%I:%M %p").time()
        end_time = datetime.strptime(classe["etime"], "%I:%M %p").time()
        if classe["teacher"]==teach: teach_return_dict.append([classe["room"],classe["class"],classe["stime"]])
        # >= <= check ifi within range
        if (start_time <= check_time and check_time <= end_time):
            if classe["teacher"]==teach: teach_return= classe["room"],classe["etime"]
            if classe["room"] in empty_rooms_list: empty_rooms_list.remove(classe["room"])
            taken_rooms_list[classe["room"]]=end_time
    if teach: return teach_return, teach_return_dict

    for clase,etim in taken_rooms_list.items():
        # empty in y mins, find the end time. and check if the end time is start time for the same room. in loop
        etime=etim
        for i in range(3):
            for classez in daywise_classes[day]:
                if classez["room"]==clase:
                    start_time = datetime.strptime(classez["stime"], "%I:%M %p").time()
                    if start_time==etime: etime=datetime.strptime(classez["etime"], "%I:%M %p").time()
            taken_rooms[clase]=int(calculate_time_difference(etime,check_time).total_seconds()/60)

    for clase in empty_rooms_list:
        # empty for x minutes, find the next start time closest (gt) to given time
        closest=None
        for classez in daywise_classes[day]:
            if classez["room"]==clase:
                start_time = datetime.strptime(classez["stime"], "%I:%M %p").time()
                end_time = datetime.strptime(classez["etime"], "%I:%M %p").time()

                diff=calculate_time_difference(start_time,check_time).total_seconds()

                if start_time >= check_time:
                    if closest:
                        if diff>closest: continue
                    closest=diff
                    empty_rooms[clase]=int(closest/60)
        if not clase in empty_rooms: empty_rooms[clase]=None

    return empty_rooms, taken_rooms

@app.get('/')
def get_home():
    user=None
    if 'user' in flask.session:
        user = flask.session['user']
    return flask.render_template('home.html',user=user)

@app.get('/icp-map')
def get_icp_map():
    return flask.render_template('map/icp_map.html', teachers=teachers)

@app.post('/icp-map')
def post_icp_map():
    post_data=flask.request.get_data().decode('utf-8')
    parsed_post_data = urllib.parse.parse_qs(post_data)

    day=time=teach=None
    if "day" in parsed_post_data:
        day=parsed_post_data["day"][0]
    if "time" in parsed_post_data:
        time=parsed_post_data["time"][0]
    if "teach" in parsed_post_data:
        teach=parsed_post_data["teach"][0]
    # try:
    returned_data=empty(day,time,teach)
    # except:
        # return "N/A"
    if teach:
        todump={"room":returned_data[0][0],"time":returned_data[0][1],"schedule":returned_data[1]}
    else:
        todump={"empty_rooms":returned_data[0],"taken_rooms":returned_data[1]}
    return json.dumps(todump).encode(encoding='utf_8')


@app.get('/icp-cal')
def get_icp_cal():
    return flask.render_template('map/icp_cal.html', cal_ids=cal_ids, sections=sections, static_cal=classwise_calendar)


##############################################################
                        # Auth
##############################################################

env_file=BASE_DIR / "credentials/.env"
load_dotenv(env_file)
events_file = BASE_DIR / 'data/events.json'
IMAGES_PATH = BASE_DIR / 'web/imgs'

client_config = {
    "web": {
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}
flow = google_auth_oauthlib.flow.Flow.from_client_config(
    client_config,
    scopes=['openid','https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile'])

flow.redirect_uri = os.getenv('web_url')+'/login'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' in flask.session:
            user = flask.session['user']
            return f(user=user, *args, **kwargs)
        else:
            return flask.redirect(flask.url_for('login'))
    return decorated_function

@app.get('/login')
def login():
    if 'user' in flask.session:
        return flask.redirect(flask.url_for('get_home'))

    authorization_url, state = flow.authorization_url(access_type='online')
    if flask.request.args.get('code'):
        flow.fetch_token(code=flask.request.args.get('code'))
        json_creds = flow.credentials.to_json()
        dict_creds = json.loads(json_creds)
        r=requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={"Authorization":"Bearer "+dict_creds['token']})
        if r.status_code != 200:
            message="Login Unsucessfull:/ Please try again later!"
            return flask.render_template('auth/login.html',url=authorization_url,message=message)
        email_name, domain_part = r.json()['email'].lower().strip().rsplit('@', 1)
        if domain_part!="icp.edu.np":
            message="Only icp.edu.np mail allowed!"
            return flask.render_template('auth/login.html',url=authorization_url,message=message)
        flask.session['user'] = email_name
        return flask.redirect(flask.url_for('get_home'))
    else:
        return flask.render_template('auth/login.html',url=authorization_url)


#captcha-bypass
def getCaptchaToken():
    r=requests.post("https://freecaptchabypass.com/createTask",json={"clientKey":os.getenv('fcb_key'),"task":{"type":"ReCaptchaV3TaskProxyLess","websiteURL":"https://app.mysecondteacher.com.np/","websiteKey":"6LeuUMonAAAAABv-aLjhx_JTT7utsNhCwSPcBb5m"}})
    if r.status_code!=200: return False
    taskid=r.json()['taskId']
    i=0
    while True:
        i+=1
        requests.get("https://tools-httpstatus.pickup-services.com/200?sleep=5000")
        r=requests.post("https://freecaptchabypass.com/getTaskResult",json={"clientKey":os.getenv('fcb_key'),"taskId":taskid})
        if r.status_code!=200: return False
        if r.json()['status']!='ready': continue
        if i>=5: return False
        return r.json()['solution']['gRecaptchaResponse']


@app.post('/login')
def post_login():
    username= flask.request.form.get('username').strip()
    password=flask.request.form.get('password').strip()
    captcha=flask.request.form.get('g-recaptcha-response')
    authorization_url, state = flow.authorization_url(access_type='online')
    if not captcha: 
        message="Captcha misisng! Please let the site load completely and try again later."
        return flask.render_template('auth/login.html',url=authorization_url,message=message)
    else: captcha=captcha.strip()
    if username and password and captcha:
        if not username.endswith('@icp.edu.np'):
            message="Only icp.edu.np mail allowed!"
            return flask.render_template('auth/login.html',url=authorization_url,message=message)

        # validate captcha
        if 'X-Forwarded-For' in flask.request.headers: remoteip=flask.request.headers.get('X-Forwarded-For').split(',')[-1].strip()
        else: remoteip=flask.request.remote_addr
        verify=requests.post('https://www.google.com/recaptcha/api/siteverify',headers = {"content-type": "text/html"},params={"secret":os.getenv('captcha_secret'),"response":captcha,"remoteip":remoteip}).json()
        if verify['success']!=True:
            message="Captha Verification failed. Please try again later!"
            return flask.render_template('auth/login.html',url=authorization_url,message=message)
        if verify['score']<0.5:
            message="Captcha says you are sus. Please try again later!"
            return flask.render_template('auth/login.html',url=authorization_url,message=message)

        # attempt to login to mst
        reCaptchaToken=getCaptchaToken()
        if not reCaptchaToken: 
            message="Error when attempting to connect to mst. Try again later!"
            return flask.render_template('auth/login.html',url=authorization_url,message=message)            
        r=requests.post("https://api.mysecondteacher.com.np/api/TokenAuth/Authenticate",
                        headers={
                            "Accept":"*/*",
                            "Alt-Used":"api.mysecondteacher.com.np",
                            "Content-Type":"application/json",
                            "Origin":"https://mysecondteacher.com.np",
                            # "Platform":"web-app",
                            "Referer":"https://app.mysecondteacher.com.np/",
                            "Sec-Fetch-Dest":"empty",
                            "Sec-Fetch-Mode":"cors",
                            "Sec-Fetch-Site":"cross-site",
                            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
                            },json={"userNameOrEmailAddress":username,"password":password,'reCaptchaToken':reCaptchaToken})
        if r.status_code!=200:
            message="Invalid Credentials!"
            return flask.render_template('auth/login.html',url=authorization_url,message=message)
        email_name, _ = username.lower().strip().rsplit('@', 1)
        flask.session['user'] = email_name
        return flask.redirect(flask.url_for('get_home'))
    return flask.render_template('auth/login.html',url=authorization_url)

@app.route('/logout')
def logout():
    flask.session.pop('user', None)
    return flask.redirect(flask.url_for('login'))


@app.route('/imgs/<path:filename>')
def serve_static(filename):
    return flask.send_from_directory(IMAGES_PATH, filename)

##############################################################
                        # Event
##############################################################
admins = ["prabesh.sapkota.a23"]
days=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Satuday"]

TIME_RANGE_START = 7 * 60  # 7 AM in minutes
TIME_RANGE_END = 19 * 60   # 7 PM in minutes
MIN_DURATION = 60          # Minimum duration in minutes


def format_date(dt):
    now = datetime.now(tz_NP)
    diff = now - dt
    date = dt.date()
    time = dt.time().strftime('%I:%M %p')
    if diff.total_seconds() <= 120:
        return 'Just now'
    elif diff.total_seconds() <= 6 * 3600:
        if int(diff.total_seconds() / 3600)==0:
            return f"{int(diff.total_seconds() / 60)} minutes ago"
        return f"{int(diff.total_seconds() / 3600)} hours ago"
    elif date == now.date():
        return time
    elif date == (now - timedelta(days=1)).date():
        return 'Yesterday ' + time
    elif date >= (now - timedelta(days=now.weekday())).date() and date <= now.date():
        return date.strftime('%A ') + time
    elif date.year == now.year and date.month == now.month:
        return date.strftime('%d %A')
    elif date.year == now.year:
        return date.strftime('%b %d')
    else:
        return date.strftime('%Y %b')


def get_event_data():
    if not os.path.exists(events_file):
        with open(events_file, 'w') as f:
            json.dump([], f)
    with open(events_file, 'r') as f:
        try:
            events = json.load(f)
        except:
            events = []
    return events


def save_event_data(data,id):
    data['id']=id
    events = get_event_data()
    events = [event for event in events if event['id'] != id]
    data['events'].sort(key=lambda x: x['day'])
    events.append(data)
    with open(events_file, 'w') as f:
        json.dump(events, f, indent=4)

def parse_event_data(req,user):
    data = {
        "title": req.form['title'],
        "updated": datetime.now(tz_NP).isoformat(),
        "creator": user,
        "events": []
    }

    events = req.form.getlist('name')
    days = req.form.getlist('day')
    start_times = req.form.getlist('stime')
    end_times = req.form.getlist('etime')
    if not start_times:
        return None
    for i in range(len(events)):
        if not start_times[i] or not end_times[i]:
            continue
        event = {
            "day": int(days[i]),
            "stime": start_times[i],
            "etime": end_times[i],
            "name": events[i]
        }
        data["events"].append(event)
    if not data["events"]:
        return None
    return data

# Function to convert time string to minutes
def time_to_minutes(t_str):
    return datetime.strptime(t_str, "%I:%M %p").hour * 60 + datetime.strptime(t_str, "%I:%M %p").minute

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

# Function to calculate free time slots
def calculate_free_time(events_data):
    # Initialize days with empty event slots
    days_events = {day: [] for day in range(1, 8)}  # Assuming days 1 to 7

    # Populate event slots for each day
    for event_data in events_data:
        for event in event_data["events"]:
            day = event["day"]
            stime = time_to_minutes(event["stime"])
            etime = time_to_minutes(event["etime"])
            days_events[day].append((stime, etime))

    free_times = {}

    # Calculate free time slots for each day
    for day, slots in days_events.items():
        slots.sort()  # Sort events by start time
        free_slots = []
        last_end = TIME_RANGE_START

        # Check time before the first event
        if slots:
            if slots[0][0] > TIME_RANGE_START:
                free_slots.append((TIME_RANGE_START, slots[0][0]))

        # Check time between events
        for start, end in slots:
            if start > last_end:
                free_slots.append((last_end, start))
            last_end = max(last_end, end)

        # Check time after the last event
        if last_end < TIME_RANGE_END:
            free_slots.append((last_end, TIME_RANGE_END))

        # Filter out slots shorter than MIN_DURATION
        free_slots = [(start, end) for start, end in free_slots if end - start >= MIN_DURATION]

        # Remove duplicate intervals
        free_slots = f7(free_slots)

        # Convert slots back to readable format
        free_times[day] = [(str(timedelta(minutes=start)), str(timedelta(minutes=end))) for start, end in free_slots]

    return free_times


def convert_time_format(time_str):
    return datetime.strptime(time_str, "%H:%M:%S").strftime("%I:%M %p")


def parse_for_view(data):
    events = []
    for day, time_ranges in data.items():
        for stime, etime in time_ranges:
            events.append({
                "day": day,
                "stime": convert_time_format(stime),
                "etime": convert_time_format(etime),
                "name": ""
            })

    output_dict = {
        "events": events,
        "title": "Calculated free time slots"
    }
    return output_dict


@app.get('/free-slots/add')
@login_required
def get_event_add(user):
    return flask.render_template('events/add.html', days=days)

@app.post('/free-slots/add')
@login_required
def post_event_add(user):
    data = parse_event_data(flask.request,user)
    if not data: return "N/a", 400
    id=str(uuid.uuid4())
    save_event_data(data,id)
    return flask.redirect(flask.url_for('get_event_edit', event_id=id))

@app.get('/free-slots/edit/<event_id>')
@login_required
def get_event_edit(user,event_id):
    if not os.path.exists(events_file):
        return "Data file not found", 404

    with open(events_file, 'r') as f:
        try:
            events = json.load(f)
        except:
            events = []

    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return "Event not found", 404
    if event['creator']!=user and user not in admins :
        return flask.redirect(flask.url_for('get_eevnt_view', event_id=event_id))
    return flask.render_template('events/edit.html', data=event, days=days)

@app.post('/free-slots/edit/<event_id>')
@login_required
def post_event_edit(user, event_id):
    events=get_event_data()
    event = next((e for e in events if e['id'] == event_id), None)
    if event is None:
        return "Event not found", 404

    if event['creator'] != user and user not in admins:
        return flask.redirect(flask.url_for('get_event_view', event_id=event_id))

    if 'delete' in flask.request.form:
        events = [event for event in events if event['id'] != event_id ]
        with open(events_file, 'w') as f:
            json.dump(events, f, indent=4)
        return flask.redirect(flask.url_for('get_event_home'))

    data = parse_event_data(flask.request, event['creator'])
    if not data: return "N/a", 400
    save_event_data(data,event_id)
    return flask.redirect(flask.url_for('get_event_view', event_id=event_id))

@app.get('/free-slots/view/<event_id>')
def get_event_view(event_id):
    events=get_event_data()
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return "Event not found", 404
    return flask.render_template('events/view.html', data=event, days=days)


@app.post('/free-slots')
def post_event_home():
    user=None
    if 'user' in flask.session:
        user = flask.session['user']
    events = get_event_data()
    ids = flask.request.form.getlist('id')
    order = flask.request.form.getlist('order')
    reorder =  'reorder' in flask.request.form

    if not ids and not reorder:
        return flask.redirect(flask.url_for('get_event_home'))

    if 'calculate' in flask.request.form:
        selected_events = []
        titles=[]
        selected=[]
        for event in events:
            event['updated'] = format_date(datetime.fromisoformat(event['updated']))
            titles.append(event['title'])
            if event['id'] in ids:
                selected_events.append(event)
                selected.append(event['title'])

        free_time_slots=calculate_free_time(selected_events)
        return flask.render_template('events/view.html', data=parse_for_view(free_time_slots), days=days, titles=titles, selected=selected)


    elif 'delete' in flask.request.form:
        if not user in admins:
            return "Forbidden!", 403
        events = [event for event in events if event['id'] not in ids]
        with open(events_file, 'w') as f:
            json.dump(events, f, indent=4)

    elif reorder:
        if not user in admins:
            return "Forbidden!", 403
        ordered_events = sorted(events, key=lambda x: order.index(str(x['id'])))
        with open(events_file, 'w') as f:
            json.dump(ordered_events, f, indent=4)

    return flask.redirect(flask.url_for('get_event_home'))

@app.post('/free-slots-recalculate')
def post_event_recalculate():
    user = None
    if 'user' in flask.session:
        user = flask.session['user']

    events = get_event_data()
    ids = flask.request.form.getlist('id')
    order = flask.request.form.getlist('order')
    reorder = 'reorder' in flask.request.form

    # Check if this is a recalculation from the view page
    selected_titles = flask.request.form.getlist('selected_title')

    if (not ids and not reorder) and not selected_titles:
        return flask.redirect(flask.url_for('get_event_home'))

    # Process the events and determine which ones are selected
    all_titles = []
    selected_events = []

    for event in events:
        event['updated'] = format_date(datetime.fromisoformat(event['updated']))
        all_titles.append(event['title'])

        # If we're recalculating based on selected_titles checkboxes
        if selected_titles and event['title'] in selected_titles:
            selected_events.append(event)
        # Or if we're calculating based on the original form's IDs
        elif not selected_titles and event['id'] in ids:
            selected_events.append(event)

    # Calculate free time slots
    free_time_slots = calculate_free_time(selected_events)
    selected = [event['title'] for event in selected_events]

    return flask.render_template(
        'events/view.html',
        data=parse_for_view(free_time_slots),
        days=days,
        titles=all_titles,
        selected=selected
    )

@app.get('/free-slots/events.json')
def get_eevnt_json():
    events = get_event_data()
    return events


@app.get('/free-slots')
def get_event_home():
    user=None
    if 'user' in flask.session:
        user = flask.session['user']
    events = get_event_data()
    for event in events:
        event['updated'] = format_date(datetime.fromisoformat(event['updated']))

    return flask.render_template('events/home.html', data=events, user=user, admins=admins)

##############################################################
                        # exam
##############################################################
exam_file=BASE_DIR / "data/exam.json"

# parse_data_file
with open(exam_file) as f:
    exam_data = json.load(f)


@app.get('/exam')
def get_exam_home():
    last_selected_class=flask.session.get('last_selected_class','')
    classes=list(exam_data.keys())
    if last_selected_class: key=last_selected_class
    else: key=classes[0]
    return flask.render_template('exam/index.djhtml', current=key, data=exam_data[key], classes=exam_data.keys())


@app.post('/exam')
def post_exam_home():
    classe=flask.request.form.get('class')
    flask.session['last_selected_class'] = classe
    if not classe in exam_data:
        return "N/a", 400
    return flask.render_template('exam/index.djhtml',current=classe, data=exam_data[classe], classes=exam_data.keys())


@app.template_filter('smart_linebreak')
def smart_linebreak(text):
    n = 16  # Fixed length after which to start looking for spaces
    if len(text) > n:
        # Split the text after n characters and then at spaces
        part1 = text[:n]
        remainder = text[n:]
        # return part1 + '<br>'.join(remainder.split())
        for r in remainder.split():
            if len(r)<5:
                part1+=r+' '
            else:
                part1+='<br>'+r
        return part1
    return text

##############################################################
                        # mst
##############################################################

gitlab_token="glpat-PCDAKKhQedujuxP4wx6u"
tree = {}
def get_tree():
    global tree
    try:
        for item in requests.get(f"https://gitlab.com/api/v4/projects/61879485/repository/tree/?ref=main&private_token={gitlab_token}&per_page=10000&recursive=true", timeout=3).json():
            parts = item['path'].split('/')
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {'__children__': {}}
                current = current[part]['__children__']
            current[parts[-1]] = {'__children__': {}}
    except: pass
    return tree
get_tree()

@app.get('/seat-plan')
def get_exam_seat():
    with open(BASE_DIR/'data/seat_plan.json') as f:
        data = json.load(f)
    return flask.render_template('map/seat_plan.html', data=data)


@app.get('/all-classes-today')
def all_classes_today():
    with open(data_file) as f:
        data = json.load(f)
    # get today's day: SUN, MON, ..
    today = datetime.now(tz_NP).strftime("%a").upper()
    schedules_today={}
    classes = data["classes"]
    for cl in classes:
        year = cl["class"]
        day = cl["day"]
        if day != today: continue
        for s in cl["sections"]:
            if not year in schedules_today:
                schedules_today[year]={}
            if not s in schedules_today[year]:
                schedules_today[year][s]=[]
            schedules_today[year][s].append([cl["stime"], cl["room"]])
    return flask.render_template('all-classes-today.html', data=schedules_today)

@app.get('/mst')
def get_mst_home():
    global tree
    if not tree:
        tree=get_tree()
    return flask.render_template('mst_/index.html', token=gitlab_token, tree=tree)


port = int(os.environ.get("PORT", 5000))
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)
