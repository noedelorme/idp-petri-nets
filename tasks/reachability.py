import numpy as np
import time
from z3 import *
from tasks.utilities import *
from objects.Net import Net


def isFireable(net: Net, Tp, m, inv=False):
    """
    Decision algorithm for membership of firing set  (Algorithm 1 of [2]).

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


def isReachable(net: Net, m, log=False):
    """
    Decision algorithm for reachability (Algorithm 2 of [2]).

    Args:
        net: the net
        m: the target marking
        log: True will print the avancement

    Return: 
        bool: True iff m is reachable from net.marking
    """

    if all(m[i]==net.marking[i] for i in range(net.p)): return True
    
    Tp = net.transitions.copy()

    count_while = 0
    while len(Tp)>0:
        count_while += 1

        nb_sol = 0
        sol = np.zeros(net.t)

        s = Solver()
        v = np.array([Real("v%i" % i) for i in range(net.t)])
        positiveCstrt = [v[i]>=0 for i in range(net.t)]
        C = net.incidenceMatrix(Tp)
        CDotv = sparseDot(C,v)
        mMinusm0 = m-net.marking
        matrixCstrt = [CDotv[i] == mMinusm0[i] for i in range(net.p)]
        s.add(positiveCstrt+matrixCstrt)

        count_for = 0
        avancement = 0
        avancement_old = 0
        if log: print(">Step "+ str(count_while))
        for t in Tp:
            count_for += 1
            avancement = int(count_for/len(Tp)*100)
            if log and (avancement-avancement_old>=5):
                print(str(avancement)+"%")
                avancement_old = avancement

            s.push()
            s.add(v[t.id]>0)

            if s.check() == sat:
                nb_sol += 1
                model = s.model()
                model_fraction = modelToFloat(model,v)
                sol += model_fraction
                
            s.pop()

        if nb_sol==0: return False
        else: sol /= nb_sol

        Tp = net.supportTransitionVector(sol)
        oTpo = set()
        for t in Tp:
            oTpo = oTpo.union(t.preset)
            oTpo = oTpo.union(t.postset)
            
        m0_oTpo = net.restriction(net.marking, oTpo)
        maxFS_m0 = isFireable(net, Tp, m0_oTpo)[1]
        Tp = Tp.intersection(maxFS_m0)

        m_oTpo = net.restriction(m, oTpo)
        maxFS_m = isFireable(net, Tp, m_oTpo, True)[1]
        Tp = Tp.intersection(maxFS_m)

        if Tp == net.supportTransitionVector(sol): return True
    return False


def isCoverable(net: Net, m, log=False):
    """
    Decision algorithm for coverability (Algorithm 3 of [2]).

    Args:
        net: the net
        m: the target marking
        log: True will print the avancement

    Return: 
        bool: True iff m is coverable from net.marking
    """

    if all(m[i]<=net.marking[i] for i in range(net.p)): return True
    
    Tp = net.transitions.copy()

    count_while = 0
    while len(Tp)>0:
        count_while += 1

        nb_sol = 0
        sol_v = np.zeros(net.t)
        sol_w = np.zeros(net.p)

        s = Solver()
        v = np.array([Real("v%i" % i) for i in range(net.t)])
        w = np.array([Real("w%i" % i) for i in range(net.p)])
        cstrt_positive_V = [v[i]>=0 for i in range(net.t)]
        cstrt_positive_W = [w[i]>=0 for i in range(net.p)]
        C = net.incidenceMatrix(Tp)
        C_dot_v = sparseDot(C,v)
        m_minus_m0 = m-net.marking
        cstrt_matrix = [C_dot_v[i]-w[i] == m_minus_m0[i] for i in range(net.p)]
        s.add(cstrt_positive_V+cstrt_positive_W+cstrt_matrix)

        count_for = 0
        avancement = 0
        avancement_old = 0
        if log: print(">Step "+ str(count_while))
        for t in Tp:
            count_for += 1
            avancement = int(count_for/len(Tp)*100)
            if log and (avancement-avancement_old>=5):
                print(str(avancement)+"%")
                avancement_old = avancement

            s.push()
            s.add(v[t.id]>0)

            if s.check() == sat:
                nb_sol += 1
                model = s.model()
                model_fraction_V = modelToFloat(model,v)
                model_fraction_W = modelToFloat(model,w)
                sol_v += model_fraction_V
                sol_w += model_fraction_W
                
            s.pop()

        count = 0
        for p in net.places:
            count += 1
            if log: print("second step: "+str(round(count/net.p*100, 2))+"%")

            s.push()
            s.add(w[p.id]>0)

            if s.check() == sat:
                nb_sol += 1
                model = s.model()
                model_fraction_V = modelToFloat(model,v)
                model_fraction_W = modelToFloat(model,w)
                sol_v += model_fraction_V
                sol_w += model_fraction_W
                
            s.pop()

        if nb_sol==0: return False
        else:
            sol_v /= nb_sol
            sol_w /= nb_sol

        Tp = net.supportTransitionVector(sol_v)
        oTpo = set()
        for t in Tp:
            oTpo = oTpo.union(t.preset)
            oTpo = oTpo.union(t.postset)
            
        m0_oTpo = net.restriction(net.marking, oTpo)
        maxFS_m0 = isFireable(net, Tp, m0_oTpo)[1]
        Tp = Tp.intersection(maxFS_m0)

        m_sol_w_oTpo = net.restriction(m+sol_w, oTpo)
        maxFS_m = isFireable(net, Tp, m_sol_w_oTpo, True)[1]
        Tp = Tp.intersection(maxFS_m)

        if Tp == net.supportTransitionVector(sol_v): return True
    return False