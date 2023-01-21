import networkx as nx
import pandas as pd
from PIL import Image, ImageDraw

new_min = -100
new_max = 100
#lat_min = 40.42524817
#lat_max = 40.44497464
#long_min = -80.03468568
#long_max = -79.98858816

# These functions are taken from beogym.py/streetview.py:

def new_lat_scale(x):
    normalized_new_val = ((x - lat_min) / (lat_max - lat_min) * (new_max - new_min)) + new_min
    return normalized_new_val

def new_long_scale(x):
    normalized_new_val = ((x - long_min) / (long_max - long_min) * (new_max - new_min)) + new_min
    return normalized_new_val

# Create the graph using the file of edges
def build_graph(filepath):
    global lat_max
    global lat_min
    global long_max
    global long_min

    data = pd.read_csv(filepath)
    G = nx.Graph()

    lat_max = max(float(data["lat1"].max(skipna=True)), 
                    float(data["lat2"].max(skipna=True)))
    lat_min = min(float(data["lat1"].min(skipna=True)), 
                    float(data["lat2"].min(skipna=True)))
    long_max = max(float(data["lon1"].max(skipna=True)), 
                    float(data["lon2"].max(skipna=True)))
    long_min = min(float(data["lon1"].min(skipna=True)), 
                    float(data["lon2"].min(skipna=True)))

    for i, point in data.iterrows():
        lon1 = new_long_scale(point["lon1"])
        lat1 = new_lat_scale(point["lat1"])
        lon2 = new_long_scale(point["lon2"])
        lat2 = new_lat_scale(point["lat2"])

        node1 = (lat1, lon1)
        node2 = (lat2, lon2)

        if not G.has_node(node1):
            G.add_node(node1, lat = point["lat1"], long=point["lon1"])
        if not G.has_node(node2):
            G.add_node(node2, lat = point["lat2"], long = point["lon2"])
        G.add_edge(node1, node2)

    return G

def draw_graph(G):

    dict = {}

    for key, data in G.nodes(data = True):

        dict[key] = (data['long'], data['lat'])

    nx.draw(G, dict)
    plt.show()

# Return all shortest paths between start node and every other node
def getShortestPaths(G, startNode):
    pathsTo = nx.shortest_path(G, source=startNode)
    for target in pathsTo:
        pathsTo[target] = pathsTo[target] + nx.shortest_path(G, source=target,
                                                             target=startNode)[1:]
    
    return pathsTo

def scale_to_img(lat_lon, h_w):
    """
    Conversion from latitude and longitude to the image pixels.
    It is used for drawing the GPS records on the map image.
    :param lat_lon: GPS record to draw (lat1, lon1).
    :param h_w: Size of the map image (w, h).
    :return: Tuple containing x and y coordinates to draw on map image.
    :param points: Upper-left, 
                    and lower-right GPS points of the map (lat1, lon1, lat2, lon2).
    """
    points = [34.027959, -118.291980, 34.016863, -118.278346]

    # https://gamedev.stackexchange.com/questions/33441/how-to-convert-a-number-from-one-min-max-set-to-another-min-max-set/33445
    old = (points[2], points[0])
    new = (0, h_w[1])
    y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
    old = (points[1], points[3])
    new = (0, h_w[0])
    x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
    # y must be reversed because the orientation of the image in the matplotlib.
    # image - (0, 0) in upper left corner; coordinate system - (0, 0) in lower left corner
    return int(x), h_w[1] - int(y)


def main():
    # Build graph
    filepath = "20ft_edges.csv"    
    G = build_graph(filepath)
    origCoords = {}
    for key, data in G.nodes(data = True):
        origCoords[key] = (data['lat'], data['long'])

    # TEST
    #print(new_lat_scale(34.027959), new_long_scale(-118.291980))
    #print(new_lat_scale(34.016863), new_long_scale(-118.278346))

    # Find all shortest paths from the source to every other node
    startNode = (52.92495789398822, 23.843143218917334)
    allPaths = getShortestPaths(G, startNode)
    '''
    for source in allPaths:
        count = len(allPaths[source].keys())
        if count >= 183:
            print(source)
    quit()
    '''

    # Get unions of paths
    MAX_NODES = 370
    newPaths = []
    currPath = nx.Graph()
    tsp = nx.approximation.traveling_salesman_problem
    for path in allPaths:
        # Current graph has enough nodes, so a new one is created
        if len(list(currPath.nodes)) + len(allPaths[path]) >= MAX_NODES:
            tspPath = tsp(currPath)
            tempPath = []
            for n in tspPath:
                tempPath.append(origCoords[n])
            newPaths.append(tempPath)

            currPath = nx.Graph()

        # Convert path to graph
        for node in allPaths[path]:
            if not currPath.has_node(node):
                currPath.add_node(node)
        for i in range(1, len(allPaths[path])):
            if not currPath.has_edge(allPaths[path][i - 1], allPaths[path][i]):
                currPath.add_edge(allPaths[path][i - 1], allPaths[path][i])
    # Add leftover path
    if len(list(currPath.nodes)) > 0:
        tspPath = tsp(currPath)
        tempPath = []
        for n in tspPath:
            tempPath.append(origCoords[n])
        newPaths.append(tempPath)

    '''
    for path in newPaths:
        print(len(path))
    '''

    # Plot the paths on separate maps
    count = 0
    for path in newPaths:
        image = Image.open('zoom16.png', 'r')

        scaledPts = []
        for d in newPaths[0]:
            x1, y1 = scale_to_img(d, (image.size[0], image.size[1]))
            scaledPts.append((x1, y1))

        draw = ImageDraw.Draw(image)
        draw.line(scaledPts, fill=(255, 0, 0), width=2)
        fileName = "path" + str(count) + ".png"
        count += 1
        image.save(fileName)
        quit()


if __name__ == "__main__":
    main()
