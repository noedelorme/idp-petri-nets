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


# path = "./nets/reachability/homemade/bad-case-5"
# net = createNet(path+".lola")
# m = createMarking(net, path+".formula")
# start = time.time()
# answer = isReachable(net, m, log=True)
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
# answer = isCoverable(net, m, log=True)
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
sep = generateLocallyClosedBiSeparator(net, net.transitions, net.marking, m)
stop = time.time()
print("--------------------------")
print("Petri net:", path)
print("Number of places:", net.p)
print("Number of transitions:", net.t)
print("Separator size:", sep.getSize())
print("Check:", checkLocallyClosedBiSeparator(net, sep, net.marking, m))
print("Time elapsed:", stop-start)
print("--------------------------")


# # Separator from Example 2 of [1]
# c1 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1]), True)])
# c2 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,-1]), np.array([0,0,0,1]), True)])
# c3 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,0]), np.array([1,1,0,0]), True)])
# c4 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([1,1,0,0]), np.array([0,0,0,0])), Atom(np.array([0,0,-1,0]), np.array([0,0,-1,0]))])
# form = Formula([c1,c2,c3,c4])
# ans = checkLocallyClosedBiSeparator(net, form, net.marking, m)
# print(ans)