import numpy as np
from scipy.sparse import csr_matrix
import time
from z3 import *
from objects.Net import Net
from tools.reader import *
from tasks.reachability import *
from tasks.separators import *


# path = "./nets/reachability/homemade/bad-case-5"
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

path = "./nets/reachability/random-walk/Boop_simple_vf_satabs.2_multi_100_0"
net = createNet(path+".lola")
b = np.zeros(net.p)
b[0]=1
b[5]=1
b[10]=1
b[16]=1
a = largestSiphon(net, net.transitions, b)
print(a)