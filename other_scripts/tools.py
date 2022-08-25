import os
import shutil
import re
import argparse
import numpy as np
from PIL import Image
import statistics

parser = argparse.ArgumentParser(description="useful image tools")

parser.add_argument('--dir', default=r'.\image_folder\in', help="input directiory", type=str)
parser.add_argument('--outdir', default=r'.\image_folder\out', help="output directory", type=str)
group = parser.add_mutually_exclusive_group()
group.add_argument('--namenum', action=argparse.BooleanOptionalAction, help="shortens name to only the associated number")
group.add_argument('--moduloslim', action=argparse.BooleanOptionalAction, help="uses modulo to determine similarity")
group.add_argument('--count', action=argparse.BooleanOptionalAction, help="counts number of files in folder")
group.add_argument('--sizeslim', action=argparse.BooleanOptionalAction, help="uses jpg file size to determine similarity")

opt = parser.parse_args()

# folder path
dir_path_out = opt.outdir
dir_path_dir = opt.dir
count = 0

if opt.count:
    for path in os.listdir(dir_path_dir): # Iterate directory
        if os.path.isfile(os.path.join(dir_path_dir, path)): # check if current path is a file
            count += 1
    print('File count:', count)

if opt.namenum:
    for filename in os.scandir(dir_path_dir): # Iterate directory
        if filename.is_file():
            a = re.findall(r'\d+.png', filename.name) #Get numbers from name
            b = a[0].replace(".png", "")
            shutil.copy2(filename.path, dir_path_out)
            os.rename(dir_path_out + "\\" + filename.name, dir_path_out + "\\" + f"{int(b):06d}" + ".png")

if opt.moduloslim:
    for filename in os.scandir(dir_path_dir): # Iterate directory
        if filename.is_file():
            a = re.findall(r'\d+.png', filename.name) #Get numbers from name
            b = a[0].replace(".png", "")
            if (int(b) % 5 == 0):
                shutil.copy2(filename.path, dir_path_out)


if opt.sizeslim:
    #remove all files in output directory
    for filename in os.scandir(dir_path_out):
        if filename.is_file():
            os.remove(filename.path)
    
    #creates jpg of each image at out location
    for filename in os.scandir(dir_path_dir):
        if filename.is_file():
            b = filename.name.replace(".png", "")
            im1 = Image.open(filename.path)
            im1.save(dir_path_out +  "\\" + b + ".jpg")
    
    #create a list of all file names
    f = []
    for filename in os.scandir(dir_path_out):
        if filename.is_file():
            f.append(filename)
    
    #split list of file names into chunks of size 15, a chunk of 10 is almost always included...
    #note: i itterate by 10 so its sorta a sliding window rather than chunks
    n = 15
    chunks = [f[i:i + n] for i in range(0, len(f), 10)]

    #find the median file size image for each chunk
    out_images = []
    for chunk in chunks:
        z = []
        for image in chunk:
            z.append(os.stat(image.path).st_size)
        zmedian = statistics.median_low(z)
        zindex = z.index(zmedian)
        out_images.append(chunk[zindex].name)

    #remove all files in output directory
    for filename in os.scandir(dir_path_out):
        if filename.is_file():
            os.remove(filename.path)
        
    #copys the images it thinks are unique to the out folder
    for filename in out_images:
        a = re.findall(r'\d+.jpg', filename)
        b = a[0].replace(".jpg", ".png")
        c = a[0].replace(".jpg", "")
        shutil.copy2(dir_path_dir + "\\" + b, dir_path_out)
        os.rename(dir_path_out + "\\" + b, dir_path_out + "\\" + f"{int(c):06d}" + ".png")

    #evaluate how well we did
    print("Evaluating results")
    print("Likely Duplicates:")
    eval_arr = []
    names_arr = []
    for filename in os.scandir(dir_path_out):
        if filename.is_file():
            v = os.stat(filename.path).st_size
            eval_arr.append({"name": filename.name, "size": v})
    raw_arr = [abs(eval_arr[i+1]["size"]-eval_arr[i]["size"]) for i in range(len(eval_arr)-1)]
    diff_arr = [{"name": eval_arr[i]["name"],"diff": abs(eval_arr[i+1]["size"]-eval_arr[i]["size"])} for i in range(len(eval_arr)-1)]
    for d in diff_arr:
        if (d["diff"] < 1000):
            print(d["name"])
    print("Smallest differences:")
    count = len(eval_arr)
    print(sorted(raw_arr)[:round(count/10)])
    print('File count:', count)


    




        


    
    

