import numpy as np
from scipy.sparse import csr_matrix
import time
from z3 import *
from objects.Net import Net
from tools.reader import *
from tasks.reachability import *
from tasks.separators import *


# path = "./nets/reachability/random-walk/dekker_vs_satabs.2_multi_100_0"
# net = createNet(path+".lola")
# m = createMarking(net, path+".formula")
# start = time.time()
# answer = isReachable(net, m)
# stop = time.time()
# print("--------------------------")
# print("Petri net:", path)
# print("Number of places:", net.p)
# print("Number of transitions:", net.t)
# print("Reachability output:", answer)
# print("Time elapsed:", stop-start)
# print("--------------------------")


# path = "./nets/coverability/mist-pn/kanban"
# net = createNet(path+".lola")
# m = createMarking(net, path+".formula")
# start = time.time()
# answer = isCoverable(net, m)
# stop = time.time()
# print("--------------------------")
# print("Petri net:", path)
# print("Number of places:", net.p)
# print("Number of transitions:", net.t)
# print("Coverability output:", answer)
# print("Time elapsed:", stop-start)
# print("--------------------------")

path = "./nets/reachability/homemade/figure-1-esparza"
net = createNet(path+".lola")
m = createMarking(net, path+".formula")
start = time.time()
sep = locallyClosedBiSeparator(net, net.transitions, net.marking, m)
stop = time.time()
print("--------------------------")
print("Petri net:", path)
print("Number of places:", net.p)
print("Number of transitions:", net.t)
print("Separator size:", sep.getSize())
# sep.print()
check = sep.check(net.marking, net.marking) and sep.check(m, m) and not sep.check(net.marking, m)
print("Sanity check:", check)
print("Time elapsed:", stop-start)
print("--------------------------")
