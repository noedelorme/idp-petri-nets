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
from tasks.simplify import *


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
    step = time.time()
    check = checkLocallyClosedBiSeparatorWithSyndrome(net, sep, net.marking, m)
    stop = time.time()
    print("--------------------------")
    print("Petri net:", path)
    print("Number of places:", net.p)
    print("Number of transitions:", net.t)
    print("Separator size:", sep.getSize())
    print("Syndrome check:", check[0])
    print("Generation time:", step-start)
    print("Syndrome check time:", stop-step)
    print("Paralelized syndrome check time:", check[1])
    print("--------------------------")


# runReachability("./nets/reachability/homemade/figure-1-esparza")
# runReachability("./nets/reachability/homemade/figure-1a-haddad")
# runReachability("./nets/reachability/homemade/bad-case-1")
# runReachability("./nets/reachability/homemade/bad-case-2")
# runReachability("./nets/reachability/homemade/bad-case-5")
# runReachability("./nets/reachability/dekker_vs_satabs.2_multi_100_0")


# runSeparator("./nets/reachability/homemade/figure-1-esparza")
# runSeparator("./nets/reachability/homemade/figure-1a-haddad")
# runSeparator("./nets/reachability/homemade/bad-case-1")
# runSeparator("./nets/reachability/homemade/bad-case-2")
# runSeparator("./nets/reachability/homemade/bad-case-5")
# runSeparator("./nets/reachability/dekker_vs_satabs.2_multi_100_0")
