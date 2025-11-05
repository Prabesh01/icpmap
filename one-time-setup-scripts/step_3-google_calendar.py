import json
import os
import time
from datetime import datetime
from datetime import timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import get_basedir

BASE_DIR=get_basedir()
data_file=BASE_DIR / "data/data.json"
credential_file=BASE_DIR / "credentials/credentials.json"
token_file=BASE_DIR / "credentials/token.json"

with open(data_file) as f:
    data = json.load(f)
sections=data["sections"]
cal_ids=data.get("cal_ids",{})
classes={}
for c in data["classes"]:
  name=c.pop("class")
  if not name in classes:
    classes[name]=[c]
  else:
    classes[name].append(c)
del data

# class schedule are different before and after the sem break.
# if set true, add classes for only pre-sem-break periods.
populate_pre_sem_break_classes=False

# new-year, saraswati-puja, shivaratri, holi, nepali new year, lobor day
holidays=["2026/01/01","2026/01/15","2026/02/15","2026/03/02","2026/04/14","2026/05/01"]
# dashain-tihar holiday range
holiday_range="2025/09/21 - 2025/11/01" # count revision week as well

y1_spring_week1="2024/02/18" # first day must be sunday
y1_autumn_week1="2025/11/02" # first day must be sunday
y2_3_week1="2025/09/07" # first day must be sunday

y1_spring_until="2024/08/24"
y1_autumn_until="2026/05/30"
y2_3_until="2026/05/30"

# first saturday of week 1 after break
y1_spring_sem_break="2024/06/08"
y1_autumn_sem_break="2026/02/21" # Saturday Week-1
y2_3_sem_break="2026/02/21" # Saturday of Week-1
y2_3_sem_break_range="2026/02/01 - 2026/02/14" # end on saturday

y1_spring_exam_weeks=["2024/05/12 - 2024/06/01","2024/08/25 - 2024/09/14"]
y1_autumn_exam_weeks=["2026/01/25 - 2026/02/14","2026/05/10 - 2026/05/30"]
y2_3_exam_weeks=["2026/01/11 - 2026/01/31","2026/05/10 - 2026/05/30"]

# not for spring intake...
reasestment_range="2026/08/02 - 2026/08/22"

###############################################################3
                 # begin deals with google calendar
###############################################################3

SCOPES = ["https://www.googleapis.com/auth/calendar"]
def gCalServ():
  creds = None

  if os.path.exists(token_file):
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          credential_file, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_file, "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)
    return service
  except Exception as error:
    print(f"An error occurred: {error}")

service=gCalServ()


# create calendar for each class - section
def create_cal():
    for k,v in sections.items():
        for s in v:
            cal_name = f"{k} - {s}".strip()
            if cal_name in cal_ids: continue
            time.sleep(5)
            calendar = {'summary': cal_name, 'timeZone': 'Asia/Kathmandu'}
            created_calendar = service.calendars().insert(body=calendar).execute()
            cal_ids[cal_name]=created_calendar['id']
            print(f"created calendar for {cal_name}.")

    with open(data_file) as f:
        data = json.load(f)
    data["cal_ids"]=cal_ids
    with open(data_file,"w") as f:
        json.dump(data,f,indent=4)

# create_cal()


