__author__ = 'Fang'


import util
import math
import datetime


INIT_DATA_DIR = "init_data"
NODE_DATA = "3p.json"
WAY_DATA = "3w.json"
INTER_DATA_DIR = "Intermediate"
WAY_ID2NAME = "ways_id2name"
MAX_NUM = 1e20
MAP_INFO = "map_info"
STEP = 0.01
GRIDS_DICT = "grids_dict"
LOGS = "pre.log"


def get_nodes():
    nodes_data = util.read_json(NODE_DATA, INIT_DATA_DIR)
    nodes_list = nodes_data[u"elements"]
    nodes_dict = dict()
    for item in nodes_list:
        if item[u"type"] == u"node":
            tmp_id = item[u"id"]
            tmp_lat = item[u"lat"]
            tmp_lon = item[u"lon"]
            nodes_dict[tmp_id] = {u"lat": tmp_lat, u"lon": tmp_lon}
    return nodes_dict


def get_ways_save_id2name():
    ways_data = util.read_json(WAY_DATA, INIT_DATA_DIR)
    ways_list = ways_data[u"elements"]
    ways_dict = dict()
    ways_id2name = dict()
    for item in ways_list:
        if (item[u"type"] == u"way") and (u"tags" in item) and (u"highway" in item[u"tags"]):
            tmp_id = item[u"id"]
            nodes_list = list()
            for node_id in item[u"nodes"]:
                if Nodes_dict.has_key(node_id):
                    tmp_node = Nodes_dict[node_id]
                    tmp_lat = tmp_node[u"lat"]
                    tmp_lon = tmp_node[u"lon"]
                    nodes_list.append({u"lat": tmp_lat, u"lon": tmp_lon})
            if len(nodes_list) > 1:
                ways_dict[tmp_id] = {u"highway": item[u"tags"][u"highway"], u"nodes": nodes_list}
                tmp_name = u""
                if u"name" in item[u"tags"]:
                    tmp_name = item[u"tags"][u"name"]
                ways_id2name[tmp_id] = tmp_name
    util.write_json(WAY_ID2NAME, INTER_DATA_DIR, ways_id2name)
    return ways_dict


def get_save_map_info():
    min_lat = min_lon = MAX_NUM
    max_lat = max_lon = -MAX_NUM
    for item in Ways_dict.values():
        for node in item[u"nodes"]:
            tmp_lat = float(node[u"lat"])
            tmp_lon = float(node[u"lon"])
            min_lat = min(min_lat, tmp_lat)
            min_lon = min(min_lon, tmp_lon)
            max_lat = max(max_lat, tmp_lat)
            max_lon = max(max_lon, tmp_lon)
    num_lat = int(math.ceil((max_lat - min_lat) / STEP) + 0.1)
    num_lon = int(math.ceil((max_lon - min_lon) / STEP) + 0.1)
    num_grids = num_lat * num_lon
    map_info = min_lat, max_lat, min_lon, max_lon, num_lat, num_lon, num_grids
    util.write_json(MAP_INFO, INTER_DATA_DIR, map_info)
    return min_lat, max_lat, min_lon, max_lon, num_lat, num_lon, num_grids


def find_grid_id(x, y):
    loc_x = int((x - Min_lat) / STEP)
    if loc_x == Num_lat:
        loc_x -= 1
    loc_y = int((y - Min_lon) / STEP)
    if loc_y == Num_lon:
        loc_y -= 1
    loc = loc_x * Num_lon + loc_y
    return loc


def gen_segment(seg_id, sx, sy, ex, ey, highway):
    return {seg_id: {u"highway": highway, u"snode": (sx, sy), u"enode": (ex, ey)}}


def save_grids():
    grids_dict = dict()
    for i in range(Num_grids):
        grids_dict[i] = list()
    for (way_id, item) in Ways_dict.items():
        nodes = item[u"nodes"]
        length = len(nodes)
        highway = item[u"highway"]
        last_lat = float(nodes[0][u"lat"])
        last_lon = float(nodes[0][u"lon"])
        last_loc = find_grid_id(last_lat, last_lon)
        for i in range(1, length):
            tmp_lat = float(nodes[i][u"lat"])
            tmp_lon = float(nodes[i][u"lon"])
            tmp_loc = find_grid_id(tmp_lat, tmp_lon)
            seg = gen_segment(unicode(last_loc) + u"_" + unicode(way_id) + u"_" + unicode(i - 1), last_lat, last_lon,
                              tmp_lat, tmp_lon, highway)
            grids_dict[last_loc].append(seg)
            if tmp_loc != last_loc:
                grids_dict[tmp_loc].append(seg)
            last_lat = tmp_lat
            last_lon = tmp_lon
            last_loc = tmp_loc
    util.write_json(GRIDS_DICT, INTER_DATA_DIR, grids_dict)


if __name__ == "__main__":
    start = datetime.datetime.now()
    Nodes_dict = get_nodes()
    Ways_dict = get_ways_save_id2name()
    Min_lat, Max_lat, Min_lon, Max_lon, Num_lat, Num_lon, Num_grids = get_save_map_info()
    save_grids()
    end = datetime.datetime.now()
    util.write_log(LOGS, "pretreatment costs %s" % str(end - start))
