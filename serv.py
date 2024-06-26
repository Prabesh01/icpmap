
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import json
import os
import jwt
import requests

from dotenv import load_dotenv
load_dotenv()

jwt_secret=os.getenv('jwt_secret')

classes={'SUN': [{'class': 'Year 1 BBA ( Spring)', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Kiran Kunwar', 'room': 'TR03- Thames'}, {'class': 'Year 1 BBA ( Spring)', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Ms. Sajena Dwa', 'room': 'TR03- Thames'}, {'class': 'Year 1 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Ashish Subedi', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BBA', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Arjun Sapkota', 'room': 'TR03- Thames'}, {'class': 'Year 2 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Sajena Dwa', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Arjun Sapkota', 'room': 'SR02- Begnas'}, {'class': 'Year 3 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Anil Rai', 'room': 'TR02- Stonehenge'}, {'class': 'Year 3 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Jeevan Pahari', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC-Spring', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Sushil Paudel', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC-Spring', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Sushil Paudel', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Sushil Paudel', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC', 'stime': '07:30 AM', 'etime': '09:00 AM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Amar Khanal', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Amar Khanal', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BIC', 'stime': '07:30 AM', 'etime': '09:00 AM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Midhir Rana', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 2 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Midhir Rana', 'room': 'TR02- Stonehenge'}, {'class': 'Year 2 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Sunil Thapa', 'room': 'Lab01- Gokyo'}, {'class': 'Year 2 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 2 BIC', 'stime': '12:30 PM', 'etime': '02:00 PM', 'teacher': 'Mr. Midhir Rana', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Sunil Thapa', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Prasant Adhikari', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'SR04- Tilicho'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'Lab01- Gokyo'}, {'class': 'Year 3 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'SR04- Tilicho'}, {'class': 'Year 3 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'Lab01- Gokyo'}, {'class': 'Year 3 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'SR01- Fewa'}, {'class': 'Year 3 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'Lab01- Gokyo'}], 'MON': [{'class': 'Year 1 BBA ( Spring)', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Ashish Subedi', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BBA ( Spring)', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Arjun Sapkota', 'room': 'SR01- Fewa'}, {'class': 'Year 1 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Sajena Dwa', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Kiran Kunwar', 'room': 'TR01- Bigben'}, {'class': 'Year 2 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Kiran Kunwar', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Jeevan Pahari', 'room': 'SR01- Fewa'}, {'class': 'Year 3 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Ashish Subedi', 'room': 'TR03- Thames'}, {'class': 'Year 3 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Vikram Rana', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Amar Khanal', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'SR03- Rara'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Amar Khanal', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Sushil Paudel', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC', 'stime': '07:30 AM', 'etime': '09:00 AM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Sushil Paudel', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Amar Khanal', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'LT02- Annapurna'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'Lab01- Gokyo'}, {'class': 'Year 2 BIC', 'stime': '08:00 AM', 'etime': '09:30 AM', 'teacher': 'Mr. Midhir Rana', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'Lab01- Gokyo'}, {'class': 'Year 2 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Midhir Rana', 'room': 'TR02- Stonehenge'}, {'class': 'Year 2 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Prasant Adhikari', 'room': 'TR03- Thames'}, {'class': 'Year 2 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Sunil Thapa', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 2 BIC', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Midhir Rana', 'room': 'TR02- Stonehenge'}, {'class': 'Year 2 BIC', 'stime': '12:30 PM', 'etime': '02:00 PM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 2 BIC', 'stime': '12:30 PM', 'etime': '02:00 PM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Sunil Thapa', 'room': 'SR02- Begnas'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'SR03- Rara'}, {'class': 'Year 3 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'SR03- Rara'}, {'class': 'Year 3 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'SR04- Tilicho'}, {'class': 'Year 3 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'SR04- Tilicho'}], 'TUE': [{'class': 'Year 1 BBA ( Spring)', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Kiran Kunwar', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BBA ( Spring)', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Ms. Sajena Dwa', 'room': 'Meeting Room'}, {'class': 'Year 1 BBA', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Ashish Subedi', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BBA', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Arjun Sapkota', 'room': 'LT02- Annapurna'}, {'class': 'Year 2 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Sajena Dwa', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Arjun Sapkota', 'room': 'SR01- Fewa'}, {'class': 'Year 3 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Anil Rai', 'room': 'TR03- Thames'}, {'class': 'Year 3 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Jeevan Pahari', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC-Spring', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Krishna Wagle', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'SR01- Fewa'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC-Spring', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC-Spring', 'stime': '03:00 PM', 'etime': '04:30 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'SR04- Tilicho'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Amar Khanal', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'SR04- Tilicho'}, {'class': 'Year 1 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'SR01- Fewa'}, {'class': 'Year 1 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Amar Khanal', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Amar Khanal', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'SR03- Rara'}, {'class': 'Year 1 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Amar Khanal', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '02:30 PM', 'etime': '04:00 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Prasant Adhikari', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '07:30 AM', 'etime': '09:00 AM', 'teacher': 'Mr. Midhir Rana', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 2 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'TR01- Bigben'}, {'class': 'Year 2 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Sunil Thapa', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 2 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Midhir Rana', 'room': 'TR03- Thames'}, {'class': 'Year 2 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '12:30 PM', 'etime': '02:00 PM', 'teacher': 'Mr. Midhir Rana', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Sunil Thapa', 'room': 'TR03- Thames'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'LT02- Annapurna'}], 'WED': [{'class': 'Year 1 BBA ( Spring)', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Ashish Subedi', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BBA ( Spring)', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Arjun Sapkota', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Sajena Dwa', 'room': 'TR03- Thames'}, {'class': 'Year 1 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Kiran Kunwar', 'room': 'TR03- Thames'}, {'class': 'Year 2 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Kiran Kunwar', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Jeevan Pahari ', 'room': 'SR02- Begnas'}, {'class': 'Year 3 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Ashish Subedi', 'room': 'TR02- Stonehenge'}, {'class': 'Year 3 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Vikram Rana', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC-Spring', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC-Spring', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Krishna Wagle', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'LT02- Annapurna'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'SR01- Fewa'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '07:30 AM', 'etime': '09:00 AM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Amar Khanal', 'room': 'SR04- Tilicho'}, {'class': 'Year 1 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Amar Khanal', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'SR03- Rara'}, {'class': 'Year 1 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'SR02- Begnas'}, {'class': 'Year 1 BIC', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Abhinav Dahal', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC', 'stime': '12:30 PM', 'etime': '02:00 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'SR04- Tilicho'}, {'class': 'Year 1 BIC', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'SR02- Begnas'}, {'class': 'Year 1 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC', 'stime': '02:30 PM', 'etime': '04:00 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC', 'stime': '03:30 PM', 'etime': '05:00 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Midhir Rana', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'TR01- Bigben'}, {'class': 'Year 2 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Midhir Rana', 'room': 'LT02- Annapurna'}, {'class': 'Year 2 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'SR03- Rara'}, {'class': 'Year 2 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'Lab01- Gokyo'}, {'class': 'Year 2 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'TR01- Bigben'}, {'class': 'Year 2 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Midhir Rana', 'room': 'LT02- Annapurna'}, {'class': 'Year 2 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Sunil Thapa', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Prasant Adhikari', 'room': 'SR04- Tilicho'}, {'class': 'Year 2 BIC', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'Lab01- Gokyo'}, {'class': 'Year 2 BIC', 'stime': '12:30 PM', 'etime': '02:00 PM', 'teacher': 'Mr. Sunil Thapa', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 2 BIC', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'SR03- Rara'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'LT02- Annapurna'}], 'THU': [{'class': 'Year 1 BBA ( Spring)', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Kiran Kunwar', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BBA ( Spring)', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Ms. Sajena Dwa', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Ashish Subedi', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BBA', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Arjun Sapkota', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Sajena Dwa', 'room': 'SR01- Fewa'}, {'class': 'Year 2 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Arjun Sapkota', 'room': 'SR01- Fewa'}, {'class': 'Year 3 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Anil Rai', 'room': 'TR03- Thames'}, {'class': 'Year 3 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Jeevan Pahari', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC-Spring', 'stime': '07:30 AM', 'etime': '09:00 AM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'SR02- Begnas'}, {'class': 'Year 1 BIC-Spring', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC-Spring', 'stime': '03:30 PM', 'etime': '05:00 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'SR04- Tilicho'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'SR03- Rara'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Amar Khanal', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC', 'stime': '07:30 AM', 'etime': '09:00 AM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Amar Khanal', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'SR03- Rara'}, {'class': 'Year 1 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'SR02- Begnas'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'SR01- Fewa'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Krishna Wagle', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Amar Khanal', 'room': 'SR04- Tilicho'}, {'class': 'Year 1 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'SR04- Tilicho'}, {'class': 'Year 1 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Amar Khanal', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC', 'stime': '03:00 PM', 'etime': '04:30 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'Lab01- Gokyo'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Prasant Adhikari', 'room': 'LT02- Annapurna'}, {'class': 'Year 2 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 2 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'LT02- Annapurna'}, {'class': 'Year 2 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 2 BIC', 'stime': '01:00 PM', 'etime': '02:30 PM', 'teacher': 'Mr. Prasant Adhikari', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'SR04- Tilicho'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'Lab01- Gokyo'}, {'class': 'Year 3 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'SR04- Tilicho'}, {'class': 'Year 3 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'Lab01- Gokyo'}, {'class': 'Year 3 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'Lab01- Gokyo'}], 'FRI': [{'class': 'Year 1 BBA ( Spring)', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Ashish Subedi', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BBA ( Spring)', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Arjun Sapkota', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Sajena Dwa', 'room': 'SR02- Begnas'}, {'class': 'Year 1 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Kiran Kunwar', 'room': 'SR02- Begnas'}, {'class': 'Year 2 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Kiran Kunwar', 'room': 'SR03- Rara'}, {'class': 'Year 2 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Jeevan Pahari', 'room': 'SR03- Rara'}, {'class': 'Year 3 BBA', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Ashish Subedi', 'room': 'TR03- Thames'}, {'class': 'Year 3 BBA', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Vikram Rana', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC-Spring', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC-Spring', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'SR04- Tilicho'}, {'class': 'Year 1 BIC-Spring', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC-Spring', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC-Spring', 'stime': '12:30 PM', 'etime': '02:00 PM', 'teacher': 'Mr. Mission Babu Sapkota', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Achyut Parajuli', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC-Spring', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC-Spring', 'stime': '03:00 PM', 'etime': '04:30 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Amar Khanal', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC', 'stime': '07:30 AM', 'etime': '09:00 AM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'SR01- Fewa'}, {'class': 'Year 1 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Amar Khanal', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'SR01- Fewa'}, {'class': 'Year 1 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Idu Nepali', 'room': 'TR01- Bigben'}, {'class': 'Year 1 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Krishna Wagle', 'room': 'TR02- Stonehenge'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'SR03- Rara'}, {'class': 'Year 1 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'Lab02- Nilgiri'}, {'class': 'Year 1 BIC', 'stime': '10:30 AM', 'etime': '12:00 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'SR01- Fewa'}, {'class': 'Year 1 BIC', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Abhinav Dahal', 'room': 'SR02- Begnas'}, {'class': 'Year 1 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'SR03- Rara'}, {'class': 'Year 1 BIC', 'stime': '11:30 AM', 'etime': '01:00 PM', 'teacher': 'Mr. Idu Nepali', 'room': 'Lab03- Open Access Lab'}, {'class': 'Year 1 BIC', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Sandip Dhakal', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '12:30 PM', 'etime': '02:00 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'TR03- Thames'}, {'class': 'Year 1 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Ashish Lamichhane', 'room': 'SR03- Rara'}, {'class': 'Year 1 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Mr. Krishna Wagle', 'room': 'Lab01- Gokyo'}, {'class': 'Year 1 BIC', 'stime': '02:00 PM', 'etime': '03:30 PM', 'teacher': 'Mr. Subash Sapkota Hamal', 'room': 'TR03- Thames'}, {'class': 'Year 2 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'LT02- Annapurna'}, {'class': 'Year 2 BIC', 'stime': '09:00 AM', 'etime': '10:30 AM', 'teacher': 'Mr. Sandeep Gurung', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 2 BIC', 'stime': '09:30 AM', 'etime': '11:00 AM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'LT02- Annapurna'}, {'class': 'Year 2 BIC', 'stime': '11:00 AM', 'etime': '12:30 PM', 'teacher': 'Mr. Sandip Adhikari', 'room': 'LT01- Machhapuchhre'}, {'class': 'Year 2 BIC', 'stime': '12:00 PM', 'etime': '01:30 PM', 'teacher': 'Mr. Prasant Adhikari', 'room': 'LT02- Annapurna'}, {'class': 'Year 2 BIC', 'stime': '01:30 PM', 'etime': '03:00 PM', 'teacher': 'Ms. Pratibha Gurung', 'room': 'LT02- Annapurna'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'SR04- Tilicho'}, {'class': 'Year 3 BIC', 'stime': '07:00 AM', 'etime': '08:30 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'Lab01- Gokyo'}, {'class': 'Year 3 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Mahesh Dhungana ', 'room': 'SR04- Tilicho'}, {'class': 'Year 3 BIC', 'stime': '08:30 AM', 'etime': '10:00 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'Lab01- Gokyo'}, {'class': 'Year 3 BIC', 'stime': '10:00 AM', 'etime': '11:30 AM', 'teacher': 'Mr. Nabaraj Adhikari', 'room': 'Lab01- Gokyo'}]}
teachers=['Mr. Kiran Kunwar', 'Ms. Sajena Dwa', 'Mr. Ashish Subedi', 'Mr. Arjun Sapkota', 'Mr. Jeevan Pahari', 'Mr. Jeevan Pahari ', 'Mr. Anil Rai', 'Mr. Vikram Rana', 'Mr. Sushil Paudel', 'Mr. Mission Babu Sapkota', 'Mr. Amar Khanal', 'Mr. Sandip Dhakal', 'Mr. Krishna Wagle', 'Mr. Achyut Parajuli', 'Mr. Ashish Lamichhane', 'Mr. Idu Nepali', 'Mr. Subash Sapkota Hamal', 'Mr. Abhinav Dahal', 'Ms. Pratibha Gurung', 'Mr. Sandeep Gurung', 'Mr. Midhir Rana', 'Mr. Sandip Adhikari', 'Mr. Sunil Thapa', 'Mr. Prasant Adhikari', 'Mr. Mahesh Dhungana ', 'Mr. Nabaraj Adhikari']
rooms=['TR03- Thames', 'Lab03- Open Access Lab', 'SR01- Fewa', 'Lab01- Gokyo', 'Meeting Room', 'TR01- Bigben', 'TR02- Stonehenge', 'LT02- Annapurna', 'SR02- Begnas', 'SR03- Rara', 'LT01- Machhapuchhre', 'SR04- Tilicho', 'Lab02- Nilgiri']

