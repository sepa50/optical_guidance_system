from encodings import search_function
from os import path

from lxml import etree
from pykml.factory import GX_ElementMaker as GX
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import nsmap
from pykml.parser import Schema
import latlon
import numpy as np
from gradient_free_optimizers import HillClimbingOptimizer

#Based loosely on
#from https://pythonhosted.org/pykml/examples/tour_examples.html#circle-around-locations
gxns = '{' + nsmap['gx'] + '}'

#Create KML doc
tour_doc = KML.kml(
    KML.Document(
      GX.Tour(
        KML.name("Test 01"),
        GX.Playlist(),
      ),
      KML.Folder(
        KML.name('Features'),
        id='features',
      ),
    )
)

#Add visualization pins
def AddPin(aLat, aLon, aName, aDesc):
  tour_doc.Document.Folder.append(
      KML.Placemark(
        KML.name("?"),
        #KML.description(
        #    "<h1>{name}</h1><br/>{desc}".format(
        #            name=aName,
        #            desc=aDesc,
        #    )
        #),
        KML.Point(
          KML.extrude(1),
          KML.altitudeMode("relativeToGround"),
          KML.coordinates("{lon},{lat},{alt}".format(
                  lon=aLon,
                  lat=aLat,
                  alt=150,
              )
          )
        ),
        id=aName.replace(' ','_')
      )
    )

#add tour locations
def AddLocation(lat, lon):
  tour_doc.Document[gxns+"Tour"].Playlist.append(
      GX.FlyTo(
        GX.duration(0.25),
        GX.flyToMode("bounce"),
        KML.LookAt(
          KML.longitude(lon),
          KML.latitude(lat),
          KML.altitude(300),
          KML.heading(0),
          KML.tilt(0),
          KML.range(0),
          KML.altitudeMode("relativeToGround"),
        )
      ),
    )
  tour_doc.Document[gxns+"Tour"].Playlist.append(GX.Wait(GX.duration(10.0)))
import tensorflow as tf

#Calcualte the lat and lon offset
#The earth isn't a sphere which makes this really hard
#So i cheated
#This uses a library that calculates the difference between two lat lon coods
#Then it performs hill climbing to find the optimal offset that produces the correct distance
def CalculateOffset(lat, lon, meters):
  l = latlon.LatLon(lat, lon)

  search_space = {
    "x": np.arange(-0.1, 0.1, 0.000001),
  }

  opt_lon = HillClimbingOptimizer(search_space)
  opt_lat = HillClimbingOptimizer(search_space)

  def objective_lat(x):
    #print(x)
    return abs(meters-(l.distance(latlon.LatLon(lat + x["x"], lon))*1000))*-1

  def objective_lon(x):
    #print(x)
    return abs(meters-(l.distance(latlon.LatLon(lat, lon + x["x"]))*1000))*-1

  opt_lon.search(objective_function=objective_lon, n_iter=10000, max_score=-1)
  opt_lat.search(objective_function=objective_lat, n_iter=10000, max_score=-1)

  #opt_lon.search(objective_function=objective_lon, n_iter=10000, verbosity="print_results", max_score=-1)
  #opt_lat.search(objective_function=objective_lat, n_iter=10000, verbosity="print_results", max_score=-1)

  return (opt_lat.best_para["x"], opt_lon.best_para["x"])

#Creates the full grid of locations centered on lat lon coordinate
def AddGrid(lat, lon, width, height, offsetlat, offsetlon):
  a = ""
  for w in range((int)(-width/2), (int)(width/2)):
    for h in range((int)(-height/2), (int)(height/2)):
      AddLocation(lat + w*offsetlat, lon + h*offsetlon)
      a += "a"
      AddPin(lat + w*offsetlat, lon + h*offsetlon, a, "")

#Input variables
lat = 53.61712500
lon = -2.24064722
meters = 400
width = 8
height = width

offsetlat, offsetlon = CalculateOffset(lat, lon, meters)
AddGrid(lat, lon, width, height, offsetlat, offsetlon)
# check that the KML document is valid using the Google Extension XML Schema
assert(Schema("kml22gx.xsd").validate(tour_doc))

#print(etree.tostring(tour_doc, pretty_print=True))

# output a KML file (named based on the Python script)
outfile = open(__file__.rstrip('.py')+'.kml','wb')
outfile.write(etree.tostring(tour_doc, pretty_print=True))