weekdays=["SUN","MON","TUE","WED","THU","FRI","SAT"]
def add_classes():
    for sheet in classes:
      print(sheet)
      clase=classes[sheet]
      for clas in clase:
        day_offset=weekdays.index(clas["day"])
        if 'year 1' in sheet.lower() and 'spring' in sheet.lower():
          if populate_pre_sem_break_classes:
            sedate=(datetime.strptime(y1_spring_week1, "%Y/%m/%d")+ timedelta(days=day_offset)).strftime("%Y-%m-%d")
            until=y1_spring_sem_break
          else:
            sedate=(datetime.strptime(y1_spring_sem_break, "%Y/%m/%d")+ timedelta(days=day_offset+1)).strftime("%Y-%m-%d")
            until=y1_spring_until
        elif 'year 1' in sheet.lower() :
          if populate_pre_sem_break_classes:
            sedate=(datetime.strptime(y1_autumn_week1, "%Y/%m/%d")+ timedelta(days=day_offset)).strftime("%Y-%m-%d")
            until=y1_autumn_sem_break
          else:
            sedate=(datetime.strptime(y1_autumn_sem_break, "%Y/%m/%d")+ timedelta(days=day_offset+1)).strftime("%Y-%m-%d")
            until=y1_autumn_until
        else:
          if populate_pre_sem_break_classes:
            sedate=(datetime.strptime(y2_3_week1, "%Y/%m/%d")+ timedelta(days=day_offset)).strftime("%Y-%m-%d")
            until= y2_3_sem_break_range.split('-')[0].strip()
          else:
            sedate=(datetime.strptime(y2_3_sem_break_range.split('-')[-1].strip(), "%Y/%m/%d")+ timedelta(days=day_offset+1)).strftime("%Y-%m-%d")
            until=y2_3_until
        for section in clas["sections"]:
          cal_name=sheet+" - "+section
          cal_name=cal_name.strip()
          if 'spring' in cal_name.lower(): continue
        
          event = {
          'summary': clas["module"],
          'location': clas["room"].split('-')[-1],
          'description': clas["code"]+'\nBy '+clas["teacher"],
          'start': {
              'dateTime': sedate+"T"+datetime.strptime(clas["stime"], "%I:%M %p").time().strftime("%H:%M")+":00+05:45",
              'timeZone': 'Asia/Kathmandu',
          },
          'end': {
              'dateTime': sedate+"T"+datetime.strptime(clas["etime"], "%I:%M %p").time().strftime("%H:%M")+":00+05:45",
              'timeZone': 'Asia/Kathmandu',
          },
          'recurrence': [
              'RRULE:FREQ=WEEKLY;UNTIL='+until.replace("/","")+"T240000Z"
          ],
          }
          print(event)
          event = service.events().insert(calendarId=cal_ids[cal_name], body=event).execute()

# add_classes()


def del_classes_when_events():
  holiday_start=datetime.strptime(holiday_range.split(' - ')[0], "%Y/%m/%d")
  holiday_end=datetime.strptime(holiday_range.split(' - ')[1], "%Y/%m/%d")
  for sheet in sections:
    print(sheet)
    def del_event_all_sections(sdate,edate=None):
      if not edate: edate=sdate
      edate=edate+timedelta(days=1)
      for section in sections[sheet]:
        cal_name=sheet+" - "+section
        cal_name=cal_name.strip()
        if 'spring' in cal_name.lower(): continue
        cal_id=cal_ids[cal_name]
        page_token = None
        while True:
          events = service.events().list(calendarId=cal_id, timeMin='T'.join(str(sdate).split())+"+05:45",timeMax='T'.join(str(edate).split())+"+05:45", timeZone="UTC+05:45").execute()
          recurrence_exceptions = []
          current_date=sdate
          while current_date < edate:
            recurrence_exceptions.append(current_date.strftime('%Y%m%d'))
            current_date += timedelta(days=1)

          ignore_the_event=False
          for event in events['items']:
            temp_recurrence_exceptions=[]
            for re in recurrence_exceptions:
               # if not dateTime in event, its prolly whole day or longer events. not a class sched. do not delete these.
               if not 'dateTime' in event["start"]: 
                ignore_the_event=True
                break
               temp_recurrence_exceptions.append(str(re)+"T"+event["start"]["dateTime"].split("T")[-1].split("+")[0].replace(":",""))
            if ignore_the_event: continue
            recurrence = event.get('recurrence', [])
            exdate_rule = None
            for rule in recurrence:
              if rule.startswith('EXDATE'):
                  exdate_rule = rule
                  break
            if exdate_rule:
                # Split the existing rule to modify it
                existing_dates = exdate_rule.split(':')[1]
                new_exdate = existing_dates + ',' + ','.join(temp_recurrence_exceptions)
                # Update the EXDATE rule
                updated_rule = 'EXDATE;TZID=Asia/Kathmandu:' + new_exdate
                recurrence.remove(exdate_rule)
                recurrence.append(updated_rule)
            else:
                # Create a new EXDATE rule
                new_exdate_rule = 'EXDATE;TZID=Asia/Kathmandu:' + ','.join(temp_recurrence_exceptions)
                recurrence.append(new_exdate_rule)                    
            event['recurrence'] = recurrence
            updated_event = service.events().update(calendarId=cal_id,eventId=event["id"],body=event).execute()
            # delete only current instance not al occurances
          page_token = events.get('nextPageToken')
          if not page_token:
            break
          
    has_sem_break_range=False
    if 'year 1' in sheet.lower() and 'spring' in sheet.lower():
        exam_week_start=datetime.strptime(y1_spring_exam_weeks[0].split(' - ')[0], "%Y/%m/%d")
        exam_week_end=datetime.strptime(y1_spring_exam_weeks[0].split(' - ')[1], "%Y/%m/%d")
    elif 'year 1' in sheet.lower():
        exam_week_start=datetime.strptime(y1_autumn_exam_weeks[0].split(' - ')[0], "%Y/%m/%d")
        exam_week_end=datetime.strptime(y1_autumn_exam_weeks[0].split(' - ')[1], "%Y/%m/%d")        
    else:
        has_sem_break_range=True
        sem_break_start=datetime.strptime(y2_3_sem_break_range.split(' - ')[0], "%Y/%m/%d")
        sem_break_end=datetime.strptime(y2_3_sem_break_range.split(' - ')[1], "%Y/%m/%d")
        exam_week_start=datetime.strptime(y2_3_exam_weeks[0].split(' - ')[0], "%Y/%m/%d")
        exam_week_end=datetime.strptime(y2_3_exam_weeks[0].split(' - ')[1], "%Y/%m/%d")   
     
    del_event_all_sections(holiday_start,holiday_end)
    for holiday in holidays:
       del_event_all_sections(datetime.strptime(holiday, "%Y/%m/%d"))
    if has_sem_break_range:
       del_event_all_sections(sem_break_start,sem_break_end)
    del_event_all_sections(exam_week_start,exam_week_end)

