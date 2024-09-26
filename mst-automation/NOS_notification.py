# 0 12 * * * nohup python3 -u /root/discord/nos.py > /root/discord/nos.log 2>&1 &

from pathlib import Path
from datetime import datetime
import json
import requests

assignments={
    "y2": {
    "NOS Log 1": "9/30/2024",
    "NOS Log 2": "11/11/2024",
    "NOS Log 3": "11/18/2024",
    "NOS Log 4": "11/25/2024",
    "NOS Log 5": "12/2/2024",
    "NOS Log 6": "12/9/2024",
    "NOS Log 7": "12/16/2024",
    "NOS Log 8": "12/23/2024",
    "NOS Log 9": "12/30/2024",
    }
}

BASE_DIR = Path(__file__).resolve().parent

creds_file=BASE_DIR/'mst_creds.json'
with open(creds_file) as f:
    creds=json.load(f)

for year in assignments:
    for assignment in assignments[year]:
        due_date=datetime.strptime(assignments[year][assignment], '%m/%d/%Y').replace(hour=23, minute=59)
        days_left=(due_date.date()-datetime.now().date()).days
        if days_left==5:
            requests.post(creds[year]['webhook'], data={'content':f'🚩 [<t:{int(due_date.timestamp())}:R>] ' +assignment})
