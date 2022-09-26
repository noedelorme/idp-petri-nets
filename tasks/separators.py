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
    # Compute Q° as a transition vector
    vectQ = np.int64(msrc==0)
    vectQo = np.zeros(net.t)
    for i in range(len(vectQ)):
        if vectQ[i]==1:
            for t in net.places[i].postset:
                if t in Up:
                    vectQo[t.id] += 1

    # While there is p in Q s.t. some t in °p is not in Q°
    flag = True
    while flag:
        flag = False
        for i in range(net.p):
            breakFirstLoop = False
            if vectQ[i]==1:
                for t in net.places[i].preset:
                    if t in Up and vectQo[t.id]==0:
                        # Then we remove p and update Q°
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
    # Compute °R as a transition vector
    vectR = np.int64(mtgt==0)
    vectoR = np.zeros(net.t)
    for i in range(len(vectR)):
        if vectR[i]==1:
            for t in net.places[i].preset:
                if t in Up:
                    vectoR[t.id] += 1

    # While there is p in R s.t. some t in p° is not in °R
    flag = True
    while flag:
        flag = False
        for i in range(net.p):
            breakFirstLoop = False
            if vectR[i]==1:
                for t in net.places[i].postset:
                    if t in Up and vectoR[t.id]==0:
                        # Then we remove p and update °R
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
    Constructs a locally closed bi-separator for (msrc,mtgt) given that mtgt 
    is not reachable from msrc using transitions in U (Algorithm 1 of [1]).

    Args:
        net: the Petri net
        U: a subset of transitions
        msrc: the source marking
        mtgt: the target marking

    Return:
        bisep: locally closed bi-separator for (msrc,mtgt)
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
            clause.forwardSyndrome[t.name] = (clause.id,[0])
            clause.backwardSyndrome[t.name] = (clause.id,[0])
        return Formula(net, [clause])
    
    # X solver initialization
    X = Solver()
    b = mtgt - msrc
    x = np.array([Real("x%i" % i) for i in range(net.t)])
    cstrt_positive = [x[i]>=0 for i in range(net.t)]
    F = net.incidenceMatrix(net.transitions)
    F_dot_x = sparseDot(F, x)
    cstrt_matrix = [F_dot_x[i] == b[i] for i in range(net.p)]
    vectU = transitionSetToVector(net, U)
    cstrt_inclusion = [simplify(Or(x[i]==0, bool(vectU[i]>0))) for i in range(net.t)]
    atoms = cstrt_positive + cstrt_matrix + cstrt_inclusion
    X.add(simplify(And(atoms)))

    # Y solver initialization
    Y = Solver()
    y = np.array([Real("y%i" % i) for i in range(net.p)])
    FT = csr_matrix(F.transpose())
    FT_dot_y = sparseDot(FT, y)
    cstrt_matrix = [FT_dot_y[t.id]>=0 for t in U]
    bT_dot_y = b.dot(y)
    Y.add(simplify(And(cstrt_matrix+[bT_dot_y <= 0])))

    # Case X empty
    if X.check() == unsat:
        Y.push()
        Y.add(bT_dot_y < 0)
        assert Y.check()==sat, "Error: Y_empty has no solution"
        y_empty = modelToFloat(Y.model(), y, "y")
        Y.pop()
        clause = Clause([Atom(y_empty, y_empty)], 0)
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
        clause_id = 0 # Incrementing clause id
        clauses_Cu = dict() # key: transition name, value: clause id
        atoms_phi_inv = dict() # key: transition name, value: atom index
        phi_inv = []
        U_diff_Up = U.difference(Up)
        for t in U_diff_Up:
            Y.push()
            Y.add(bT_dot_y < FT_dot_y[t.id])
            assert Y.check()==sat, "Error: Y has no solution"
            yt = modelToFloat(Y.model(), y, "y")
            Y.pop()
            atom = Atom(yt, yt)
            phi_inv.append(atom)
            atoms_phi_inv[t.name] = len(phi_inv)-1
            clause = Clause([Atom(yt, yt, strict=True)], clause_id)
            clause_id += 1
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
        Up_diff_QoUoR = Up.difference(QoUoR)
        psi = generateLocallyClosedBiSeparator(net, Up_diff_QoUoR, msrc, mtgt)

        # Compute case 2 clause
        C2 = Clause(phi_inv+[Atom(-vectQ, vectR, strict=True)], clause_id)
        clause_id += 1
        clauses_case2 = [C2]

        # Compute case 3 clauses
        clauses_case3 = []
        atomSiphonTrap = Atom(vectR, -vectQ)
        for clause in psi.clauses:
            clause3 = Clause(phi_inv+[atomSiphonTrap]+clause.atoms, clause_id)
            clause_id += 1
            clause3.forwardSyndromeIH = clause.forwardSyndrome
            clause3.backwardSyndromeIH = clause.backwardSyndrome
            clauses_case3.append(clause3)

        # Syndrome assignement for C2
        for u in U_diff_Up:
            C2.forwardSyndrome[u.name] = (clauses_Cu[u.name],[atoms_phi_inv[u.name]])
            C2.backwardSyndrome[u.name] = (clauses_Cu[u.name],[atoms_phi_inv[u.name]])
        for u in Up:
            C2.forwardSyndrome[u.name] = (C2.id,[i for i in range(C2.size)])
            C2.backwardSyndrome[u.name] = (C2.id,[i for i in range(C2.size)])

        # Forward syndrome assignement for Ci
        for Ci in clauses_case3:
            for u in U_diff_Up:
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
            for u in U_diff_Up:
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


