### Prepare

1. For Google Oauth Login in web, create OAUTH Client ID from [here](https://console.cloud.google.com/apis/credentials) and keep GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in credentials/.env file. Also add flask's web_url.
 - Type: Web application
 - Authorized redirect URI: flask_web_url/login and http://127.0.0.1:5000/login

2. For google calendar automation with step_3.py, download credentials.json file from Google Cloud Project as mentioned [here](https://developers.google.com/calendar/api/quickstart/python). 
 - Type: Web application
 - Authorized redirect URI: flask_web_url with trailing slash and http://localhost/

 3. Add xlsx files for all classes's schedule and exam schedule in data-sources and mention the path in scripts/step_1.py.

 4. In scripts/setp_3.py, manually add holidays, exam weeks and other required dates from line 30 to line 55.

 5. Install required packages:
  - `python -m venv .venv`
  - `.venv/bin/pip install -r requirements.txt`

 ### Run

 - Just once for the first time, run step-1,2,3,4.py files in order.
 - `.venv/bin/python web/main.py`
 - Visit http://127.0.0.1:5000
