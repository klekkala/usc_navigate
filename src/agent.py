
class Agent():

    def __init__(self, turning_range, data_helper, view_resolution):
        
        self.dh = data_helper
        self.turning_range = turning_range
        self.view_res = view_resolution
        self.reset()

    def reset(self):

        self.agent_pos_curr = self.dh.reset()
        self.agent_pos_prev = self.agent_pos_curr
        self.curr_image_name = self.dh.image_name(self.agent_pos_curr)
        print("Image name: ", self.curr_image_name)
        self.curr_angle = 0
        self.curr_view = self.dh.panorama_split(self.curr_angle, self.curr_image_name, self.view_res)

        return self.curr_view

        # The behaviour of go_back: go straight back but keep looking at the same angle. Similar to google maps.
    def go_back(self, agents_pos, prev, curr_angle, turning_range = 45):

        print("\n")
        print("taking a step back to previous position: ", prev)
        return self.dh.find_nearest(agents_pos, prev, curr_angle, "backward")

    def go_straight(self, agents_pos, prev, curr_angle, turning_rate = 45):

        print("\n")
        print("taking a step straight from my current position: ", agents_pos)
        return self.dh.find_nearest(agents_pos, prev, curr_angle, "forward")

    def go_left(self, agents_pos, prev, curr_angle, turning_range = 45):

        new_angle = self.dh.fix_angle(curr_angle + turning_range)
        curr_image = self.dh.image_name(agents_pos)
        self.dh.panorama_split(new_angle, curr_image)
        return agents_pos, curr_image, new_angle

    def go_right(self, agents_pos, prev, curr_angle, turning_range = 45):

        new_angle = self.dh.fix_angle(curr_angle - turning_range)
        curr_image = self.dh.image_name(agents_pos)
        self.dh.panorama_split(new_angle, curr_image)
        return agents_pos, curr_image, new_angle