# del_classes_when_events()

def add_events():
    holiday_start=datetime.strptime(holiday_range.split(' - ')[0], "%Y/%m/%d")
    holiday_end=datetime.strptime(holiday_range.split(' - ')[1], "%Y/%m/%d")
    for sheet in sections:
      print(sheet)
      def add_event_all_sections(summary,evstart,evend):
        transparency="transparent"
        if 'exam' in summary.lower() or 'semester break' in summary.lower(): transparency="opaque"
        event = {
        'summary': summary,
        'start': {
            'date': evstart.strftime("%Y-%m-%d"),
            'timeZone': 'Asia/Kathmandu',
        },
        'end': {
            'date': evend.strftime("%Y-%m-%d"),
            'timeZone': 'Asia/Kathmandu',
        },
        'transparency':transparency
        }

        for section in sections[sheet]:
          cal_name=sheet+" - "+section
          cal_name=cal_name.strip()
          if 'spring' in cal_name.lower(): continue
          event = service.events().insert(calendarId=cal_ids[cal_name], body=event).execute()

      week_cnt_sec=0
      has_sem_break_range=False
      week_cnt_pri=1
      if 'year 1' in sheet.lower() and 'spring' in sheet.lower():
        sedate=y1_spring_week1
        until=y1_spring_until
        sem_break=y1_spring_sem_break
        exam_week_start=datetime.strptime(y1_spring_exam_weeks[0].split(' - ')[0], "%Y/%m/%d")
        exam_week_end=datetime.strptime(y1_spring_exam_weeks[0].split(' - ')[1], "%Y/%m/%d")
      elif 'year 1' in sheet.lower() :
        sedate=y1_autumn_week1
        until=y1_autumn_until
        sem_break=y1_autumn_sem_break
        exam_week_start=datetime.strptime(y1_autumn_exam_weeks[0].split(' - ')[0], "%Y/%m/%d")
        exam_week_end=datetime.strptime(y1_autumn_exam_weeks[0].split(' - ')[1], "%Y/%m/%d")        
      else:
        sedate=y2_3_week1
        until=y2_3_until
        sem_break=y2_3_sem_break
        has_sem_break_range=True
        sem_break_start=datetime.strptime(y2_3_sem_break_range.split(' - ')[0], "%Y/%m/%d")
        sem_break_end=datetime.strptime(y2_3_sem_break_range.split(' - ')[1], "%Y/%m/%d")
        exam_week_start=datetime.strptime(y2_3_exam_weeks[0].split(' - ')[0], "%Y/%m/%d")
        exam_week_end=datetime.strptime(y2_3_exam_weeks[0].split(' - ')[1], "%Y/%m/%d")   
      sem_break=datetime.strptime(sem_break, "%Y/%m/%d")  
      next_sat=(datetime.strptime(sedate, "%Y/%m/%d")- timedelta(days=1))
      until=datetime.strptime(until, "%Y/%m/%d")
      sem_break_added=False
      while True:
        next_sat=next_sat + timedelta(days=7)

        if next_sat>until:
           break
        if next_sat>=holiday_start and next_sat<=holiday_end:
           continue
        
        if has_sem_break_range:
           if next_sat>=sem_break_start and next_sat<=sem_break_end:
              if not sem_break_added:
                add_event_all_sections("Semester Break",sem_break_start,sem_break_end + timedelta(days=1))
                sem_break_added=True
              continue
           
        if next_sat==sem_break: week_cnt_sec=1

        # event summary...   
        if week_cnt_sec:
            summary=f"Week {week_cnt_pri} / Week {week_cnt_sec}"
        else:
            summary=f"Week {week_cnt_pri}"

        if next_sat>=exam_week_start and next_sat<=exam_week_end:
          evstart=next_sat - timedelta(days=6)
          evend=next_sat  + timedelta(days=1)
          summary+=" Exam Week"        
        else:
          evstart=  evend = next_sat      
        week_cnt_pri+=1
        if week_cnt_sec: week_cnt_sec+=1
        add_event_all_sections(summary,evstart,evend)

      has_reassess_range=False  
      reassess_start=datetime.strptime(reasestment_range.split(' - ')[0], "%Y/%m/%d")
      reassess_end=datetime.strptime(reasestment_range.split(' - ')[1], "%Y/%m/%d")

      if 'year 1' in sheet.lower() and 'spring' in sheet.lower():
        exam_week_start=datetime.strptime(y1_spring_exam_weeks[1].split(' - ')[0], "%Y/%m/%d")
        exam_week_end=datetime.strptime(y1_spring_exam_weeks[1].split(' - ')[1], "%Y/%m/%d")
      elif 'year 1' in sheet.lower():
        has_reassess_range=True
        exam_week_start=datetime.strptime(y1_autumn_exam_weeks[1].split(' - ')[0], "%Y/%m/%d")
        exam_week_end=datetime.strptime(y1_autumn_exam_weeks[1].split(' - ')[1], "%Y/%m/%d")        
      else:
        has_reassess_range=True
        exam_week_start=datetime.strptime(y2_3_exam_weeks[1].split(' - ')[0], "%Y/%m/%d")
        exam_week_end=datetime.strptime(y2_3_exam_weeks[1].split(' - ')[1], "%Y/%m/%d")   
      if has_reassess_range:
        add_event_all_sections("Reassessment",reassess_start,reassess_end + timedelta(days=1))
      add_event_all_sections("Exam Week",exam_week_start,exam_week_end + timedelta(days=1))

