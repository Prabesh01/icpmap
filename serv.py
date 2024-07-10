import flask
import uuid
from datetime import datetime, timedelta
import pytz
tz_NP = pytz.timezone('Asia/Kathmandu')
import os
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow
import requests
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

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

flow.redirect_uri = 'http://127.0.0.1:5000/login'

app = flask.Flask(__name__)
app.secret_key = str(uuid.uuid4())

login_html='''
<a href="{{ url }}">Login with Google</a>
<p> Only icp.edu.np email allowed!</p>
{{ message }}
'''

@app.get('/login')
def login():
    if 'user' in flask.session:
        return flask.redirect(flask.url_for('get_home'))

    message=''
    if flask.request.args.get('code'):
        flow.fetch_token(code=flask.request.args.get('code'))
        json_creds = flow.credentials.to_json()
        dict_creds = json.loads(json_creds)
        r=requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={"Authorization":"Bearer "+dict_creds['token']})
        if r.status_code != 200: 
            message="Login Unsucessfull:/ Please try again later!"
            return flask.render_template_string(login_html,url=authorization_url,message=message)
        email_name, domain_part = r.json()['email'].lower().strip().rsplit('@', 1)
        if domain_part!="icp.edu.np":
            message="Only icp.edu.np mail allowed!" 
            return flask.render_template_string(login_html,url=authorization_url,message=message)
        flask.session['user'] = email_name
        return flask.redirect(flask.url_for('get_home'))
    else:
        authorization_url, state = flow.authorization_url(access_type='online')
        return flask.render_template_string(login_html,url=authorization_url)

@app.route('/logout')
def logout():
    flask.session.pop('user', None)
    return flask.redirect(flask.url_for('login'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' in flask.session:
            user = flask.session['user']
            return f(user=user, *args, **kwargs)
        else:
            return flask.redirect(flask.url_for('login'))
    return decorated_function

admins = ["prabesh.sapkota.a23"]
DATA_FILE = 'events.json'
days=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Satuday"]

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


def get_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    with open(DATA_FILE, 'r') as f:
        try:
            events = json.load(f)
        except:
            events = []
    return events


def save_data(data,id):
    data['id']=id
    events = get_data()
    events = [event for event in events if event['id'] != id]
    events.append(data)
    with open(DATA_FILE, 'w') as f:
        json.dump(events, f, indent=4)

def parse_data(req,user):
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

@app.get('/add')
@login_required
def get_add(user):
    return flask.render_template('add.html', days=days)

@app.post('/add')
@login_required
def post_add(user):
    data = parse_data(flask.request,user)
    if not data: return "N/a", 400
    id=str(uuid.uuid4())
    save_data(data,id)
    return flask.redirect(flask.url_for('get_edit', event_id=id))

@app.get('/edit/<event_id>')
@login_required
def get_edit(user,event_id):
    if not os.path.exists(DATA_FILE):
        return "Data file not found", 404

    with open(DATA_FILE, 'r') as f:
        try:
            events = json.load(f)
        except:
            events = []

    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return "Event not found", 404
    if event['creator']!=user and user not in admins :
        return flask.redirect(flask.url_for('get_view', event_id=event_id))
    return flask.render_template('edit.html', data=event, days=days)

@app.post('/edit/<event_id>')
@login_required
def post_edit(user, event_id):
    events=get_data()
    event = next((e for e in events if e['id'] == event_id), None)
    if event is None:
        return "Event not found", 404

    if event['creator'] != user and user not in admins:
        return flask.redirect(flask.url_for('get_view', event_id=event_id))

    if 'delete' in flask.request.form:
        events = [event for event in events if event['id'] != event_id ]
        with open(DATA_FILE, 'w') as f:
            json.dump(events, f, indent=4)
        return flask.redirect(flask.url_for('get_home'))

    data = parse_data(flask.request, user)
    if not data: return "N/a", 400
    save_data(data,event_id)
    return flask.redirect(flask.url_for('get_view', event_id=event_id))

@app.get('/view/<event_id>')
@login_required
def get_view(user, event_id):
    events=get_data()
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return "Event not found", 404
    return flask.render_template('view.html', data=event, days=days)

@app.get('/')
@login_required
def get_home(user):
    events = get_data()
    for event in events:
        event['updated'] = format_date(datetime.fromisoformat(event['updated']))

    return flask.render_template('home.html', data=events, user=user, admins=admins)

TIME_RANGE_START = 7 * 60  # 7 AM in minutes
TIME_RANGE_END = 19 * 60   # 7 PM in minutes
MIN_DURATION = 60          # Minimum duration in minutes

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

@app.post('/')
@login_required
def post_home(user):
    events = get_data()
    ids = flask.request.form.getlist('id')
    if not ids:
        return flask.redirect(flask.url_for('get_home'))
    if 'calculate' in flask.request.form:
        selected_events = []
        for event in events:
            event['updated'] = format_date(datetime.fromisoformat(event['updated']))
            if event['id'] in ids:
                selected_events.append(event)

        free_time_slots=calculate_free_time(selected_events)
        return flask.render_template('home.html', data=events, user=user, admins=admins, free_time_slots=free_time_slots, days=days)

    elif 'delete' in flask.request.form:
        if not user in admins:
            return "Forbidden!", 403
        events = [event for event in events if event['id'] not in ids]
        with open(DATA_FILE, 'w') as f:
            json.dump(events, f, indent=4)
    return flask.redirect(flask.url_for('get_home'))


if __name__ == '__main__':
    app.run(debug=True)
