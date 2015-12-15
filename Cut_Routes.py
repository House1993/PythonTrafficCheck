__author__ = 'Fang'

import unicodecsv
import os
import utilities as util

SPEED_FILE_ORI = "utfa.csv"
SPEED_DIR = "init_data/speed/"
MILEAGE_INFO = -1
TIME_POSITION_IN_CSV = 1
THIRTY_MINUTES = 1800

def Cut_Route(folder):
    ori_list = []
    with open(SPEED_FILE_ORI) as input_csv:
        reader = unicodecsv.reader(input_csv)
        for row in reader:
            ori_list.append(row)
    file_idx = 0
    length = len(ori_list)
    row_written = -1
    last_diff = 0
    last_time = int(1e20)
    i = 0
    time_i = util.str_time_to_second(ori_list[0][TIME_POSITION_IN_CSV])
    mileage_i = float(ori_list[0][MILEAGE_INFO].split(":")[1].split("k")[0])
    j = 1
    while j < length:
        mileage_j = float(ori_list[j][MILEAGE_INFO].split(":")[1].split("k")[0])
        time_j = util.str_time_to_second(ori_list[j][TIME_POSITION_IN_CSV])
        if mileage_i == mileage_j:
            if time_j - last_time >= THIRTY_MINUTES:
                if row_written != last_diff:
                    k = row_written
                    while k <= last_diff:
                        with open(folder + str(file_idx) + ".csv", "a") as output_csv:
                            writer = unicodecsv.writer(output_csv)
                            writer.writerows(ori_list[k])
                        k += 1
                    row_written = -1
                    file_idx += 1
        else:
            last_diff = i
            last_time = time_i
            if row_written == -1:
                row_written = last_diff
        i += 1
        time_i = time_j
        mileage_i = mileage_j
        j += 1
    if row_written != -1:
        k = row_written
        while k < length:
            with open(folder + str(file_idx) + ".csv", "a") as output_csv:
                writer = unicodecsv.writer(output_csv)
                writer.writerows(ori_list[k])
            k += 1

if __name__ == "__main__":
    folder = SPEED_DIR + SPEED_FILE_ORI.split(".")[0] + "/"
    os.mkdir(folder)
    Cut_Route(folder)