def atomicImplicationZ3(net: Net, psi: Atom, psip: Atom, t: Transition, inv=False):
    """
    Check atomic t-implication (explained in section 6 of [1]).

    Args:
        net: the Petri net
        psi: the first atomic proposition
        psip: the second atomic proposition
        t: the transition
        inv: True will peform the check in the transpose net

    Return:
        bool: True iff psi t-implies psip
    """
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
    s.add(lamb>=0)
    atoms = [lamb*a[i]>=ap[i] for i in range(2*net.p)]
    product = 0
    for i in range(2*net.p):
        product += (lamb*a[i]-ap[i])*l[i]
    product = simplify(product)
    if not psip.strict:
        atoms.append(product>=minus_bp)
    elif not psi.strict:
        atoms.append(product>minus_bp)
    else:
        atoms.append(Or(product>minus_bp, And(product==minus_bp, lamb>0)))

    s.add(simplify(And(atoms)))
    check = s.check()
    return check==sat


def atomicImplication(net: Net, psi: Atom, psip: Atom, t: Transition, inv=False):
    """
    Check atomic t-implication (explained in section 6 of [1]).

    Args:
        net: the Petri net
        psi: the first atomic proposition
        psip: the second atomic proposition
        t: the transition
        inv: True will peform the check in the transpose net

    Return:
        bool: True iff psi t-implies psip
    """
    # print("*****")
    # Return True if X empty
    if psi.strict:
        check = not all(psi.a>=0) or not all(psi.ap<=0)
        if not check: return True
    else:
        delta_t_minus = net.tVectorMinus(t)
        ap_dot_delta_t_minus = np.dot(psi.ap, delta_t_minus)
        check = ap_dot_delta_t_minus>=0
        check |= ap_dot_delta_t_minus<0 and (not all(psi.a>=0) or not all(-psi.ap>=0))
        if not check: return True

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
    
    
    
    lowerbound = 0
    upperbound = None
    for i in range(2*net.p):
        if a[i]==0 and ap[i]==0:
            pass
        elif a[i]==0 and ap[i]>0:
            return False
        elif a[i]==0 and ap[i]<0:
            pass
        elif a[i]>0 and ap[i]==0:
            pass
        elif a[i]>0 and ap[i]>0:
            lowerbound = max(lowerbound, ap[i]/a[i])
        elif a[i]>0 and ap[i]<0:
            pass
        elif a[i]<0 and ap[i]==0:
            if upperbound != None:
                upperbound = min(upperbound, 0)
            else:
                upperbound = 0
        elif a[i]<0 and ap[i]>0:
            return False
        elif a[i]<0 and ap[i]<0:
            if upperbound != None:
                upperbound = min(upperbound, ap[i]/a[i])
            else:
                upperbound = ap[i]/a[i]
    if upperbound!=None and lowerbound>upperbound: return False
    
    # (lamb*a-ap)*l = lamb*alpha-beta
    # alpha = a[0]*l[0] + a[1]*l[1] + ...
    # beta = ap[0]*l[0] + ap[1]*l[1] + ...
    alpha = 0
    beta = 0
    for i in range(2*net.p):
        alpha += a[i]*l[i]
        beta += ap[i]*l[i]

    if alpha==0:
        if not psip.strict:
            return minus_bp<=-beta
        elif not psi.strict:
            return minus_bp<-beta
        else:
            return minus_bp<-beta or (minus_bp == -beta and upperbound>0)
    else:
        L = (minus_bp+beta)/alpha
        if not psip.strict:
            # print(lowerbound)
            # print(upperbound)
            lowerbound = max(lowerbound, L)
            # print(lowerbound)
            # print(upperbound)
            return upperbound==None or lowerbound<=upperbound
        elif not psi.strict:
            if L>lowerbound:
                lowerbound = L # and lowerbound is now strict
                return upperbound==None or lowerbound<upperbound
            else:
                return upperbound==None or lowerbound<=upperbound
        else:
            if L>lowerbound:
                # lowerbound is now strict
                if upperbound==None or L<upperbound: return True
            else:
                if upperbound==None or lowerbound<=upperbound: return True
            return upperbound>=L and L>=lowerbound and L>0


