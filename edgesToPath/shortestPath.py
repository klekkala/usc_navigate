import networkx as nx
import pandas as pd

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
            G.add_node(node1, lat = lat1, long = lon1)
        if not G.has_node(node2):
            G.add_node(node2, lat = lat2, long = lon2)
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


def main():
    # Build graph
    filepath = "20ft_edges.csv"    
    G = build_graph(filepath)

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
            newPaths.append(tsp(currPath))
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
        newPaths.append(tsp(currPath))

    '''
    for path in newPaths:
        print(path)
    '''

if __name__ == "__main__":
    main()
