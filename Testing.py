# -*- coding:utf-8 -*-
__author__ = 'Neo'

import os
import math
import datetime
import utilities
import unicodecsv

INIT_DATA_DIR = "init_data"
INER_DATA_DIR = "Intermediate"
LONGITUDE_POSITION_IN_CSV = 2
LATITUDE_POSITION_IN_CSV = 3
TIME_POSITION_IN_CSV = 1
ROAD_TYPE_POSITION_IN_CSV = 10
TEST_FOLDER = 'speed'

RADIUS = 6371000

class Speed_Overload_Testing:
    __average_speeds = {}
    __speed_limit = {}

    def overload_test(self, folder):
        self.speed_test(folder)

    def __init__(self):
        s_time = datetime.datetime.now()
        self.__speed_limit = utilities.read_json('speed_limit', INIT_DATA_DIR)
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "get_speed_limit cost %s\n" % str(cost_time)
        utilities.write_log('matching.log', log)

    def __cal_probe_distance(self, s_lat, s_lon, e_lat, e_lon):
        s_lat = math.radians(s_lat)
        s_lon = math.radians(s_lon)
        e_lat = math.radians(e_lat)
        e_lon = math.radians(e_lon)
        theta_lat = s_lat - e_lat
        theta_long = s_lon - e_lon
        first = pow(math.sin(theta_lat / 2.0), 2)
        second = math.cos(s_lat) * math.cos(e_lat) * pow(math.sin(theta_long / 2.0), 2)
        angle = 2 * math.asin(math.sqrt(first + second))
        return math.floor(RADIUS * angle + 0.5)

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
            former_lon = float(row_former[LONGITUDE_POSITION_IN_CSV])
            former_lat = float(row_former[LATITUDE_POSITION_IN_CSV])
            former_minite = float(row_former[TIME_POSITION_IN_CSV].split(':')[1])
            former_second = float(row_former[TIME_POSITION_IN_CSV].split(':')[2])
            former_type = row_former[ROAD_TYPE_POSITION_IN_CSV]
            later_lon = float(row_later[LONGITUDE_POSITION_IN_CSV])
            later_lat = float(row_later[LATITUDE_POSITION_IN_CSV])
            later_minite = float(row_later[TIME_POSITION_IN_CSV].split(':')[1])
            later_second = float(row_later[TIME_POSITION_IN_CSV].split(':')[2])
            distance_later = self.__cal_probe_distance(former_lat, former_lon, later_lat, later_lon)
            time_later = (later_minite + 60.0 - former_minite) % 60.0 * 60.0 + later_second - former_second
            # print time_later
            # print later_minite, former_minite, later_second, former_second
            # 做两个循环外变量,否则捕捉异常时会出错
            distance_former = distance_later
            time_former = time_later
            v_former = distance_later / time_later
            is_overspeed = v_former > self.__speed_limit[former_type]
            row_former.extend([v_former, is_overspeed])
            rows_list.append(row_former)
            try:
                while True:
                    row_former = row_later
                    former_lon = later_lon
                    former_lat = later_lat
                    former_minite = later_minite
                    former_second = later_second
                    former_type = row_former[ROAD_TYPE_POSITION_IN_CSV]
                    distance_former = distance_later
                    time_former = time_later
                    row_later = reader_iter.next()
                    later_lon = float(row_later[LONGITUDE_POSITION_IN_CSV])
                    later_lat = float(row_later[LATITUDE_POSITION_IN_CSV])
                    later_minite = float(row_later[TIME_POSITION_IN_CSV].split(':')[1])
                    later_second = float(row_later[TIME_POSITION_IN_CSV].split(':')[2])
                    distance_later = self.__cal_probe_distance(former_lat, former_lon, later_lat, later_lon)
                    time_later = (later_minite + 60.0 - former_minite) % 60.0 * 60.0 + later_second - former_second
                    if time_later == 0:
                        v_former = 0
                    else:
                        v_former = (distance_former + distance_later) / (time_former + time_later)
                    is_overspeed = v_former > self.__speed_limit[former_type]
                    row_former.extend([v_former, is_overspeed])
                    rows_list.append(row_former)
            except StopIteration:
                v_former = distance_former / time_former
                is_overspeed = v_former > self.__speed_limit[former_type]
                row_former.extend([v_former, is_overspeed])
                rows_list.append(row_former)
        with open(INER_DATA_DIR + "/" + folder_name + "_res/" + file_name, 'w') as output_csv:
            writer = unicodecsv.writer(output_csv)
            writer.writerows(rows_list)

if __name__ == "__main__":
    speed_test = Speed_Overload_Testing()
    utilities.write_log('speed.log', '\n')
    s_time = datetime.datetime.now()
    speed_test.speed_test(TEST_FOLDER)
    e_time = datetime.datetime.now()
    cost_time = e_time - s_time
    log = "speed test cost %s\n" % str(cost_time)
    utilities.write_log('testing.log', log)
