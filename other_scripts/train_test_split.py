import os
import random
import math
import shutil
from pathlib import Path
root = ".\image_folder\out\\formatted"
drone_dir = root + "\drone"
sat_dir = root + "\sat"

out_drone_dir = root + "\\test_drone"
out_sat_dir = root + "\\test_sat"

Path(out_drone_dir).mkdir(parents=True, exist_ok=True)
Path(out_sat_dir).mkdir(parents=True, exist_ok=True)

drone_subfolders = [ f.name for f in os.scandir(drone_dir) if f.is_dir() ]

sample = random.sample(drone_subfolders, math.ceil(len(drone_subfolders)/5))

for i in sample:
    shutil.move(drone_dir + "\\" + i, out_drone_dir)
    shutil.move(sat_dir + "\\" + i, out_sat_dir)
