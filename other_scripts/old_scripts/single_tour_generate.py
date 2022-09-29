import argparse
import math

import res.kml_resources as rkml
#Based loosely on
#from https://pythonhosted.org/pykml/examples/tour_examples.html#circle-around-locations

#parser is used to allow command line running
#for automation of running this script use a bash file
parser = argparse.ArgumentParser(description="image generation")

parser.add_argument('--lat', help='latitude', type=str, required=True)
parser.add_argument('--lon', help='longitude', type=str, required=True)
parser.add_argument('--distance',default=400, help='distance between points', type=int)
parser.add_argument('--width',default=9, help='grid width', type=int)
parser.add_argument('--height',default=9, help='grid height', type=int)
parser.add_argument('--altitude',default=300, help='altitude above ground', type=int)
parser.add_argument('--name',default="default-drone", help='filename', type=str)
parser.add_argument('--duration',default=10, help='time at each point', type=int)
parser.add_argument('--precompute', action=argparse.BooleanOptionalAction)
parser.add_argument('--verbose', action=argparse.BooleanOptionalAction)
parser.add_argument('--debug', action=argparse.BooleanOptionalAction)
parser.add_argument('--autoheight', action=argparse.BooleanOptionalAction)

opt = parser.parse_args()

#create grid
if opt.autoheight:
  if opt.verbose:
    print("Minimum ground distance calculated as: " + str(opt.altitude * math.tan(30.019 * (math.pi/180))) + " Altitude: " + str(opt.altitude))
  rkml.AddGrid(opt.lat, opt.lon, opt.width, opt.height, opt.altitude * math.tan(30.019 * (math.pi/180)), opt.altitude, opt.precompute, opt.name, opt.duration, opt.verbose, opt.debug)
else:
 rkml.AddGrid(opt.lat, opt.lon, opt.width, opt.height, opt.distance, opt.altitude, opt.precompute, opt.name, opt.duration, opt.verbose, opt.debug)
