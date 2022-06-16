from math import *
import numpy as np
from scipy.sparse import csr_matrix
import time
from z3 import *
from tasks.utilities import *
from objects.Net import Net
from objects.Formula import Formula, Clause, Atom


def largestSiphon(net: Net, Up, msrc):
    """
    Find the largest siphon Q of N_Up such that msrc(Q)=0.
    
    Args:
        net: the Petri net
        Up: a subset of transitions
        msrc: the source marking

    Return:
        Q: the largest siphon of N_Up such that msrc(Q)=0
        vectQ: the vector corresponding to Q
    """
    vectQ = np.int64(msrc==0)
    vectQo = np.zeros(net.t)
    # compute Q° as a transition vector
    for i in range(len(vectQ)):
        if vectQ[i]==1:
            for t in net.places[i].postset:
                if t in Up:
                    vectQo[t.id] += 1

    # while there is p in vectQ s.t. some t in °p is not in Q°
    flag = True
    while flag:
        flag = False
        for i in range(net.p):
            breakFirstLoop = False
            if vectQ[i]==1:
                for t in net.places[i].preset:
                    if vectQo[t.id]==0:
                        # then we remove p and update Q°
                        vectQ[i] = 0
                        for u in net.places[i].postset:
                            vectQo[u.id] = max(0,vectQo[u.id]-1)
                        flag = True
                        breakFirstLoop = True
                        break
            if breakFirstLoop: break
    
    return vectQ



def largestTrap(net: Net, Up, mtgt):
    """
    Find the largest trap R of N_Up such that mtgt(R)=0.
    
    Args:
        net: the Petri net
        Up: a subset of transitions
        mtgt: the target marking

    Return:
        R: the largest trap of N_Up such that mtgt(Q)=0
        vectR: the vector corresponding to R
    """
    vectR = np.int64(mtgt==0)
    vectoR = np.zeros(net.t)
    # compute °Q as a transition vector
    for i in range(len(vectR)):
        if vectR[i]==1:
            for t in net.places[i].preset:
                if t in Up:
                    vectoR[t.id] += 1

    # while there is p in vectR s.t. some t in p° is not in °Q
    flag = True
    while flag:
        flag = False
        for i in range(net.p):
            breakFirstLoop = False
            if vectR[i]==1:
                for t in net.places[i].postset:
                    if vectoR[t.id]==0:
                        # then we remove p and update °Q
                        vectR[i] = 0
                        for u in net.places[i].preset:
                            vectoR[u.id] = max(0,vectoR[u.id]-1)
                        flag = True
                        breakFirstLoop = True
                        break
            if breakFirstLoop: break
    
    return vectR



def locallyClosedBiSeparator(net: Net, U, msrc, mtgt):
    """
    Constructs a locally closed bi-separator for (msrc,mtgt) given 
    that mtgt is not reachable from msrc using transitions in U.

    Args:
        net: the Petri net
        U: a subset of transitions
        msrc: the source marking
        mtgt: the target marking

    Return:
        bisep: a bi-separator for (msrc,mtgt)
    """
    if len(U)==0:
        p = 0
        while msrc[p]==mtgt[p] and p<net.p: p+=1
        assert p>=net.p, "Error: msrc=mtgt"
        a = np.zeros(net.p)
        a[p] = copysign(1,msrc[p]-mtgt[p])

        return Formula(Clause([Atom(a,a)]))
    
    b = mtgt - msrc

    X = Solver()
    x = np.array([Real("x%i" % i) for i in range(net.t)])
    F = net.incidenceMatrix(net.transitions)
    FDotx = sparseDot(F, x)
    matrixCstrt = [FDotx[i] == b[i] for i in range(net.p)]
    vectU = transitionSetToVector(net, U)
    inclusionCstrt = [Or(x[i]==0, vectU[i]>0) for i in range(net.t)]
    X.add(matrixCstrt+inclusionCstrt)

    Y = Solver()
    y = np.array([Real("x%i" % i) for i in range(net.p)])
    FTDoty = sparseDot(F.transpose, y)
    matrixCstrt = [FTDoty[t.id]>=0 for t in U]
    Y.add(matrixCstrt)
    bTDoty = b.dot(y)
    Y.add(bTDoty <= 0)

    if X.check() == unsat:
        Y.push()
        Y.add(bTDoty < 0)
        Y.check()
        yempty = modelToFloat(Y.model(),y)
        Y.pop()
        return Formula(Clause([Atom(yempty,yempty)]))
    else:
        Up = 0 #TODO
