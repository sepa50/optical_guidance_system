import argparse
import os
from pykml import parser
from pykml.factory import GX_ElementMaker as GX
from pykml.factory import KML_ElementMaker as KML
import math
import res.kml_resources as rkml
from pathlib import Path
import res.file_manip_resources as rfm

# Get the defualt location of myplaces.kml, the file that saves the current points within google earth pro
directory = os.getenv("APPDATA") + "\..\LocalLow\Google\GoogleEarth\myplaces.kml"

argparser = argparse.ArgumentParser(description="create tours")
argparser.add_argument(
    "--delat",
    help="latitude that is used for delimiter",
    type=float,
    required=True,
)
argparser.add_argument(
    "--delon",
    help="longitude that is used for delimiter",
    type=float,
    required=True,
)
argparser.add_argument("--dir", default=directory, help="location of kml with points", type=str)
argparser.add_argument("--outdir", default=r"./kml", help="output location of kml files", type=str)
argparser.add_argument("--distance", default=400, help="distance between points", type=int)
argparser.add_argument("--width", help="grid width", type=int, required=True)
argparser.add_argument("--height", help="grid height", type=int, required=True)
argparser.add_argument("--altitude", default=300, help="altitude above ground", type=int)
argparser.add_argument("--name", default="tour_path", help="filename", type=str)
argparser.add_argument("--duration", default=10, help="time at each point", type=int)
argparser.add_argument("--batchsize", default=10, help="size of a batch", type=int)
argparser.add_argument("--precompute", action=argparse.BooleanOptionalAction)
argparser.add_argument("--verbose", action=argparse.BooleanOptionalAction)
argparser.add_argument("--debug", action=argparse.BooleanOptionalAction)

opt = argparser.parse_args()

opt.outdir = rfm.unique_name_generate(opt.outdir, opt.name)
Path(opt.outdir).mkdir(parents=True, exist_ok=True)

#TODO: Fix horrible hardcoded values
kml_file = r"myplaces.kml"
with open(kml_file) as f:
    doc = parser.parse(f)
    root = doc.getroot()

#create core
tour_doc = KML.kml(
    KML.Document(
        GX.Tour(
            KML.name(opt.name + " Tour"),
            GX.Playlist(),
        ),
        KML.Folder(
            KML.name(opt.name + " Points"),
            id="features",
        ),
    )
)

print("Minimum ground distance calculated as: " + str(opt.altitude * math.tan(30.019 * (math.pi/180))) + " Altitude: " + str(opt.altitude))

# loop over all points, generate a tour for every point
i = 0
for coordinate_str in doc.findall(".//{*}coordinates"):
    if (i % opt.batchsize == 0 and i != 0):
        j = math.ceil(i / opt.batchsize)
        rkml.SaveGrid(kml=tour_doc, title=opt.name + str(j), debug=opt.debug, outdir=opt.outdir)

        tour_doc = KML.kml(
            KML.Document(
                GX.Tour(
                    KML.name(opt.name + " Tour"),
                    GX.Playlist(),
                ),
                KML.Folder(
                    KML.name(opt.name + " Points"),
                    id="features",
                ),
            )
        )
    
    coordinate_array = str(coordinate_str).split(",")
    lat = coordinate_array[1]
    lon = coordinate_array[0]

    rkml.AddGridPoints(kml=tour_doc, lat=lat, lon=lon, width=opt.width, height=opt.height, meters=opt.distance, alt=opt.altitude, precompute=opt.precompute, duration=opt.duration, verbose=opt.verbose, debug=opt.debug)
    rkml.AddPin(lat=opt.delat, lon=opt.delon, name="delimiter", alt=100, etree=tour_doc)
    rkml.AddLocation(lat=opt.delat, lon=opt.delon, alt=100, etree=tour_doc, duration=10)

    i += 1

rkml.SaveGrid(kml=tour_doc, title=opt.name + str(math.ceil(i / opt.batchsize)), debug=opt.debug, outdir=opt.outdir)
# rkml.AddGrid(lat=lat, lon=lon, width=opt.width, height=opt.height, meters=opt.distance, alt=opt.altitude, precompute=opt.precompute, title=opt.name + "-" + str(i), duration=opt.duration, verbose=opt.verbose, debug=opt.debug, outdir=opt.outdir)
