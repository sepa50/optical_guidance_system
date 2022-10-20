from itertools import pairwise
import os
import shutil
import re
import argparse
from PIL import Image
import statistics
import imagehash
import alive_progress
import math

parser = argparse.ArgumentParser(description="useful image tools")

parser.add_argument('--dir', default=r'.\image_folder\in', help="input directiory", type=str)
parser.add_argument('--outdir', default=r'.\image_folder\out', help="output directory", type=str)

group = parser.add_mutually_exclusive_group()
group.add_argument('--count', action=argparse.BooleanOptionalAction, help="counts number of files in folder")
group.add_argument('--namenum', action=argparse.BooleanOptionalAction, help="shortens name to only the associated number")
group.add_argument('--moduloslim', action=argparse.BooleanOptionalAction, help="uses modulo to determine similarity")
group.add_argument('--sizeslim', action=argparse.BooleanOptionalAction, help="uses jpg file size to determine similarity")
group.add_argument('--hashslim', action=argparse.BooleanOptionalAction, help="uses phash to determine similarity")
group.add_argument('--evalslim', action=argparse.BooleanOptionalAction, help="evaluates similarity with hashes")
group.add_argument('--name2d', action=argparse.BooleanOptionalAction, help="renames as the original 2d array")

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
    for filename in os.scandir(directory):
        if filename.is_file():
            f.append(filename)
    return f

def count_files(directory):
    return len(get_files(directory))

#Counts the number of files in the input directory
if opt.count:
    print('File count:', count_files(dir_path_dir))

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

#Good way to quickly generate unique images
#Uses a special kind of hash that is designed for image comparison
if opt.hashslim:
    #for dhash = threshold 11 GREAT
    #for phash = threshold 15 GREAT
    hash_func = imagehash.phash
    threshold = 15
    warning = 20

    #delete files in out directory
    delete_directory_content(dir_path_out)

    #generate image hash of each image
    f = get_files(dir_path_dir)
    image_hashes = []

    with alive_progress.alive_bar(len(f), title="Generating Hashes", length=100) as bar:
        for idx, n in enumerate(f):
            h = hash_func(Image.open(n.path))
            image_hashes.append(h)
            bar()

    unique_hashes = list(dict.fromkeys(image_hashes))

    difference_arr = [y-x for (x, y) in pairwise(unique_hashes)]

    #remove similar 
    for i in reversed(range(0, len(unique_hashes)-1)):
        if difference_arr[i] <= threshold:
            unique_hashes.pop(i)

    #create list of images with unique hashes
    unique_images = []
    for h in unique_hashes:
        i = image_hashes.index(h)
        unique_images.append(f[i])

    #move files
    for filename in unique_images:
        shutil.copy2(filename.path, dir_path_out)
    
    print("File Count: " + str(count_files(dir_path_out)))

#Evaluates a given file amount slimming operation using a number of hash functions  
if opt.evalslim:
    a_threshold = 6
    p_threshold = 15
    d_threshold = 11

    f = get_files(dir_path_dir)

    a_hashes = []
    p_hashes = []
    d_hashes = []

    with alive_progress.alive_bar(len(f), title="Generating Hashes", length=100) as bar:
        for idx, n in enumerate(f):
            img = (Image.open(n.path))
            a = imagehash.average_hash(img)
            p = imagehash.phash(img)
            d = imagehash.dhash(img)
            a_hashes.append(a)
            p_hashes.append(p)
            d_hashes.append(d)
            bar()

    a_difference = [y-x for (x, y) in pairwise(a_hashes)]
    p_difference = [y-x for (x, y) in pairwise(p_hashes)]
    d_difference = [y-x for (x, y) in pairwise(d_hashes)]

    print("File Count: " + str(len(f)))
    print("Evaluating hashes for possible duplicates: ")
    found = False
    for i in range(len(a_difference)):
        s = ""
        if a_difference[i] < a_threshold:
            s += "index "+ f[i].name +" failed A threshold ("+ str(a_difference[i]) +" > " + str(a_threshold) +"); "
        if p_difference[i] < p_threshold:
            s += "index "+ f[i].name +" failed P threshold ("+ str(a_difference[i]) +" > " + str(p_threshold) +"); "
        if d_difference[i] < d_threshold:
            s += "index "+ f[i].name +" failed D threshold ("+ str(a_difference[i]) +" > " + str(d_threshold) +"); "
        if (s != ""):
            found = True
            print(s)
    if not found:
        print("All values passed all thresholds")

#names the files in the format: 000(x,y).png
if opt.name2d:
    c = count_files(dir_path_dir)
    root = math.sqrt(c)
    if root != round(root):
        raise Exception("Invalid number of files at desination")
    print("Root calculated as: " + str(root))
    minimum = (root - 1) / 2
    i = 0
    for idx, filename in enumerate(os.scandir(dir_path_dir)): # Iterate directory
        if filename.is_file():
                x = idx - math.floor(idx / root) * root - minimum
                y = math.floor(idx / root) - minimum
                name = "(" + str(int(x)) + "x" + str(int(y)) + ")"
                os.rename(filename.path, dir_path_dir + "\\" + f"{int(i):04d}" + name + ".png")
                i += 1