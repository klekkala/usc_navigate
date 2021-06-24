from data_helper import dataHelper
from agent import Agent
import math
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
import cv2
from MplCanvas import MplCanvas

from stable_baselines3.common.env_checker import check_env

class BeoGym(gym.Env):

    def __init__(self, csv_file = "data/pittsburg_500.csv", turning_range = 45, view_resolution = (720, 1080)):
        
        super(BeoGym, self).__init__()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low = 0, high = 255, shape = (*view_resolution, 3), dtype= np.uint8)
        self.seed()

        # Initialize data helper:
        self.dh = dataHelper()
        self.dh.read_routes(csv_file)

        self.agent = Agent(turning_range, self.dh, view_resolution)

    def reset(self):

        return self.agent.reset()

    def step(self, action):

        if action  == 0:
            pos, curr_img_name, self.agent.curr_angle = self.agent.go_left(self.agent.agent_pos_curr, self.agent.agent_pos_prev, self.agent.curr_angle, self.agent.turning_range)
        elif action == 1:
            pos, curr_img_name, self.agent.curr_angle = self.agent.go_right(self.agent.agent_pos_curr, self.agent.agent_pos_prev, self.agent.curr_angle, self.agent.turning_range)
        elif action == 2:
            pos, curr_img_name, self.agent.curr_angle = self.agent.go_straight(self.agent.agent_pos_curr, self.agent.agent_pos_prev, self.agent.curr_angle, self.agent.turning_range)
        elif action == 3:
            pos, curr_img_name, self.agent.curr_angle = self.agent.go_back(self.agent.agent_pos_curr, self.agent.agent_pos_prev, self.agent.curr_angle, self.agent.turning_range)

        self.agent.agent_pos_prev = self.agent.agent_pos_curr
        self.agent.agent_pos_curr = pos
        self.agent.curr_view = self.dh.panorama_split(self.agent.curr_angle, curr_img_name)
        done = False

        # If reach goal then give goal reward and then done. Else, just get the reward for completing a step.
        if self.reach_goal(self.agent.curr_view):
            reward = 10
            done = True
        else:
            # Negative reward or positive?
            reward = 1

        info = {}

        return self.agent.curr_view, reward, done, info

    def render(self, mode='human'):

        self.dh.update_plot(self.agent.agent_pos_curr, self.agent.agent_pos_prev, self.agent.curr_angle)

        cv2.imshow('window', self.agent.curr_view)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Copied this from CarlaEnv
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
        
    def reach_goal(self, curr_view):
        # Detect whether the goal has been reached? 
        # What is the goal? is it just a coordinate?

        return 0

    def reward_fn(self):
        pass

if __name__ == "__main__":

    env = BeoGym()
    env.seed(1)
    check_env(env) # Checking to see if the custom env is compatible with stable-baselines3

    # Testing set actions:
    #actions = [2, 3, 3, 3, 2]
    #for action in actions:
    #    obs, reward, done, info = env.step(action)

    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    print("Obs: ", obs)
    print("Reward: ", reward)
    print("Done: ", done)
    env.dh.show_plot()
    env.render()
    print("Resetting the environment.")
    obs = env.reset()
    print("Resetted Obs: ", obs)
    env.render()
    env.close()
