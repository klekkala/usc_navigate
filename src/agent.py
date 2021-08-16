from gym import spaces
from scalable_agent.experiment import Agent
from config import *

class BeoGymAgent(Agent):

    def __init__(self):

        self.action_space = spaces.Discrete(CONFIG_DICT["num_actions"])

        super(Agent, self).__init__(CONFIG_DICT["num_actions"])

    
