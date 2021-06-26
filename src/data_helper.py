import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random
import cv2
import numpy as np
import math
from MplCanvas import MplCanvas

import Equirec2Perspec as E2P
new_min = -100
new_max = 100
lat_min = 40.42524817            ## this is for first 500 in pittsburg need to generalize this for all places
lat_max = 40.44497464
long_min = -80.03468568
long_max = -79.98858816


class dataHelper():

    def __init__(self):

        self.G = nx.Graph()
        self.end_points = []

        # Create canvas for plot rendering:
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.xdata = []
        self.ydata = []


    def new_lat_scale(self, x):
        normalized_new_val = ((x - lat_min) / (lat_max - lat_min) * (new_max - new_min)) + new_min
        return normalized_new_val

    def new_long_scale(self, x):
        normalized_new_val = ((x - long_min) / (long_max - long_min) * (new_max - new_min)) + new_min
        return normalized_new_val

    def image_name(self, pos):
        return self.image_names[pos]

    def panorama_split(self, theta, image, resolution = (720, 1080)):
        print("\n")
        print("Showing image: ", image + ".jpg")
        print("Current viewing angle: ", theta)
        print("\n")
        equ = E2P.Equirectangular("data/Pittsburgh/"+image+".jpg")  # Load equirectangular image

        #
        # FOV unit is degree
        # theta is z-axis angle(right direction is positive, left direction is negative)
        # phi is y-axis angle(up direction positive, down direction negative)
        # height and width is output image dimension
        #

        img = equ.GetPerspective(90, -theta, 0, *resolution)  # Specify parameters(FOV, theta, phi, height, width)
        #cv2.imshow('window', img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        return img


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
                if route_no == prev_route and prev_pos != (-1,-1): # Why is prev_pos only compares to one integer while it is a tuple?
                    # So the edges only connect nodes of the same route?
                    print("adding edge")
                    x.append(scaled_lat) # What are these x, y lists for? Look at the elif below.
                    y.append(scaled_long)
                    self.G.add_edge(prev_pos, current_node)   # need to add something like a direction on this edge like right left straight...

                elif route_no != prev_route:                                       ## going to a new route
                    plt.plot(x, y, '-o', linewidth=1, markersize=2) # x and y used to plot the previous route.
                    if(prev_pos!= (-1,-1)): # end_points mean the end point of each route.
                        self.end_points.append(prev_pos)
                    x=[]
                    y=[]


            prev_pos = current_node
            prev_route = route_no
        #save the graph as a json?
        self.image_names = nx.get_node_attributes(self.G, 'image_name')
        plt.savefig("filename5.png")


    def read_routes(self, csv_file = "data/pittsburg_500.csv" ):
        data = pd.read_csv(csv_file, keep_default_na=False)
        self.build_graph(data)

    def find_adjacent(self, pos, action = "next"):
        #print("Finding next position based on action/direction and position \n")
        if action == "next":
            #print(self.end_points)
            #print("Current node: \n", pos)
            #print("Adjacent nodes and edges: \n", (self.G.adj[pos])) # Finding adjacent nodes and edges to pos node.
            #adj_nodes_list = [keys for keys,value in self.G.adj[pos].items()]
            #print("Coordinate of the adjacent nodes: \n", adj_nodes_list)

            return list([keys for keys,value in self.G[pos].items()]) # Return list of keys of nodes adjacent to node with key pos. 

    def reset(self):
        # reset the position of the agent
        print("Resets the position to a start \n")
        #i = random.choice(range(len(self.end_points)))
        i = 250
        return self.end_points[i]
    
    # Function to find the distances to adjacent nodes.
    # This is used to check to see if the node found is actually the nearest node.
    def find_distances(self, pos, adj_nodes_list):

        distance_list = []

        for node in adj_nodes_list:
            distance_list.append(np.linalg.norm(np.array(pos) - np.array(node)))

        return distance_list

    def fix_angle(self, angle):

        if angle < 0: 
            angle = 360 + angle
        elif angle >= 360:
            angle = angle - 360

        return angle


    # This function should also convert from triangular to abosulute angle?
    def get_angle(self, curr, prev):
        if (curr[0] - prev[0]) != 0 :
            slope = (curr[1] - prev[1]) / (curr[0] - prev[0])
        else:
            return 0
        #print(slope)
        angle = math.degrees(math.atan(slope))
        # The direction is from the second to the fourth quadrant.
        # So angle is negative.
        if (curr[0] > prev[0] and curr[1] < prev[1]):
            angle = 360 + angle
        # Direction: from fourth to second quadrant.
        # Angle is negative.
        elif (curr[0] < prev[0] and curr[1] > prev[1]):
            angle = 180 + angle
        # Direction: from first to third.
        # Angle is positive.
        elif (curr[0] < prev[0] and curr[1] < prev[1]):
            angle = 180 + angle

        #angle = fix_angle(angle)
        return angle


    # Convention we are using: in the angle_range, the first value always represent the right boundary of the cone.
    # While the second value represent the left boundary of the cone.
    # This function return 1 if angle is in range, 0 if not.
    def angle_in_range(self, angle, angle_range):
        # This is the case where the fix_angle adjusted the angle to be only from 0 to 360.
        if angle_range[0] > angle_range[1]:
            if angle < angle_range[1] or angle > angle_range[0]:
                return 1
            else:
                return 0
        # This is the regular case:
        else:
            if angle > angle_range[0] and angle < angle_range[1]:
                return 1
            else:
                return 0


    # Note on the process of finding the nearest node:
    # My speculation:
    # 1. Find the current angle cone of the agent, which is where the agent is looking in absolute angles. 
    # 2. Then get the adjacent nodes' absolute angles. Note: adjacent is defined as being connected by an edge.
    # 3. Filter the adjacent nodes by fov cone using the abosolute angles.
    # 4. Move to the nearest node within the cone.
    # Note: Process of graph creation: Dynamic_plot.py called build_graph. Build_graph go through every line
    # of the csv file then add all the nodes. What about edges?

    def find_nearest(self, curr_pos, prev_pos,curr_angle, direction):
        print("\n")

        # This is the view angle.
        center_angle = self.fix_angle(curr_angle)

        # The search angle is based on positions. Independent of viewing angle.
        search_angle = self.get_angle(curr_pos, prev_pos)

        left_bound = self.fix_angle(search_angle+90)
        right_bound = self.fix_angle(search_angle-90)
        
        # Check the current view angle against the search angle range:
        if direction == "forward":

            if self.angle_in_range(curr_angle, (right_bound, left_bound)) :
                search_angle_range = (right_bound , left_bound)
            else:
                search_angle_range = (left_bound, right_bound)

        elif direction == "backward":

            if self.angle_in_range(curr_angle, (right_bound, left_bound)) :
                search_angle_range = (left_bound , right_bound)
            else:
                search_angle_range = (right_bound, left_bound)

        print("Current center angle: ", center_angle)
        next_pos_list = self.find_adjacent(curr_pos) # This is a list of adjacent nodes to node agents_pos_1
        decision = curr_pos
        image_name = self.image_name(curr_pos)
        print("Current node: ", curr_pos)
        print("Possible next nodes: ", len(next_pos_list))
        print("List of adjacent nodes: ", next_pos_list)
        print("Distances from current node to the adjacent nodes: ", self.find_distances(curr_pos, next_pos_list))
        print("Search angle range: ", search_angle_range)
        filtered_pos_list = []
        # Filtering the adjacent nodes by angle cone.
        for pos in next_pos_list:
            # Getting the angle between the current nodes and all adjacent nodes.
            angle = self.get_angle(pos, curr_pos)
            print("Angle from ", curr_pos,"to ", pos, "is ", angle)

            if self.angle_in_range(angle, search_angle_range):
                filtered_pos_list.append(pos)

        print("Filtered adjacent nodes list: ", filtered_pos_list)

        if (len(filtered_pos_list) == 0):

            print("\n")
            print("No nodes found. Agent standing still.")

        else:

            filtered_distances_list = self.find_distances(curr_pos, filtered_pos_list)
            print("Distances from current node to the filtered adjacent nodes: ", filtered_distances_list)
            print("Index of min value: ", (min(filtered_distances_list)))
            decision = filtered_pos_list[filtered_distances_list.index(min(filtered_distances_list))]
            print("The nearest node within the angle cone is: " , decision)
            print("Found a node within the angle cone. New node position: ", decision)
            image_name = self.image_name(decision)
            print("Showing new node's image: ", image_name)

        self.panorama_split(center_angle, image_name)
        return decision, image_name, center_angle

    # The next two functions help in the render method.
    def draw_angle_cone(self, curr_pos, angle, color = 'm'):

        x = curr_pos[0]
        y = curr_pos[1]

        angle_range = [self.fix_angle(angle - 45), self.fix_angle(angle + 45)]
        line_length = 50

        for angle in angle_range:

            end_y = y + line_length * math.sin(math.radians(angle))
            end_x = x + line_length * math.cos(math.radians(angle))

            self.canvas.axes.plot([x, end_x], [y, end_y], ':' + color )

        self.canvas.draw()

    def update_plot(self, curr_pos, prev_pos, curr_angle):

        y_prev = prev_pos[1]
        x_prev = prev_pos[0]

        y = curr_pos[1]
        x = curr_pos[0]

        self.ydata = self.ydata + [y]
        self.xdata = self.xdata + [x]

        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(self.xdata, self.ydata, '-ob')

        adj_nodes_list = [keys for keys, values in self.G.adj[(x,y)].items()]
        num_adj_nodes = len(adj_nodes_list)
        adj_nodes_list = np.array( [[x_coor, y_coor] for x_coor, y_coor in adj_nodes_list])

        x_pos_list = np.array([x] * num_adj_nodes)
        y_pos_list = np.array([y] * num_adj_nodes)

        self.canvas.axes.plot([x_pos_list,adj_nodes_list[:,0]], [y_pos_list, adj_nodes_list[:,1]], '--or')
        self.canvas.axes.plot(x, y, color = 'green', marker = 'o')
        self.canvas.axes.text(x, y, '({}, {})'.format(x, y))
        self.canvas.axes.plot(x_prev, y_prev, color = 'purple', marker = 'o')

        # Current view of the agent.
        self.draw_angle_cone(curr_pos, curr_angle, color = 'g')

        self.canvas.axes.set_xlim([new_min, new_max])
        self.canvas.axes.set_ylim([new_min, new_max])

        self.canvas.draw()

        self.canvas.show()

    def bird_eye_view(self, curr_pos, radius):

        adjacent_pos_list = self.find_adjacent(curr_pos)
        distances_list = self.find_distances(curr_pos, adjacent_pos_list)
        in_range_nodes_list = []

        for distance, pos in zip(distances_list, adjacent_pos_list):

            if distance <= radius:

                in_range_nodes_list.append(pos)

        bird_eye_graph = self.G.subgraph(in_range_nodes_list)

        return bird_eye_graph

    def draw_bird_eye_view(self, curr_pos, radius, graph):

        self.bev_graph = MplCanvas(self, width=5, height=4, dpi=100)

        nodes_list = [keys for keys, values in graph.nodes().items()]

        num_nodes = len(nodes_list)

        nodes_list = np.array([[x_coor, y_coor] for x_coor, y_coor in nodes_list])

        x = curr_pos[0]
        y = curr_pos[1]

        x_pos_list = np.array([x] * num_nodes)
        y_pos_list = np.array([y] * num_nodes)

        self.bev_graph.axes.plot([x_pos_list,nodes_list[:,0]], [y_pos_list, nodes_list[:,1]], '--or')
        self.bev_graph.axes.plot(x, y, color = 'green', marker = 'o')
        self.bev_graph.axes.text(x, y, '({}, {})'.format(x, y))
        self.bev_graph.axes.set_xlim([new_min, new_max])
        self.bev_graph.axes.set_ylim([new_min, new_max])

        # Draw a circle to see if the BEV is done correctly.
        draw_circle= plt.Circle(curr_pos, radius = radius, fill = False)
        self.bev_graph.axes.add_artist(draw_circle) 

        self.bev_graph.draw()

        self.bev_graph.show()