def clauseImplication(net: Net, phi: Clause, phip: Clause, t: Transition, inv=False):
    """
    Check clausal t-implication (explained in section 6 of [1]).

    Args:
        net: the Petri net
        phi: the first clause
        phip: the second clause
        t: the transition
        inv: True will peform the check in the transpose net

    Return:
        bool: True iff phi t-implies phip
    """
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
    Check in a given formula is a locally closed bi-separator for (msrc,mtgt) 
    (explained in section 6 of [1]).

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


def checkLocallyClosedBiSeparatorWithSyndrome(net: Net, phi: Formula, msrc, mtgt, log=False):
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
    nb_atomic_check_performed = 0

    if not phi.check(msrc, msrc) or not phi.check(mtgt, mtgt) or phi.check(msrc, mtgt):
        return False, max_time, nb_atomic_check_performed
    
    step = 1
    step_avancement = 0
    for t in net.transitions:
        if log:
            print(">Step "+str(step)+"/"+str(net.t*2))
            step += 1
            step_avancement = 1
        for C in phi.clauses:
            if log:
                print(str(step_avancement)+"/"+str(len(phi.clauses)))
                step_avancement += 1
            j = C.forwardSyndrome[t.name][0]
            Cp = phi.clauses[j]
            for j in range(Cp.size):
                psip_j = Cp.atoms[j]
                i = C.forwardSyndrome[t.name][1][j]
                psi_i = C.atoms[i]
                start = time.time()
                check = atomicImplication(net, psi_i, psip_j, t)
                nb_atomic_check_performed += 1
                stop = time.time()
                max_time = max(max_time, stop-start)
                total_time += stop-start
                if not check:
                    return False, max_time, nb_atomic_check_performed
    
    for t in net.transitions:
        if log:
            print(">Step "+str(step)+"/"+str(net.t*2))
            step += 1
            step_avancement = 1
        for C in phi.clauses:
            if log:
                print(str(step_avancement)+"/"+str(len(phi.clauses)))
                step_avancement += 1
            j = C.backwardSyndrome[t.name][0]
            Cp = phi.clauses[j]
            for j in range(Cp.size):
                psip_j = Cp.atoms[j]
                i = C.backwardSyndrome[t.name][1][j]
                psi_i = C.atoms[i]
                start = time.time()
                check = atomicImplication(net, psi_i, psip_j, t, inv=True)
                nb_atomic_check_performed += 1
                stop = time.time()
                max_time = max(max_time, stop-start)
                total_time += stop-start
                if not check:
                    return False, max_time, nb_atomic_check_performed

    return True, max_time, nb_atomic_check_performed