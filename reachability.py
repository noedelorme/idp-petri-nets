import numpy as np
from z3 import *
from net import Net

def isFireableDumb(net: Net, Tp, m, inv=False):
    """
    Decision algorithm for membership of firing set

    Args:
        net: the net
        Tp: the set of transitions to check
        m: a marking
        inv: True iff we check in the inverse net

    Return: 
        bool: True iff Tp is a firing set
        Tpp: the maximal firing set included in Tp
    """
    Tpp = set()
    Pp = net.supportMarking(m)
    while Tpp != Tp:
        new = False
        for t in Tp.difference(Tpp):
            if not inv:
                if(t.preset.issubset(Pp)):
                    Tpp.add(t)
                    Pp = Pp.union(t.postset)
                    new = True
            else:
                if(t.postset.issubset(Pp)):
                    Tpp.add(t)
                    Pp = Pp.union(t.preset)
                    new = True
        if not new: return (False,Tpp)
    return (True,Tpp)



def isFireable(net: Net, Tp, m, inv=False):
    """
    Decision algorithm for membership of firing set

    Args:
        net: the net
        Tp: the subset of transitions to check
        m: a marking
        inv: True iff we check in the inverse net

    Return: 
        bool: True iff Tp is a firing set
        Tpp: the maximal firing set included in Tp
    """
    Tpp = Tp.copy()
    Pp = net.supportMarking(m)
    while len(Tpp)>0:
        new = False
        removed = []
        for t in Tpp:
            if not inv:
                if(t.preset.issubset(Pp)):
                    removed.append(t)
                    Pp = Pp.union(t.postset)
                    new = True
            else:
                if(t.postset.issubset(Pp)):
                    removed.append(t)
                    Pp = Pp.union(t.preset)
                    new = True
        for t in removed: Tpp.remove(t)
        if not new: return (False,Tp.difference(Tpp))
    return (True,Tp.difference(Tpp))



def isReachable(net: Net, m):
    """
    Decision algorithm for reachability

    Args:
        net: the net
        m: the target marking

    Return: 
        bool: True iff m is reachable from net.marking
    """
    if all(m[i]==net.marking[i] for i in range(net.p)): return True

    Tp = net.transitions

    while len(Tp)>0:
        nbsol = 0
        sol = np.zeros(net.t)
        C = net.incidenceMatrix(Tp)
        for t in Tp:
            s = Solver()
            v = np.array([Real("v%i" % i) for i in range(net.t)])
            c1 = [v[i]>=0 for i in range(net.t)]
            c2 = [v[t.id]>0]
            CDotv = C.dot(v)
            mMinusm0 = m-net.marking
            c3 = [CDotv[i] == mMinusm0[i] for i in range(net.p)]
            s.add(c1 + c2 + c3)
            if s.check() == sat:
                nbsol += 1
                model = np.array([s.model()[v[i]].as_fraction() for i in range(net.t)])
                sol += np.array([float(x.numerator)/float(x.denominator) for x in model])
        if nbsol==0: return False
        else: sol /= nbsol

        Tp = net.supportTransitionVector(sol)
        oTpo = set()
        for t in Tp:
            oTpo = oTpo.union(t.preset)
            oTpo = oTpo.union(t.postset)
            
        m0oTpo = net.restriction(net.marking, oTpo)
        maxFSm0 = isFireable(net, Tp, m0oTpo)[1]
        Tp = Tp.intersection(maxFSm0)

        moTpo = net.restriction(m, oTpo)
        maxFSm = isFireable(net, Tp, moTpo, True)[1]
        Tp = Tp.intersection(maxFSm)

        if Tp == net.supportTransitionVector(sol): return True
    return False