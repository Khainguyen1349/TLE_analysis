# -*- coding: utf-8 -*-

# Copyright Colton Riedel (2019)
# License: MIT

import datetime
import urllib.request, urllib.error, urllib.parse
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv
import pymap3d as pm


def main():
    path = "LS2D.txt"

    start = input("Enter start date and time (UTC, blank=system time) " \
            + "(YYYY MM DD HH MM SS MICROS): (OPTIONAL!)")

    if start.strip() == "":
        time = datetime.datetime.utcnow()
        print("  \033[36mUsing current system time (UTC): " \
                + time.isoformat(' ') + "\033[0m")
    else:
        try:
            time = datetime.datetime.strptime(start.strip(), "%Y %m %d %H %M %S %f")
            print("  \033[36mParsed start time as: " + time.isoformat(' ') \
                    + "\033[0m")
        except:
            print("  \033[31mUnable to parse start time from: " + start)
            print("        example of suitable input: " \
                    + "2019 01 09 22 05 16 01\033[0m")
            exit(1)

    inc_field = input("Enter field to be incremented [hr, min, sec, us]: ")

    try:
        inc = int(input("Enter incrementation value: "))
    except:
        print("  \033[31mUnable to parse value\033[0m")
        exit(1)

    us_inc = inc

    if inc_field.strip() == "hr":
        us_inc = us_inc * 3.6e9

        print("  \033[36mEach time step will increase by " + str(inc) \
                + " hour(s) (" + str(us_inc) + "μs)\033[0m")
    elif inc_field.strip() == "min":
        us_inc = us_inc * 6e7

        print("  \033[36mEach time step will increase by " + str(inc) \
                + " minute(s) (" + str(us_inc) + "μs)\033[0m")
    elif inc_field.strip() == "sec":
        us_inc = us_inc * 1e6

        print("  \033[36mEach time step will increase by " + str(inc) \
                + " second(s) (" + str(us_inc) + "μs)\033[0m")
    elif inc_field.strip() == "us":
        print("  \033[36mEach time step will increase by " + str(us_inc) \
                + "μs\033[0m")
    else:
        print("  \033[31mUnable to parse time increment field\033[0m")
        exit(1)

    try:
        num_samples = int(\
                input("Enter total number of samples: "))
    except:
        print("  \033[31mUnable to parse value\033[0m")
        exit(1)
    f = open(path, "r")
    for x in f:
        if x.startswith("1 "):
            line1 = "$$" + x +"$"
             
            print ("Line1: %s" % (line1))
        elif x.startswith("2 "):
            line2 = ".." + x + "."
             
            print ("Line2: %s" % (line2))
        else:
            output_filename = x[:-5] + time.strftime("%Y_%m_%d_%H_%M_%S_%f") + \
                              "-" + str(us_inc) + "-" + str(num_samples) + ".csv"
            print("File name: " + output_filename)
    f.close()

    satellite = twoline2rv(line1, line2, wgs84)
    outfile = open(output_filename, "w")
    for i in range(num_samples):
        datestamp = time.strftime("%Y,%m,%d,%H,%M,%S.%f")

        second = float(str(time.second) + "." + str(time.microsecond))

        position, v = satellite.propagate(time.year, time.month, time.day, \
                time.hour, time.minute, second)

        position_string = ","
        if (position[0] > 0):
            position_string += " "
        position_string += str(position[0]) + ","

        while len(position_string) < 16:
            position_string += " "

        if (position[1] > 0):
            position_string += " "

        position_string += str(position[1]) + ","

        while len(position_string) < 31:
            position_string += " "

        if (position[2] > 0):
            position_string += " "

        position_string += str(position[2])
        #print("x, y, z" +": " + str(position[0]) +", "+ str(position[1]) +", "+ str(position[2]))
        x=position[0]
        y=position[1]
        z=position[2]
        

        
        ## Fabien check this!!!! using ecef2aer function 
        lat0, long0, h0 = 43.58, 7.12, 10
        az, el, srange = pm.ecef2aer(position[0]*1000, position[1]*1000, position[2]*1000, lat0, long0, h0,  None, True)
        print("az, el, srange, dist_to_earth_center: " + \
              str(az) +", " + str(el) + ", " + str(srange)+ ", " + str(abs((x**2 +y**2 + z**2))**(1/2)))
        
        outfile.write(datestamp + position_string + ", " +\
                      str(az) +", " + str(el) + ", " + str(srange)+ ", " + str(abs((x**2 +y**2 + z**2))**(1/2))+ "\n");

        time = time + datetime.timedelta(microseconds=us_inc)

    outfile.close()
main()
