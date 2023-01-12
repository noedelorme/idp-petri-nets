"""
Read a Petri Net file and create the corresponding Net object.
"""

import numpy as np
from objects.Net import *

def cleanLine(line):
    """
    Erase space, dot comma and line break from a string.
    """
    return line.replace(" ","").replace(";","").replace("\n","")

def createNet(path):
    """
    Creates a Petri net from a .lola file.

    Args:
        path: path of the .lola file

    Return:
        net: the Petri net as a Net object
    """
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
    """
    Creates a marking from a .formula file.

    Args:
        net: the corresponding Petri net
        path: path of the .formula file

    Return:
        marking: the marking as a np.array 
    """
    formula = ""
    with open(path, "r") as file:
        formula = file.read()

    formula = formula.replace("AGEF","")
    formula = formula.replace("EF","")
    formula = formula.replace("AG","")
    formula = formula.replace("\n","")
    formula = formula.strip()
    formula = formula.replace("(","")
    formula = formula.replace(")","")

    atoms = formula.split("AND")
    marking = np.zeros(net.p)
    for text in atoms:
        temp = text.replace(" ","")
        temp = temp.replace(">","")
        temp = temp.replace("<","")
        placeName = temp.split("=")[0]
        token = float(temp.split("=")[1])
        marking[net.placeIds[placeName]] = token

    return marking


def parsePetriFile(path):
    name = path
    p = 0
    t = 0
    places = []
    transitions = set()
    marking = []

    placeIds = dict()
    transitionIds = dict()

    bad_covers = []

    with open(path, "r") as file:
        file.readline() #\n
        file.readline() #Columns:
        file.readline() #\n

        line = file.readline()
        while "Transitions:" not in line:
            line = file.readline()
            while len(line.split(":"))<=1:
                line = line.replace("\t","")
                line = line.replace(" ","")
                p_name = line.split("=")[0]
                p_token = int(line.split("=")[1])
                places.append(Place(p, p_name, p_token))
                marking.append(p_token)
                placeIds[p_name] = p
                p += 1
                line = file.readline()

        line = file.readline()         
        while "bad_covers:" not in line:
            line = line.replace("\t","")
            line = line.replace(" ","")
            line = line.replace("}","")
            line = line.replace("{","")
            line = line.replace("\n","")
            content = line.split(":")
            t_name = content[0]
            preset_string = content[1].split("->")[0]
            postset_string = content[1].split("->")[1]

            inArcs = set()
            for p_string in preset_string.split(","):
                inArcs.add(InArc(places[placeIds[p_string]], 1))
            
            outArcs = set()
            for p_string in postset_string.split(","):
                outArcs.add(InArc(places[placeIds[p_string]], 1))

            transitionIds[t_name] = t
            transitions.add(Transition(t, t_name, inArcs, outArcs))
            t += 1
            line = file.readline()
    
        line = file.readline() #\n
        line = file.readline() #\n
        line = file.readline()
        while len(line)>0:
            current_cover = np.zeros(p)
            line = line.replace("\t","")
            line = line.replace(" ","")
            line = line.replace("}","")
            line = line.replace("{","")
            line = line.replace("\n","")
            for p_string in line.split(","):
                current_cover[placeIds[p_string]] = 1
            bad_covers.append(current_cover)
            line = file.readline() #\n
            line = file.readline()

    return Net(name, places, transitions, np.array(marking), placeIds, transitionIds),bad_covers