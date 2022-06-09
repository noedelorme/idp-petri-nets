import numpy as np
from scipy.sparse import csr_matrix
import time
from z3 import *
from tasks.utilities import *
from objects.Net import Net
from objects.Separator import Formula, Clause, Atom


def largestSiphon(net: Net, Up, msrc):
    """
    Find the largest siphon Q of N_Up such that msrc(Q)=0.
    
    Args:
        net: the Petri net
        Up: a subset of transitions
        msrc: the source marking

    Return:
        Q: the largest siphon of N_Up such that msrc(Q)=0
    """
    pass



def largestTrap(net: Net, Up, mtgt):
    """
    Find the largest trap R of N_Up such that mtgt(R)=0.
    
    Args:
        net: the Petri net
        Up: a subset of transitions
        mtgt: the target marking

    Return:
        R: the largest trap of N_Up such that mtgt(R)=0
    """
    pass



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
        return False #TODO
    
    b = mtgt - msrc

    X = Solver()
    x = np.array([Real("x%i" % i) for i in range(net.t)])
    F = net.incidenceMatrix(net.transitions)
    FDotx = sparseDot(F, x)
    matrixCstrt = [FDotx[i] == b[i] for i in range(net.p)]
    inclusionCstrt = [] #TODO
    X.add(matrixCstrt+inclusionCstrt)

    Y = Solver()
    y = np.array([Real("x%i" % i) for i in range(net.p)])
    FTDoty = sparseDot(F.transpose, y)
    matrixCstrt = [FTDoty[t.id] for t in U]
    Y.add(matrixCstrt)
    bTy = b.dot(y)
    Y.add(bTy <= 0)

    if X.check() == unsat:
        Y.push()
        Y.add(bTy < 0)
        Y.check()
        yempty = modelToFloat(Y.model(),y)
        Y.pop()
        return False #TODO
    else:
        Up = 0 #TODO
