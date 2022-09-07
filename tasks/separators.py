from math import *
import numpy as np
from scipy.sparse import csr_matrix
import time
from z3 import *
from tasks.utilities import *
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
    # Case U empty
    if len(U)==0:
        p = 0
        while msrc[p]==mtgt[p] and p<net.p:
            p += 1
        assert p<net.p, "Error: msrc=mtgt"
        a = np.zeros(net.p)
        a[p] = copysign(1,msrc[p]-mtgt[p])

        clause = Clause([Atom(a, a)])
        for t in net.transitions:
            clause.syndrome[t.name] = clause
        return Formula([clause])
    
    # X solver initialization
    X = Solver()
    b = mtgt - msrc
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

    # Y solver initialization
    Y = Solver()
    y = np.array([Real("y%i" % i) for i in range(net.p)])
    FT = csr_matrix(F.transpose())
    FTDoty = sparseDot(FT, y)
    matrixCstrt = [FTDoty[t.id]>=0 for t in U]
    Y.add(matrixCstrt)
    bTDoty = b.dot(y)
    Y.add(bTDoty <= 0)

    # Case X empty
    if X.check() == unsat:
        Y.push()
        Y.add(bTDoty < 0)
        assert Y.check()==sat, "Error: Y_empty has no solution"
        yempty = modelToFloat(Y.model(),y)
        Y.pop()
        clause = Clause([Atom(yempty, yempty)])
        for t in net.transitions:
            clause.syndrome[t.name] = clause
        return Formula([clause])

    #Case X none empty
    else:
        Up = set()
        for u in U:
            X.push()
            X.add(x[u.id]>0)
            if X.check() == sat:
                Up.add(u)
            X.pop()
        
        # Compute case 1 clauses
        clauses_case1 = []
        clauses_Cu_UDiffUp = dict()
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
            for u in net.transitions:
                clause.syndrome[u.name] = clause
            clauses_case1.append(clause)
            clauses_Cu_UDiffUp[t.name] = clause
            if np.dot(yt,msrc)>np.dot(yt,mtgt):
                return Formula([clause])

        # Compute largest siphon and trap
        vectQ = largestSiphon(net, Up, msrc)
        Q = placeVectorToSet(net, vectQ)
        Qo = placeSetPostset(net, Q)
        vectR = largestTrap(net, Up, mtgt)
        R = placeVectorToSet(net, vectR)
        oR = placeSetPreset(net, R)
        
        # Compute recursive call
        QoUoR = Qo.union(oR)
        UpDiffQoUoR = Up.difference(QoUoR)
        psi = generateLocallyClosedBiSeparator(net, UpDiffQoUoR, msrc, mtgt)

        # Compute case 2 clause
        clause2 = Clause(phi_inv+[Atom(-vectQ, vectR, strict=True)])
        clauses_case2 = [clause2]

        # Compute case 3 clauses
        for i in range(len(psi.clauses)):
            psi.clauses[i].syndromeId = i

        clauses_case3 = []
        atomSiphonTrap = Atom(vectR, -vectQ)
        for clause in psi.clauses:
            clause3 = Clause(phi_inv+[atomSiphonTrap]+clause.atoms)
            clause3.syndromeId = clause.syndromeId
            clauses_case3.append(Clause(phi_inv+[atomSiphonTrap]+clause.atoms))
        

        # Syndrom assignement
        for u in UDiffUp:
            clause2.syndrome[u.name] = clauses_Cu_UDiffUp[u.name]
            for clause3 in clauses_case3:
                clause3.syndrome[u.name] = clauses_Cu_UDiffUp[u.name]
        for u in Up:
            if u in oR:
                clause2.syndrome[u.name] = clause2
                for clause3 in clauses_case3:
                    clause3.syndrome[u.name] = clause2
            elif u in Qo:
                clause2.syndrome[u.name] = clause2
                for clause3 in clauses_case3:
                    clause3.syndrome[u.name] = clause2
            else:
                clause2.syndrome[u.name] = clause2
                for clause in psi.clauses:
                    clauses_case3[clause.syndromeId].syndrome[u.name] = clauses_case3[clause.syndrome[u.name].syndromeId]

        # Formula concatenation
        clauses = clauses_case1 + clauses_case2 + clauses_case3
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
    
    # If X not empty
    a,ap,minus_bp,l = None,None,None,None
    if not inv:
        a = np.concatenate((psi.a, -psi.ap))
        ap = np.concatenate((psip.a, -psip.ap))
        minus_bp = np.dot(ap, np.concatenate((np.zeros(net.p), net.tVector(t))))
        l = np.concatenate((np.zeros(net.p), net.tVectorMinus(t)))
    else:
        a = np.concatenate((-psi.ap, psi.a))
        ap = np.concatenate((-psip.ap, psip.a))
        minus_bp = np.dot(ap, np.concatenate((np.zeros(net.p), -net.tVector(t))))
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
    
    return s.check()==sat


def clauseImplication(net: Net, phi: Clause, phip: Clause, t: Transition, inv=False):
    flag_j = True
    for phip_j in phip.atoms:
        flag_i = False
        for phi_i in phi.atoms:
            if atomicImplication(net, phi_i, phip_j, t, inv):
                flag_i = True
                break
        flag_j &= flag_i
    return flag_j


def checkLocallyClosedBiSeparator(net: Net, phi: Formula, msrc, mtgt):
    """
    Check in a given formula is a locally closed bi-separator for (msrc,mtgt).

    Args:
        net: the Petri net
        phi: the formula
        msrc: the source marking
        mtgt: the target marking

    Return:
        bool: True iff phi is a locally closed bi-separator for (msrc,mtgt)
    """

    if not phi.check(msrc, msrc) or not phi.check(mtgt, mtgt) or phi.check(msrc, mtgt):
        return False
    
    for t in net.transitions:
        for phi_i in phi.clauses:
            flag = False
            for phi_j in phi.clauses:
                if clauseImplication(net, phi_i, phi_j, t):
                    flag = True
                    break
            if not flag: return False

    for t in net.transitions:
        for phi_i in phi.clauses:
            flag = False
            for phi_j in phi.clauses:
                if clauseImplication(net, phi_i, phi_j, t, True):
                    flag = True
                    break
            if not flag: return False
    
    return True

def checkLocallyClosedBiSeparatorWithSyndrome(net: Net, phi: Formula, msrc, mtgt):
    """
    Check in a given formula is a locally closed bi-separator for (msrc,mtgt), 
    using the syndrome computed during generateLocallyClosedBiSeparator.

    Args:
        net: the Petri net
        phi: the formula
        msrc: the source marking
        mtgt: the target marking

    Return:
        bool: True iff phi is a locally closed bi-separator for (msrc,mtgt)
    """

    if not phi.check(msrc, msrc) or not phi.check(mtgt, mtgt) or phi.check(msrc, mtgt):
        return False
    
    for t in net.transitions:
        for clause in phi.clauses:
            if not clauseImplication(net, clause, clause.syndrome[t.name], t):
                return False

    for t in net.transitions:
        for clause in phi.clauses:
            if not clauseImplication(net, clause, clause.syndrome[t.name], t, True):
                return False
    

    return True