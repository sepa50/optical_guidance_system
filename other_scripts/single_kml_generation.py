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
from distutils.log import error
import enum
from fileinput import filename
from re import X
import res.kml_resources as rkml
import csv


if __name__ ==  '__main__':
    argparser = argparse.ArgumentParser(description="Create tours")

    argparser.add_argument("--lat", default=-38.049268, help="latitude", type=float)
    argparser.add_argument("--lon", default=145.194157, help="longitude", type=float)

    argparser.add_argument("--outdir", default=r"./kml", help="output location of kml files", type=str)


    argparser.add_argument("--radius", required=True, help="radius of image grid", type=int)
    argparser.add_argument("--altitude", required=True, help="height looking directly down", type=int)

    argparser.add_argument("--name", default="tour", help="filename", type=str)

    argparser.add_argument("--duration", default=10, help="time at each point", type=int)

    argparser.add_argument("--precompute", action=argparse.BooleanOptionalAction)
    argparser.add_argument("--verbose", action=argparse.BooleanOptionalAction)
    argparser.add_argument("--debug", action=argparse.BooleanOptionalAction)
    argparser.add_argument("--pins", action=argparse.BooleanOptionalAction)

    opt = argparser.parse_args()

    min_dist = opt.altitude * math.tan(30 * (math.pi/180))*2 #distance is in radius so *2 to get width
    if opt.verbose: print("Minimum ground distance calculated as: " + str(min_dist) + " Altitude: " + str(opt.altitude))

    #Creates the tour objects for pykml
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

    #widths of sat and drone images
    fudge_factor = -min_dist / 70 #min_dist is slightly too much, fudge_factor corrects
    s_width = min_dist + fudge_factor
    
    #radius of satellite images
    s_radius = opt.radius

    #Main capture area generation loop
    def CaptureArea(lat, lon):
        

        
        #determine deltaLat and deltaLon for 1m localized
        if opt.verbose: print("Calculating 1m localized offset distance")
        lat1, lon1 = rkml.OffsetComputation(lat=lat, lon=lon, meters=1, precompute=opt.precompute, verbose=opt.verbose, max_score=-0.01)

        #generate lat lon locations
        if opt.verbose: print("Calculating grid locations")
        #this generation method allows for better grouping of images, however doesn't allow for overlapping images
        s_grid_locs = rkml.GetGridLocations(lat=lat, lon=lon, radius=s_radius, meters=s_width, precompute=opt.precompute, verbose=opt.verbose, debug=opt.debug)

        cols = int(math.sqrt(len(s_grid_locs)))
        s_grid_locs_2d = np.reshape(np.array(s_grid_locs), (cols, cols))
        
        data = [["name", "lat", "lon"]]
        print(cols)
        csv_i = -(cols-1)/2
        csv_j = -(cols-1)/2

        for i, x in enumerate(s_grid_locs_2d):
            for j, y in enumerate(x):
                if (i % 3 == 0 and j % 3 == 0):
                    for oi in range(0,3):
                        for oj in range(0,3):

                            ele = s_grid_locs_2d[i+oi][j+oj]

                            rkml.AddLocation(lat=ele["lat"], lon=ele["lon"], alt=opt.altitude, etree=sat_tour, duration=opt.duration)
                            
                            data.append([str(csv_j) + "," + str(csv_i) + ".png", ele["lat"], ele["lon"]])

                            csv_i += 1
                            if csv_i > (cols-1)/2:
                                csv_i = -(cols-1)/2
                                csv_j += 1
                            
                            if opt.pins:
                                rkml.AddPin(lat=ele["lat"], lon=ele["lon"], name="S:" + str(ele["x"]) + "," + str(ele["y"]), alt=opt.altitude, etree=sat_tour)

        filename = opt.name + ".csv"

        with open(filename, 'w', newline='') as filename:
            wr = csv.writer(filename, quoting=csv.QUOTE_ALL)
            for row in data:
                wr.writerow(row)
            #wr.writerows(data)

    CaptureArea(opt.lat, opt.lon)

    #Save the kml
    if opt.verbose: print("Saving KML")
    rkml.SaveGrid(kml=sat_tour, title=opt.name, debug=opt.debug, outdir=opt.outdir)