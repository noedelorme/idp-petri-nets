import numpy as np
from scipy.sparse import csr_matrix
from z3 import *

class Place:
    def __init__(self, id, name, tokens):
        self.id = id
        self.name = name
        self.tokens = tokens
        self.preset = set()
        self.postset = set()
    
    def __repr__(self):
        return self.name + ":" + str(self.id) + "(" + str(self.tokens) + ")"

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
    def __init__(self, id, name, inArcs, outArcs):
        self.id = id
        self.name = name
        self.preset = set()
        self.postset = set()
        self.inArcs = inArcs
        self.outArcs = outArcs
        for inArc in inArcs:
            self.preset.add(inArc.place)
        for outArc in outArcs:
            self.postset.add(outArc.place)

    def __repr__(self):
        line = "[" + self.name + ":" + str(self.id) + "]["
        for inArc in self.inArcs:
            line += inArc.place.name + ":" + str(inArc.place.id) + "(" + str(inArc.weight) + ") "
        line = line[:-1] + "]["
        for outArc in self.outArcs:
            line += outArc.place.name + ":" + str(outArc.place.id) + "(" + str(outArc.weight) + ") "
        line = line[:-1] + "]"
        return line
    
    def fire(self):
        enabled = all(inArc.isEnabled() for inArc in self.inArcs)
        if enabled:
            for inArc in self.inArcs: inArc.use()
            for outArc in self.outArcs: outArc.use()
        return enabled

class Net:
    def __init__(self, name, places, transitions, marking, placeIds, transitionIds):
        self.name = name
        self.p = len(places)
        self.t = len(transitions)
        self.places = places
        self.transitions = transitions
        self.marking = marking
        self.placeIds = placeIds
        self.transitionIds = transitionIds

    def print(self):
        print("------------------------------------")
        print("Petri net:", self.name)
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
        return csr_matrix(C)