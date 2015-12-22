# -*- coding:utf-8 -*-
__author__ = 'Neo & Fang'

import os
import math
import datetime
import utilities as util
import unicodecsv

INIT_DATA_DIR = "init_data"
INER_DATA_DIR = "Intermediate"
GRIDE_FILE = 'grids_dict'
WAY_ID2NAME_FILE = 'ways_id2name'
LONGITUDE_POSITION_IN_CSV = 2
LATITUDE_POSITION_IN_CSV = 3

RADIUS = 6371000
MAXDIST = 1e20
STEP = 0.01

# Map_Match 只有一个match方法,输入为切割好的轨迹所在文件夹的名称
class Map_Match:
    __min_lat = 0
    __max_lat = 0
    __min_lon = 0
    __max_lon = 0
    __num_lat = 0
    __num_lon = 0
    __num_grids = 0
    __grids = {}
    __ways = {}
    __row_for_log = 0

    # 输入是文件夹名称
    # 文件夹内每个文件是剪好的一条轨迹
    # 循环打开每个文件,对每个文件做轨迹匹配
    # 匹配完在每个csv文件每行末尾增加字段:路段名称,道路类型,匹配距离
    # 路段名称的格式是 分块id_道路id_分块内部序号,其中道路id与osm提供的id是一致的.
    def match(self, folder_name):
        os.mkdir(INER_DATA_DIR + "/" + folder_name)
        for file in os.listdir(INIT_DATA_DIR + "/" + folder_name + "/"):
            self.__row_for_log = 0
            util.write_log('matching.log', "%s start:\n" % file)
            self.__match_per_freight(file, folder_name)

    def __init__(self):

        s_time = datetime.datetime.now()
        self.__min_lat, self.__max_lat, self.__min_lon, self.__max_lon, self.__num_lat, \
        self.__num_lon, self.__num_grids = util.read_json('map_info', INER_DATA_DIR)
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "get_range_of_map cost %s\n" % str(cost_time)
        util.write_log('matching.log', log)

        s_time = datetime.datetime.now()
        self.__grids = util.read_json(GRIDE_FILE, INER_DATA_DIR)
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "get_grids cost %s\n" % str(cost_time)
        util.write_log('matching.log', log)

        s_time = datetime.datetime.now()
        self.__ways = util.read_json(WAY_ID2NAME_FILE, INER_DATA_DIR)
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "get_way_id_to_name cost %s\n" % str(cost_time)
        util.write_log('matching.log', log)

    def __match_per_freight(self, file_name, folder_name):
        rows_list = []
        with open(INIT_DATA_DIR + "/" + folder_name + "/" + file_name) as input_csv:
            reader = unicodecsv.reader(input_csv)
            for row in reader:
                self.__row_for_log += 1
                try:
                    matched_segment, segment_type, distance = \
                    self.__match_point_naive(float(row[LATITUDE_POSITION_IN_CSV]), float(row[LONGITUDE_POSITION_IN_CSV]))
                except Exception:
                    util.write_log('matching.log', "position show ( %s , %s )\n" % (row[LATITUDE_POSITION_IN_CSV], row[LONGITUDE_POSITION_IN_CSV]))
                    matched_segment, segment_type, distance = '', 'unclassified', MAXDIST
                try:
                    matched_way_name = self.__ways[matched_segment.split("_")[1]]
                except Exception:
                    util.write_log('matching.log', "row %d position ( %s , %s ) match segment %s\n" % (self.__row_for_log, row[LATITUDE_POSITION_IN_CSV], row[LONGITUDE_POSITION_IN_CSV], matched_segment))
                    matched_way_name = ""
                row.extend([matched_way_name, matched_segment, segment_type, distance])
                rows_list.append(row)
        with open(INER_DATA_DIR + "/" + folder_name + "/" + file_name, 'w') as output_csv:
            writer = unicodecsv.writer(output_csv)
            writer.writerows(rows_list)

    def __match_point_naive(self, lat, lon):
        neighbor_grid = self.__find_neighbor(lat, lon)
        min_dist = MAXDIST
        min_route = ''
        min_type = 'unclassified'
        for grid_id in neighbor_grid:
            try:
                routes = self.__grids[str(grid_id)]
            except Exception:
                loc_x, loc_y = self.__find_grid(lat, lon)
                loc_id = loc_x * self.__num_lon + loc_y
                util.write_log('matching.log', "( %f , %f ) loc is ( %d , %d ) in grid %s found grid %s\n" % (lat, lon, loc_x, loc_y, str(loc_id), str(grid_id)))
                continue
            for route in routes:
                dist = self.__cal_point_route(lat, lon, route)
                if dist < min_dist:
                    min_route = route.keys()[0]
                    min_type = route.values()[0]['highway']
                    min_dist = dist
        return min_route, min_type, min_dist

    def __find_grid(self, x, y):
        loc_x = int((x - self.__min_lat) / STEP)
        if loc_x == self.__num_lat:
            loc_x -= 1
        loc_y = int((y - self.__min_lon) / STEP)
        if loc_y == self.__num_lon:
            loc_y -= 1
        return loc_x, loc_y

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

    def __find_neighbor(self, lat, lon):
        loc_x, loc_y = self.__find_grid(lat, lon)
        loc_id = loc_x * self.__num_lon + loc_y
        coner_x = self.__min_lat + STEP * loc_x
        coner_y = self.__min_lon + STEP * loc_y
        tmp_x = lat - coner_x
        tmp_y = lon - coner_y
        ret = [loc_id]
        # self
        up = loc_id - self.__num_lon
        down = loc_id + self.__num_lon
        left = loc_id - 1
        right = loc_id + 1
        upleft = up - 1
        upright = up + 1
        downleft = down - 1
        downright = down + 1
        if tmp_x < STEP / 2:
            # up
            if loc_x != 0:
                ret.append(up)
            if tmp_y < STEP / 2:
                # left up
                if loc_y != 0:
                    ret.append(left)
                    if loc_x != 0:
                        ret.append(upleft)
            else:
                # right up
                if loc_y != self.__num_lon - 1:
                    ret.append(right)
                    if loc_x != 0:
                        ret.append(upright)
        else:
            # down
            if loc_x != self.__num_lat - 1:
                ret.append(down)
            if tmp_y < STEP / 2:
                # left down
                if loc_y != 0:
                    ret.append(left)
                    if loc_x != self.__num_lat - 1:
                        ret.append(downleft)
            else:
                # right down
                if loc_y != self.__num_lon - 1:
                    ret.append(right)
                    if loc_x != self.__num_lat - 1:
                        ret.append(downright)
        return ret

    def __cal_point_route(self, lat, lon, segment):
        s_x = float(segment.values()[0]["snode"][0])
        s_y = float(segment.values()[0]["snode"][1])
        e_x = float(segment.values()[0]["enode"][0])
        e_y = float(segment.values()[0]["enode"][1])
        p_x, p_y = self.__get_project_point(lat, lon, s_x, s_y, e_x, e_y)
        if (p_x - s_x) * (p_x - e_x) < 1e-8 and (p_y - s_y) * (p_y - e_y) < 1e-8:
            return self.__cal_probe_distance(lat, lon, p_x, p_y)
        else:
            return min(self.__cal_probe_distance(lat, lon, s_x, s_y),
                       self.__cal_probe_distance(lat, lon, e_x, e_y))

    def __get_project_point(self, x0, y0, x1, y1, x2, y2):
        fenzi = (x1-x0) * (x1-x2) + (y1-y0) * (y1-y2)
        fenmu = math.pow(x1-x2, 2) + math.pow(y1-y2, 2)
        if fenmu == 0.0:
            return x1, y1
        temp = fenzi / fenmu
        ret_x = x1 + temp * (x2-x1)
        ret_y = y1 + temp * (y2-y1)
        return ret_x, ret_y

if __name__ == "__main__":
    s_time = datetime.datetime.now()
    map_matching = Map_Match()
    map_matching.match("speed/B50656")
    e_time = datetime.datetime.now()
    cost_time = e_time - s_time
    log = "Total cost %s\n" % str(cost_time)
    util.write_log('matching.log', log)
