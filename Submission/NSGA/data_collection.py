#%%
from tqdm import tqdm
import requests as rq
import numpy as np
import json
import sys
import time
import matplotlib.pyplot as plt
from speccy_collection import *
import pandas as pd
import h5py

def start_data_collection():
    # control input range (Adjust here only, rest is automated)
    # recommend you to change the step: using 1 step for each input will need 122 hours
    # should also adjust the starting point
    cct_step = 250
    cct_range = list(range(2000,6500,cct_step))
    bri_step = 50
    bri_range = list(range(0,254,bri_step))
    data_collection_num = 2
    number_of_data_points = len(bri_range)*len(cct_range)

    ## Start Calibration and Data Collection Phase
    for state in tqdm(range(data_collection_num)):
        print(f"Start Collection No.{state} - Expected Number of Data Points:{number_of_data_points}")
        for i,bri in enumerate(bri_range):
            for j,cct in enumerate(cct_range):
                ct = 1000000.0/cct
                # setup current control input combination
                main(bri, cct, 5, 20)

    # Load CSV file into a pandas DataFrame
    df = pd.read_csv('lighting_data.csv')
    dataset = df.to_numpy()
    # Specify the file path for the HDF5 file
    hdf5_file_path = 'data.h5'

    # Extract individual columns for clarity
    bri = dataset[:, 0].astype(np.float64)
    cct = dataset[:, 1].astype(np.float64)
    ct = dataset[:, 2].astype(np.float64)
    photopic_lux = dataset[:, 4].astype(np.float64)
    melanopic_lux = dataset[:, 5].astype(np.float64)
    cct = dataset[:, 6].astype(np.float64)
    mdr = dataset[:, 7].astype(np.float64)
    cri = dataset[:, 8].astype(np.float64)

    # Create an HDF5 file
    with h5py.File(hdf5_file_path, 'w') as hf:
        hf.create_dataset('bri', data=bri)
        hf.create_dataset('ct', data=ct)
        hf.create_dataset('photopic_lux', data=photopic_lux)
        hf.create_dataset('melanopic_lux', data=melanopic_lux)
        hf.create_dataset('cct', data=cct)
        hf.create_dataset('mdr', data=mdr)
        hf.create_dataset('cri', data=cri)