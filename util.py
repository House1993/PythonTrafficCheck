__author__ = 'Fang'


import os
import json
import time


def read_json(file_name, dir_name):
    os.chdir(dir_name)
    with open(file_name) as inFile:
        data = json.load(inFile)
    os.chdir('..')
    return data


def write_json(file_name, dir_name, data):
    os.chdir(dir_name)
    with open(file_name, "wb") as outFile:
        json.dump(data, outFile)
    os.chdir('..')


def write_log(log_file_name, log_info):
    os.chdir("Logs")
    with open(log_file_name, 'a') as log:
        log.write(log_info)
    os.chdir('..')


def str_time_to_second(str_time):
    tup_time = time.strptime(str_time.split(".")[0], "%Y-%m-%d %H:%M:%S")
    seconds = time.mktime(tup_time)
    return seconds
