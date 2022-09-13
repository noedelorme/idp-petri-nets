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
        if self.strict:
            return str(self.a)+"*m<"+str(self.ap)+"*m'"
        else: 
            return str(self.a)+"*m<="+str(self.ap)+"*m'"

    def check(self, m, mp):
        if self.strict:
            return np.dot(self.a,m)<np.dot(self.ap,mp)
        else:
            return np.dot(self.a,m)<=np.dot(self.ap,mp)


class Clause:
    """
    Class for conjonctive clause of atomic proposition.

    Attributs:
        size: number of atoms
        id: index of the clause in the formula
        atoms: array of atoms
        forwardSyndrome: forward syndrome
        forwardSyndromeIH: forward induction hypothesis
        backwardSyndrome: backward syndrome
        backwardSyndromeIH: backward induction hypothesis
    """

    def __init__(self, atoms, id):
        self.size = len(atoms)
        self.id = id
        self.atoms = atoms
        self.forwardSyndrome = dict()
        self.forwardSyndromeIH = None
        self.backwardSyndrome = dict()
        self.backwardSyndromeIH = None
    
    def __repr__(self):
        text = ""
        for i in range(len(self.atoms)):
            text += str(self.atoms[i])
            if i!=len(self.atoms)-1:
                text += " AND "
        return text
    
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
        net: the net that the formula is refered to
    """

    def __init__(self, net, clauses):
        self.size = len(clauses)
        self.clauses = clauses
        self.net = net
    
    def print(self):
        for i in range(len(self.clauses)):
            print(self.clauses[i])
            if i!=len(self.clauses)-1:
                print("OR")
    
    def getSize(self):
        text = str(self.size) + "("
        for clause in self.clauses:
            text += str(clause.size) + ","
        text = text[:-1] + ")"
        return text
    
    def addClause(self, clause):
        self.clauses.append(clause)
        self.size += 1

    def check(self, m, mp):
        for clause in self.clauses:
            if clause.check(m,mp):
                return True
        return False