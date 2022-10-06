from itertools import pairwise
import shutil
import argparse
from PIL import Image
import imagehash
import os 
from collections import Counter
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm
from bisect import bisect_left
from pathlib import Path
import res.file_manip_resources as rfm
import re

parser = argparse.ArgumentParser(description="useful image tools")
parser.add_argument('--name', help="name of output directory", type=str)
parser.add_argument('--dir', default=r'.\image_folder\in', help="input directiory", type=str)
parser.add_argument('--outdir', default=r'.\image_folder\out', help="output directory", type=str)
parser.add_argument('--delimiter', default=r'.\image_folder\delimiter\del.png', help="output directory", type=str)
parser.add_argument('--verbose', action=argparse.BooleanOptionalAction)
opt = parser.parse_args()

#set default value for --name
if not opt.name:
    opt.name = "out"

#magic values
#change at own risk
threshold = 15
delimiter_threshold = 10
odd_threshold = 5
warning = 20

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
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def get_files(directory):
    f = []
    for filename in os.scandir(directory):
        if filename.is_file():
            filename.name
            f.append(filename)
    return f

def count_files(directory):
    return len(get_files(directory))

def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before

opt.outdir = rfm.unique_name_generate(opt.outdir, opt.name)
#ensure paths exist
Path(opt.outdir).mkdir(parents=True, exist_ok=True)
Path(opt.dir).mkdir(parents=True, exist_ok=True)
Path(os.path.dirname(opt.delimiter)).mkdir(parents=True, exist_ok=True)

#check delimiter exists
if (not os.path.isfile(opt.delimiter)):
    raise Exception("\n\nFailed to find delimiter.\n")

#check input directory has files in it
if os.path.isdir(opt.dir) and os.path.exists(opt.dir):
    if len(os.listdir(opt.dir)) == 0:
        raise Exception("\n\nNo files in input directory\n")

#delete files in out directory
#sanity check, should normally be empty
delete_directory_content(opt.outdir)

#Generate hash of delimiter
try:
    delimiter = imagehash.phash(Image.open(opt.delimiter))
except:
    raise Exception("\n\nFailed to load and hash delimiter.\n")

#get files in input directory
f = get_files(opt.dir)
image_hashes = []
paths = [direntry.path for direntry in f]

#calculate hashes for each file in input directory
def phash_calc(file_obj):
    return imagehash.phash(Image.open(file_obj))

num_cores = multiprocessing.cpu_count()
image_hashes = Parallel(n_jobs=num_cores)(delayed(phash_calc)(i) for i in tqdm(paths, desc="Hashing Images: "))

#generate dictionary of hash to index
image_hashes_dict = {}
for idx, hsh in enumerate(image_hashes):
    image_hashes_dict[str(hsh)] = idx

#Removes images that are not similar to any other image
counter = Counter(image_hashes)
hashes_filtered = image_hashes.copy()
unique_hashes = []
unique_hashes_set = set()
for key in tqdm(reversed(counter.keys()), desc="Removing Loners: ", total=len(counter.keys())):
    if counter[key] == 1: #remove values that are on their own
        if (abs(key - delimiter) <= delimiter_threshold):
            continue
        
        idx = image_hashes_dict[str(key)] #get index
        close = []
        for val in range(max(0, idx - 10), min(idx + 11, len(image_hashes))): #look at window around index
            if (val != idx): #skip itself
                close.append(image_hashes[val])

        has_close = False
        for val in close: #if values within winow around index are within range
            if abs(val - key) <= odd_threshold:
                has_close = True

        if not has_close: #skip removal
            hashes_filtered.remove(key)

#removes images that are exactly the same as other images
if opt.verbose: print("Removing identicle images")
for v in tqdm(hashes_filtered, desc="Removing Duplicates: "): #remove duplicate values
    if v not in unique_hashes_set or abs(v - delimiter) <= delimiter_threshold:
        unique_hashes.append(v)
        unique_hashes_set.add(v)

#remove images that are similar and positionally close to each other
if opt.verbose: print("Evaluating neighbours")
difference_arr = [abs(y-x) for (x, y) in pairwise(unique_hashes)]

#remove similar 
if opt.verbose: print("Removing similar neighbours")
removed_count = 0
for i in reversed(range(0, len(unique_hashes)-1)):
     if difference_arr[i] <= threshold:
        removed_count += 1
        unique_hashes.pop(i)

#seperate images by the delimiter image
if opt.verbose: print("Seperating by delimiter")
subdivide_result = []
subdivide_temp_arr = []
subdivide_itr = iter(unique_hashes)
num = 0
for element in subdivide_itr:
    if (abs(element-delimiter) <= delimiter_threshold):
        num += 1

        subdivide_result.append(subdivide_temp_arr)
        subdivide_temp_arr = []
        continue
    else:
        subdivide_temp_arr.append(element)

def collect_images(hash_val, unfiltered_hash_dict, paths_arr):
    i = unfiltered_hash_dict[str(hash_val)]
    return paths_arr[i]

def save_images(filename, path):
    shutil.copy(filename, path)

if opt.verbose: print("Saving Files")

#save images
#this can be parallelized however it doesn't improve speed
for idx, hash_arr in enumerate(subdivide_result):
    path = opt.outdir + "\\" + str(idx)
    print(path, len(hash_arr))

    if not os.path.exists(path):
        os.makedirs(path)

    out_paths = []

    for h in hash_arr:
        out_paths.append(collect_images(h, image_hashes_dict, paths))

    for p in out_paths:
        save_images(p, path)