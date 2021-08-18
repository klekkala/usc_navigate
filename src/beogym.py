from data_helper import DataHelper
#from agent import BeoGymAgent
import math
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
import cv2
from MplCanvas import MplCanvas

from config import *

#from stable_baselines3.common.env_checker import check_env
#from stable_baselines3.common.vec_env import DummyVecEnv
#from stable_baselines3.common.env_util import make_vec_env
#from stable_baselines3.common.evaluation import evaluate_policy

#from stable_baselines3 import PPO, A2C

import tensorflow as tf

# New design so that it fits with IMPALA:
# Agent file should only store the architecture and info about action_spaces.
# The environment file will store general information about the agent.

# The environment also needs to implement the following methods:
# 1. initial(): Return the initial observation.
# 2. step(action): take an action and return a tuple of (reward, done, observation)
# 3. _tensor_psecs(method_name, unused_kwargs, constructor_kwargs): return a nest of TensorSpec
# with the initial and step methods' output's specification.
# 4. close(): close is used in the TFProxy. Need to look at DeepmindLab to see what does close() do.


# ALSO, check to see if the seed setting works in BeoGym. If this does not work then cannot test.


# This environment will then be wrapped by the FlowEnvironment

class BeoGymEnv(gym.Env):

    def __init__(self):
        
        super(BeoGymEnv, self).__init__()
        
        self.dh = DataHelper()
        self.reset()

        # Agent information:

        self.turning_range = CONFIG_DICT["turning_range"]
        self.view_res = CONFIG_DICT["view_res"]
        
        self.observation_space = spaces.Box(low = 0, high = 255, shape = (*CONFIG_DICT["view_res"], 3), dtype= np.uint8)
        self.seed(CONFIG_DICT["seed"])

        # Settings:
        self.game = CONFIG_DICT["game"]
        self.max_steps = CONFIG_DICT["max_steps"]
        self.min_radius_meters = CONFIG_DICT["min_radius_meters"] # The radius around the goal that can be considered the goal itself.
        self.max_radius_meters = CONFIG_DICT["max_radius_meters"] # The outer radius around the goal where the rewards kicks in.
        self.min_distance_reached = CONFIG_DICT["min_distance_reached"] # The closest distance the agent has been so far to the goal.
        self.goal_reward = CONFIG_DICT["goal_reward"]
        self.curr_step = 0

        # Sample goal:
        if CONFIG_DICT["goal"] is not None:
            self.courier_goal = goal
        else:
            # Pick a random goal.
            while True:

                self.courier_goal = self.dh.sample_location()
                self.initial_distance_to_goal = self.dh.distance_to_goal(self.agent_pos_curr, self.courier_goal)

                # Make sure the goal is not within the max_radius_meters to the agent's current position. Also, the sampled goal
                # should not be the same as the agent's current position:
                if (self.initial_distance_to_goal > self.max_radius_meters and self.courier_goal != self.agent_pos_curr):
                    break

            print("Goal is None. Sampled a location as goal: ", self.courier_goal)

        # Logging: to be implemented.

    def reset(self):

        self.agent_pos_curr = self.dh.reset()
        self.agent_pos_prev = self.agent_pos_curr
        self.curr_image_name = self.dh.image_name(self.agent_pos_curr)
        print("Image name: ", self.curr_image_name)
        self.curr_angle = 0
        self.curr_view = self.dh.panorama_split(self.curr_angle, self.curr_image_name, self.view_res)

        return self.curr_view

    def initial(self):

        return self.reset()

    def go_back(self):

        print("\n")
        print("taking a step back to previous position: ", self.agent_pos_prev)
        new_pos, curr_image, new_angle = self.dh.find_nearest(self.agent_pos_curr, self.agent_pos_prev, self.curr_angle, "forward")
        self.update_agent(new_pos, curr_image, new_angle)

    def go_forward(self):

        print("\n")
        print("taking a step forwawrd from my current position: ", self.agent_pos_curr)
        new_pos, curr_image, new_angle = self.dh.find_nearest(self.agent_pos_curr, self.agent_pos_prev, self.curr_angle, "forward")
        self.update_agent(new_pos, curr_image, new_angle)

    def go_left(self):

        new_angle = self.dh.fix_angle(self.curr_angle + self.turning_range)
        curr_image = self.dh.image_name(self.agent_pos_curr)
        self.curr_angle = new_angle
        self.curr_view = self.dh.panorama_split(new_angle, curr_image)


    def go_right(self):

        new_angle = self.dh.fix_angle(self.curr_angle - self.turning_range)
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

        if action  == MOVE_LEFT:
            self.go_left()
        elif action == MOVE_RIGHT:
            self.go_right()
        elif action == MOVE_FORWARD:
            self.go_forward()
        elif action == MOVE_BACK:
            self.go_back()

    def step(self, action):

        done = False
        info = {}

        self.take_action(action)

        # Keep track of the number of steps in an episode:
        self.curr_step += 1

        if (self.curr_step >= self. max_steps):
            
            done = True
            info['time_limit_reached'] = True

        print("comparison: ", self.game == 'courier')

        # Three different type of games: https://arxiv.org/pdf/1903.01292.pdf
        if self.game == 'courier':
            reward, done = self.courier_reward_fn()
        elif self.game == 'coin':
            reward, done = self.coin_reward_fn()
        elif self.game == 'instruction':
            reward, done = self.instruction_reward_fn()

        return reward, done, self.curr_view

        # The following return tuple works with stable-baselines3
        #return self.curr_view, reward, done, info
        
    
    @staticmethod
    def _tensor_specs(method_name):
        """Returns a nest of `TensorSpec` with the method's output specification."""
        width = CONFIG_DICT["view_res"][1]
        height = CONFIG_DICT["view_res"][0]

        observation_spec = [
            tf.contrib.framework.TensorSpec([height, width, 3], tf.uint8),
            tf.contrib.framework.TensorSpec([], tf.string),
        ]

        if method_name == 'initial': # Initial returns the inital state.
            return observation_spec
        elif method_name == 'step': # Step returns a tuple of (reward, done, observation)
            return (
                tf.contrib.framework.TensorSpec([], tf.float32),
                tf.contrib.framework.TensorSpec([], tf.bool),
                observation_spec,
            )


    def render(self, mode='human'):

        self.dh.update_plot(self.agent_pos_curr, self.agent_pos_prev, self.curr_angle)

        cv2.imshow('window', self.curr_view)
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
        if self.agent_pos_curr in self.dh.visited_locations:

            return reward, found_goal

        # If distance is not None then we are in testing mode:
        if distance is None:

            distance_to_goal = self.dh.distance_to_goal(self.agent_pos_curr, self.courier_goal)

            # Add current location to visited locations list:
            self.dh.visited_locations.add(self.agent_pos_curr)

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

    def get_BEV(self):

        pass



