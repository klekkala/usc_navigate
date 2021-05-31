import data_helper as dh
import math



directions = {"straight":0 , "right":90 , "left":270, }
def step(direction, position):
    # takes a step from the current position in the direction specified
    # calls find_next from data_helper by passing action and position
    print("taking a step to the", direction, "from my current position", position)

def go_back(agents_pos, prev, o):
    o.panaroma_split(0, 30, o.image_name((prev)))
    return prev , o.image_name(prev)

def go_straight(agents_pos, prev, o):
    curr_angle = get_angle(agents_pos, prev)
    angle_range=(fix_angle(curr_angle-45),fix_angle(curr_angle+45))
    return find_nearest(agents_pos, angle_range, 0, o)


def go_left(agents_pos, prev, o):
    curr_angle = get_angle(agents_pos, prev)
    angle_range = (fix_angle(curr_angle +90 - 45), fix_angle(curr_angle+90 + 45))
    return find_nearest(agents_pos, angle_range, 270, o)

def go_right(agents_pos, prev, o):
    curr_angle = get_angle(agents_pos, prev)
    angle_range = (fix_angle(curr_angle -90 - 45), fix_angle(curr_angle-90 + 45))
    return find_nearest(agents_pos, angle_range, 90, o)



def fix_angle(angle):
    if angle < 0:
        angle = 360 + angle
    elif angle >= 360:
        angle = angle - 360

    return angle

def get_angle(pos_1, pos_2):
    if (pos_2[0] - pos_1[0]) != 0 :
        slope = (pos_2[1] - pos_1[1]) / (pos_2[0] - pos_1[0])
    else:
        return 0
    #print(slope)
    angle = math.degrees(math.atan(slope))
    angle = fix_angle(angle)
    return angle

def find_nearest(agents_pos_1, angle_range, orig_angle, o):
    center_angle = fix_angle(angle_range[0] + 45)        #this is an absolute angle
    min_angle = 1000
    next_pos = o.find_next(agents_pos_1)
    decision = o.find_next(agents_pos_1)[0]
    found = 0
    image_name = o.image_name(agents_pos_1)
    print("possible next actions", len(next_pos))
    for pos in next_pos:
        agents_pos = pos  # check what None is for? ( (pos), None))
        #print("agents_pos", agents_pos)
        #print("image_name", o.image_name(agents_pos))
        angle = get_angle(agents_pos_1, agents_pos)
        angle_diff = fix_angle(angle - center_angle)
        if angle_diff < min_angle and (angle > angle_range[0] and angle < angle_range[1] ):
            found = 1
            min_angle = angle
            decision = agents_pos
            image_name = o.image_name(agents_pos)
    if found == 1:
        print("found something")
        o.panaroma_split(0, 30, image_name)
        return decision, image_name
    if found == 0:
        print("not found")
        o.panaroma_split(orig_angle, 30, image_name)
        return decision, image_name



