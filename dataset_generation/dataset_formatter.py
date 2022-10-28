#This is for taking the dataset and putting it into the format of an ImageFolder

# Input format:
# done1, drone2, ... drone5
#   0
#       0000, 0001, ... 0080
#           img1.png ... img5.png
#   1
#   ...
#   5
# sat1, sat2, ... sat5
#   0
#       0000, 0001, ... 0080
#           img1.png ... img9.png
#   1
#   ...
#   5

# Output Format:
# drone
#   0000
#       img1.png ... img5.png
#   0001
#   ...
#   9999
# sat
#   0000
#       img1.png ... img9.png
#   0001
#   ...
#   9999

#create path list:
#   loop over all sat folders, get paths
#   for each sat folder, attempt to find matching drone folder
#   if fail:
#       remove sat folder
from pathlib import Path
import os
import shutil
from tqdm.auto import tqdm
import argparse

parser = argparse.ArgumentParser(description="useful image tools")
parser.add_argument('--drone', help="name of output directory", default = "out", type=str)
parser.add_argument('--sat', help="name of output directory", default = "out", type=str)
parser.add_argument('--outdir', default=r'.\image_folder\formatted', help="input directory", type=str)
opt = parser.parse_args()

#base_path = ".\image_folder\out\\"

#out_path = base_path + "formatted1"
out_path = opt.outdir

out_path_drone = out_path + "\\drone"
out_path_sat = out_path + "\\sat"

Path(out_path_drone).mkdir(parents=True, exist_ok=True)
Path(out_path_sat).mkdir(parents=True, exist_ok=True)

#drone_path = base_path + "drone1"
drone_path = opt.drone
#sat_path = base_path + "sat1"
sat_path = opt.sat


drone_subfolders = [ f.name for f in os.scandir(drone_path) if f.is_dir() ]
sat_subfolders = [ f.name for f in os.scandir(sat_path) if f.is_dir() ]

out_subfolders = [ int(f.name) for f in os.scandir(out_path_drone) if f.is_dir() ] + [ int(f.name) for f in os.scandir(out_path_sat) if f.is_dir() ]
out_subfolders.sort(reverse=True)

if len(out_subfolders) > 0:
    c = out_subfolders[0] + 1
else:
    c = 0

for n in tqdm(drone_subfolders, desc="Main Loop"):
    if n in sat_subfolders:

        drone_sub_path = str(drone_path) + "\\" + n
        sat_sub_path = str(sat_path) + "\\" + n

        drone_img_folders = [ f.name for f in os.scandir(drone_sub_path) if f.is_dir() ]
        sat_img_folders = [ f.name for f in os.scandir(sat_sub_path) if f.is_dir() ]

        for i in tqdm(drone_img_folders, desc="Copying " + str(n), leave=False):
            if i in sat_img_folders:
                drone_final_path = drone_sub_path + "\\" + i
                sat_final_path = sat_sub_path + "\\" + i
                
                drone_out_folder = out_path_drone + f"\\{c:04d}"
                sat_out_folder = out_path_sat + f"\\{c:04d}"

                shutil.copytree(drone_final_path,  drone_out_folder)
                shutil.copytree(sat_final_path,  sat_out_folder)

                c += 1
        #print(drone_img_folders, sat_img_folders)

#print(subfolders)