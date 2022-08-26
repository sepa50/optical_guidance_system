import os
import shutil
import re
import argparse
import numpy as np
from PIL import Image
import statistics
import imagehash

parser = argparse.ArgumentParser(description="useful image tools")

parser.add_argument('--dir', default=r'.\image_folder\in', help="input directiory", type=str)
parser.add_argument('--outdir', default=r'.\image_folder\out', help="output directory", type=str)
group = parser.add_mutually_exclusive_group()
group.add_argument('--count', action=argparse.BooleanOptionalAction, help="counts number of files in folder")
group.add_argument('--namenum', action=argparse.BooleanOptionalAction, help="shortens name to only the associated number")
group.add_argument('--moduloslim', action=argparse.BooleanOptionalAction, help="uses modulo to determine similarity")
group.add_argument('--sizeslim', action=argparse.BooleanOptionalAction, help="uses jpg file size to determine similarity")
group.add_argument('--hashslim', action=argparse.BooleanOptionalAction, help="uses phash to determine similarity")
opt = parser.parse_args()

#sets the folder path varibles
dir_path_out = opt.outdir
dir_path_dir = opt.dir

def shorten_names(directory, out_directory):
    for filename in os.scandir(directory): # Iterate directory
        if filename.is_file():
            a = re.findall(r'\d+.png', filename.name) #Get numbers from name
            b = a[0].replace(".png", "")
            if directory == out_directory:
                 os.rename(directory + "\\" + filename.name, directory + "\\" + f"{int(b):06d}" + ".png")
            else:
                shutil.copy2(filename.path, out_directory)
                os.rename(out_directory + "\\" + filename.name, out_directory + "\\" + f"{int(b):06d}" + ".png")

def delete_directory_content(directory):
        for filename in os.scandir(directory):
            if filename.is_file():
                os.remove(filename.path)

def get_files(directory):
    f = []
    for filename in os.scandir(dir_path_out):
        if filename.is_file():
            f.append(filename)
    return f

#Counts the number of files in the input directory
if opt.count:
    count = 0
    for path in os.listdir(dir_path_dir):
        if os.path.isfile(os.path.join(dir_path_dir, path)):
            count += 1
    print('File count:', count)

#Renames all files in the directory to NUMBER.png
if opt.namenum:
    shorten_names(dir_path_dir, dir_path_out)

#Uses modulo to guess what files will be duplicates, generates around 1 duplicate per image
if opt.moduloslim:
    for filename in os.scandir(dir_path_dir): # Iterate directory
        if filename.is_file():
            a = re.findall(r'\d+.png', filename.name) #Get numbers from name
            b = a[0].replace(".png", "")
            if (int(b) % 5 == 0):
                shutil.copy2(filename.path, dir_path_out)

#Uses file size of a .jpg to determine similarity of files
#Not safe, will have issues, better solution needed
if opt.sizeslim:
    #remove all files in output directory
    delete_directory_content(dir_path_out)
    
    #creates jpg of each image at out location
    for filename in os.scandir(dir_path_dir):
        if filename.is_file():
            b = filename.name.replace(".png", "")
            im1 = Image.open(filename.path)
            im1.save(dir_path_out +  "\\" + b + ".jpg")
    
    #create a list of all file names
    f = get_files(dir_path_out)
    
    #split list of file names into chunks of size 15, a chunk of 10 is almost always included...
    #note: i itterate by 10 so its sorta a sliding window rather than chunks
    n = 15 #window size
    w = 10 #step size
    chunks = [f[i:i + n] for i in range(0, len(f), w)]

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
    delete_directory_content(dir_path_out)
    
    #copys the images it thinks are unique to the out folder
    for filename in out_images:
        a = re.findall(r'\d+.jpg', filename)
        b = filename.replace(".jpg", ".png")
        #c = a[0].replace(".jpg", "")
        shutil.copy2(dir_path_dir + "\\" + b, dir_path_out)
        #os.rename(dir_path_out + "\\" + b, dir_path_out + "\\" + f"{int(c):06d}" + ".png")

    #rename files
    shorten_names(dir_path_out, dir_path_out)

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
            #can be used to auto delete 0 bit difference images
            #if (d["diff"] == 0):
            #    os.remove(dir_path_out + "\\" + d["name"])
            #    print(d["name"] + " - 0 (Auto Removed)")
            #else:
                print(d["name"] + " - " + str(d["diff"]))
    print("Smallest differences:")
    count = len(eval_arr)
    print(sorted(raw_arr)[:round(count/10)])
    print("File count (Doesn't count auto removed):", count)

if opt.hashslim:
    #delete files in out directory
    delete_directory_content(dir_path_out)
    #generate image hash of each image
    #generate difference array
    #if difference is not large cull
    #repeat untill differences are all large