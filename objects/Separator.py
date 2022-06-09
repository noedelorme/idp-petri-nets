import numpy as np
from scipy.sparse import csr_matrix
from z3 import *
from objects.Net import Net


class Atom:
    """
    Class for atomic proposition of the form a*x<=b or a*x<b.
    """

    def __init__(self):
        pass



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
    
    def addAtom(self, atom):
        self.atoms.append(atom)
        self.size += 1



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
    
    def addClause(self, clause):
        self.clauses.append(clause)
        self.size += 1