# add_events()


def make_cals_public():
  tot=len(cal_ids.items())
  cnt=0
  for _,id in cal_ids.items():
    cnt+=1
    print(f"{cnt}/{tot}")
    rule = {
        'scope': {
            'type': 'default'
        },
        'role': 'reader'
    }

    service.acl().insert(calendarId=id, body=rule).execute()

# make_cals_public()


def clear_calendar():
    for cal_name,cal_id in cal_ids.items():
        if cal_name!="xxx": continue

        page_token = None
        while True:
            events = service.events().list(calendarId=cal_id, pageToken=page_token).execute()
            for event in events['items']:
                service.events().delete(calendarId=cal_id, eventId=event["id"]).execute()
            page_token = events.get('nextPageToken')
            if not page_token:
                break

# clear_calendar()


def delete_all_events_from_calendar():
    for cal_name,cal_id in cal_ids.items():
        if not cal_name.startswith('Year 3 BIC - '): continue
        print(cal_name)
        page_token = None
        while True:
            events = service.events().list(calendarId=cal_id, pageToken=page_token).execute()
            for event in events['items']:
                if 'originalStartTime' in event:
                  continue
                else:
                  if not 'dateTime' in event["start"]: 
                    service.events().delete(calendarId=cal_id, eventId=event["id"]).execute()
            page_token = events.get('nextPageToken')
            if not page_token:
                break

# delete_all_events_from_calendar()
