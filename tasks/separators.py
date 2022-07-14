from math import *
import numpy as np
from scipy.sparse import csr_matrix
import time
from z3 import *
from tasks.utilities import *
from objects.Net import Net
from objects.Net import Net, Transition, Place
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



def generateLocallyClosedBiSeparator(net: Net, U, msrc, mtgt):
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
        psi = generateLocallyClosedBiSeparator(net, UpDiffQoUoR, msrc, mtgt)

        case2 = Clause(phi_inv+[Atom(-vectQ, vectR, strict=True)])

        clauses_case3 = []
        atomSiphonTrap = Atom(vectR, -vectQ)
        for clause in psi.clauses:
            clauses_case3.append(Clause(phi_inv+[atomSiphonTrap]+clause.atoms))

        clauses = clauses_case1 + [case2] + clauses_case3
        bisep = Formula(clauses)
        return bisep



def atomicImplication(net: Net, psi: Atom, psip: Atom, t: Transition, inv=False):
    # Return True if X empty
    if psi.strict:
        check = not all(psi.a>=0) and not all(psi.ap<=0)
        if not check:
            return True
    else:
        flag = False
        for u in net.transitions:
            delta_u_minus = net.tVectorMinus(u)
            ap_dot_delta_u_minus = np.dot(psi.ap, delta_u_minus)
            check = ap_dot_delta_u_minus>=0
            check |= ap_dot_delta_u_minus<0 and not all(psi.a>=0) and not all(-psi.ap>=0)
            if check:
                flag = True
                break
        if not flag:
            return True
    
    # print("X not empty")

    # If X not empty
    a,ap,minus_bp,l = None,None,None,None
    if not inv:
        a = np.concatenate((psi.a, -psi.ap))
        ap = np.concatenate((psip.a, -psip.ap))
        minus_bp = np.dot(a, np.concatenate((np.zeros(net.p), net.tVector(t))))
        l = np.concatenate((np.zeros(net.p), net.tVectorMinus(t)))
    else:
        a = np.concatenate((-psi.ap, psi.a))
        ap = np.concatenate((-psip.ap, psip.a))
        minus_bp = np.dot(a, np.concatenate((np.zeros(net.p), -net.tVector(t))))
        l = np.concatenate((np.zeros(net.p), net.tVectorPlus(t)))

    s = Solver()
    lamb = Real("lamb")
    
    s.add([lamb*a[i]>=ap[i] for i in range(2*net.p)])
    product = 0
    for i in range(2*net.p):
        product += (lamb*a[i]-ap[i])*l[i]
    product = simplify(product)
    if not psip.strict:
        s.add(product>=minus_bp)
    elif not psi.strict:
        s.add(product>minus_bp)
    else:
        s.add(Or(product>minus_bp, And(product==minus_bp, lamb>0)))
    
    # print(s)
    
    return s.check()==sat



def checkLocallyClosedBiSeparator(net: Net, phi: Formula, msrc, mtgt):
    for t in net.transitions:
        for clause_i in phi.clauses:
            flag_clause_i = False
            for clause_j in phi.clauses:
                flag_clause_j = True
                for psi in clause_i.atoms:
                    flag_psi = False
                    for psip in clause_j.atoms:
                        if atomicImplication(net, psi, psip, t):
                            flag_psi = True
                            break
                    if not flag_psi:
                        flag_clause_j = False
                        break
                if flag_clause_j:
                    flag_clause_i = True
                    break
            if not flag_clause_i:
                answer = False
                return answer
    print("test")
    for t in net.transitions:
        for clause_i in phi.clauses:
            flag_clause_i = False
            for clause_j in phi.clauses:
                flag_clause_j = True
                for psi in clause_i.atoms:
                    flag_psi = False
                    for psip in clause_j.atoms:
                        if atomicImplication(net, psi, psip, t, inv=True):
                            flag_psi = True
                            break
                    if not flag_psi:
                        flag_clause_j = False
                        break
                if flag_clause_j:
                    flag_clause_i = True
                    break
            if not flag_clause_i:
                answer = False
                return answer
    
    return True