import data_helper as dh

def reset():
    # reset the position of the agent
    print("resets the position to the start")

def step(direction, position):
    # takes a step from the current position in the direction specified
    # calls find_next from data_helper by passing action and position
    print("taking a step to the", direction, "from my current position", position )

def main():
    dh.read_routes()



if __name__ == "__main__":
    main()