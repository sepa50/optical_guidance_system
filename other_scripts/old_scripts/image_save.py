import numpy
from PIL import Image
import json

#adds data to the json dictionary
#saves image as png using id as name
def save_image(img, data_dictionary, input_json_obj):
    img.save("image_folder/" + str(input_json_obj["id"]) + ".png") #save image to file
    data_dictionary["images"].append(input_json_obj) #add data to dictionary

#saves data to json
def save_json(data_dictionary, file_path):
    with open(file_path, "w") as outfile:
        json.dump(data_dictionary, outfile)

#generates randomized images
#saves those images to json dictionary
def gen_fake_data(data_dictionary, starting_index):
    for i in range(starting_index, starting_index+10):
        #get data
        imarray = numpy.random.rand(100,100,3) * 255
        img = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
        d = {
            "id": i,
            "other metadata": "bla bla bla"
        }
        #pass data and index
        save_image(img, data_dictionary, d)

#open the json file
f = open('metadata.json')
#load data into python dict
data = json.load(f)
#generate fake data and save it
gen_fake_data(data, len(data["images"]))
#save json
save_json(data, "metadata.json")