def calculate_time_difference(reference_time, check_time):
  time_delta = timedelta(hours=abs(check_time.hour - reference_time.hour),
                         minutes=abs(check_time.minute - reference_time.minute),
                         seconds=abs(check_time.second - reference_time.second))

  return time_delta

weekdays=["SUN","MON","TUE","WED","THU","FRI","SAT"]
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
    for classe in classes[day]:
        if not classe["room"] in rooms: print(classe["room"])
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
            for classez in classes[day]:
                if classez["room"]==clase:
                    start_time = datetime.strptime(classez["stime"], "%I:%M %p").time()
                    if start_time==etime: etime=datetime.strptime(classez["etime"], "%I:%M %p").time()
            taken_rooms[clase]=int(calculate_time_difference(etime,check_time).total_seconds()/60)

    for clase in empty_rooms_list:
        # empty for x minutes, find the next start time closest (gt) to given time
        closest=None 
        for classez in classes[day]:
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

def encode_jwt(userid,email):
    encoded_data = jwt.encode(payload={"id": userid,"email":email},
                            key=jwt_secret,
                            algorithm="HS256")
    return encoded_data

def decode_jwt(token: str):
    try:
        decoded_data = jwt.decode(jwt=token,
                                key=jwt_secret,
                                algorithms=["HS256"])
    except: return False
    return decoded_data

