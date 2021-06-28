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

    def __init__(self, agent, data_helper, goal, game = 'courier',  max_steps = 1000, seed = None):
        
        super(BeoGym, self).__init__()
        
        self.dh = data_helper
        self.agent = agent

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low = 0, high = 255, shape = (*self.agent.view_res, 3), dtype= np.uint8)
        self.seed(seed)

        # Settings:
        self.game = 'courier'
        self.max_steps = 1000
        self.curr_step = 0
        self.min_radius_meters = 5 # The radius around the goal that can be considered the goal itself.
        self.max_radius_meters = 20 # The outer radius around the goal where the rewards kicks in.
        self.min_distance_reached = 15 # The closest distance the agent has been so far to the goal.
        self.goal_reward = 100

        # Sample goal:
        if goal is not None:
            self.courier_goal = goal
        else:
            # Pick a random goal.
            while True:

                self.courier_goal = self.dh.sample_location()
                self.initial_distance_to_goal = self.dh.distance_to_goal(self.agent.agent_pos_curr, self.courier_goal)

                # Make sure the goal is not within the max_radius_meters to the agent's current position. Also, the sampled goal
                # should not be the same as the agent's current position:
                if (self.initial_distance_to_goal > self.max_radius_meters and self.courier_goal != self.agent.agent_pos_curr):
                    break

            print("Goal is None. Sampled a location as goal: ", self.courier_goal)

    def reset(self):

        return self.agent.reset()

    def step(self, action):

        done = False

        self.agent.take_action(action)

        # Keep track of the number of steps in an episode:
        self.curr_step += 1
        if (self.curr_step == self. max_steps):
            
            done = True
        print("comparison: ", self.game == 'courier')
        # Three different type of games: https://arxiv.org/pdf/1903.01292.pdf
        if self.game == 'courier':
            reward, done = self.courier_reward_fn()
        elif self.game == 'coin':
            reward, done = self.coin_reward_fn()
        elif self.game == 'instruction':
            reward, done = self.instruction_reward_fn()

        info = {}

        return self.agent.curr_view, reward, done, info

    def render(self, mode='human'):

        self.dh.update_plot(self.agent.agent_pos_curr, self.agent.agent_pos_prev, self.agent.curr_angle)

        cv2.imshow('window', self.agent.curr_view)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Copied this from CarlaEnv
    def seed(self, seed):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    
    # Implementation will be similar to this file: https://github.com/deepmind/streetlearn/blob/master/streetlearn/python/environment/courier_game.py
    def courier_reward_fn(self, distance = None):

        reward = 0
        found_goal = False

        # Does not give reward if the agent visited old locations:
        if self.agent.agent_pos_curr in self.dh.visited_locations:

            return reward, found_goal

        # If distance is not None then we are in testing mode:
        if distance is None:

            distance_to_goal = self.dh.distance_to_goal(self.agent.agent_pos_curr, self.courier_goal)

            # Add current location to visited locations list:
            self.dh.visited_locations.add(self.agent.agent_pos_curr)

        else:
            
            distance_to_goal = distance

        # The goal is reached:
        if distance_to_goal < self.min_radius_meters:
            reward = self.goal_reward
            found_goal = True
        else:
            if distance_to_goal < self.max_radius_meters:
                print("max_radius_meters: ", self.max_radius_meters)
                print("min_distance_reached: ", self.min_distance_reached)
                # Only rewards the agent if the agent has decreased the closest distance so far to the goal:
                if distance_to_goal < self.min_distance_reached:
                    
                    # Reward is linear function to the distance to goal:
                    reward = (self.goal_reward *
                        (self.max_radius_meters - distance_to_goal) /
                        (self.max_radius_meters - self.min_radius_meters))

                    self.min_distance_reached = distance_to_goal
        
        return reward, found_goal

    def coin_reward_fn(self):
        
        pass

    def instruction_reward_fn(self):
        
        pass


if __name__ == "__main__":

    csv_file = "data/pittsburg_500.csv"
    dh = dataHelper(csv_file)
    turning_range = 45
    view_res = (720, 1080)
    agent = Agent(dh, turning_range,  view_res)
    
    seed = 1

    goal = None # Sample from dataset.

    env = BeoGym(agent, dh, goal, seed = seed)

    #check_env(env) # Checking to see if the custom env is compatible with stable-baselines3

    # Testing set actions:
    #actions = [2, 3, 3, 3, 2]
    #for action in actions:
    #    obs, reward, done, info = env.step(action)

    #action = env.action_space.sample()
    action = 2
    #obs, reward, done, info = env.step(action)
    #print("\n")
    #print("Reward: ", reward)
    #print("Done: ", done)
    env.render()

    #radius = [5, 10, 15, 20 , 25]

    # Testing BEV:
    #for r in radius:

    #    graph = env.dh.bird_eye_view(env.agent.agent_pos_curr, r)
    #    if graph is None:
    #        break
    #    env.dh.draw_bird_eye_view(env.agent.agent_pos_curr, r, graph)
    #    env.render()

    # How to test reward?
    distances = [25, 15, 10, 5, 3, 1]
    for d in distances:
        print("Distance: ", d)
        r, d = env.courier_reward_fn(d)
        print("Reward: ", r)
        print("Done: ", d)

    env.close()
    
 