from enum import unique
from itertools import pairwise
import shutil
import argparse
import math
from PIL import Image
import imagehash
import alive_progress
import os 
from collections import Counter
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm
from bisect import bisect_left


parser = argparse.ArgumentParser(description="useful image tools")
parser.add_argument('--dir', default=r'.\image_folder\in', help="input directiory", type=str)
parser.add_argument('--outdir', default=r'.\image_folder\out', help="output directory", type=str)
parser.add_argument('--delimiter', default=r'.\image_folder\delimiter\del.png', help="output directory", type=str)
parser.add_argument('--verbose', action=argparse.BooleanOptionalAction)
opt = parser.parse_args()

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

#delete files in out directory
delete_directory_content(opt.outdir)

#generate image hash of each image
f = get_files(opt.dir)
image_hashes = []
try:
    delimiter = imagehash.phash(Image.open(opt.delimiter))
except:
    raise Exception("Failed to load and hash delimiter.")

paths = [direntry.path for direntry in f]

def phash_calc(file_obj):
    h = imagehash.phash(Image.open(file_obj))
    return h

num_cores = multiprocessing.cpu_count()

image_hashes = Parallel(n_jobs=num_cores)(delayed(phash_calc)(i) for i in tqdm(paths, desc="Hashing Images: "))

image_hashes_dict = {}
for idx, hsh in enumerate(image_hashes):
    image_hashes_dict[str(hsh)] = idx

#with alive_progress.alive_bar(len(f), title="Generating Hashes", length=100) as bar:
#    for idx, n in enumerate(f):
#        h = hash_func(Image.open(n.path))
#        image_hashes.append(h)
#        bar()

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
            #print(f[idx].name)
            hashes_filtered.remove(key)

for v in tqdm(hashes_filtered, desc="Removing Duplicates: "): #remove duplicate values
    if v not in unique_hashes_set or abs(v - delimiter) <= delimiter_threshold:
        unique_hashes.append(v)
        unique_hashes_set.add(v)

#print(len(unique_hashes))

#for key in counter_removal:
#    del counter[key]

#for v in unique_hashes:
    #print(str(v))

if opt.verbose: print("Removing identicle images")

#unique_hashes = list(dict.fromkeys(hashes_filtered))
#unique_hashes = list(counter.keys())

if opt.verbose: print("Evaluating neighbours")
difference_arr = [abs(y-x) for (x, y) in pairwise(unique_hashes)]

#print("Uniques: ", len(unique_hashes))

#remove similar 
if opt.verbose: print("Removing similar neighbours")
removed_count = 0
for i in reversed(range(0, len(unique_hashes)-1)):
     if difference_arr[i] <= threshold:
        removed_count += 1
        #if (abs(unique_hashes[i]-delimiter) <= delimiter_threshold):
           #idx = image_hashes_dict[str(unique_hashes[i])]
           #print(f[idx].name, difference_arr[i], i)
        #else:
        #    unique_hashes.pop(i)
        unique_hashes.pop(i)

#print("Removed: ", removed_count)

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
        #next(subdivide_itr, None)
        continue
    else:
        subdivide_temp_arr.append(element)
#subdivide_result.append(unique_hashes)

def collect_images(hash_val, unfiltered_hash_dict, paths_arr):
    i = unfiltered_hash_dict[str(hash_val)]
    return paths_arr[i]

def save_images(filename, path):
    
    shutil.copy(filename, path)

if opt.verbose: print("Saving Files")
#for idx, n in enumerate(subdivide_result):



#for i in subdivide_result:
#    print(len(i))
#print(len(subdivide_result))
#Parallel(n_jobs=num_cores)(delayed(save_result)(i) for i in indexed_subdivide_result)

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

    #out_paths = Parallel(n_jobs=num_cores)(delayed(collect_images)(h, image_hashes, paths) for h in tqdm(file[1]))
    #print(len(out_paths))
    #with ThreadPoolExecutor(10) as exe:
            # submit all copy tasks
            #_ = [exe.submit(save_images, filename, path) for filename in tqdm(out_paths)]

    #Parallel(n_jobs=num_cores)(delayed(save_images)(p, path) for p in tqdm(out_paths))