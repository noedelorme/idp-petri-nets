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


# path = "./nets/reachability/homemade/bad-case-1"
# net = createNet(path+".lola")
# m = createMarking(net, path+".formula")
# start = time.time()
# answer = isReachable(net, m, log=False)
# stop = time.time()
# print("--------------------------")
# print("Petri net:", path)
# print("Number of places:", net.p)
# print("Number of transitions:", net.t)
# print("Reachability output:", answer)
# print("Check time:", stop-start)
# print("--------------------------")


path = "./nets/reachability/homemade/figure-1-esparza"
net = createNet(path+".lola")
m = createMarking(net, path+".formula")
start = time.time()
sep = generateLocallyClosedBiSeparator(net, net.transitions, net.marking, m)
step = time.time()
check = checkLocallyClosedBiSeparator(net, sep, net.marking, m)
stop = time.time()
print("--------------------------")
print("Petri net:", path)
print("Number of places:", net.p)
print("Number of transitions:", net.t)
print("Separator size:", sep.getSize())
print("Check:", check)
print("Generation time:", step-start)
print("Check time:", stop-step)
print("--------------------------")


c1 = Clause([Atom(np.array([0,1,0,1]), np.array([0,-0.4,0,1]))])
c2 = Clause([Atom(np.array([0,0,1,1]), np.array([2,0,0,1]), True)])
form = Formula([c1,c2])
ans = checkLocallyClosedBiSeparator(net, form, net.marking, m)
print(ans)



# t = list(net.transitions)[0]
# print(t)
# print(clauseImplication(net, sep.clauses[3], sep.clauses[0], t))
# print(clauseImplication(net, sep.clauses[3], sep.clauses[1], t))
# print(clauseImplication(net, sep.clauses[3], sep.clauses[2], t))
# print(clauseImplication(net, sep.clauses[3], sep.clauses[3], t))


# # Separator from Example 2 of [1]
# c1 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1]), True)])
# c2 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,-1]), np.array([0,0,0,1]), True)])
# c3 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,0]), np.array([1,1,0,0]), True)])
# c4 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([1,1,0,0]), np.array([0,0,0,0])), Atom(np.array([0,0,-1,0]), np.array([0,0,-1,0]))])
# form = Formula([c1,c2,c3,c4])
# ans = checkLocallyClosedBiSeparator(net, form, net.marking, m)
# print(ans)