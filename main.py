from unittest import result
import numpy as np
from scipy.sparse import csr_matrix
import time
from z3 import *
from objects.Net import Net
from objects.Formula import Formula, Clause, Atom
from tools.reader import *
from tasks.reachability import *
from tasks.separators import *


def runReachability(path):
    net = createNet(path+".lola")
    m = createMarking(net, path+".formula")
    start = time.time()
    answer = isReachable(net, m, log=False)
    stop = time.time()
    print("--------------------------")
    print("Petri net:", path)
    print("Number of places:", net.p)
    print("Number of transitions:", net.t)
    print("Reachability output:", answer)
    print("Check time:", stop-start)
    print("--------------------------")


def runSeparator(path):
    net = createNet(path+".lola")
    m = createMarking(net, path+".formula")
    start = time.time()
    sep = generateLocallyClosedBiSeparator(net, net.transitions, net.marking, m)
    step1 = time.time()
    check1 = checkLocallyClosedBiSeparator(net, sep, net.marking, m)
    step2 = time.time()
    check2 = checkLocallyClosedBiSeparatorWithSyndrome(net, sep, net.marking, m)
    stop = time.time()
    print("--------------------------")
    print("Petri net:", path)
    print("Number of places:", net.p)
    print("Number of transitions:", net.t)
    print("Separator size:", sep.getSize())
    print("Standard check:", check1)
    print("Syndrome check:", check2)
    print("Generation time:", step1-start)
    print("Standrad check time:", step2-step1)
    print("Syndrome check time:", stop-step2)
    print("--------------------------")


# runReachability("./nets/reachability/homemade/figure-1-esparza")
# runReachability("./nets/reachability/homemade/figure-1a-haddad")
# runReachability("./nets/reachability/homemade/bad-case-1")
# runReachability("./nets/reachability/homemade/bad-case-2")
# runReachability("./nets/reachability/homemade/bad-case-5")


runSeparator("./nets/reachability/homemade/figure-1-esparza")
# runSeparator("./nets/reachability/homemade/figure-1a-haddad")
# runSeparator("./nets/reachability/homemade/bad-case-1")
# runSeparator("./nets/reachability/homemade/bad-case-2")
# runSeparator("./nets/reachability/homemade/bad-case-5")






# # Separator from Example 2 of [1]
# path = "./nets/reachability/homemade/figure-1-esparza"
# net = createNet(path+".lola")
# m = createMarking(net, path+".formula")
# c1 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1]), True)])
# c2 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,-1]), np.array([0,0,0,1]), True)])
# c3 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,0]), np.array([1,1,0,0]), True)])
# c4 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([1,1,0,0]), np.array([0,0,0,0])), Atom(np.array([0,0,-1,0]), np.array([0,0,-1,0]))])
# form = Formula([c1,c2,c3,c4])
# ans = checkLocallyClosedBiSeparator(net, form, net.marking, m)
# print(ans)
