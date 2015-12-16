__author__ = 'Tissue'

import os
import json
import pickle
import time
import glob

INER_DATA_DIR = "Intermediate"
LOG_DIR = "Logs"

def read_json(file_name, dir_name):
    os.chdir(dir_name)
    with open(file_name) as inFile:
        ret_dict = json.load(inFile)
    os.chdir('..')
    return ret_dict

def write_json(file_name, dir_name, data_dict):
    os.chdir(dir_name)
    with open(file_name, "wb") as outFile:
        json.dump(data_dict, outFile)
    os.chdir('..')

def read_pickle(file_name):
    os.chdir(INER_DATA_DIR)
    with open(file_name) as inFile:
        ret_pick = pickle.load(inFile)
    os.chdir('..')
    return ret_pick

def write_pickle(file_name, data):
    os.chdir(INER_DATA_DIR)
    with open(file_name, "wb") as outFile:
        pickle.dump(data, outFile)
    os.chdir('..')

def write_log(log_file_name, log_info):
    os.chdir(LOG_DIR)
    with open(log_file_name, 'a') as log:
        log.write(log_info)
    os.chdir('..')

def str_time_to_second(str_time):
    tup_time = time.strptime(str_time.split(".")[0], "%Y-%m-%d %H:%M:%S")
    seconds = time.mktime(tup_time)
    return seconds
