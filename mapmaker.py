
import matplotlib.pyplot as plt
import pandas as pd
import numpy
import requests
#import cv2
from PIL import Image, ImageOps, ImageChops
from io import BytesIO
import os

apikey = "AIzaSyA2BEmbwVbpINCm_w6PSCnysZnlJDAr7oM"


# These functions are taken from streetview.py:
def sendRequest(url, to=15):
    r = False
    try:
        r = requests.get(url, timeout=to)
    except requests.exceptions.Timeout:
        aioClientLog.info("Connection Timout")
    except requests.exceptions.TooManyRedirects:
        aioClientLog.info("Connection TooManyRedirects")
    except requests.exceptions.RequestException as e:
        #aioClientLog.debug("Connection Fail")
        #print e
        return r
    except Exception as e:
        aioClientLog.exception(e)
        return r

    return r

def getImage(url):
    cvImage = None
    r = sendRequest(url)
    try:
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content))
            #cvImage = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
            return img
    except IOError as e:
        print("IO Error")
        print(e)
    except AttributeError as e:
        print("Error")
        print(e)
    except Exception as e:
        print(e)

    print("Error. Printing status code of the request:\n")
    print(r.status_code)
    return cvImage

def getSteps(jsonfile):

    numberOfSteps = len(jsonfile['routes'][0]['legs'])

    steps = [jsonfile['routes'][0]['legs'][i]['steps'] for i in range(numberOfSteps)]

    return steps

# These function are taken from beogym.py:
def new_lat_scale(x, lat_min, lat_max, new_lat_min, new_lat_max):
    normalized_new_val = ((x - lat_min) / (lat_max - lat_min) * (new_lat_max - new_lat_min)) + new_lat_min
    return normalized_new_val


def new_long_scale(x, long_min, long_max, new_long_min, new_long_max):
    normalized_new_val = ((x - long_min) / (long_max - long_min) * (new_long_max - new_long_min)) + new_long_min
    return normalized_new_val


##############################################################

# This function is to display a map and then allow the user to click and then get the
# coordinate of the click into a csv file.
def getGraph(filename):

    if os.path.isfile("%s.csv" % filename):
        ans = input("File %s.csv already exists. Please either change the name to create a new file or continue to write to the old file. Continute to write to the old file? (y/n)" % (
            filename
        ))
        if ans == "n" or ans == "N":
            print("Returning from function. \n")
            return
        elif ans == "y" or ans == "Y":
            pass


    plt.figure(figsize=[6.4, 6.4], dpi= 200)
    #plt.figure(figsize=[4.096, 4.096], dpi = 1000)

    mapImage = plt.imread("uscmaps/zoom16.png")
    plt.imshow(mapImage[::-1], origin="lower")
    
    #plt.show()

    #plt.scatter(x,y)meanLat
    #plt.axis("off")

    points = plt.ginput(4, timeout = 0, show_clicks = True)


    with open("%s.csv" % filename, "w") as f:
        # Check to see if the file is empty. Only write the header if it is.
        if os.stat("%s.csv" % filename).st_size == 0:
            f.write("lon,lat\n")

        for point in points:
            f.write("%f,%f\n" % (point[0], point[1]))
            print("Point (%f,%f) recorded.\n" % (point[0], point[1]))
        

# Getting maps of USC at different zoom levels then save them:
def getMaps():

    location = "University+Of+Southern+California,Los+Angeles,CA"
    zoom_levels = [13,14,15,16]
    size = "640x640" # This is the max res.
    scale = "2" # This is the max scale.
    form = "png32"

    for zoom in zoom_levels:

        url = "https://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=%i&size=%s&scale=%s&format=%s&key=%s" % (
            location, zoom, size, scale, form, apikey
        )

        image = getImage(url)

        if image is None:
            print("Image is None. Check the request.")
            return

        image.save("uscmaps/zoom%i.png" % (zoom))

# This function zoom in at the middle of an image but still keeping the same size.
def zoomIn(image, scale):

    width, height = image.size
    center = width / 2
    left = center - width / (scale * 2)
    top = center - height / (scale * 2)
    right = width - left
    bottom = height - top

    image = image.crop((left, top, right, bottom))

    return image.resize((width, height))

# This is to overlay the two images.
def overlay(zoomScale, leftShift, bottomShift):

    # The map of USC:
    background = Image.open("uscmaps/zoom16.png")
    #foreground = Image.open("usccampusgraph_expanded_v2.png")
    # Foreground should be transparent.
    foreground = Image.open("usccampusgraph_manual.png")

    width, height = foreground.size
    # Foreground and background resolution: 1280x1280
    #left = 240
    #top = 200
    #right = 1280
    #bottom = 1280

    #foreground = foreground.crop((left, top, right, bottom))
    #foreground = foreground.resize((width, height))

    foreground = zoomIn(foreground, zoomScale)
    foreground = ImageChops.offset(foreground, leftShift, bottomShift)

    blend = Image.alpha_composite(background, foreground)
    blend.save("uscmaps/blended.png", "PNG")

