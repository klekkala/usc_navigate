
class Agent():

    def __init__(self, data_helper, turning_range, view_resolution):
        
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
    def go_back(self):

        print("\n")
        print("taking a step back to previous position: ", self.agent_pos_prev)
        new_pos, curr_image, new_angle = self.dh.find_nearest(self.agent_pos_curr, self.agent_pos_prev, self.curr_angle, "forward")
        self.update_agent(new_pos, curr_image, new_angle)

    def go_straight(self):

        print("\n")
        print("taking a step straight from my current position: ", self.agent_pos_curr)
        new_pos, curr_image, new_angle = self.dh.find_nearest(self.agent_pos_curr, self.agent_pos_prev, self.curr_angle, "forward")
        self.update_agent(new_pos, curr_image, new_angle)

    def go_left(self):

        new_angle = self.dh.fix_angle(curr_angle + turning_range)
        curr_image = self.dh.image_name(self.agent_pos_curr)
        self.curr_angle = new_angle
        self.curr_view = self.dh.panorama_split(new_angle, curr_image)


    def go_right(self):

        new_angle = self.dh.fix_angle(curr_angle - turning_range)
        curr_image = self.dh.image_name(self.agent_pos_curr)
        self.curr_angle = new_angle
        self.curr_view = self.dh.panorama_split(new_angle, curr_image)


    # Update the current status of the agent:
    def update_agent(self, new_pos, curr_image, new_angle):

        self.agent_pos_prev = self.agent_pos_curr
        self.agent_pos_curr = new_pos
        self.curr_angle = new_angle
        self.curr_view = self.dh.panorama_split(self.curr_angle, curr_image)

    def take_action(self, action):

        if action  == 0:
            self.go_left()
        elif action == 1:
            self.go_right()
        elif action == 2:
            self.go_straight()
        elif action == 3:
            self.go_back()