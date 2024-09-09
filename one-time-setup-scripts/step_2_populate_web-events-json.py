import json
import uuid
import datetime
import re

import pytz
tz_NP = pytz.timezone('Asia/Kathmandu')
datetime_NP = str(datetime.datetime.now(tz_NP))

from config import get_basedir

BASE_DIR=get_basedir()
data_file=BASE_DIR / "one-time-setup-scripts/data.json"

with open(data_file) as f:
    data = json.load(f)

weekdays=["SUN","MON","TUE","WED","THU","FRI","SAT"]
event_data={}

for c in data["classes"]:
    teacher_key=c["teacher"].split(' ',1)[-1]
    secs=c["sections"]
    sec_key=""
    if len(secs)>1:
        sec_key=f"{secs[0]}-{secs[-1]}"
    else: sec_key=secs[0]
    c_key=f"[{sec_key}] {c['class']}"

    day=weekdays.index(c["day"])+1

    teacher_note=f"{c['class']} [{sec_key}]"
    student_note=f"{c['module']} @ {c['room']}"

    to_append = {
        "day": day,
        "stime": c["stime"],
        "etime": c["etime"],
    }

    event_data.setdefault(teacher_key, []).append({
        **to_append,
        "name": teacher_note,
    })
    for sec in secs:
        c_key=f"[{sec}] {c['class']}"
        event_data.setdefault(c_key, []).append({
            **to_append,
            "name": student_note,
        })
del data

def custom_sort_key(item):
    title = item["title"]
    if title.startswith("["):
        # Extract year and section information
        match = re.match(r'\[([^]]+)\]\s*Year\s*(\d+)\s*(.*)', title)
        if match:
            section, year, program = match.groups()
            # Sort by year first, then by section
            return (int(year), section, program)
    return (0, title)  # For teacher keys, sort alphabetically

events = [
    {
        "id": str(uuid.uuid4()),
        "title": k,
        "creator": "_system",
        "updated": datetime_NP,
        "events": sorted(v, key=lambda x: x["day"]),
    }
    for k, v in event_data.items()
]

events.sort(key=custom_sort_key)
# events.sort(key=lambda x: x["title"][:7], reverse=False)

with open(BASE_DIR / "web/events.json","w") as f:
    json.dump(events,f,indent=4)