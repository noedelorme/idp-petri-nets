from unittest import result
import numpy as np
from scipy.sparse import csr_matrix
import time
from os import listdir
from z3 import *
from objects.Net import Net
from objects.Formula import Formula, Clause, Atom
from tools.reader import *
from tasks.reachability import *
from tasks.separators import *
from tasks.simplify import *


def runReachability(path, log=False):
    net = createNet(path+".lola")
    m = createMarking(net, path+".formula")
    start = time.time()
    answer = isReachable(net, m, log=log)
    stop = time.time()
    print("--Reachability check------")
    print("Petri net:", path)
    print("Number of places:", net.p)
    print("Number of transitions:", net.t)
    print("Reachability output:", answer)
    print("Check time:", stop-start)
    print("--------------------------")


def runCoverability(path, log=False):
    net = createNet(path+".lola")
    m = createMarking(net, path+".formula")
    start = time.time()
    answer = isCoverable(net, m, log=log)
    stop = time.time()
    print("--Coverability check------")
    print("Petri net:", path)
    print("Number of places:", net.p)
    print("Number of transitions:", net.t)
    print("Coverability output:", answer)
    print("Check time:", stop-start)
    print("--------------------------")


def runSeparator(path, log=False):
    net = createNet(path+".lola")
    m = createMarking(net, path+".formula")
    start = time.time()
    sep = generateLocallyClosedBiSeparator(net, net.transitions, net.marking, m)
    step = time.time()
    check = checkLocallyClosedBiSeparatorWithSyndrome(net, sep, net.marking, m, log=log)
    stop = time.time()
    nb_atomic_check = 0
    for clause in sep.clauses:
        for t in net.transitions:
            nb_atomic_check += len(clause.forwardSyndrome[t.name][1])
            nb_atomic_check += len(clause.backwardSyndrome[t.name][1])
    print("--Separator generation----")
    print("Petri net:", path)
    print("Number of places:", net.p)
    print("Number of transitions:", net.t)
    print("Separator size:", sep.getSize())
    print("Syndrome check:", check[0])
    print("Number of atomic checks:", nb_atomic_check)
    print("Number of performed atomic checks:", check[2])
    print("Generation time:", step-start)
    print("Syndrome check time:", stop-step)
    print("Paralelized syndrome check time:", check[1])
    print("--------------------------")



path = "./nets/unreachable/homemade/bad-case-20"
net = createNet(path+".lola")
m = createMarking(net, path+".formula")
sep = generateLocallyClosedBiSeparator(net, net.transitions, net.marking, m)
print("Number of places:", net.p)
print("Number of transitions:", net.t)
print("Separator size:", sep.getSize())
nb_atomic_check = 0
for clause in sep.clauses:
    for t in net.transitions:
        nb_atomic_check += len(clause.forwardSyndrome[t.name][1])
        nb_atomic_check += len(clause.backwardSyndrome[t.name][1])
print(nb_atomic_check)




# runReachability("./nets/unreachable/homemade/figure-1-esparza")
# runReachability("./nets/unreachable/homemade/figure-1a-haddad")
# runReachability("./nets/unreachable/homemade/bad-case-1")
# runReachability("./nets/unreachable/homemade/bad-case-2")
# runReachability("./nets/unreachable/homemade/bad-case-5")

# runSeparator("./nets/unreachable/homemade/bad-case-20", True)
# runSeparator("./nets/unreachable/homemade/figure-1a-haddad")
# runSeparator("./nets/unreachable/homemade/bad-case-1")
# runSeparator("./nets/unreachable/homemade/bad-case-2")
# runSeparator("./nets/unreachable/homemade/bad-case-5")



# path = "./nets/unreachable/homemade/"
# files = [f[:-5] for f in listdir(path) if f[-3]=="o"]
# for file in files:
#     print("**************************")
#     runReachability(path+file)
#     runSeparator(path+file)