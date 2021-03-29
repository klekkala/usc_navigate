import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random
new_min = -100
new_max = 100
lat_min = 40.42524817            ## this is for first 500 in pittsburg need to generalize this for all places
lat_max = 40.44497464
long_min = -80.03468568
long_max = -79.98858816


class dataHelper:
    G = nx.Graph()
    end_points = []

    def new_lat_scale(self, x):
        normalized_new_val = ((x - lat_min) / (lat_max - lat_min) * (new_max - new_min)) + new_min
        return normalized_new_val

    def new_long_scale(self, x):
        normalized_new_val = ((x - long_min) / (long_max - long_min) * (new_max - new_min)) + new_min
        return normalized_new_val

    def image_name(self, pos):
        return self.image_names[pos]


    def build_graph(self, data):
        i = 0
        prev_route = -1
        prev_pos = (-1,-1)
        prev_name = "abc"
        x = []
        y = []
        for index, row in data.iterrows():
            route_no = row['route_no']
            lat = row['latitude']
            long = row['longitude']
            scaled_lat = self.new_lat_scale(lat)
            scaled_long = self.new_long_scale(long)
            image_name = row['image_name']
            current_node = (scaled_lat,scaled_long)
            if (image_name not in self.G):
                self.G.add_node((scaled_lat,scaled_long),image_name = image_name, latitude = lat, longitude=long, yaw =row['yaw'], )  # saves a node as image name
                print((scaled_lat,scaled_long), image_name)
                if route_no == prev_route and prev_pos!=-1:
                    print("adding edge")
                    x.append(scaled_lat)
                    y.append(scaled_long)
                    self.G.add_edge(prev_pos, current_node)   # need to add something like a direction on this edge like right left straight...

                elif route_no != prev_route:                                       ## going to a new route
                    plt.plot(x, y, '-o', linewidth=1, markersize=2)
                    if(prev_pos!= (-1,-1)):
                        self.end_points.append(prev_pos)
                    x=[]
                    y=[]


            prev_pos = current_node
            prev_route = route_no
        #save the graph as a json?
        self.image_names = nx.get_node_attributes(self.G, 'image_name')
        plt.savefig("filename5.png")


    def read_routes(self, csv_file = "../data/pittsburg_500.csv" ):
        data = pd.read_csv(csv_file, keep_default_na=False)
        self.build_graph(data)

    def find_next(self, pos, action = "next"):
        print("finds next position based on action/direction and position")
        if action == "next":
            #print(self.end_points)
            return list(self.G.nodes.data(pos))[0]

    def reset(self):
        # reset the position of the agent
        print("resets the position to a start")
        i = random.choice(range(len(self.end_points)))
        return self.end_points[i]



