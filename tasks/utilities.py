import numpy as np
from scipy.sparse import csr_matrix
from z3 import *

def sparseDot(A,v):
    """
    Computes the matrix product A*v.

    Args:
        A: a p*t matrix in CSR format
        v: a np.array of size t
    
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
    for i in range(n):
        texts = model[vars[i]].as_string().split("/")
        if len(texts)==1:
            modelFloat[i] = float(texts[0])
        else:
            modelFloat[i] = float(texts[0])/float(texts[1])
    return modelFloat