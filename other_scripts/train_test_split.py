import os
import random
import math
import shutil
from pathlib import Path
import argparse
from distutils.dir_util import copy_tree

parser = argparse.ArgumentParser(description="Splits the training and testing data randomly")
parser.add_argument('--input_dir', default = ".\image_folder\out\\formatted", help="Location of input directory", type=str)
parser.add_argument('--output_dir', default = ".\image_folder\out\\split", help="Location of output directory", type=str)
parser.add_argument('--test_size', default = 20, help="Percentage of data used for testing", type=int)
opt = parser.parse_args()

drone_dir = opt.input_dir + "\drone"
sat_dir = opt.input_dir + "\sat"

out_drone_dir = opt.output_dir + "\drone"
out_sat_dir =opt.output_dir + "\sat"

out_drone_test_dir = opt.output_dir + "\\test_drone"
out_sat_test_dir = opt.output_dir + "\\test_sat"

Path(out_drone_dir).mkdir(parents=True, exist_ok=True)
Path(out_sat_dir).mkdir(parents=True, exist_ok=True)

Path(out_drone_test_dir).mkdir(parents=True, exist_ok=True)
Path(out_sat_test_dir).mkdir(parents=True, exist_ok=True)

drone_subfolders = [ f.name for f in os.scandir(drone_dir) if f.is_dir() ]

sample = random.sample(drone_subfolders, math.ceil(len(drone_subfolders)/100 * opt.test_size))

copy_tree(drone_dir, out_drone_dir)
copy_tree(sat_dir, out_sat_dir)

for i in sample:
    shutil.move(out_drone_dir + "\\" + i, out_drone_test_dir)
    shutil.move(out_sat_dir + "\\" + i, out_sat_test_dir)
