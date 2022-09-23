# Authors:
# prints results to terminal for bug finding and realtime reading


def printResults(injection ,getRawGPS1, getcurrentGlobal): 
    
    #get global positional data
    globalLat = getcurrentGlobal.lat*10**(-7)
    globalLong = getcurrentGlobal.lon*10**(-7)
   
    #get raw gps1 data
    rawLat = getRawGPS1.lat*10**(-7)
    rawLon = getRawGPS1.lon*10**(-7)
    
    #find error in injected data
    injectErrorLat = round((rawLat - injection["lat"]),7)
    injectErrorLon = round((rawLon - injection["lon"]),7)

    #print results
    printbar = "\n=============================================\n"
    
    globalResult = "Global co ordinate = " + str(round(globalLat,7)) +", " + str(round(globalLong,7))
    injectResult = "injected co ordinates = " + str(injection["lat"]) +", " + str(injection["lat"])
    injectError = "Error in tracking = " + str(injectErrorLat) + ", " + str(injectErrorLon)
    rawResult = "Raw co ordinates from GPS actual = " + str(rawLat) + ", " +str(rawLon)
    print(printbar + injectError + printbar + globalResult + printbar + injectResult + printbar + rawResult)
    