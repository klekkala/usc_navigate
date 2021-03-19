import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
new_min = -100
new_max = 100
lat_min = 40.42524817            ## this is for first 500 in pittsburg need to generalize this for all places
lat_max = 40.44497464
long_min = -80.03468568
long_max = -79.98858816

def new_lat_scale(x):
    normalized_new_val = ((x - lat_min)/(lat_max-lat_min) * (new_max-new_min) )+ new_min
    return normalized_new_val

def new_long_scale(x):
    normalized_new_val = ((x - long_min)/(long_max-long_min) * (new_max-new_min) )+ new_min
    return normalized_new_val


def build_graph(data):
    G = nx.Graph()
    i = 0
    prev_route = -1
    prev_pos = -1
    prev_name = "abc"
    x = []
    y = []
    for index, row in data.iterrows():
        route_no = row['route_no']
        lat = row['latitude']
        long = row['longitude']
        scaled_lat = new_lat_scale(lat)
        scaled_long = new_long_scale(long)
        image_name = row['image_name']
        current_node = (scaled_lat,scaled_long)
        if (image_name not in G):
            G.add_node((scaled_lat,scaled_long),image_name = image_name, latitude = lat, longitude=long, yaw =row['yaw'], )  # saves a node as image name
            print((scaled_lat,scaled_long), image_name)
            if route_no == prev_route and prev_pos!=-1:
                print("adding edge")
                x.append(scaled_lat)
                y.append(scaled_long)
                G.add_edge(prev_pos, current_node)   # need to add something like a direction on this edge like right left straight...
            elif route_no != prev_route:                                       ## going to a new route
                plt.plot(x, y, '-', linewidth=1, markersize=10)
                x=[]
                y=[]


        prev_pos = current_node
        prev_route = route_no
    #save the graph as a json?
    plt.savefig("filename5.png")

    '''fig, ax = plt.subplots(figsize=(10, 10))
    nx.draw(G,node_size = 1,ax=ax)
    plt.savefig("filename5.png")'''

def read_routes():
    data = pd.read_csv("../data/pittsburg_500.csv", keep_default_na=False)
    build_graph(data)

def find_next(action, position):
    print("finds next position based on action/direction and position")


