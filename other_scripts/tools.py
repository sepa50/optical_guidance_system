import os
import shutil
import re
import argparse
import numpy as np
from PIL import Image
import statistics

parser = argparse.ArgumentParser(description="useful image tools")

parser.add_argument('--dir', default=r'.\image_folder\in', help="modified directiory", type=str)
parser.add_argument('--outdir', default="", help="output directory", type=str)
parser.add_argument('--namenum', action=argparse.BooleanOptionalAction)
parser.add_argument('--modulo', action=argparse.BooleanOptionalAction)
parser.add_argument('--count', action=argparse.BooleanOptionalAction)
parser.add_argument('--autoslim', action=argparse.BooleanOptionalAction)
opt = parser.parse_args()

# folder path
if opt.outdir != "":
    dir_path_out = opt.outdir
else:
    dir_path_out = opt.dir
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

if opt.modulo:
    for filename in os.scandir(dir_path_dir): # Iterate directory
        if filename.is_file():
            a = re.findall(r'\d+.png', filename.name) #Get numbers from name
            b = a[0].replace(".png", "")
            if (int(b) % 5 == 0):
                shutil.copy2(filename.path, dir_path_out)


if opt.autoslim:
    if dir_path_out == dir_path_dir:
        raise SystemExit('would destructively damage dir_path_dir, please specify dir_path_out')
    #remove all files in output directory
    for filename in os.scandir(dir_path_out):
        if filename.is_file():
            os.remove(filename.path)
    
    def reject_outliers(data, m = 2.):
        d = np.abs(data - np.median(data))
        mdev = np.median(d)
        s = d/mdev if mdev else 0.
        return data[s<m]
    
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
    
    #split list of file names into chunks of size 10
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
            print(d["name"] + " may be a duplicate")
    print("\nSmallest differences:")
    print(sorted(raw_arr)[:10])

    count = 0
    for path in os.listdir(dir_path_out): # Iterate directory
        if os.path.isfile(os.path.join(dir_path_out, path)): # check if current path is a file
            count += 1
    print('File count:', count)
    




        


    
    

