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

    # while there is p in Q s.t. some t in °p is not in Q°
    flag = True
    while flag:
        flag = False
        for i in range(net.p):
            breakFirstLoop = False
            if vectQ[i]==1:
                for t in net.places[i].preset:
                    if t in Up and vectQo[t.id]==0:
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

    # while there is p in R s.t. some t in p° is not in °Q
    flag = True
    while flag:
        flag = False
        for i in range(net.p):
            breakFirstLoop = False
            if vectR[i]==1:
                for t in net.places[i].postset:
                    if t in Up and vectoR[t.id]==0:
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
    # print("--------------Recursive call, len(U)=:", len(U))

    if len(U)==0:
        p = 0
        while msrc[p]==mtgt[p] and p<net.p:
            p += 1
        assert p<net.p, "Error: msrc=mtgt"
        a = np.zeros(net.p)
        a[p] = copysign(1,msrc[p]-mtgt[p])

        return Formula([Clause([Atom(a, a)])])
    
    b = mtgt - msrc

    X = Solver()
    x = np.array([Real("x%i" % i) for i in range(net.t)])
    positiveCstrt = [x[i]>=0 for i in range(net.t)]
    F = net.incidenceMatrix(net.transitions)
    X.add(positiveCstrt)
    FDotx = sparseDot(F, x)
    matrixCstrt = [FDotx[i] == b[i] for i in range(net.p)]
    X.add(matrixCstrt)
    vectU = transitionSetToVector(net, U)
    inclusionCstrt = [simplify(Or(x[i]==0, bool(vectU[i]>0))) for i in range(net.t)]
    X.add(inclusionCstrt)

    Y = Solver()
    y = np.array([Real("y%i" % i) for i in range(net.p)])
    FT = csr_matrix(F.transpose())
    FTDoty = sparseDot(FT, y)
    matrixCstrt = [FTDoty[t.id]>=0 for t in U]
    Y.add(matrixCstrt)
    bTDoty = b.dot(y)
    Y.add(bTDoty <= 0)

    if X.check() == unsat:
        Y.push()
        Y.add(bTDoty < 0)
        assert Y.check()==sat, "Error: Y_empty has no solution"
        yempty = modelToFloat(Y.model(),y)
        Y.pop()
        return Formula([Clause([Atom(yempty, yempty)])])
    else:
        Up = set()
        for u in U:
            X.push()
            X.add(x[u.id]>0)
            if X.check() == sat:
                Up.add(u)
            X.pop()
        
        clauses_case1 = []
        phi_inv = []
        UDiffUp = U.difference(Up)
        for t in UDiffUp:
            Y.push()
            Y.add(bTDoty < FTDoty[t.id])
            assert Y.check()==sat, "Error: Y has no solution"
            yt = modelToFloat(Y.model(),y)
            Y.pop()
            phi_inv.append(Atom(yt, yt))
            clause = Clause([Atom(yt, yt, strict=True)])
            clauses_case1.append(clause)
            if np.dot(yt,msrc)>np.dot(yt,mtgt):
                return Formula([clause])

        vectQ = largestSiphon(net, Up, msrc)
        Q = placeVectorToSet(net, vectQ)
        Qo = placeSetPostset(net, Q)
        vectR = largestTrap(net, Up, mtgt)
        R = placeVectorToSet(net, vectR)
        oR = placeSetPreset(net, R)
        
        QoUoR = Qo.union(oR)
        UpDiffQoUoR = Up.difference(QoUoR)
        psi = locallyClosedBiSeparator(net, UpDiffQoUoR, msrc, mtgt)

        case2 = Clause(phi_inv+[Atom(-vectQ, vectR, strict=True)])

        clauses_case3 = []
        atomSiphonTrap = Atom(vectR, -vectQ)
        for clause in psi.clauses:
            clauses_case3.append(Clause(phi_inv+[atomSiphonTrap]+clause.atoms))

        clauses = clauses_case1 + [case2] + clauses_case3
        bisep = Formula(clauses)
        return bisep