if __name__ == "__main__":

    #agent = BeoGymAgent()
    env = BeoGymEnv()
    #check_env(env) # Checking to see if the custom env is compatible with stable-baselines3

    # Training:
    #n_envs = 4 # Number of environments
    #train_env = make_vec_env(env, n_envs= n_envs)

    # Environment for evaluation:
    #eval_eps = 100
    #eval_env = BeoGymEnv(agent, dh, goal, seed = seed)

    #n_expriments = 3 # Number of experiments.
    #train_steps = 10000

    #model = A2C('MlpPolicy', train_env, verbose = 1)

    #rewards = []

    #for experiment in range(n_expriments):
    #    train_env.reset()
    #    model.learn(total_timesteps= train_steps)
    #    mean_reward, _ = evaluate_policy(model,eval_env, n_eval_episodes=eval_eps)
    #    rewards.append(mean_reward)

    #action = env.agent.action_space.sample()
    #action = 2
    #obs, reward, done, info = env.step(action)
    #print("\n")
    #print("Reward: ", reward)
    #print("Done: ", done)
    #env.render()

    radius = [5, 10, 15, 20 , 25]

    # Testing BEV:
    for r in radius:

        graph = env.dh.bird_eye_view(env.agent.agent_pos_curr, r)

        if graph is None:
            break

        env.dh.draw_bird_eye_view(env.agent.agent_pos_curr, r, graph)
        env.render()

    # How to test reward?
    #distances = [25, 15, 10, 5, 3, 1]
    #for d in distances:
    #    print("Distance: ", d)
    #    r, d = env.courier_reward_fn(d)
    #    print("Reward: ", r)
    #    print("Done: ", d)

    env.close()
    
 