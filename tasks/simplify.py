from math import *
import numpy as np
from z3 import *
from objects.Net import Net, Transition, Place
from objects.Formula import Formula, Clause, Atom

def checkClauseUselessness(form: Formula, i):
    # form = A or B with A = C1 and B = C2 or C3
    # If (A and not-B) unsatisfiable, then A is useless
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


def simplifySeparator(sep: Formula):
    simplified = False
    currentSep = sep
    while not simplified:
        clauseRemoved = False
        for i in range(len(currentSep.clauses)):
            clause = currentSep.clauses[i]
            if checkClauseUselessness(currentSep, i):
                currentSep.clauses.pop(i) # remove clause from currentSep
                currentSep.size -= 1
                clauseRemoved = True
                break
        if not clauseRemoved: 
            simplified = True
    return currentSep