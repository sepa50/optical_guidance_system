import os
import shutil

# folder path
dir_path_sat = r'.\raw\raw-sat'
dir_path_drone = r'.\raw\raw-video'
count = 0
# Iterate directory
for path in os.listdir(dir_path_sat):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path_sat, path)):
        count += 1
print('File count:', count)



name = "raw-video-"
filetype = ".png"
out_path = r'.\processed-data'
for x in range(count):
    path = os.path.join(out_path + "\\sat", f"{x:04d}")
    if os.path.exists(path):
        shutil.rmtree(path)

for x in range(count):
    path = os.path.join(out_path + "\\sat", f"{x:04d}")
    if not os.path.exists(path):
        os.makedirs(path)

for x in range(count):
    path = os.path.join(out_path + "\\video", f"{x:04d}")
    if os.path.exists(path):
        shutil.rmtree(path)

for x in range(count):
    path = os.path.join(out_path + "\\video", f"{x:04d}")
    if not os.path.exists(path):
        os.makedirs(path)


for x in range(count):
    shutil.copy2(dir_path_sat + "\\" + name + f"{x:06d}"+ filetype, out_path + "\\sat" + "\\" + f"{x:04d}" + "\\" + name + f"{x:06d}"+ filetype)

for x in range(count):
    shutil.copy2(dir_path_drone + "\\" + name + f"{x:06d}"+ filetype, out_path + "\\video" + "\\" + f"{x:04d}" + "\\" + name + f"{x:06d}"+ filetype)
#Count number of files in raw/raw-sat
#for each record
#create new folder in processed-data
#add in sat image
#add in drone view