import numpy as np
from z3 import *

class Place:
    def __init__(self, id, tokens):
        self.id = id
        self.tokens = tokens
        self.preset = set()
        self.postset = set()
    
    def __repr__(self):
        return str(self.id) + "(" + str(self.tokens) + ")"

class InArc:
    def __init__(self, place, weight):
        self.weight = weight
        self.place = place

    def isEnabled(self):
        return self.place.tokens >= self.weight
    
    def use(self):
        self.place.tokens -= self.weight

class OutArc:
    def __init__(self, place, weight):
        self.weight = weight
        self.place = place
    
    def use(self):
        self.place.tokens += self.weight

class Transition:
    def __init__(self, id, inArcs, outArcs):
        self.id = id
        self.preset = set()
        self.postset = set()
        self.inArcs = inArcs
        self.outArcs = outArcs
        for inArc in inArcs:
            self.preset.add(inArc.place)
        for outArc in outArcs:
            self.postset.add(outArc.place)

    def __repr__(self):
        line = "[" + str(self.id) + "]["
        for inArc in self.inArcs:
            line += str(inArc.place.id) + "(" + str(inArc.weight) + ") "
        line = line[:-1] + "]["
        for outArc in self.outArcs:
            line += str(outArc.place.id) + "(" + str(outArc.weight) + ") "
        line = line[:-1] + "]"
        return line
    
    def fire(self):
        enabled = all(inArc.isEnabled() for inArc in self.inArcs)
        if enabled:
            for inArc in self.inArcs: inArc.use()
            for outArc in self.outArcs: outArc.use()
        return enabled

class Net:
    def __init__(self, path):
        self.path = path
        self.p = 0
        self.t = 0
        self.places = []
        self.transitions = set()
        self.marking = np.zeros(self.p)

        with open(path, "r") as file:
            lines = file.readlines()

            [self.p,self.t] = [int(x) for x in lines[0].split(" ")]
            self.marking = np.array([float(x) for x in lines[1].split(" ")])

            self.places = [Place(i,self.marking[i]) for i in range(self.p)]

            for i in range(self.t):
                transitionId = int(lines[3 + i*4])

                inArcsTable = lines[3 + i*4+1].split(" ")
                inArcs = set()
                for inArc in inArcsTable:
                    temp = inArc.split(":")
                    id = int(temp[0])
                    weight = float(temp[1])
                    inArcs.add(InArc(self.places[id], weight))

                outArcsTable = lines[3 + i*4+2].split(" ")
                outArcs = set()
                for outArc in outArcsTable:
                    temp = outArc.split(":")
                    id = int(temp[0])
                    weight = float(temp[1])
                    outArcs.add(InArc(self.places[id], weight))

                self.transitions.add(Transition(transitionId, inArcs, outArcs))

    def print(self):
        print("------------------------------------")
        print("Petri net:", self.path)
        print("Places:")
        print(self.places)
        print("Transitions:")
        for transition in self.transitions:
            print(transition)
        print("------------------------------------")

        
    def supportMarking(self, m):
        return set([x for x in self.places if m[x.id]>0])
    
    def supportTransitionVector(self, v):
        return set([x for x in self.transitions if v[x.id]>0])
    
    def restriction(self, m, P):
        marking = np.zeros(self.p)
        for p in P:
            marking[p.id] = m[p.id]
        return marking
    
    def incidenceMatrix(self, Tp):
        C = np.zeros((self.p,self.t))
        for t in Tp:
            for outArc in t.outArcs:
                C[outArc.place.id][t.id] += outArc.weight
            for inArc in t.inArcs:
                C[inArc.place.id][t.id] -= inArc.weight
        return C