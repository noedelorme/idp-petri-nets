import numpy as np
from scipy.sparse import csr_matrix
from z3 import *
from objects.Net import Net


class Atom:
    """
    Class for atomic proposition of the form a*m<=ap*mp or a*m<ap*mp.

    Attributs:
        a: numpy array
        ap: numpy array
        strict: True iff strict atom
    """

    def __init__(self, a, ap, strict=False):
        self.a = a
        self.ap = ap
        self.strict = strict
    
    def __repr__(self):
        return (self.a, self.ap)

    def check(self, m, mp):
        return np.dot(self.a,m)<=np.dot(self.ap,mp)


class Clause:
    """
    Class for conjonctive clause of atomic proposition.

    Attributs:
        size: number of atoms
        atoms: array of atoms
    """

    def __init__(self, atoms):
        self.size = len(atoms)
        self.atoms = atoms
    
    def __repr__(self):
        return self.atoms
    
    def addAtom(self, atom):
        self.atoms.append(atom)
        self.size += 1

    def check(self, m, mp):
        for atom in self.atoms:
            if not atom.check(m,mp):
                return False
        return True



class Formula:
    """
    Class for locally closed bi-separator, which are quantifier-free 
    homogeneous DFN formulas.

    Attributs:
        size: number of clauses
        clauses: array of clauses
    """

    def __init__(self, clauses):
        self.size = len(clauses)
        self.clauses = clauses
    
    def __repr__(self):
        return self.clauses
    
    def addClause(self, clause):
        self.clauses.append(clause)
        self.size += 1

    def check(self, m, mp):
        for clause in self.clauses:
            if clause.check(m,mp):
                return True
        return False