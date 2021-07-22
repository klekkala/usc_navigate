
import networkx as nx
import pandas as pd
import requests
from random import sample
import gistfile1
import matplotlib.pyplot as plt
import json

apikey = "AIzaSyA2BEmbwVbpINCm_w6PSCnysZnlJDAr7oM"
itemode = "walking"


new_min = -100
new_max = 100
#lat_min = 40.42524817
#lat_max = 40.44497464
#long_min = -80.03468568
#long_max = -79.98858816

# These functions are taken from beogym.py/streetview.py:

def new_lat_scale(x):
    normalized_new_val = ((x - lat_min) / (lat_max - lat_min) * (new_max - new_min)) + new_min
    return normalized_new_val

def new_long_scale(x):
    normalized_new_val = ((x - long_min) / (long_max - long_min) * (new_max - new_min)) + new_min
    return normalized_new_val

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


def getSteps(jsonfile):

    numberOfSteps = len(jsonfile['routes'][0]['legs'])

    steps = [jsonfile['routes'][0]['legs'][i]['steps'] for i in range(numberOfSteps)]

    return steps


def getRoute(route):

    r = sendRequest(route)

    try:
        if r.status_code == 200:

            jsonobj = json.loads(r.content)
            steps = getSteps(jsonobj)

            return steps

    except Exception as e:
        print e
        pass
    return None



# Plan:
# 1. Sampled two points and get the direction from one point to the other.
# 2. Use the functions in streetview.py to get the coordinates for every in-between points.
# 3. Add all the points into a dataframe or a list or a set. Do not add the points that is already there.
# 4. Repeat until the number of UNIQUE points converges. How??




# This function is to query the routes between random waypoints.
# Maybe store the coordinates inside a csv?
# Format: route_no, source, destination, waypoints

def create_graph_csv(list):

    #waypoints = pd.read_csv("usccampusimginfo.csv")

    #waypoints = waypoints.drop_duplicates(subset = ["lat", "lon"])

    #list = []

    #for i, row in waypoints.iterrows():

    #    lattitude = row["lat"]
    #    longitude = row["lon"]

    #    list.append((lattitude, longitude))

    # File to write down the waypoints' information:
    f = open("uscroutesinfo_expanded.csv", "w+")
    f.write("route_no,latitude,longitude\n")

    route_no = 0

    # Two for loops to make sure we don't miss any routes:
    for src in list:

        for dst in list:

            try:

                if src == dst:

                    continue

                route = "https://maps.googleapis.com/maps/api/directions/json?origin=%s,%s&destination=%s,%s&mode=%s&key=%s" % (
                    src[0],src[1], dst[0], dst[1], itemode, apikey)

                steps = getRoute(route)
                route_no += 1

                # For every route, there are multiple steps. Each steps has multiple in-between points.
                for s in steps:
                    p1 = s[0]['start_location']
                    p2 = s[0]['end_location']
                    polyline = s[0]['polyline']['points']
                    # Note that the points in the set after decode will have long, lat format instead of lat, long.
                    pts = gistfile1.decode(polyline)

                    # Add start and end location in since they were not included.
                    pts.append(( float(p1["lng"] ), float(p1["lat"])))
                    pts.append(( float(p2["lng"] ), float(p2["lat"])))

                    for pt in pts:

                        f.write("%s,%s,%s\n" % (route_no, pt[1], pt[0]))

                    print pts
                    print "This seg has %d pts" % len(pts)
                    print("\n")
                    print("Current route_no: %i" %(route_no))
                    print("\n")

            except Exception as e:
                print e
                continue
    
    print("CSV File created.\n")
    f.close()


# This function is to put the info from the graph_csv file into a networkx graph:

def build_graph(G):

    i = 0
    prev_route = -1
    prev_pos = (-1,-1)
    prev_name = "abc"
    x = []
    y = []

    data = pd.read_csv("uscroutesinfo_expanded.csv")

    global lat_max
    global lat_min
    global long_max
    global long_min

    lat_max = float(data["latitude"].max(skipna = True))
    lat_min = float(data["latitude"].min(skipna = True))
    long_max = float(data["longitude"].max(skipna = True))
    long_min = float(data["longitude"].min(skipna = True))

    print("\n")
    print("Building graph. \n")

    for i, point in data.iterrows():

        lat = point['latitude']
        long = point['longitude']
        route_no = point['route_no']

        scaled_lat = new_lat_scale(lat)
        scaled_long = new_long_scale(long)
        
        current_node = (scaled_lat,scaled_long)

        if (current_node not in G):
            G.add_node(current_node , lat = scaled_lat, long = scaled_long)  # saves a node as image name
            #print((scaled_lat,scaled_long), image_name)
            if route_no == prev_route and prev_pos != (-1,-1):
                # So the edges only connect nodes of the same route?
                #print("adding edge")
                G.add_edge(prev_pos, current_node)   # need to add something like a direction on this edge like right left straight...
                x.append(scaled_long) # What are these x, y lists for? Look at the elif below.
                y.append(scaled_lat)

            elif route_no != prev_route:

                #plt.plot(x, y, '-o', linewidth=1, markersize=2)
                plt.scatter(x, y)

                x=[]
                y=[]

        prev_pos = current_node
        prev_route = route_no

    # Save the drawn graph.
    plt.savefig("usccampusgraph_expanded.png")

# Sample num_points coordinates along the latitude and the longitude.
def sample_coordinates(data, num_points):
    
    lat_max = float(data["latitude"].max(skipna = True))
    lat_min = float(data["latitude"].min(skipna = True))
    long_max = float(data["longitude"].max(skipna = True))
    long_min = float(data["longitude"].min(skipna = True))

    lat_list = []
    long_list = []
    result = []

    for n in range(num_points + 1):

        lat_proportion = (lat_max - lat_min) / float(num_points)
        long_proportion = (long_max - long_min) / float(num_points)

        lat_list.append(lat_min + n * lat_proportion)
        long_list.append(long_min + n * long_proportion)

    for lat in lat_list:

        for long in long_list:

            result.append((lat, long))


    return result



def read_routes():

    # NOTICE: Code that was used to create uscroutesinfo.csv is lost. Hence, be careful with not changing or deleting that file.
    data = pd.read_csv("uscroutesinfo.csv", keep_default_na=False)

    # Routes: 2065 - 2150 are the error points. So filter them out.
    data = data.loc[ (data["route_no"] < 2065) | (data["route_no"] > 2150)]

    # List of incorrectly directed routes:
    list = [6561, 6647, 6733, 6819, 6905, 6991, 7163, 7249, 7335, 7421]
    # Filter them out:
    data = data.loc[~data["route_no"].isin(list)]

    # Sample the coordinates along x and y axis.
    coor_list = sample_coordinates(data, 9)

    create_graph_csv(coor_list)


def draw_graph(G):

    dict = {}

    for key, data in G.nodes(data = True):

        dict[key] = (data['long'], data['lat'])

    nx.draw(G, dict)
    plt.show()



def main():

    #read_routes()

    G = nx.Graph()
    build_graph(G)
    nx.write_graphml(G, "usccampusgraph_expanded.graphml")

    G = nx.read_graphml("usccampusgraph_expanded.graphml")

    # Graph is already drawn once in the build_graph function.
    #draw_graph(G)



if __name__ == "__main__":
    main()
