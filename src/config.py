MOVE_LEFT = 0
MOVE_RIGHT = 1
MOVE_FORWARD = 2
MOVE_BACK = 3

ACTION_LIST = [MOVE_LEFT, MOVE_RIGHT, MOVE_FORWARD, MOVE_BACK]

CONFIG_DICT = {
    "csv_file": "data/pittsburgh_valid_v1_100s_5wp_2500m_routes.csv",
    "action_list" : ACTION_LIST,
    "num_actions":len(ACTION_LIST),
    "view_res": (720, 1080),
    "turning_range": 45,
    "seed": 1,
    "goal": None,
    "game": "courier",
    "max_steps": 1000,
    "min_radius_meters" : 5, # The radius around the goal that can be considered the goal itself.
    "max_radius_meters" : 20, # The outer radius around the goal where the rewards kicks in.
    "min_distance_reached" : 15, # The closest distance the agent has been so far to the goal.
    "goal_reward" : 100

}