import pandas as pd
import networkx as nx
#import matplotlib.pyplot as plt

def build_graph(data):
    G = nx.Graph()
    i = 0
    prev_route = -1
    prev_node = (-1,-1)
    prev_name = "abc"
    for index, row in data.iterrows():
        route_no = row['route_no']
        lat = row['latitude']
        long = row['longitude']
        image_name = row['image_name']
        current_node = (lat, long)
        if (image_name not in G):
            G.add_node(image_name, latitude = lat, longitude=long, yaw =row['yaw'], )  # saves a node as image name
            print(image_name)
        else:
            if route_no == prev_route and prev_node!=(-1-1):
                G.add_edge(prev_name,image_name)   # need to add something like a direction on this edge like right left straight...
        prev_name = image_name
        prev_node = current_node
        prev_route = route_no
    #save the graph as a json?
    #nx.draw(G,node_size = 1)
    #plt.savefig("filename.png")

def read_routes():
    data = pd.read_csv("../data/pittsburg_500.csv", keep_default_na=False)
    build_graph(data)

def find_next(action, position):
    print("finds next position based on action/direction and position")


