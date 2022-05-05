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
        self.marking = []

        with open(path, "r") as file:
            lines = file.readlines()

            [self.p,self.t] = [int(x) for x in lines[0].split(" ")]
            self.marking = [int(x) for x in lines[1].split(" ")]

            self.places = [Place(i,self.marking[i]) for i in range(self.p)]

            for i in range(self.t):
                transitionId = int(lines[3 + i*4])

                inArcsTable = lines[3 + i*4+1].split(" ")
                inArcs = set()
                for inArc in inArcsTable:
                    [id,weight] = [int(x) for x in inArc.split(":")]
                    inArcs.add(InArc(self.places[id], weight))

                outArcsTable = lines[3 + i*4+2].split(" ")
                outArcs = set()
                for outArc in outArcsTable:
                    [id,weight] = [int(x) for x in outArc.split(":")]
                    outArcs.add(InArc(self.places[id], weight))

                self.transitions.add(Transition(transitionId, inArcs, outArcs))

    def print(self):
        print("Printing Petri net:", self.path)
        print("Printing places:")
        print(self.places)
        print("Printing transitions:")
        for transition in self.transitions:
            print(transition)

        
    def supportMarking(self, m):
        return set([x for x in self.places if m[x.id]>0])
    
    def supportTransitionVector(self, v):
        return set([x for x in self.transitions if v[x.id]>0])
    
    def restriction(self, m, P):
        marking = [0 for i in range(self.p)]
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

    def isFireable(self, Tp, m):
        """Decision algorithm for membership of firing set"""
        Tpp = set()
        Pp = self.supportMarking(m)
        while Tpp != Tp:
            new = False
            for t in Tp.difference(Tpp):
                if(t.preset.issubset(Pp)):
                    Tpp.add(t)
                    Pp = Pp.union(t.postset)
                    new = True
            if not new: return (False,Tpp)
        return (True,Tpp)
    
    def isFireableInv(self, Tp, m):
        """Decision algorithm for membership of firing set in inverse net"""
        Tpp = set()
        Pp = self.supportMarking(m)
        while Tpp != Tp:
            new = False
            for t in Tp.difference(Tpp):
                if(t.postset.issubset(Pp)):
                    Tpp.add(t)
                    Pp = Pp.union(t.preset)
                    new = True
            if not new: return (False,Tpp)
        return (True,Tpp)

    def isReachable(self, m):
        """Decision algorithm for reachability"""
        if m == self.marking: return True

        Tp = self.transitions

        while len(Tp)>0:
            nbsol = 0
            sol = np.zeros(self.t)
            for t in Tp:
                s = Solver()
                v = np.array([Real("v%i" % i) for i in range(self.t)])
                c1 = [v[i]>=0 for i in range(self.t)]
                c2 = [v[t.id]>0]
                CDotv = self.incidenceMatrix(Tp).dot(v)
                mMinusm0 = np.array(m)-np.array(self.marking)
                c3 = [CDotv[i] == (mMinusm0)[i] for i in range(self.t)]
                s.add(c1 + c2 + c3)
                if s.check() == sat:
                    nbsol += 1
                    model = np.array([s.model()[v[i]].as_fraction() for i in range(self.t)])
                    sol += np.array([float(x.numerator)/float(x.denominator) for x in model])
            if nbsol==0: return False
            else: sol /= nbsol

            Tp = self.supportTransitionVector(sol)
            oTpo = set()
            for t in Tp:
                oTpo.union(t.preset)
                oTpo.union(t.postset)
            
            m0oTpo = self.restriction(self.marking, oTpo)
            maxFSm0 = self.isFireable(Tp, m0oTpo)[1]
            Tp = Tp.intersection(maxFSm0)

            moTpo = self.restriction(m, oTpo)
            maxFSm0Inv = self.isFireableInv(Tp, moTpo)[1]
            Tp = Tp.intersection(maxFSm0Inv)

            if Tp == self.supportTransitionVector(sol): return True

        return False