# This function is to process the data gathered using the directions API: 
def processData():

    graph1 = pd.read_csv("uscroutesinfo.csv")

    # Routes: 2065 - 2150 are the error points. So filter them out.
    graph1 = graph1.loc[ (graph1["route_no"] < 2065) | (graph1["route_no"] > 2150)]

    # List of incorrectly directed routes:
    list = [6561, 6647, 6733, 6819, 6905, 6991, 7163, 7249, 7335, 7421]
    # Filter them out:
    graph1 = graph1.loc[~graph1["route_no"].isin(list)]

    graph2 = pd.read_csv("usccampusimginfov4.csv")

    graph1 = graph1[graph1["latitude"] != "None"]
    graph2 = graph2[graph2["lat"] != "None"]

    graph1 = graph1.drop_duplicates(subset = ["latitude", "longitude"])
    graph2 = graph2.drop_duplicates(subset = ["lat", "lon"])

    y = graph1["latitude"].append(graph2["lat"], ignore_index = True)
    x = graph1["longitude"].append(graph2["lon"], ignore_index = True)

    y = y.astype("float64")
    x = x.astype("float64")

    final = pd.concat([x, y], axis = 1)
    final.to_csv("usccampusgraph_final.csv", header = ["lon", "lat"])


# This function attempts to convert the coordinates of the manually inputted points 
# in the usccampusgraph_manual to the scale in the usccampusgraph_final.
# Then the coordinates is plotted in usccampusgraph_manual.png
def convertCoordinates(longScaleParam, latScaleParam):

    toCoordinate  = pd.read_csv("usccampusgraph_final.csv")
    fromCoordinate = pd.read_csv("usccampusgraph_manual.csv")

    xTo = toCoordinate["lon"]
    yTo = toCoordinate["lat"]

    yTo = yTo.astype("float64")
    xTo = xTo.astype("float64")

    new_long_max = numpy.max(xTo)
    new_long_min = numpy.min(xTo)
    new_lat_max = numpy.max(yTo)
    new_lat_min = numpy.min(yTo)

    #meanLatTo = numpy.mean(yTo)
    #meanLonTo = numpy.mean(xTo)

    xFrom = fromCoordinate["lon"]
    yFrom = fromCoordinate["lat"]

    xFrom = xFrom.astype("float64")
    yFrom = yFrom.astype("float64")

    long_max = numpy.max(xFrom)
    long_max = long_max * longScaleParam
    long_min = numpy.min(xFrom)
    lat_max = numpy.max(yFrom)
    lat_max = lat_max * latScaleParam
    lat_min = numpy.min(yFrom)

    convertedX = numpy.zeros(len(xFrom))
    convertedY = numpy.zeros(len(yFrom))

    #xFrom = xFrom.apply(new_long_scale)
    #yFrom = yFrom.apply(new_lat_scale)

    for i in range(len(xFrom)):
        
        convertedX[i] = new_long_scale(xFrom[i], long_min, long_max, new_long_min, new_long_max)
        convertedY[i] = new_lat_scale(yFrom[i], lat_min, lat_max, new_lat_min, new_lat_max)


    # Save the converted coordinates into usccampusgraph_manual_converted.csv
    d = {"long": convertedX, "lat": convertedY}
    df = pd.DataFrame(data=d)
    df.to_csv("usccampusgraph_manual_converted.csv")

    
    # Plot the graph
    plt.figure(figsize=[6.4, 6.4], dpi= 200)
    plt.scatter(xTo, yTo, color="r", s=2)
    axes = plt.gca()
    # Get the range of the axes in the plot of usccampusgraph_final:
    y_min, y_max = axes.get_ylim()
    x_min, x_max = axes.get_xlim()
    #plt.savefig("test.png")
    plt.clf()

    plt.scatter(convertedX, convertedY, s= 2)
    # The range of the usccampusgraph_final is used to plot usccampusgraph_manual
    # for consistency in the visuals.
    plt.ylim([y_min, y_max])
    plt.xlim([x_min, x_max])
    plt.axis("off")
    plt.savefig("usccampusgraph_manual.png", transparent = True)
    plt.show()

def main():

    # ProcessData is already called so no need to call again.
    #processData()

    # GetMaps is already called so no need to call again.
    #getMaps()

    # The three following functions can and should be execute multiple times as follows:
    # 1. Call ONLY getGraph first in order to manually click on the map and get the matplotlib coordinates.
    # 2. Then comment out the getGraph function and the uncomment the convertCoordinates() and overlay()
    # 3. Then repeatedly adjust the parameters for convertCoordinates and overlay in order to make 
    # the scaling fit.

    filename = "usccampusgraph_manual"
    #getGraph(filename)
    # IMPORTANT: Adjust these parameters to adjust the scaling,
    longScaleParam = 1.02
    latScaleParam = 1.29
    convertCoordinates(longScaleParam, latScaleParam)

    #Manually adjust these parameters so that the graph can overlay perfectly on top of the map.
    zoomScale = 1.21 # Zoom levels of the foreground, which are dots in this case.
    leftShift = -75 # Shift image to the left.
    bottomShift = -100 # Shift image down.
    overlay(zoomScale, leftShift, bottomShift)


if __name__ == "__main__":
    main()



