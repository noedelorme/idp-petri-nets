# Read a Petri Net file and create the corresponding Net object.

import numpy as np
from objects.Net import *

def cleanLine(line):
    return line.replace(" ","").replace(";","").replace("\n","")

def createNet(path):
    name = path
    p = 0
    t = 0
    places = []
    transitions = set()
    marking = np.zeros(p)

    placeIds = dict()
    transitionIds = dict()

    with open(path, "r") as file:
        file.readline() #PLACE

        placeNames = cleanLine(file.readline()).split(",")
        p = len(placeNames)
        for i in range(p):
            placeIds[placeNames[i]] = i
        
        file.readline() #\n
        file.readline() #MARKING

        placeTokens = cleanLine(file.readline()).split(",")
        marking = np.zeros(p)
        for text in placeTokens:
            placeName = text.split(":")[0]
            token = float(text.split(":")[1])
            marking[placeIds[placeName]] = token
        
        places = [Place(placeIds[placeName], placeName, marking[placeIds[placeName]]) for placeName in placeNames]
        
        file.readline() #\n

        transitionLines = file.readlines()
        transitionLines = [line for line in transitionLines if line != "\n"]

        t = int(len(transitionLines)/3)
        for i in range(t):
            transitionName = cleanLine(transitionLines[3*i][11:])
            consume = cleanLine(transitionLines[3*i+1][8:]).split(",")
            produce = cleanLine(transitionLines[3*i+2][8:]).split(",")

            inArcs = set()
            for text in consume:
                if len(text)>0:
                    placeName = text.split(":")[0]
                    weight = float(text.split(":")[1])
                    inArcs.add(InArc(places[placeIds[placeName]], weight))

            outArcs = set()
            for text in produce:
                if len(text)>0:
                    placeName = text.split(":")[0]
                    weight = float(text.split(":")[1])
                    outArcs.add(OutArc(places[placeIds[placeName]], weight))
            
            transitionIds[transitionName] = i
            transitions.add(Transition(i, transitionName, inArcs, outArcs))


    return Net(name, places, transitions, marking, placeIds, transitionIds)

def createMarking(net, path):
    formula = ""
    with open(path, "r") as file:
        formula = file.read()

    formula = formula.replace("EF","")
    formula = formula.replace("\n","")
    formula = formula.strip()
    formula = formula.replace("(","")
    formula = formula.replace(")","")

    atoms = formula.split(" AND ")
    marking = np.zeros(net.p)
    for text in atoms:
        temp = text.replace(" ","")
        placeName = temp.split("=")[0]
        token = float(temp.split("=")[1])
        marking[net.placeIds[placeName]] = token

    return marking