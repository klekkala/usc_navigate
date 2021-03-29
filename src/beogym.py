import data_helper as dh


def step(direction, position):
    # takes a step from the current position in the direction specified
    # calls find_next from data_helper by passing action and position
    print("taking a step to the", direction, "from my current position", position )


def main():
    o = dh.dataHelper()
    o.read_routes()
    agents_pos = o.reset()
    print("image_name", o.image_name(agents_pos))
    print("agents_pos", agents_pos)
    agents_pos = o.find_next(agents_pos)[0]     #check what None is for? ( (pos), None))
    print("agents_pos",agents_pos)
    print("image_name", o.image_name(agents_pos))


if __name__ == "__main__":
    main()

