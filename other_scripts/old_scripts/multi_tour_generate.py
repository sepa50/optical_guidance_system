from pykml import parser
import argparse
import os
import res.kml_resources as rkml
#Get the defualt location of myplaces.kml, the file that saves the current points within google earth pro
directory = os.getenv('APPDATA') + "\..\LocalLow\Google\GoogleEarth\myplaces.kml"

argparser = argparse.ArgumentParser(description="create tours")

argparser.add_argument('--dir',default=directory, help='location of kml with points', type=str)
argparser.add_argument('--outdir',default=r"./kml", help='output location of kml files', type=str)
argparser.add_argument('--distance',default=400, help='distance between points', type=int)
argparser.add_argument('--width',default=9, help='grid width', type=int)
argparser.add_argument('--height',default=9, help='grid height', type=int)
argparser.add_argument('--altitude',default=300, help='altitude above ground', type=int)
argparser.add_argument('--name',default="default", help='filename', type=str)
argparser.add_argument('--duration',default=10, help='time at each point', type=int)
argparser.add_argument('--precompute', action=argparse.BooleanOptionalAction)
argparser.add_argument('--verbose', action=argparse.BooleanOptionalAction)
argparser.add_argument('--debug', action=argparse.BooleanOptionalAction)

opt = argparser.parse_args()

kml_file = r"myplaces.kml"
with open(kml_file) as f:
  doc = parser.parse(f)
  root = doc.getroot()

#loop over all points, generate a tour for every point
i = 0
for coordinate_str in doc.findall(".//{*}coordinates"):
  coordinate_array = str(coordinate_str).split(",")
  lat = coordinate_array[1]
  lon = coordinate_array[0]

  rkml.AddGrid(lat=lat, lon=lon, width=opt.width, height=opt.height, meters=opt.distance, alt=opt.altitude, precompute=opt.precompute, title=opt.name + "-" + str(i), duration=opt.duration, verbose=opt.verbose, debug=opt.debug, outdir=opt.outdir)
  i += 1



