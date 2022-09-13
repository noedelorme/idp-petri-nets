import numpy as np
from scipy.sparse import csr_matrix
from z3 import *
from objects.Net import Net


def sparseDot(A,v):
    """
    Computes the matrix product A*v.

    Args:
        A: a p*t matrix in CSR format
        v: a np.array of Z3 Real of size t
    
    Return:
        Av: matrix product Av as np.array
    """
    p,t = A.shape
    Av = np.array([RealVal(0) for i in range(p)])

    currentIndPtr = 0
    for i in range(p):
        sum = RealVal(0)
        for j in range(A.indptr[currentIndPtr], A.indptr[currentIndPtr+1]):
            sum += A.data[j]*v[A.indices[j]]
        Av[i] = simplify(sum)
        currentIndPtr += 1

    return Av


def modelToFloat(model, vars):
    """
    Converts a Z3 model into a float numpy array.

    Args:
        model: a Z3 model
        vars: a np.array of the varaibles
    
    Return:
        modelFloat: np.array of float
    """
    n = len(vars)
    modelFloat = np.zeros(n)
    for d in model.decls():
        id = int(d.name()[1:])
        texts = model[d].as_string().split("/")
        if len(texts)==1:
            modelFloat[id] = float(texts[0])
        else:
            modelFloat[id] = float(texts[0])/float(texts[1])
    return modelFloat


def placeVectorToSet(net: Net, vectS):
    """
    Convert a place vector into set vector.

    Args:
        net: the net
        vectS: the place vector
    
    Return:
        S: the set vector
    """
    S = set()
    for i in range(net.p):
        if vectS[i]>0:
            S.add(net.places[i])
    return S


def transitionSetToVector(net: Net, U):
    """
    Convert a transition set into a transition vector.

    Args:
        net: the net
        U: the transition set
    
    Return:
        vectU: the transition vector
    """
    vectU = np.zeros(net.t)
    for t in U:
        vectU[t.id] = 1
    return vectU


def placeSetPostset(net: Net, S):
    """
    Compute the postset of a set of places.

    Args:
        net: the net
        S: the place set
    
    Return:
        postset: the postset of S
    """
    postset = set()
    for p in S:
        postset = postset.union(p.postset)
    return postset


def placeSetPreset(net: Net, S):
    """
    Compute the preset of a set of places.

    Args:
        net: the net
        S: the place set
    
    Return:
        preset: the preset of S
    """
    preset = set()
    for p in S:
        preset = preset.union(p.preset)
    return preset