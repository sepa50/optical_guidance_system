from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
from pykml.factory import nsmap
import latlon
from gradient_free_optimizers import RepulsingHillClimbingOptimizer
from hyperactive.optimizers import DownhillSimplexOptimizer
import numpy as np
import shelve
from pykml.parser import Schema
from lxml import etree
import time
import geopy.distance
import hyperactive
import os

gxns = "{" + nsmap["gx"] + "}"


def AddGroundOverlays(lat, lon, radius, alt, image_path, verbose, tree):

    Dlat, Dlon = OffsetComputation(lat=lat, lon=lon, meters=radius, precompute=True, verbose=verbose)

    fudge_factor = 2
    alt_fudge_factor = 50
    
    latL = lat - Dlat * fudge_factor * alt/alt_fudge_factor
    latH = lat + Dlat * fudge_factor * alt/alt_fudge_factor
    lonL = lon - Dlon * fudge_factor * alt/alt_fudge_factor
    lonH = lon + Dlon * fudge_factor * alt/alt_fudge_factor

    abs_path = os.path.abspath(image_path)

    
    ele = KML.GroundOverlay(
        KML.name("ColorBlock"), 
        KML.Icon(
            KML.href(abs_path),
            KML.viewBoundScale(str(0.75))
        ), 
        KML.altitude(str(alt)),
        KML.altitudeMode("absolute"),
        KML.LatLonBox(
            KML.north(str(latH)),
            KML.south(str(latL)),
            KML.east(str(lonH)),
            KML.west(str(lonL))
        )
    )

    tree.Document.append(ele)


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
def AddLocationComplex(lat, lon, angle, tilt, distance, alt, etree, duration):
    etree.Document[gxns + "Tour"].Playlist.append(
        GX.FlyTo(
            GX.duration(0),
            GX.flyToMode("bounce"),
            KML.LookAt(
                KML.longitude(lon),
                KML.latitude(lat),
                KML.altitude(alt),
                KML.heading(angle),
                KML.tilt(tilt),
                KML.range(distance),
                KML.altitudeMode("relativeToGround"),
            ),
        ),
    )
    etree.Document[gxns + "Tour"].Playlist.append(GX.Wait(GX.duration(duration)))


