from datetime import datetime
import json

import openpyxl

from config import get_basedir

BASE_DIR=get_basedir()
assestment_file = BASE_DIR / "data-sources/23-24/Assessment_Schedule.xlsx"
exam_file = BASE_DIR / "data-sources/23-24/Exam_Schedule.xlsx"
exam_data_file = BASE_DIR / "data/exam.json"

exam_data = {}


def parse_assestment_file(source):
    dataframe = openpyxl.load_workbook(source)
    for sheet in dataframe.sheetnames:
        exam_data[sheet] = []
        dataframe1=dataframe[sheet]
        module=None
        for row in range(4, dataframe1.max_row):
            row_1=dataframe1[row][1].value
            if row_1: module = row_1.strip()
            if module and not any(x['module']==module for x in exam_data[sheet]):
                code=dataframe1[row][2].value.strip()
                credit=str(dataframe1[row][5].value).strip()
                exam_data[sheet].append({"module": module, "code": code, "credits": credit, "exams": []})
            exams_index = next((i for i, x in enumerate(exam_data[sheet]) if x['module'] == module), None)
            
            _, exam_date=dataframe1[row][-1].value.strip().split(',')
            date_split = exam_date.split()
            exam_year=date_split[-1].strip()
            exam_date=" ".join(date_split[:-1]).strip()
            date_split=exam_date.split('-')
            if '-' in exam_date:
                start_date, end_date=date_split[0].strip(), date_split[1].strip()
            else: end_date=start_date=date_split[0]
            start_date=datetime.strptime(f"{start_date} {exam_year}", "%d %B %Y").strftime("%Y-%m-%d")
            end_date=datetime.strptime(f"{end_date} {exam_year}", "%d %B %Y").strftime("%Y-%m-%d")
            
            exam_data[sheet][exams_index]['exams'].append({
                'title':dataframe1[row][7].value.strip(),
                'percentage': int(dataframe1[row][8].value*100),
                'start_date': start_date,
                'end_date': end_date
                })
    with open(exam_data_file, 'w') as f:
        json.dump(exam_data, f, indent=4)

parse_assestment_file(assestment_file)
