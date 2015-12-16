# -*- coding:utf-8 -*-
__author__ = 'Neo'

import os
import datetime
import utilities as util
import unicodecsv

INIT_DATA_DIR = "init_data"
INER_DATA_DIR = "Intermediate"
TIME_POSITION_IN_CSV = 1
ROAD_TYPE_POSITION_IN_CSV = -2
MILEAGE_INFO = -5
TEST_FOLDER = 'speed/B50656'

RADIUS = 6371000

class Speed_Overload_Testing:
    __average_speeds = {}
    __speed_limit = {}

    def __init__(self):
        s_time = datetime.datetime.now()
        self.__speed_limit = util.read_json('speed_limit', INIT_DATA_DIR)
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "get_speed_limit cost %s\n" % str(cost_time)
        util.write_log('matching.log', log)

    def speed_test(self, folder_name):
        # 输入是文件夹名称
        # 文件夹内每个文件是剪好的一条轨迹
        # 循环打开每个文件,对每个文件做轨迹匹配
        # 匹配完在每个csv文件每行末尾增加字段:seg_id,dis
        for file in os.listdir(INER_DATA_DIR + "/" + folder_name + "/"):
            self.__speed_test_per_freight(file, folder_name)

    def __speed_test_per_freight(self, file_name, folder_name):
        rows_list = []
        with open(INER_DATA_DIR + "/" + folder_name + "/" + file_name) as input_csv:
            reader = unicodecsv.reader(input_csv)
            reader_iter = reader.__iter__()
            row_former = reader_iter.next()
            row_later = reader_iter.next()
            former_time = util.str_time_to_second(row_former[TIME_POSITION_IN_CSV])
            former_mileage = float(row_former[MILEAGE_INFO].split(":")[1].split("k")[0])
            former_type = row_former[ROAD_TYPE_POSITION_IN_CSV]
            later_time = util.str_time_to_second(row_later[TIME_POSITION_IN_CSV])
            later_mileage = float(row_later[MILEAGE_INFO].split(":")[1].split("k")[0])
            # print time_later
            # print later_minite, former_minite, later_second, former_second
            # 做两个循环外变量,否则捕捉异常时会出错
            distance_former = distance_later = later_mileage - former_mileage
            time_former = time_later = later_time - former_time
            v_former = 0
            if time_later != 0:
                v_former = distance_later * 1000 / time_later
            is_overspeed = v_former > self.__speed_limit[former_type]
            row_former.extend([v_former, is_overspeed])
            rows_list.append(row_former)
            try:
                while True:
                    row_former = row_later
                    former_time = later_time
                    former_mileage = later_mileage
                    former_type = row_former[ROAD_TYPE_POSITION_IN_CSV]
                    distance_former = distance_later
                    time_former = time_later
                    row_later = reader_iter.next()
                    later_time = util.str_time_to_second(row_later[TIME_POSITION_IN_CSV])
                    later_mileage = float(row_later[MILEAGE_INFO].split(":")[1].split("k")[0])
                    distance_later = later_mileage - former_mileage
                    time_later = later_time - former_time
                    v_former = 0
                    if time_later != 0:
                        v_former = (distance_former + distance_later) * 1000 / (time_former + time_later)
                    is_overspeed = v_former > self.__speed_limit[former_type]
                    row_former.extend([v_former, is_overspeed])
                    rows_list.append(row_former)
            except StopIteration:
                v_former = 0
                if time_former != 0:
                    v_former = distance_former * 1000 / time_former
                is_overspeed = v_former > self.__speed_limit[former_type]
                row_former.extend([v_former, is_overspeed])
                rows_list.append(row_former)
        with open(INER_DATA_DIR + "/" + folder_name + "_res/" + file_name, 'w') as output_csv:
            writer = unicodecsv.writer(output_csv)
            writer.writerows(rows_list)

if __name__ == "__main__":
    s_time = datetime.datetime.now()
    speed_test = Speed_Overload_Testing()
    speed_test.speed_test(TEST_FOLDER)
    e_time = datetime.datetime.now()
    cost_time = e_time - s_time
    log = "speed test cost %s\n" % str(cost_time)
    util.write_log('testing.log', log)
