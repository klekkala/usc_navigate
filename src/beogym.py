import data_helper as dh
import math



class BeoGym():

    def __init__(self):

        self.turning_range = 45
        self.action_list = ["left", "right", "straight", "back"]

    # The behaviour of go_back: go straight back but keep looking at the same angle. Similar to google maps.
    def go_back(self, agents_pos, prev, o, curr_angle):
        print("\n")
        print("taking a step back to previous position: ", prev)
        return self.find_nearest(agents_pos, prev, curr_angle, o, "backward")

    def go_straight(self, agents_pos, prev, o, curr_angle):
        print("\n")
        print("taking a step straight from my current position: ", agents_pos)
        return self.find_nearest(agents_pos, prev, curr_angle, o, "forward")

    def go_left(self, agents_pos, prev, o, curr_angle, turning_range = 45):

        new_angle = self.fix_angle(curr_angle + turning_range)
        curr_image = o.image_name(agents_pos)
        o.panorama_split(new_angle, curr_image)
        return agents_pos, curr_image, new_angle

    def go_right(self, agents_pos, prev, o, curr_angle, turning_range = 45):
        new_angle = self.fix_angle(curr_angle - turning_range)
        curr_image = o.image_name(agents_pos)
        o.panorama_split(new_angle, curr_image)
        return agents_pos, curr_image, new_angle


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

    def find_nearest(self, curr_pos, prev_pos,curr_angle, o, direction):
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
        next_pos_list = o.find_adjacent(curr_pos) # This is a list of adjacent nodes to node agents_pos_1
        decision = curr_pos
        image_name = o.image_name(curr_pos)
        print("Current node: ", curr_pos)
        print("Possible next nodes: ", len(next_pos_list))
        print("List of adjacent nodes: ", next_pos_list)
        print("Distances from current node to the adjacent nodes: ", o.find_distances(curr_pos, next_pos_list))
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

            filtered_distances_list = o.find_distances(curr_pos, filtered_pos_list)
            print("Distances from current node to the filtered adjacent nodes: ", filtered_distances_list)
            print("Index of min value: ", (min(filtered_distances_list)))
            decision = filtered_pos_list[filtered_distances_list.index(min(filtered_distances_list))]
            print("The nearest node within the angle cone is: " , decision)
            print("Found a node within the angle cone. New node position: ", decision)
            image_name = o.image_name(decision)
            print("Showing new node's image: ", image_name)

        o.panorama_split(center_angle, image_name)
        return decision, image_name, center_angle

    def step(self, action):

        if action  == "left":
            curr_pos, curr_img, curr_angle = self.go_left()
        elif action == "right":
            curr_pos, curr_img, curr_angle = self.go_right()
        elif action == "straight":
            curr_pos, curr_img, curr_angle = self.go_straight()
        elif action == "back":
            curr_pos, curr_img, curr_angle = self.go_back()

        # Placeholders:
        obs = curr_img
        reward = 0
        done = False
        info = 0

        return obs, reward, done, info
