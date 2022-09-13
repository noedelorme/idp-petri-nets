from math import *
import numpy as np
from z3 import *
from objects.Net import Net, Transition, Place
from objects.Formula import Formula, Clause, Atom

def checkClauseUselessness(form: Formula, i):
    """
    Check if a clause is useless.
    
    Args:
        form: the formula
        i: the index of the clause to check

    Return:
        bool: True iff the clause is useless
    """
    if form.size <= 1:
        return False

    A = form.clauses[i]
    B = form.clauses[:i]+form.clauses[i+1:]

    s = Solver()
    n = form.net.p
    x = np.array([Real("x%i" % i) for i in range(n)])
    xp = np.array([Real("xp%i" % i) for i in range(n)])

    andA = []
    for atom in A.atoms:
        if atom.strict:
            andA.append(np.dot(atom.a,x)<np.dot(atom.ap,xp))
        else:
            andA.append(np.dot(atom.a,x)<=np.dot(atom.ap,xp))
    AZ3 = And(andA)

    orB = []
    for clause in B:
        andB = []
        for atom in clause.atoms:
            if atom.strict:
                andB.append(np.dot(atom.a,x)<np.dot(atom.ap,xp))
            else:
                andB.append(np.dot(atom.a,x)<=np.dot(atom.ap,xp))
        orB.append(And(andB))
    BZ3 = Or(orB)

    cstrt = And(AZ3, Not(BZ3))
    s.add(simplify(cstrt))
    return s.check() == unsat


def simplifySeparator(form: Formula):
    """
    Simplify a formula by removing useless clauses.
    
    Args:
        form: the formula

    Return:
        currentSep: the simplified formula
    """
    simplified = False
    current_form = form
    while not simplified:
        clause_removed = False
        for i in range(len(current_form.clauses)):
            clause = current_form.clauses[i]
            if checkClauseUselessness(current_form, i):
                current_form.clauses.pop(i) # remove clause from current_form
                current_form.size -= 1
                clause_removed = True
                break
        if not clause_removed: 
            simplified = True
    return current_form