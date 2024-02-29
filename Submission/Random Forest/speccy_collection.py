import argparse
import logging
import math
import requests as rq
import numpy as np
import json
import sys
import os
import time
import csv
import matplotlib.pyplot as plt
from metrics import *

URL_GET = 'https://ece4809api.intlightlab.com/get-spectrum-room'
URL_POST = 'https://ece4809api.intlightlab.com/set-lights' 
HEADERS = {'Authorization': 'Bearer 94623b78-4f2c-4412-b646-4c3364cec730'}


def tune_lights(bri, cct, max_retries, wait_time):
    ct = 1000000.0 / cct
    control_input = {"bri": bri, "ct": ct}
    
    for _ in range(max_retries):
        try:
            response = rq.post(URL_POST, headers=HEADERS, json=control_input)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print(f"Posting Request - Current Control Input - BRI:{bri}, CCT:{cct}, CT:{ct}")
            return {
                "bri": bri,
                "cct": cct,
                "ct": ct
            }
        except rq.exceptions.RequestException as e:
            print(f"Error in posting data to server: {e}")
            time.sleep(wait_time)

    # Handle the case when all retries fail
    print("Failed to post data to server after maximum retries.")
    return None

def collect_lights(max_retries, wait_time):
    specky_data = None
    
    for _ in range(max_retries):
        try:
            specky_data = rq.get(URL_GET, headers=HEADERS)
            specky_data.raise_for_status()  # Raise an exception for HTTP errors
            specky_data = json.loads(specky_data.text)
            print("Getting Request")
            return specky_data
        except rq.exceptions.RequestException as e:
            print(f"Error in getting data from server: {e}")
            time.sleep(wait_time)

    # Handle the case when all retries fail
    print("Failed to get data from the server after maximum retries.")
    return None


def processSPD(specky_data):

    spd = specky_data['SPM']
    spd_interp = spd[::5]

    all_lux= alpha_opic_cal(spd_interp) 
    Photopic_lux = specky_data['plux']
    Melanopic_lux = specky_data['mlux']
    CCT = get_CCT(spd_interp)
    CRI,R9 = get_CRI(spd_interp,ref=reflight(CCT))
    MDER = Melanopic_lux/Photopic_lux

    print(f"Finished Request - Plux:{Photopic_lux:.4f},Mlux:{Melanopic_lux:.4f},CCT:{CCT:.4f},MDER:{MDER:.4f},CRI:{CRI:.4f}")

    return {
        "all_lux": all_lux,
        "Photopic_lux": Photopic_lux,
        "Melanopic_lux":Melanopic_lux,
        "CCT": CCT,
        "MDER": MDER,
        "CRI": CRI,
        "R9": R9
    }

def processMetrics(specky_data,user_input):

    spd = specky_data['SPM']
    spd_interp = spd[::5]

    all_lux= alpha_opic_cal(spd_interp) 
    Photopic_lux = specky_data['plux']
    Melanopic_lux = specky_data['mlux']
    CCT = get_CCT(spd_interp)
    CRI,R9 = get_CRI(spd_interp,ref=reflight(CCT))
    MDER = Melanopic_lux/Photopic_lux

    match user_input:
        case 0:
            return Photopic_lux,Melanopic_lux,CRI
        case 1:
            return Photopic_lux,CCT,CRI
        case 2:
            return Photopic_lux,MDER,CRI
        case 3:
            return Melanopic_lux,CCT,CRI
        case 4:
            return Melanopic_lux,MDER,CRI
        case 5:
            return CCT,MDER,CRI

def save(bri, cct, ct, all_lux, Photopic_lux, Melanopic_lux, CCT, MDER, CRI, R9):
    # Define the file path for the CSV file
    file_path = "lighting_data.csv"

    # Check if the file exists, and create it if it doesn't
    file_exists = os.path.exists(file_path)
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "bri", "cct", "ct",
            "all_lux", "Photopic_lux", "Melanopic_lux",
            "CCT", "MDER", "CRI", "R9"
        ])
        
        # If the file is newly created, write the header row
        if not file_exists:
            writer.writeheader()

        # Write the data as a new row
        writer.writerow({
            "bri": bri,
            "cct": cct,
            "ct": ct,
            "all_lux": all_lux,
            "Photopic_lux": Photopic_lux,
            "Melanopic_lux": Melanopic_lux,
            "CCT": CCT,
            "MDER": MDER,
            "CRI": CRI,
            "R9": R9
        })

def main(brightness, corrColorTemp, maxRetries=5, waitTime=20):
    ctrl_input = tune_lights(bri=brightness, cct=corrColorTemp, max_retries=maxRetries, wait_time=waitTime)

    if (ctrl_input is None):
        return
    
    time.sleep(5)

    speccy_data = collect_lights(maxRetries, waitTime)

    if speccy_data is None:
        return

    ctrl_output = processSPD(speccy_data)

    save(ctrl_input['bri'], ctrl_input['cct'], ctrl_input['ct'],
         ctrl_output['all_lux'], ctrl_output['Photopic_lux'], ctrl_output['Melanopic_lux'], 
         ctrl_output['CCT'], ctrl_output['MDER'], ctrl_output['CRI'], ctrl_output['R9'])




# if __name__ == '__main__':
    
#     parser = argparse.ArgumentParser(description="Task with parameters")
#     parser.add_argument("--bri", type=int, required=True, help="Brightness value")
#     parser.add_argument("--cct", type=int, required=True, help="CCT value")
#     parser.add_argument("--max_retries", type=int, default=5, help="Maximum number of retries for server requests")
#     parser.add_argument("--wait_time", type=int, default=20, help="Time to wait between retries")
#     args = parser.parse_args()

#      # Access the variables from args and pass them to the task function
#     bri = args.bri
#     cct = args.cct
#     max_retries = args.max_retries
#     wait_time = args.wait_time

#     # Now you can use these variables as needed
#     print(f"Brightness: {bri}")
#     print(f"CCT: {cct}")
#     print(f"Max Retries: {max_retries}")
#     print(f"Wait Time: {wait_time}")

#     # Call the task function with the parsed variables
#     main(bri, cct, max_retries, wait_time)