# empty() # "SUN",datetime.strptime("08:01 AM", "%I:%M %p").time())# ,"Mr. Sushil Paudel")
class Redirect(SimpleHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()
        return
    
    def login_redir(self):
        self.send_response(302)
        self.send_header('Location', "/login")
        self.end_headers()
        return

    def cookie_check(self):
        cookies = self.parse_cookies(self.headers["Cookie"])
        if "sid" in cookies:
            self.user = decode_jwt(cookies["sid"])
            if not self.user: 
                if self.path!="/login": self.login_redir()
                return
        else:
            if self.path!="/login": self.login_redir()
            return
        if self.path=="/login":
            self.send_response(302)
            self.send_header('Location', "/")
            self.end_headers()
            return


    def read_file(self,file):
        with open(file, 'rb') as file:
            self.wfile.write(file.read())   
        

    def do_GET(self):

        if '/imgs/' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'image/'+self.path.split('.')[-1])
            self.end_headers()
            try:
                with open('imgs/'+self.path.split('/')[-1], 'rb') as file:
                    self.wfile.write(file.read())
            except: return
            return
        
        if self.path=="/logout":
            self.send_response(302)
            self.send_header('Set-Cookie', "sid=_")
            self.send_header('Location', "/login")
            self.end_headers()
            return
        
        if self.path=="/guest_login":
            self.cookie = "sid={}".format(encode_jwt(0,"Guest User"))
            self.send_response(302)
            self.send_header('Set-Cookie', self.cookie)
            self.send_header('Set-Cookie', "user={}".format("Guest User"))
            self.send_header('Location', "/")
            self.end_headers()
            return

        self.cookie_check()

        routes = {
            "/": self.home,
            "/login": self.login,
            "/icp_map":self.map,
            "/icp_cal":self.cal,
        }
        if not self.path in routes: 
            self.wfile.write(bytes('NA', 'UTF-8'))
            return
            
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        routes[self.path]()
        # self.wfile.write(bytes(content, "utf-8"))
        return
    def map(self):
        self.read_file('icp_map.html')
    def cal(self):
        self.read_file('icp_cal.html')
    def home(self):
        self.read_file('index.html')
        # return "Welcome User!" if self.user else "Welcome Stranger!"
    def login(self):
        self.read_file('login.html')

    def parse_cookies(self, cookie_list):
        try:
            return dict(((c.split("=")) for c in cookie_list.split(";"))) \
            if cookie_list else {}
        except: return {}

    def populate_db(self, auth):
        pass

    def do_POST(self):
        self.cookie_check()

        if self.path=="/login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_post_data = urllib.parse.parse_qs(post_data)
        
            try:
                username=parsed_post_data["username"][0].strip()
                if not username.endswith('@icp.edu.np'): 
                    self.login_redir()
                    return
                password=parsed_post_data["password"][0].strip()
            except: 
                self.login_redir()
                return
            r=requests.post("https://api.mysecondteacher.com.np/api/TokenAuth/Authenticate",json={"userNameOrEmailAddress":username,"password":password})
            if r.status_code!=200: 
                self.login_redir()
                return
            # self.populate_db(r.json()["result"]["accessToken"])
            self.cookie = "sid={}".format(encode_jwt(r.json()["result"]["userId"],username))
            self.send_response(302)
            self.send_header('Set-Cookie', self.cookie)
            self.send_header('Set-Cookie', "user={}".format(username))
            self.send_header('Location', "/")
            self.end_headers()
            return

        routes = {
            "/": self.map_post,
        }


        routes[self.path]()
    
    
    def map_post(self):
        if self.path=="/":

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
        
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_post_data = urllib.parse.parse_qs(post_data)
        
            day=time=teach=None
            if "day" in parsed_post_data:
                day=parsed_post_data["day"][0]
            if "time" in parsed_post_data:
                time=parsed_post_data["time"][0]
            if "teach" in parsed_post_data:
                teach=parsed_post_data["teach"][0]
            try:
              returned_data=empty(day,time,teach) 
            except:
                 self.wfile.write(bytes('NA', 'UTF-8'))
                 return
            if teach:
                todump={"room":returned_data[0][0],"time":returned_data[0][1],"schedule":returned_data[1]}
            else:
                todump={"empty_rooms":returned_data[0],"taken_rooms":returned_data[1]}
            self.wfile.write(json.dumps(todump).encode(encoding='utf_8'))
            return

port = int(os.environ.get("PORT", 5000))
HTTPServer(("0.0.0.0", port), Redirect).serve_forever()