def AddLocation(lat, lon, alt, etree, duration):
    etree.Document[gxns + "Tour"].Playlist.append(
        GX.FlyTo(
            GX.duration(0),
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
def CalculateOffsetDepricated(lat, lon, meters, verbose, max_score=-0.2):
    l = latlon.LatLon(float(lat), float(lon))

    search_space = {
        "x": np.arange(-0.1, 0.1, 0.000001),
    }

    opt_lon = RepulsingHillClimbingOptimizer(search_space)
    opt_lat = RepulsingHillClimbingOptimizer(search_space)

    def objective_lat(x):
        return abs(meters - (l.distance(latlon.LatLon(float(lat) + x["x"], float(lon))) * 1000)) * -1

    def objective_lon(x):
        return abs(meters - (l.distance(latlon.LatLon(float(lat), float(lon) + x["x"])) * 1000)) * -1

    if verbose:
        opt_lon.search(objective_function=objective_lon, n_iter=10000, max_score=max_score)
        opt_lat.search(objective_function=objective_lat, n_iter=10000, max_score=max_score)
        # opt_lon.search(objective_function=objective_lon, n_iter=10000, verbosity="print_results", max_score=-1)
        # opt_lat.search(objective_function=objective_lat, n_iter=10000, verbosity="print_results", max_score=-1)
    else:
        opt_lon.search(objective_function=objective_lon, n_iter=10000, verbosity=False, max_score=max_score)
        opt_lat.search(objective_function=objective_lat, n_iter=10000, verbosity=False, max_score=max_score)

    # print(opt_lat.best_para["x"], opt_lon.best_para["x"])
    return (abs(opt_lat.best_para["x"]), abs(opt_lon.best_para["x"]))


# unfortunately have to be globally visable because of multithreading stuff
def objective_lat(x):
    return (
        abs(
            x.pass_through["m"]
            - geopy.distance.distance(x.pass_through["o"], (x.pass_through["lat"] + x["x"], x.pass_through["lon"])).m
        )
        * -1
    )


def objective_lon(x):
    return (
        abs(
            x.pass_through["m"]
            - geopy.distance.distance(x.pass_through["o"], (x.pass_through["lat"], x.pass_through["lon"] + x["x"])).m
        )
        * -1
    )


def CalculateOffset(lat, lon, meters, verbose, max_score=-0.05):

    start_time = time.time()

    origin = (lat, lon)

    search_space = {"x": list(np.arange(-0.1, 0.1, 0.000001))}

    pass_through = {"m": meters, "o": origin, "lat": lat, "lon": lon}

    optimizer = DownhillSimplexOptimizer()
    hyper_lat = hyperactive.Hyperactive(verbosity=False)
    hyper_lon = hyperactive.Hyperactive(verbosity=False)

    hyper_lat.add_search(
        objective_function=objective_lat,
        search_space=search_space,
        n_iter=5000,
        max_score=max_score,
        n_jobs=-1,
        pass_through=pass_through,
        optimizer=optimizer,
        memory="share",
        early_stopping={"n_iter_no_change": 1000},
    )
    hyper_lat.run()

    lat_para = hyper_lat.best_para(objective_lat)
    lat_score = hyper_lat.best_score(objective_lat)

    hyper_lon.add_search(
        objective_function=objective_lon,
        search_space=search_space,
        n_iter=5000,
        max_score=max_score,
        n_jobs=-1,
        pass_through=pass_through,
        optimizer=optimizer,
        memory="share",
        early_stopping={"n_iter_no_change": 1000},
    )
    hyper_lon.run()

    lon_para = hyper_lon.best_para(objective_lon)
    lon_score = hyper_lon.best_score(objective_lon)

    if verbose:
        print(
            "Generated data:",
            "Lat: {:.4f}".format(lat_score),
            "Lon: {:.4f}".format(lon_score),
            "Time: {:.2f}".format(time.time() - start_time),
        )

    return abs(lat_para["x"]), abs(lon_para["x"])


# Wrapper on CalculateOffset. Handles recalling precomputed values & saving computed values.
def OffsetComputation(lat, lon, meters, precompute, verbose, max_score=-0.2):
    # Gets precomputed data, saves time when running script regularly
    key = str(lat) + "|" + str(lon) + "|" + str(meters)
    if precompute:
        data = shelve.open("precomputed")
        if not key in data.keys():
            if verbose:
                print("Data was not in shelve, generating data")
            offsetlat, offsetlon = CalculateOffset(float(lat), float(lon), meters, verbose, max_score)
            data[key] = {"offsetlat": str(offsetlat), "offsetlon": str(offsetlon)}
        else:
            offsetlat = data[key]["offsetlat"]
            offsetlon = data[key]["offsetlon"]
        data.close()
    else:
        if verbose:
            print("Generating Data...")
        offsetlat, offsetlon = CalculateOffset(float(lat), float(lon), meters, verbose, max_score)
        data = shelve.open("precomputed")
        data[key] = {"offsetlat": str(offsetlat), "offsetlon": str(offsetlon)}
        data.close()

    return float(offsetlat), float(offsetlon)
    # create lat and lon values


# generates all grid locations for a given origin with the format [{lat, lon, x, y}]
def GetGridLocations(lat, lon, radius, meters, precompute, verbose, debug):
    offsetlat, offsetlon = OffsetComputation(lat=lat, lon=lon, meters=meters, precompute=precompute, verbose=verbose)

    data = []
    for w in range(-radius, radius + 1):
        for h in range(-radius, radius + 1):
            adjusted_lat = w * offsetlat + float(lat)
            adjusted_lon = h * offsetlon + float(lon)
            d = {"lat": adjusted_lat, "lon": adjusted_lon, "x": w, "y": h}
            data.append(d)
            # AddLocation(lat=adjusted_lat, lon=adjusted_lon, alt=alt, etree=kml, duration=duration)
            # AddPin(lat=adjusted_lat, lon=adjusted_lon, name=str(w) + ", " + str(h), alt=alt, etree=kml)
            if debug:
                if w == radius and h == radius:
                    print(adjusted_lat, adjusted_lon)

    return data

def GetOverlappingGridLocations(lat, lon, radius, inner_radius, inner_meters, meters, precompute, verbose, debug):
    offsetlat, offsetlon = OffsetComputation(lat=lat, lon=lon, meters=meters, precompute=precompute, verbose=verbose)

    data = []
    for w in range(-radius, radius + 1):
        for h in range(-radius, radius + 1):
            adjusted_lat = w * offsetlat + float(lat)
            adjusted_lon = h * offsetlon + float(lon)
            d = {"lat": adjusted_lat, "lon": adjusted_lon, "x": w, "y": h}
            data.append(d)
            # AddLocation(lat=adjusted_lat, lon=adjusted_lon, alt=alt, etree=kml, duration=duration)
            # AddPin(lat=adjusted_lat, lon=adjusted_lon, name=str(w) + ", " + str(h), alt=alt, etree=kml)
            if debug:
                if w == radius and h == radius:
                    print(adjusted_lat, adjusted_lon)

    return data


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
