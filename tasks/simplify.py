from math import *
import numpy as np
from z3 import *
from objects.Net import Net, Transition, Place
from objects.Formula import Formula, Clause, Atom

def checkClauseUsefulness(form: Formula, clause: Clause):
    pass

def simplifySeparator(sep: Formula):
    simplified = False
    currentSep = sep
    while not simplified:
        clauseRemoved = False
        for clause in sep.clauses:
            if not checkClauseUsefulness(currentSep, clause):
                currentSep = currentSep
                # remove clause from currentSep
                clauseRemoved = True
                break
        if not clauseRemoved: 
            simplified = True