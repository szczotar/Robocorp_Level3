from RPA.HTTP import HTTP
from RPA.JSON import JSON
from RPA.Tables import Tables
from RPA.Robocorp.WorkItems import WorkItems, State
import os

import requests
import pandas as pd
import json
import logging
import datetime

http = HTTP()
# json = JSON()
tables = Tables()
queue = WorkItems()
os.chdir("output")
#logging patternP
logging.basicConfig(filename=f"{os.getcwd()}/logs.log",format='%(asctime)s %(message)s', datefmt ="%d-%m-%Y %H:%M:%S", 
                    level=logging.INFO)

class CoutryCodeError(Exception):
    def __init__(self, message = None, errors = None):
        super().__init__(message)
        self.errors = errors
  
class APIResposneError(Exception):
    def __init__(self, message = None, errors = None):
        super().__init__(message)
        self.errors = errors

def validate(payload):
    valid = len(payload["country"]) == 3 
    return valid

def Post_data(payload):
    r = requests.post("https://robocorp.com/inhuman-insurance-inc/sales-system-api",json=json.dumps(payload))
    valid = r.status_code == 200
    return valid

def Handle_businessException(err):
    # logging.error(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + err.message())
    queue.release_input_work_item(state= State.FAILED, exception_type="BUSINESS", message= "Country code is wrong")

def Handle_APIException(err):
    # logging.error(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + err.message())
    queue.release_input_work_item(state= State.FAILED, exception_type="APPLICATION", message= "API internal serve error")

def Release_WorkItem():
    # logging.info(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " item done")
    queue.release_input_work_item(state= State.DONE, exception_type="APPLICATION", message= "item done")

def Process_data():
    try:
        payload = queue.get_work_item_payload()
        if not validate(payload): raise CoutryCodeError("Country code is wrong")
        if not Post_data(payload): raise APIResposneError("API internal serve error")
        Release_WorkItem()
   
    except CoutryCodeError as err:
        Handle_businessException(err)

    except APIResposneError as err:
        Handle_APIException(err)

def Main():
    queue.get_input_work_item()
    queue.for_each_input_work_item(Process_data)

if __name__ == "__main__":
    Main()