from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
from pykml.factory import nsmap
import latlon
from gradient_free_optimizers import HillClimbingOptimizer
import numpy as np
import shelve
from pykml.parser import Schema
from lxml import etree

gxns = "{" + nsmap["gx"] + "}"

# Add visualization pins
def AddPin(lat, lon, name, alt, etree):
    etree.Document.Folder.append(
        KML.Placemark(
            KML.name(name),
            KML.Point(
                KML.extrude(1),
                KML.altitudeMode("relativeToGround"),
                KML.coordinates(
                    "{lon},{lat},{alt}".format(
                        lon=lon,
                        lat=lat,
                        alt=alt,
                    )
                ),
            ),
        )
    )


# add tour locations


def AddLocation(lat, lon, alt, etree, duration):
    etree.Document[gxns + "Tour"].Playlist.append(
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
            ),
        ),
    )
    etree.Document[gxns + "Tour"].Playlist.append(GX.Wait(GX.duration(duration)))


# Calculates the offset for the lat and lon coordinates that translates to the given number of meters.
# Due to issues with earth's curvature it uses a hill climing calgorithm to approximate a perfect solution


def CalculateOffset(lat, lon, meters, verbose):
    l = latlon.LatLon(float(lat), float(lon))

    search_space = {
        "x": np.arange(-0.1, 0.1, 0.000001),
    }

    opt_lon = HillClimbingOptimizer(search_space)
    opt_lat = HillClimbingOptimizer(search_space)

    def objective_lat(x):
        return abs(meters - (l.distance(latlon.LatLon(float(lat) + x["x"], float(lon))) * 1000)) * -1

    def objective_lon(x):
        return abs(meters - (l.distance(latlon.LatLon(float(lat), float(lon) + x["x"])) * 1000)) * -1

    if verbose:
        opt_lon.search(objective_function=objective_lon, n_iter=10000)
        opt_lat.search(objective_function=objective_lat, n_iter=10000)
        # opt_lon.search(objective_function=objective_lon, n_iter=10000, verbosity="print_results", max_score=-1)
        # opt_lat.search(objective_function=objective_lat, n_iter=10000, verbosity="print_results", max_score=-1)
    else:
        opt_lon.search(objective_function=objective_lon, n_iter=10000, verbosity=False)
        opt_lat.search(objective_function=objective_lat, n_iter=10000, verbosity=False)

    # print(opt_lat.best_para["x"], opt_lon.best_para["x"])
    return (abs(opt_lat.best_para["x"]), abs(opt_lon.best_para["x"]))


# Wrapper on CalculateOffset. Handles recalling precomputed values & saving computed values.


def OffsetComputation(lat, lon, meters, precompute, verbose):
    # Gets precomputed data, saves time when running script regularly
    key = str(lat) + "|" + str(lon) + "|" + str(meters)
    if precompute:
        data = shelve.open("precomputed")
        if not key in data.keys():
            print("Data was not in shelve, generating data")
            offsetlat, offsetlon = CalculateOffset(float(lat), float(lon), meters, verbose)
            data[key] = {"offsetlat": str(offsetlat), "offsetlon": str(offsetlon)}
        else:
            offsetlat = data[key]["offsetlat"]
            offsetlon = data[key]["offsetlon"]
        data.close()
    else:
        print("Generating Data...")
        offsetlat, offsetlon = CalculateOffset(float(lat), float(lon), meters, verbose)
        data = shelve.open("precomputed")
        data[key] = {"offsetlat": str(offsetlat), "offsetlon": str(offsetlon)}
        data.close()

    return float(offsetlat), float(offsetlon)

def AddGridPoints(kml, lat, lon, width, height, meters, alt, precompute, duration, verbose, debug):

    offsetlat, offsetlon = OffsetComputation(lat=lat, lon=lon, meters=meters, precompute=precompute, verbose=verbose)

    # Generate the points
    for w in range(-width, width + 1):
        for h in range(-height, height + 1):
            adjusted_lat = w * offsetlat + float(lat)
            adjusted_lon = h * offsetlon + float(lon)
            AddLocation(lat=adjusted_lat, lon=adjusted_lon, alt=alt, etree=kml, duration=duration)
            AddPin(lat=adjusted_lat, lon=adjusted_lon, name=str(w) + ", " + str(h), alt=alt, etree=kml)
            if debug:
                if w == width and h == height:
                    print(adjusted_lat, adjusted_lon)

def AddGrid(lat, lon, width, height, meters, alt, precompute, title, duration, verbose, debug, outdir):
    # Create the base file structure
    tour_doc = KML.kml(
        KML.Document(
            GX.Tour(
                KML.name(title + " Tour"),
                GX.Playlist(),
            ),
            KML.Folder(
                KML.name(title + " Points"),
                id="features",
            ),
        )
    )

    # Generate the offsets
    offsetlat, offsetlon = OffsetComputation(lat=lat, lon=lon, meters=meters, precompute=precompute, verbose=verbose)

    # Generate the points
    for w in range(-width, width + 1):
        for h in range(-height, height + 1):
            adjusted_lat = w * offsetlat + float(lat)
            adjusted_lon = h * offsetlon + float(lon)
            AddLocation(lat=adjusted_lat, lon=adjusted_lon, alt=alt, etree=tour_doc, duration=duration)
            AddPin(lat=adjusted_lat, lon=adjusted_lon, name=str(w) + ", " + str(h), alt=alt, etree=tour_doc)
            if debug:
                if w == width and h == height:
                    print(adjusted_lat, adjusted_lon)

    # Print grid for debugging
    if debug:
        print(etree.tostring(tour_doc, pretty_print=True))

    # Verify Schema
    # assert(Schema("kml22gx.xsd").validate(tour_doc))
    Schema("kml22gx.xsd").assertValid(tour_doc)

    # Output a KML file (named based on the Python script)
    outfile = open(outdir + "/" + title + ".kml", "wb")
    outfile.write(etree.tostring(tour_doc, pretty_print=True))

def SaveGrid(kml, title, debug, outdir):
        # Print grid for debugging
    if debug:
        print(etree.tostring(kml, pretty_print=True))

    # Verify Schema
    # assert(Schema("kml22gx.xsd").validate(tour_doc))
    Schema("kml22gx.xsd").assertValid(kml)

    # Output a KML file (named based on the Python script)
    outfile = open(outdir + "/" + title + ".kml", "wb")
    outfile.write(etree.tostring(kml, pretty_print=True))