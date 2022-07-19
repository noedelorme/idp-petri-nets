import numpy as np
import time
from z3 import *
from tasks.utilities import *
from objects.Net import Net


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



def isReachable(net: Net, m, log=False):
    """
    Decision algorithm for reachability

    Args:
        net: the net
        m: the target marking

    Return: 
        bool: True iff m is reachable from net.marking
    """

    if all(m[i]==net.marking[i] for i in range(net.p)): return True
    
    Tp = net.transitions.copy()

    count_while = 0
    while len(Tp)>0:
        count_while += 1

        nbsol = 0
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
            if log and (avancement-avancement_old>=5 or avancement<=avancement_old):
                print(str(avancement)+"%")
                avancement_old = avancement

            s.push()
            s.add(v[t.id]>0)

            if s.check() == sat:
                nbsol += 1
                model = s.model()
                # modelFraction = np.array([model[v[i]].as_fraction() for i in range(net.t)])
                # sol += np.array([float(x.numerator)/float(x.denominator) for x in modelFraction])
                modelFraction = modelToFloat(model,v)
                sol += modelFraction
                
            s.pop()

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



def isCoverable(net: Net, m, log=False):
    """
    Decision algorithm for coverability

    Args:
        net: the net
        m: the target marking

    Return: 
        bool: True iff m is coverable from net.marking
    """

    if all(m[i]<=net.marking[i] for i in range(net.p)): return True
    
    Tp = net.transitions.copy()

    count_while = 0
    while len(Tp)>0:
        count_while += 1

        nbsol = 0
        solv = np.zeros(net.t)
        solw = np.zeros(net.p)

        s = Solver()
        v = np.array([Real("v%i" % i) for i in range(net.t)])
        w = np.array([Real("w%i" % i) for i in range(net.p)])
        positiveCstrtV = [v[i]>=0 for i in range(net.t)]
        positiveCstrtW = [w[i]>=0 for i in range(net.p)]
        C = net.incidenceMatrix(Tp)
        CDotv = sparseDot(C,v)
        mMinusm0 = m-net.marking
        matrixCstrt = [CDotv[i]-w[i] == mMinusm0[i] for i in range(net.p)]
        s.add(positiveCstrtV+positiveCstrtW+matrixCstrt)

        count_for = 0
        avancement = 0
        avancement_old = 0
        if log: print(">Step "+ str(count_while))
        for t in Tp:
            count_for += 1
            avancement = int(count_for/len(Tp)*100)
            if log and (avancement-avancement_old>=5 or avancement<=avancement_old):
                print(str(avancement)+"%")
                avancement_old = avancement

            s.push()
            s.add(v[t.id]>0)

            if s.check() == sat:
                nbsol += 1
                model = s.model()
                modelFractionV = modelToFloat(model,v)
                modelFractionW = modelToFloat(model,w)
                solv += modelFractionV
                solw += modelFractionW
                
            s.pop()

        count = 0
        for p in net.places:
            count += 1
            print("second step: "+str(round(count/net.p*100, 2))+"%")

            s.push()
            s.add(w[p.id]>0)

            if s.check() == sat:
                nbsol += 1
                model = s.model()
                modelFractionV = modelToFloat(model,v)
                modelFractionW = modelToFloat(model,w)
                solv += modelFractionV
                solw += modelFractionW
                
            s.pop()

        if nbsol==0: return False
        else:
            solv /= nbsol
            solw /= nbsol

        Tp = net.supportTransitionVector(solv)
        oTpo = set()
        for t in Tp:
            oTpo = oTpo.union(t.preset)
            oTpo = oTpo.union(t.postset)
            
        m0oTpo = net.restriction(net.marking, oTpo)
        maxFSm0 = isFireable(net, Tp, m0oTpo)[1]
        Tp = Tp.intersection(maxFSm0)

        msolwoTpo = net.restriction(m+solw, oTpo)
        maxFSm = isFireable(net, Tp, msolwoTpo, True)[1]
        Tp = Tp.intersection(maxFSm)

        if Tp == net.supportTransitionVector(solv): return True
    return False