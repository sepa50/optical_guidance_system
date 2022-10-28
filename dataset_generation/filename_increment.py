import os

dir = ".\image_folder\out\sat1\\1"

drone_subfolders = [ f.name for f in os.scandir(dir) if f.is_dir() ]

drone_subfolders.reverse()

for i in drone_subfolders:
    if int(i) > 21:
        os.rename(dir + "\\" + i, dir + "\\" + f"{int(i)+1:04d}")

