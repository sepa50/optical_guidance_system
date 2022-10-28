import argparse
import math
import os
import numpy as np 
import shutil
import itertools
parser = argparse.ArgumentParser(description="useful image tools")
parser.add_argument('--drone_dir',help="drone image directiory", type=str, required=True)
parser.add_argument('--sat_dir', help="sat image directiory", type=str, required=True)
parser.add_argument('--out_dir', help="output directory", type=str, required=True)
parser.add_argument('--drone_stride', help="distance between drone images", type=int, required=True)
parser.add_argument('--sat_stride', help="distance between satellite images", type=int, required=True)

opt = parser.parse_args()

#Sanity check that stide is a clean multiple
if not (opt.drone_stride / opt.sat_stride).is_integer():
    raise Exception("Invalid stride")

window_size = int(opt.drone_stride / opt.sat_stride)
print("Window size: " + str(window_size))

def get_files(directory):
    f = []
    for filename in os.scandir(directory):
        if filename.is_file():
            f.append(filename)
    return f

def count_files(directory):
    return len(get_files(directory))

#get lists of all files in each folder
drone_files = get_files(opt.drone_dir)
sat_files = get_files(opt.sat_dir)

#get side with
#ASSUMPTION: Perfect Square
drone_width = math.sqrt(len(drone_files))
sat_width = math.sqrt(len(sat_files))

#Sanity check that file counts are correct
if not drone_width.is_integer() or not sat_width.is_integer():
    raise Exception("Invalid number of files at desination")

drone_width = int(drone_width)
sat_width = int(sat_width)

print("Drone grid size: " + str(drone_width) + "x" + str(drone_width))
print("Sat grid size: "+ str(sat_width) + "x" + str(sat_width))

drone_grid = [drone_files[i:i + drone_width] for i in range(0, len(drone_files), drone_width)] 
sat_grid = [sat_files[i:i + sat_width] for i in range(0, len(sat_files), sat_width)]

drone_grid_flat = list(itertools.chain.from_iterable(drone_grid))

related_grid = []
for h_index, row in enumerate(sat_grid):
    for w_index, element in enumerate(row):
        if h_index % window_size == 0 and w_index % window_size == 0 and h_index / window_size < drone_width and w_index / window_size < drone_width:
            grid = []
            for i in range(3):
                for j in range(3):
                    grid.append(sat_grid[h_index+i][w_index+j])
            #print(h_index / window_size, w_index / window_size)
            related_grid.append(grid)

if len(related_grid) != len(drone_grid_flat):
    print("Related Grid Size: " + str(len(related_grid)))
    print("Drone Grid Size: " + str(len(drone_grid_flat)))
    raise Exception("Something went wrong while relating grids")

sat_path = opt.out_dir +"\\sat"
drone_path = opt.out_dir +"\\drone"


if not os.path.exists(sat_path):
    os.mkdir(sat_path)
if not os.path.exists(drone_path):
    os.mkdir(drone_path)
index_offset = len(next(os.walk(drone_path))[1])
for idx, drone_element in enumerate(drone_grid_flat):
    sat_path_relation = sat_path + "\\" + f"{idx+index_offset:04d}"
    drone_path_relation = drone_path + "\\" + f"{idx+index_offset:04d}"
    if os.path.exists(sat_path_relation):
        shutil.rmtree(sat_path_relation)
    if os.path.exists(drone_path_relation):
        shutil.rmtree(drone_path_relation)
    os.mkdir(sat_path_relation)
    os.mkdir(drone_path_relation)

    drone_name = 0
    shutil.copy2(drone_element.path, drone_path_relation + "\\" + str(drone_name) + ".png")

    for element_index, sat_element in enumerate(related_grid[idx]):
        sat_name = str(element_index)
        shutil.copy2(sat_element.path, sat_path_relation + "\\" + sat_name + ".png")
