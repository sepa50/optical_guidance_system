if __name__ ==  '__main__':
    import argparse
    import os
    import math
    from pykml import parser
    from pykml.factory import GX_ElementMaker as GX
    from pykml.factory import KML_ElementMaker as KML
    import res.file_manip_resources as rfm
    import numpy as np
    import geopy.distance
import enum
import res.kml_resources as rkml

# Get the defualt location of myplaces.kml, the file that saves the current points within google earth pro
#directory = os.getenv("APPDATA") + "\..\LocalLow\Google\GoogleEarth\myplaces.kml"
directory = r"myplaces.kml"

if __name__ ==  '__main__':
    argparser = argparse.ArgumentParser(description="Create tours")

    argparser.add_argument("--path", default=directory, help="location of kml with points", type=str)
    argparser.add_argument("--outdir", default=r"./kml", help="output location of kml files", type=str)

    argparser.add_argument("--radius", required=True, help="radius of image grid", type=int)
    argparser.add_argument("--altitude", required=True, help="height looking directly down", type=int)

    argparser.add_argument("--name", default="tour", help="filename", type=str)

    argparser.add_argument("--duration", default=10, help="time at each point", type=int)
    argparser.add_argument("--batchsize", default=5, help="kml batch size", type=int)

    argparser.add_argument("--delimiter", action=argparse.BooleanOptionalAction)

    argparser.add_argument("--precompute", action=argparse.BooleanOptionalAction)
    argparser.add_argument("--verbose", action=argparse.BooleanOptionalAction)
    argparser.add_argument("--debug", action=argparse.BooleanOptionalAction)

    opt = argparser.parse_args()

    min_dist = opt.altitude * math.tan(30 * (math.pi/180))*2 #distance is in radius so *2 to get width
    if opt.verbose: print("Minimum ground distance calculated as: " + str(min_dist) + " Altitude: " + str(opt.altitude))

    #Creates the tour objects for pykml
    def CreateTourObjects():
        sat_tour = KML.kml(
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

        drone_tour = KML.kml(
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

        return sat_tour, drone_tour

    sat_tour, drone_tour = CreateTourObjects()

    #calculates the height of the camera and the angle of the camera to capture a certain slice of land at a certain angle (2D)
    def CalculateCameraPosition(x, w, v=30):
        #outside these angles things go funky
        if (x < 67.5 or x > 67.5 + 90): 
            raise Exception("Invalid angle: " + x)

        #angles of main triangle
        al = 180 - (180 - x) - v
        ar = 180 - al - v*2

        #angles of main triangle
        al = 180 - (180 - x) - v
        ar = 180 - al - v*2

        H = -1
        if (al > 90):
            #calculate hypotenuse 
            h = math.sin(math.radians(ar)) * w / math.sin(math.radians(v*2))
            #calculate as right angle
            H = math.sin(math.radians(180 - al)) * h / math.sin(math.radians(90))
            
        elif (ar > 90):
            #calculate hypotenuse 
            h = math.sin(math.radians(al)) * w / math.sin(math.radians(v*2))
            #calculate as right angle
            H = math.sin(math.radians(180 - ar)) * h / math.sin(math.radians(90))
            
        else:
            #herons formula
            a = math.sin(math.radians(ar)) * w / math.sin(math.radians(v*2))
            b = math.sin(math.radians(al)) * w / math.sin(math.radians(v*2))
            p = (a + b + w) / 2
            area = math.sqrt(p * (p-a) * (p-b) * (p-w))
            H = 2 * (area / w)

        W = 0
        A = 180 - x - 90
        #print(A, H, x)
        if (x > 90):
            W = math.sin(math.radians(A)) * H / math.sin(math.radians(x))
        elif (x < 90):
            W = math.sin(math.radians(A)) * H / math.sin(math.radians(x))
        
        return H, A, W

    # Generates a set of camera transformations in the format {alt, deltaLat, deltaLon, direction, tilt}
    # Tour processing has major trouble with close angles, hence i don't use close angles at all here
    # Attempted good sets:
    #   [67.5, 90, 112.5] (5 images / loc)
    #   [67.5, 112.5] (4 images / loc)
    # Attempted bad sets:
    #   [67.5, 78.75, 112.5]
    #   np.arange(67.5, 90, 11.25)
    #   np.arange(70, 70-45+90+0.001, step)
    #   np.arange(67.5, 67.5-45+90+0.001, step)
    def GenerateCameraViews(width, camera_pos=[67.5, 90, 112.5]):
        datax = []
        datay = []

        for i, d in enumerate(camera_pos):
            h, a, w = CalculateCameraPosition(d, width)

            alt = h
            direction = math.atan2(w, 0)* (180 / math.pi)

            datax.append({"alt": alt, "deltaLat": 0, "deltaLon": w, "direction":direction+90, "tilt":abs(a) }) #magic direction number
            if (d != 90): #ensure 90 isn't captured twice
                datay.append({"alt": alt, "deltaLat": w, "deltaLon": 0, "direction":direction, "tilt":abs(a) }) 

        data = datax + datay
        return data

    #widths of sat and drone images
    fudge_factor = -min_dist / 70 #min_dist is slightly too much, fudge_factor corrects
    s_width = min_dist + fudge_factor
    d_width = s_width * 2

    #offset between drone images
    d_offset = s_width * 3
    
    #radius of satellite images
    s_radius = opt.radius*3 + 1

    if opt.verbose: print("Generating camera permutations")
    #Generates camera permutations for all views around a specific lat lon coordinate
    d_views = GenerateCameraViews(d_width)

    if opt.verbose: print("Generating delimiter")
    #I thought about paramatising this but frankly its not needed.
    delat = 53.344005 #53.366583
    delon = 0.217581 #0.545578
    dealt1 = 300
    dealt2 = 3000
    #delat2 = 68.79228333
    #delon2 = -39.08091389

    if opt.delimiter:
        #create delimiter tour
        delim_tour = KML.kml(
            KML.Document(
                GX.Tour(
                    KML.name("delimiter" + " Tour"),
                    GX.Playlist(),
                ),
                KML.Folder(
                    KML.name("delimiter" + " Points"),
                    id="features",
                )
            )
        )

        #add locations for capturing delimiter images
        rkml.AddLocation(lat=delat, lon=delon, alt=dealt1, etree=delim_tour, duration=10)
        rkml.AddLocation(lat=delat, lon=delon, alt=dealt2, etree=delim_tour, duration=10)

        #add pins for easy visualization
        rkml.AddPin(lat=delat, lon=delon, name="delim1", alt=dealt1, etree=delim_tour)
        rkml.AddPin(lat=delat, lon=delon, name="delim2", alt=dealt2, etree=delim_tour)

        #add overlays of colors to allow for perfect delimiters
        rkml.AddGroundOverlays(lat=delat, lon=delon, alt=dealt1-200, image_path=r".\kml\img\red.png", radius=s_width, tree=delim_tour, verbose=opt.verbose)
        rkml.AddGroundOverlays(lat=delat, lon=delon, alt=dealt2-1000, image_path=r".\kml\img\white.png", radius=s_width, tree=delim_tour, verbose=opt.verbose)

        #save delimiter tour
        rkml.SaveGrid(kml=delim_tour, title="delimiter", debug=opt.debug, outdir=opt.outdir)

    def AddLocationDelimiter(tour):
        rkml.AddLocation(lat=delat, lon=delon, alt=dealt1, etree=tour, duration=opt.duration)

    def AddCaptureAreaDelimiter(tour):
        rkml.AddLocation(lat=delat, lon=delon, alt=dealt2, etree=tour, duration=opt.duration)

    #Main capture area generation loop
    def CaptureArea(lat, lon):
        #determine deltaLat and deltaLon for 1m localized
        if opt.verbose: print("Calculating 1m localized offset distance")
        lat1, lon1 = rkml.OffsetComputation(lat=lat, lon=lon, meters=1, precompute=opt.precompute, verbose=opt.verbose, max_score=-0.01)

        #generate lat lon locations
        if opt.verbose: print("Calculating grid locations")
        s_grid_locs = rkml.GetGridLocations(lat=lat, lon=lon, radius=s_radius, meters=s_width, precompute=opt.precompute, verbose=opt.verbose, debug=opt.debug)
        d_grid_locs = rkml.GetGridLocations(lat=lat, lon=lon, radius=opt.radius, meters=d_offset, precompute=opt.precompute, verbose=opt.verbose, debug=opt.debug)

        #for each location within the generated locations
        if opt.verbose: print("Generating tour locations at each grid location")
        for g in d_grid_locs:
            for v in d_views:
                rkml.AddLocationComplex(lat=g["lat"]+v["deltaLat"]*lat1, lon=g["lon"]+v["deltaLon"]*lon1, angle=v["direction"]+90, tilt=v["tilt"], distance=0, alt=v["alt"], etree=drone_tour, duration=opt.duration)
            rkml.AddPin(lat=g["lat"], lon=g["lon"], name="D:"+str(g["x"]) + "," + str(g["y"]), alt=opt.altitude, etree=drone_tour)
            AddLocationDelimiter(drone_tour)

        cols = int(math.sqrt(len(s_grid_locs)))
        s_grid_locs_2d = np.reshape(np.array(s_grid_locs), (cols, cols))

        #this generation method allows for better grouping of images
        for i, x in enumerate(s_grid_locs_2d):
            for j, y in enumerate(x):
                if (i % 3 == 0 and j % 3 == 0):
                    for oi in range(0,3):
                        for oj in range(0,3):

                            ele = s_grid_locs_2d[i+oi][j+oj]

                            rkml.AddLocation(lat=ele["lat"], lon=ele["lon"], alt=opt.altitude, etree=sat_tour, duration=opt.duration)
                            rkml.AddPin(lat=ele["lat"], lon=ele["lon"], name="S:" + str(ele["x"]) + "," + str(ele["y"]), alt=opt.altitude, etree=sat_tour)

                    AddLocationDelimiter(sat_tour)

        #simple non-delimited sat generation loop
        # for s in s_grid_locs:
        #     rkml.AddLocation(lat=s["lat"], lon=s["lon"], alt=opt.altitude, etree=sat_tour, duration=opt.duration)
        #     rkml.AddPin(lat=s["lat"], lon=s["lon"], name="S:" + str(s["x"]) + "," + str(s["y"]), alt=opt.altitude, etree=sat_tour)

        AddCaptureAreaDelimiter(drone_tour)
        AddCaptureAreaDelimiter(sat_tour)

    #Load data from file
    with open(opt.path) as f:
        doc = parser.parse(f)
        root = doc.getroot()

    #Collect locations from an input file and ensure there is no overlap
    if opt.verbose: print("Loading and checking coordinates")
    locations = []
    for i, coordinate_str in enumerate(doc.findall(".//{*}coordinates")):
        coordinate_array = str(coordinate_str).split(",")
        lat = coordinate_array[1]
        lon = coordinate_array[0]

        data_point = (lat,lon)

        for l in locations:
            #diagonal distance to furthest point in capture area
            safe_distance = math.sqrt(((s_radius * s_width - s_width*0.5)**2)*2)

            if geopy.distance.distance(l, data_point).m <= safe_distance:
                raise Exception("Point " + str(i) + " is within safe distance of another point")

        locations.append(data_point)
    
    if opt.verbose: print("Performing capture area generation")
    for i, loc in enumerate(locations):
        #perform capture area batching
        if (i % opt.batchsize == 0 and i != 0):
            j = math.ceil(i / opt.batchsize)

            rkml.SaveGrid(kml=sat_tour, title=opt.name + "-sat" + str(j), debug=opt.debug, outdir=opt.outdir)
            rkml.SaveGrid(kml=drone_tour, title=opt.name + "-drone" + str(j), debug=opt.debug, outdir=opt.outdir)

            #resets the tours
            sat_tour, drone_tour = CreateTourObjects()

        lat = loc[0]
        lon = loc[1]

        if opt.verbose: print("Generating Capture Area " + str(i))

        #Add a capture area's points to the path
        CaptureArea(lat, lon)

    if opt.verbose:
        print("Generated " + str(len(locations)) + " Capture Areas")
        print("Drone Expected Images: " + str((opt.radius*2+1)**2 * len(d_views)))
        print("Sat Expected Images: " + str((s_radius*2+1)**2))

    #Save the kml
    if opt.verbose: print("Saving KML")
    rkml.SaveGrid(kml=sat_tour, title=opt.name + "-sat" + str(math.ceil(len(locations) / opt.batchsize)), debug=opt.debug, outdir=opt.outdir)
    rkml.SaveGrid(kml=drone_tour, title=opt.name + "-drone" + str(math.ceil(len(locations) / opt.batchsize)), debug=opt.debug, outdir=opt.outdir)