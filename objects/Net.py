import numpy as np
from scipy.sparse import csr_matrix
from z3 import *


class Place:
    """
    Class for places.

    Attributs:
        id: id of the place
        name: name of the place
        tokens: numbe rof tokens in the place
        preset: preset of the place
        postset: postset of the place
    """

    def __init__(self, id, name, tokens):
        self.id = id
        self.name = name
        self.tokens = tokens
        self.preset = set()
        self.postset = set()
    
    def __repr__(self):
        return self.name + ":" + str(self.id) + "(" + str(self.tokens) + ")"



class InArc:
    """
    Class for incoming arcs.

    Attributs:
        weight: weight of the arc
        place: incoming place
    """

    def __init__(self, place, weight):
        self.weight = weight
        self.place = place

    def isEnabled(self, alpha):
        return self.place.tokens >= alpha*self.weight
    
    def use(self, alpha):
        self.place.tokens -= alpha*self.weight



class OutArc:
    """
    Class for outgoing arcs.

    Attributs:
        weight: weight of the arc
        place: outgoing place
    """

    def __init__(self, place, weight):
        self.weight = weight
        self.place = place
    
    def use(self, alpha):
        self.place.tokens += alpha*self.weight



class Transition:
    """
    Class for transitions.

    Attributs:
        id: id of the transition
        name: name of the transition
        preset: preset of the transition
        postset: postset of the transition
        inArcs: set of incoming arcs
        outArcs: set of outcoming arcs
    """

    def __init__(self, id, name, inArcs, outArcs):
        self.id = id
        self.name = name
        self.preset = set()
        self.postset = set()
        self.inArcs = inArcs
        self.outArcs = outArcs
        for inArc in inArcs:
            self.preset.add(inArc.place)
            inArc.place.postset.add(self)
        for outArc in outArcs:
            self.postset.add(outArc.place)
            outArc.place.preset.add(self)

    def __repr__(self):
        # line = "[" + self.name + ":" + str(self.id) + "]["
        # for inArc in self.inArcs:
        #     line += inArc.place.name + ":" + str(inArc.place.id) + "(" + str(inArc.weight) + ") "
        # line = line[:-1] + "]["
        # for outArc in self.outArcs:
        #     line += outArc.place.name + ":" + str(outArc.place.id) + "(" + str(outArc.weight) + ") "
        # line = line[:-1] + "]"
        # return line
        return self.name
    
    def fire(self, alpha):
        enabled = all(inArc.isEnabled(alpha) for inArc in self.inArcs)
        if enabled:
            for inArc in self.inArcs: inArc.use(alpha)
            for outArc in self.outArcs: outArc.use(alpha)
        return enabled



class Net:
    """
    Class for continuous Petri Net.

    Attributs:
        name: name of the Petri net
        p: number of places
        t: number of transitions
        places: array of places
        transitions: set of transitions
        marking: initial marking
        placeIds: dictionary place.name->place.id
        transitionIds: dictionary transition.name->transition.id
    """

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
        """
        Compute the support of a marking.

        Args:
            m: a marking
        
        Return:
            set: support of m (set of places)
        """
        return set([x for x in self.places if m[x.id]>0])
    
    def supportTransitionVector(self, v):
        """
        Compute the support of a transition vector.

        Args:
            v: a transition vector
        
        Return:
            set: support of v (set of transitions)
        """
        return set([x for x in self.transitions if v[x.id]>0])
    
    def restriction(self, m, P):
        """
        Restricts a marking to a set of places.

        Args:
            m: a marking
            P: a set of places
        
        Return:
            marking: marging m[P]
        """
        marking = np.zeros(self.p)
        for p in P:
            marking[p.id] = m[p.id]
        return marking
    
    def incidenceMatrix(self, Tp):
        """
        Constructs the incidence matrix in CSR format restricted 
        to a given set of transitions.

        Args:
            Tp: a set of transitions

        Return:
            C: restriction of incidence matrix to Tp
        """
        C = np.zeros((self.p,self.t))
        for t in Tp:
            for outArc in t.outArcs:
                C[outArc.place.id][t.id] += outArc.weight
            for inArc in t.inArcs:
                C[inArc.place.id][t.id] -= inArc.weight
        return csr_matrix(C)