from lxml import etree
from pykml.factory import GX_ElementMaker as GX
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import nsmap
from pykml.parser import Schema
import latlon
import numpy as np
from gradient_free_optimizers import HillClimbingOptimizer
import argparse
import decimal
import shelve
import math
#Based loosely on
#from https://pythonhosted.org/pykml/examples/tour_examples.html#circle-around-locations

#Add visualization pins
def AddPin(aLat, aLon, aName, aAlt):
  tour_doc.Document.Folder.append(
      KML.Placemark(
        KML.name(aName),
        KML.Point(
          KML.extrude(1),
          KML.altitudeMode("relativeToGround"),
          KML.coordinates("{lon},{lat},{alt}".format(
                  lon=aLon,
                  lat=aLat,
                  alt=aAlt,
              )
          )
        )
      )
    )

#add tour locations
def AddLocation(lat, lon, alt):
  tour_doc.Document[gxns+"Tour"].Playlist.append(
      GX.FlyTo(
        GX.duration(0.25),
        GX.flyToMode("bounce"),
        KML.LookAt(
          KML.longitude(lon),
          KML.latitude(lat),
          KML.altitude(alt),
          KML.heading(0),
          KML.tilt(0),
          KML.range(0),
          KML.altitudeMode("relativeToGround"),
        )
      ),
    )
  tour_doc.Document[gxns+"Tour"].Playlist.append(GX.Wait(GX.duration(opt.duration)))

#Calcualte the lat and lon offset
#The earth isn't a sphere which makes this really hard
#So i cheated
#This uses a library that calculates the difference between two lat lon coods
#Then it performs hill climbing to find the optimal offset that produces the correct distance
def CalculateOffset(lat, lon, meters):
  l = latlon.LatLon(float(lat), float(lon))

  search_space = {
    "x": np.arange(-0.1, 0.1, 0.000001),
  }

  opt_lon = HillClimbingOptimizer(search_space)
  opt_lat = HillClimbingOptimizer(search_space)

  def objective_lat(x):
    return abs(meters-(l.distance(latlon.LatLon(float(lat) + x["x"], float(lon)))*1000))*-1
  
  def objective_lon(x):
    return abs(meters-(l.distance(latlon.LatLon(float(lat), float(lon) + x["x"]))*1000))*-1
  
  if opt.verbose:
    opt_lon.search(objective_function=objective_lon, n_iter=10000)
    opt_lat.search(objective_function=objective_lat, n_iter=10000)
    #opt_lon.search(objective_function=objective_lon, n_iter=10000, verbosity="print_results", max_score=-1)
    #opt_lat.search(objective_function=objective_lat, n_iter=10000, verbosity="print_results", max_score=-1)
  else:
    opt_lon.search(objective_function=objective_lon, n_iter=10000, verbosity=False)
    opt_lat.search(objective_function=objective_lat, n_iter=10000, verbosity=False)

  #print(opt_lat.best_para["x"], opt_lon.best_para["x"])
  return (abs(opt_lat.best_para["x"]), abs(opt_lon.best_para["x"]))

#Creates the full grid of locations centered on lat lon coordinate
def AddGrid(lat, lon, width, height, meters, alt, precompute):

  #Gets precomputed data, saves time when running script regularly
  key = str(lat)+"|"+str(lon)+"|"+str(meters)
  if precompute:
    data = shelve.open('precomputed')
    if not key in data.keys():
      print("Data was not in shelve, generating data")
      offsetlat, offsetlon = CalculateOffset(float(lat), float(lon), meters)
      offsetlat = decimal.Decimal(offsetlat)
      offsetlon = decimal.Decimal(offsetlon)
      data[key] = {"offsetlat": str(offsetlat), "offsetlon": str(offsetlon)}
    else:
      offsetlat = decimal.Decimal(data[key]["offsetlat"])
      offsetlon = decimal.Decimal(data[key]["offsetlon"])
    data.close()
  else:
    print("Generating Data...")
    offsetlat, offsetlon = CalculateOffset(float(lat), float(lon), meters)
    offsetlat = decimal.Decimal(offsetlat)
    offsetlon = decimal.Decimal(offsetlon)
    data = shelve.open('precomputed')
    data[key] = {"offsetlat": str(offsetlat), "offsetlon": str(offsetlon)}
    data.close()

  #main generation loop
  for w in range(-width, width+1):
    for h in range(-height, height+1):
      adjusted_lat = decimal.Decimal(w)*offsetlat + decimal.Decimal(lat)
      adjusted_lon = decimal.Decimal(h)*offsetlon + decimal.Decimal(lon)
      AddLocation(adjusted_lat, adjusted_lon, alt)
      AddPin(aLat=adjusted_lat, aLon=adjusted_lon, aName=str(w)+", "+str(h), aAlt=alt)
      if opt.debug:
        if w == width and h == height:
          print(adjusted_lat, adjusted_lon)

#parser is used to allow command line running
#for automation of running this script use a bash file
parser = argparse.ArgumentParser(description="image generation")

parser.add_argument('--lat',default='53.61712500', help='latitude', type=str)
parser.add_argument('--lon',default='-2.24064722', help='longitude', type=str)
parser.add_argument('--distance',default=400, help='distance between points', type=int)
parser.add_argument('--width',default=9, help='grid width', type=int)
parser.add_argument('--height',default=9, help='grid height', type=int)
parser.add_argument('--altitude',default=300, help='altitude above ground', type=int)
parser.add_argument('--name',default="default-drone", help='filename', type=str)
parser.add_argument('--precompute', action=argparse.BooleanOptionalAction)
parser.add_argument('--verbose', action=argparse.BooleanOptionalAction)
parser.add_argument('--debug', action=argparse.BooleanOptionalAction)
parser.add_argument('--duration',default=10, help='time at each point', type=int)
parser.add_argument('--autoheight', action=argparse.BooleanOptionalAction)
opt = parser.parse_args()

#Google link thing
gxns = '{' + nsmap['gx'] + '}'

#Create KML doc
tour_doc = KML.kml(
    KML.Document(
      GX.Tour(
        KML.name(opt.name + " Tour"),
        GX.Playlist(),
      ),
      KML.Folder(
        KML.name(opt.name + " Points"),
        id='features',
      )
    )
)
#print(opt.altitude * math.tan(30.019 * (math.pi/180)))
#create grid
if opt.autoheight:
  if opt.verbose:
    print("Minimum ground distance calculated as: " + str(opt.altitude * math.tan(30.019 * (math.pi/180))) + " Altitude: " + str(opt.altitude))
  AddGrid(opt.lat, opt.lon, opt.width, opt.height, opt.altitude * math.tan(30.019 * (math.pi/180)), opt.altitude, opt.precompute)
else:
  AddGrid(opt.lat, opt.lon, opt.width, opt.height, opt.distance, opt.altitude, opt.precompute)
#Print grid for debugging
if opt.debug:
  print(etree.tostring(tour_doc, pretty_print=True))

#Verify Schema
assert(Schema("kml22gx.xsd").validate(tour_doc))

#Output a KML file (named based on the Python script)
outfile = open(opt.name+'.kml','wb')
outfile.write(etree.tostring(tour_doc, pretty_print=True))