from RPA.HTTP import HTTP
from RPA.JSON import JSON
from RPA.Tables import Tables
from RPA.Robocorp.WorkItems import WorkItems
import os
import requests
import pandas as pd
http = HTTP()
json = JSON()
tables = Tables()
queue = WorkItems()

os.chdir("output")
r = requests.get("https://github.com/robocorp/inhuman-insurance-inc/raw/main/RS_198.json")
data_json = r.json()
table = pd.DataFrame(data_json["value"])

sorted_table = table.loc[(table['NumericValue'] < 5.0) & (table['Dim1'] == "BTSX")].sort_values("TimeDim", ascending=False)
sorted_table.to_excel(f"{os.getcwd()}/trafic.xlsx", index = False)
queue.get_input_work_item()

for row in sorted_table.index:
    queue.create_output_work_item()
    queue.set_work_item_variable("country",sorted_table.loc[row,'SpatialDim'])
    queue.set_work_item_variable("year", str(sorted_table.loc[row,'TimeDim']))
    queue.set_work_item_variable("rate",str(sorted_table.loc[row,'NumericValue']))
    queue.save_work_item()

# http.download("https://github.com/robocorp/inhuman-insurance-inc/raw/main/RS_198.json", f"{os.getcwd()}/trafic.json", overwrite=True)
# data_json = json.load_json_from_file(f"{os.getcwd()}/trafic.json")
# tabl = tables.create_table(data_json)

# print(tabl)

