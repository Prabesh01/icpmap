import pandas as pd
import json
from config import get_basedir

BASE_DIR=get_basedir()

file_path = BASE_DIR / "data-sources/current/Seat Plan.xlsx"
out_path = BASE_DIR / "data/seat_plan.json"

excel_data = pd.ExcelFile(file_path)
seat_data = {}

for sheet_name in excel_data.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    sheet_name = sheet_name.strip()
    print(f"\n\n################\nProcessing sheet: {sheet_name}\n################")
    seat_data[sheet_name] = {"entrance":[],"max_row": 0, "max_col": 0, "seats": {}}
    seat = seat_data[sheet_name]["seats"]
    x_val = 0
    students = []
    end = False
    for _, row in df.iterrows():
        new_row_start = False
        y_val = e_val = 0
        for col in df.columns:
            e_val += 1
            cell_value = str(row[col])
            # print(cell_value, end="\t")
            if cell_value:
                cell_value = cell_value.strip()
                if cell_value=="nan": continue
                if cell_value.lower() == "entrance":
                    seat_data[sheet_name]["entrance"] = [x_val, e_val]
                    end = True
                    break
                if y_val==0: print()
                print(cell_value, end=" -- ")
                if not '-' in cell_value:
                    students.append(cell_value)
                else:
                    new_row_start = True
                    if not students: student=""
                    else: student=students[0]
                    seat[cell_value] = {"x": x_val, "y": y_val,"student": student}
                    students = students[1:]
            if end: break
            y_val += 1
        if end: break
        if new_row_start:
            x_val += 1
            print(f'\n-------------------------{x_val}-----------------------------', end="")

# get max row and column for each sheet
for sheet_name in seat_data:
    for key in seat_data[sheet_name]["seats"]:
        max_row = seat_data[sheet_name]["max_row"]
        max_col = seat_data[sheet_name]["max_col"]
        x = seat_data[sheet_name]["seats"][key]["x"]+1
        y = seat_data[sheet_name]["seats"][key]["y"]+1
        if x > max_row: seat_data[sheet_name]["max_row"] = x
        if y > max_col: seat_data[sheet_name]["max_col"] = y

    y = seat_data[sheet_name]["entrance"][1]
    if y > max_col: seat_data[sheet_name]["entrance"][1] = max_col
    else: seat_data[sheet_name]["entrance"][1] = 0

# Save to JSON
with open(out_path, "w") as json_file:
    json.dump(seat_data, json_file, indent=4)

print("\nSeat plan saved as seat_plan.json")

# import openpyxl
# import json

# file_path = "Seat Plan.xlsx"

# dataframe = openpyxl.load_workbook(file_path)
# seat_data = {}

# for sheet_name in dataframe.sheetnames:
#     df = dataframe[sheet_name]
#     sheet_name = sheet_name.strip()
#     print(f"\n\n################\nProcessing sheet: {sheet_name}\n################")
#     seat_data[sheet_name] = {"entrance":[],"max_row": 0, "max_col": 0, "seats": {}}
#     seat = seat_data[sheet_name]["seats"]
#     x_val = 0
#     students = []
#     end = False
#     for row in range(0, df.max_row):
#     # for _, row in df.iter_rows():
#         new_row_start = False
#         y_val = e_val = 0
#         for col in df.iter_cols(1, df.max_column):
#         # for col in df.columns:
#             cell_value = col[row].value
#             e_val+= 1
#             if cell_value:
#                 cell_value = cell_value.strip()
#                 if cell_value.lower() == "entrance":
#                     seat_data[sheet_name]["entrance"] = [x_val, e_val]
#                     end = True
#                     break
#                 if y_val==0: print()
#                 print(cell_value, end=" -- ")
#                 if not '-' in cell_value:
#                     students.append(cell_value)
#                 else:
#                     new_row_start = True
#                     if not students: student=""
#                     else: student=students[0]
#                     seat[cell_value] = {"x": x_val, "y": y_val,"student": student}
#                     students = students[1:]
#                 y_val += 1
#         if end: break
#         if new_row_start:
#             x_val += 1
#             print(f'\n-------------------------{x_val}-----------------------------')

# # get max row and column for each sheet
# for sheet_name in seat_data:
#     for key in seat_data[sheet_name]["seats"]:
#         max_row = seat_data[sheet_name]["max_row"]
#         max_col = seat_data[sheet_name]["max_col"]
#         x = seat_data[sheet_name]["seats"][key]["x"]+1
#         y = seat_data[sheet_name]["seats"][key]["y"]+1
#         if x > max_row: seat_data[sheet_name]["max_row"] = x
#         if y > max_col: seat_data[sheet_name]["max_col"] = y

#     y = seat_data[sheet_name]["entrance"][1]
#     if y > max_col: seat_data[sheet_name]["entrance"][1] = max_col
#     else: seat_data[sheet_name]["entrance"][1] = 0

# # Save to JSON
# with open("seat_plan2.json", "w") as json_file:
#     json.dump(seat_data, json_file, indent=4)

# print("\nSeat plan saved as seat_plan2.json")

