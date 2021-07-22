import json
from IPython import embed

with open("usccampusdata.json", "r") as f:

    jsonobj = json.load(f)


def getSteps(jsonfile):

    numberOfSteps = len(jsonobj['routes'][0]['legs'])

    steps = [jsonobj['routes'][0]['legs'][i]['steps'] for i in range(numberOfSteps)]

    return steps

steps = getSteps(jsonobj)

embed()
