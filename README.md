Beogym.py:
--------------------------------------------
Contains function that lets the agent go back and forth, left and right. Retrieve the next image the agent will be facing when the key is pressed.

step: 
TBD. Placeholder to get direction like (front, left, back, right) and position and get next step

go_back:
goes to prev position
displays previous image


go_straight:
computes current orientation using curr and prev position
finds the nearest position/image if agent were to continue straight in the same direction

go_left:
computes current orientation, finds the nearest position if agent were to turn left from current position.

go_right:
computes current orientation, finds the nearest position/image if agent were to turn right from current position

fix angle:
convert angle to 0-369 range

get _angle:
calculate angle between two positions using slope and tan function 



find_nearest:
based on the orientation and direction instructions to the agent find the next position agent can take.

Data_helper.py
--------------------------------------------

dataHelper:
class that loads the data set and saves it into a network graph.

TBD the code is specific of pittsburg first 500 csv file. Need to try it out on all datasets combined.

new_lat_scale/ new_long_scale:
normalizes the lat long to fit in -100 to 100 scale

image_name:
returns image name given a position

panaroma_split:
splits the panaroma image and displays image. 
Code for splitting panaroma used from the below git repository:
https://github.com/fuenwang/Equirec2Perspec

Following parameters need to be given in this function to split the panaroma:
FOV, theta, phi, height, width

build_graph:
reads the routes .txt file and adds nodes to the graph the way they are linked in the routes.txt
this function also saves the plot of the graph created 
and stores a dictionary that links each position to its image name for image name retrieval.

read_routes:
 reads the csv file and calls build graph function

find_next:
returns all possible next positions the agent can take from current position.

reset:
resets agent to a random start point.



Dynamic_plot.py:
--------------------------------------------

MplCanvas:
Class for creating agents dynamic movement plot.

MainWindow:
Class for pyqt interface.
1.	Handles left right up down keypress events to call respective function in beogym.py
2.	Updates curr and prev position based on the next step taken
3.	Updates plot to show the next step agent has taken
Main:
Initializes data helper object 
Reads all routes and creates a graph.
Reset position of agent to a random start point.
Takes one arbitrary step in a direction to get initial orientation.
Waits for key presses to take next step and displays images from positions reached.


**USC Campus related files:**
--------------------------------------------

usccampusimginfo.csv - Information connecting the real coordinates of the images to the image name on the Google API.

uscroutesinfo.csv - Each coordinate in usccampusimginfo.csv was used twice, once as source and another as destination in order to get these routes. The latitude and longitude columns are the points along the route. Note that most coordinates does not have images associated with it as we set the travel mode to walking and the images were taken by a van.

usccampusgraph.graphml - The graph that contains all the routes in uscroutesinfo.csv.

uscroutesinfo_expanded.csv - Similar to the above but the source and the destination for the routes are sampled from the range between min_lat, max_lat, min_long and max_long (not from the usccampusimginfo.csv). Please see the sample_coordinate function in graphmaker.py. Note that most coordinates does not have images associated with it as we set the travel mode to walking and the images were taken by a van.

usccampusgraph_expanded.graphml - The graph that contains all the routes in uscroutesinfo_expanded.csv. 

usccampusimg.7z - 7z file that contains the folder for the images. For more information regarding how the file names are formatted, look at the downloadImage function.









