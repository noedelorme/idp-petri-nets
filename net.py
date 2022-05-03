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
        self.places = []
        self.transitions = set()

        with open(path, "r") as file:
            lines = file.readlines()

            [p,t] = [int(x) for x in lines[0].split(" ")]
            self.marking = [int(x) for x in lines[1].split(" ")]

            self.places = [Place(i,self.marking[i]) for i in range(p)]

            for i in range(t):
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

        
    def support(self, m):
        return set([x for x in self.places if m[x.id]>0])

    def isFireable(self, Tp):
        """Decision algorithm for membership of firing set"""
        Tpp = set()
        Pp = self.support(self.marking)
        while Tpp != Tp:
            new = False
            for t in Tp.difference(Tpp):
                if(t.preset.issubset(Pp)):
                    Tpp.add(t)
                    Pp = Pp.union(t.postset)
                    new = True
            if not new: return (False,Tpp)
        return (True,Tpp)

    def isReachable(m):
        """Decision algorithm for reachability"""
        return False