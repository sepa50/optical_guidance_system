import os 
from datetime import datetime

#Takes a given directory and appends a folder named 'name' to it.
#If a folder by that name already exists, create a new one with the name 'name1'
#Repeat until a non-existant folder exists
def unique_name_generate(directory, name):

   #if the name is taken
    if os.path.isdir(directory+"\\"+name):

        name = name + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

    #set output directory to new dir
    directory += "\\"+name

    return directory