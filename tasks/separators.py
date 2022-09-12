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

        clause = Clause([Atom(a, a)], 0)
        for t in net.transitions:
            clause.forwardSyndrome[t.name] = clause.id
            clause.backwardSyndrome[t.name] = clause.id
        return Formula(net, [clause])
    
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
        clause = Clause([Atom(yempty, yempty)], 0)
        for t in net.transitions:
            clause.forwardSyndrome[t.name] = (clause.id,[0])
            clause.backwardSyndrome[t.name] = (clause.id,[0])
        return Formula(net, [clause])

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
        clauseId = 0 # Incrementing  clause id
        clauses_Cu = dict() # key: transition name, value: clause id
        atoms_phi_inv = dict() # key: transition name, value: atom index
        phi_inv = []
        UDiffUp = U.difference(Up)
        for t in UDiffUp:
            Y.push()
            Y.add(bTDoty < FTDoty[t.id])
            assert Y.check()==sat, "Error: Y has no solution"
            yt = modelToFloat(Y.model(),y)
            Y.pop()
            atom = Atom(yt, yt)
            phi_inv.append(atom)
            atoms_phi_inv[t.name] = len(phi_inv)-1
            clause = Clause([Atom(yt, yt, strict=True)], clauseId)
            clauseId += 1
            for u in net.transitions:
                clause.forwardSyndrome[u.name] = (clause.id,[0])
                clause.backwardSyndrome[u.name] = (clause.id,[0])
            clauses_Cu[t.name] = clause.id
            clauses_case1.append(clause)
            if np.dot(yt,msrc)>np.dot(yt,mtgt):
                clause.id = 0
                return Formula(net, [clause])

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
        C2 = Clause(phi_inv+[Atom(-vectQ, vectR, strict=True)], clauseId)
        clauseId += 1
        clauses_case2 = [C2]

        # Compute case 3 clauses
        clauses_case3 = []
        atomSiphonTrap = Atom(vectR, -vectQ)
        for clause in psi.clauses:
            clause3 = Clause(phi_inv+[atomSiphonTrap]+clause.atoms, clauseId)
            clauseId += 1
            clause3.forwardSyndromeIH = clause.forwardSyndrome
            clause3.backwardSyndromeIH = clause.backwardSyndrome
            clauses_case3.append(clause3)

        # Syndrome assignement for C2
        for u in UDiffUp:
            C2.forwardSyndrome[u.name] = (clauses_Cu[u.name],[atoms_phi_inv[u.name]])
            C2.backwardSyndrome[u.name] = (clauses_Cu[u.name],[atoms_phi_inv[u.name]])
        for u in Up:
            C2.forwardSyndrome[u.name] = (C2.id,[i for i in range(C2.size)])
            C2.backwardSyndrome[u.name] = (C2.id,[i for i in range(C2.size)])

        # Forward syndrome assignement for Ci
        for Ci in clauses_case3:
            for u in UDiffUp:
                Ci.forwardSyndrome[u.name] = (clauses_Cu[u.name],[atoms_phi_inv[u.name]])
            for u in Up:
                if u in oR:
                    Ci.forwardSyndrome[u.name] = (C2.id,[i for i in range(C2.size)])
                elif u in Qo:
                    Ci.forwardSyndrome[u.name] = (C2.id,[len(phi_inv) for i in range(C2.size)])
                else:
                    j = Ci.forwardSyndromeIH[u.name][0]+len(clauses_case1)+1
                    syndrome_phi_inv_theta = [i for i in range(len(phi_inv)+1)]
                    syndrome_IH = [x+len(phi_inv)+1 for x in Ci.forwardSyndromeIH[u.name][1]]
                    Ci.forwardSyndrome[u.name] = (j, syndrome_phi_inv_theta+syndrome_IH)

        # Backward syndrome assignement for Ci
        for Ci in clauses_case3:
            for u in UDiffUp:
                Ci.backwardSyndrome[u.name] = (clauses_Cu[u.name],[atoms_phi_inv[u.name]])
            for u in Up:
                if u in Qo:
                    Ci.backwardSyndrome[u.name] = (C2.id,[i for i in range(C2.size)])
                elif u in oR:
                    Ci.backwardSyndrome[u.name] = (C2.id,[len(phi_inv) for i in range(C2.size)])
                else:
                    j = Ci.backwardSyndromeIH[u.name][0]+len(clauses_case1)+1
                    syndrome_phi_inv_theta = [i for i in range(len(phi_inv)+1)]
                    syndrome_IH = [x+len(phi_inv)+1 for x in Ci.backwardSyndromeIH[u.name][1]]
                    Ci.backwardSyndrome[u.name] = (j, syndrome_phi_inv_theta+syndrome_IH)

        # Formula concatenation
        clauses = clauses_case1 + clauses_case2 + clauses_case3
        bisep = Formula(net, clauses)
        return bisep




def atomicImplication(net: Net, psi: Atom, psip: Atom, t: Transition, inv=False):
    # Return True if X empty
    if psi.strict:
        check = not all(psi.a>=0) and not all(psi.ap<=0)
        if not check:
            return True
    else:
        delta_t_minus = net.tVectorMinus(t)
        ap_dot_delta_t_minus = np.dot(psi.ap, delta_t_minus)
        check = ap_dot_delta_t_minus>=0
        check |= ap_dot_delta_t_minus<0 and not all(psi.a>=0) or not all(-psi.ap>=0)
        if not check:
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
        max_time: maximal time of atomic implication checks
    """
    max_time = 0
    total_time = 0

    if not phi.check(msrc, msrc) or not phi.check(mtgt, mtgt) or phi.check(msrc, mtgt):
        return False
    
    for t in net.transitions:
        for C in phi.clauses:
            j = C.forwardSyndrome[t.name][0]
            Cp = phi.clauses[j]
            for j in range(Cp.size):
                psip_j = Cp.atoms[j]
                i = C.forwardSyndrome[t.name][1][j]
                psi_i = C.atoms[i]
                start = time.time()
                check = atomicImplication(net, psi_i, psip_j, t)
                stop = time.time()
                max_time = max(max_time, stop-start)
                total_time += stop-start
                if not check:
                    return False, max_time
    
    for t in net.transitions:
        for C in phi.clauses:
            j = C.backwardSyndrome[t.name][0]
            Cp = phi.clauses[j]
            for j in range(Cp.size):
                psip_j = Cp.atoms[j]
                i = C.backwardSyndrome[t.name][1][j]
                psi_i = C.atoms[i]
                start = time.time()
                check = atomicImplication(net, psi_i, psip_j, t, inv=True)
                stop = time.time()
                max_time = max(max_time, stop-start)
                total_time += stop-start
                if not check:
                    return False, max_time

    return True, max_time