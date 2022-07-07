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
sep = generateLocallyClosedBiSeparator(net, net.transitions, net.marking, m)
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


sep.print()

# ans = checkLocallyClosedBiSeparator(net, sep, net.marking, m)
# print(ans)


c1 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1]), True)])
c2 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,-1]), np.array([0,0,0,1]), True)])
c3 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,0]), np.array([1,1,0,0]), True)])
c4 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([1,1,0,0]), np.array([0,0,0,0])), Atom(np.array([0,0,-1,0]), np.array([0,0,-1,0]))])
form = Formula([c1,c2,c3,c4])

ans = checkLocallyClosedBiSeparator(net, form, net.marking, m)
print(ans)

t1 = list(net.places[0].postset)[0]
t2 = list(net.places[0].postset)[2]
t3 = list(net.places[0].postset)[1]
t4 = list(net.places[2].postset)[0]

a44s = Atom(np.array([0,0,0,1]), np.array([0,0,0,1]), True)
a44 = Atom(np.array([0,0,0,1]), np.array([0,0,0,1]))
am44s = Atom(np.array([0,0,0,-1]), np.array([0,0,0,1]), True)
a12ps = Atom(np.array([0,0,0,0]), np.array([1,1,0,0]), True)
a12 = Atom(np.array([1,1,0,0]), np.array([0,0,0,0]))
am3m3p = Atom(np.array([0,0,-1,0]), np.array([0,0,-1,0]))

# print("=============")
# print(atomicImplication(net, a44, a44, t3))
# print(atomicImplication(net, a12, a44, t3))
# print(atomicImplication(net, am3m3p, a44, t3))
# print("=============")
# print(atomicImplication(net, a44, a12, t3))
# print(atomicImplication(net, a12, a12, t3))
# print(atomicImplication(net, am3m3p, a12, t3))
# print("=============")
# print(atomicImplication(net, a44, am3m3p, t3))
# print(atomicImplication(net, a12, am3m3p, t3))
# print(atomicImplication(net, am3m3p, am3m3p, t3))


relations = [
    (c1,c1,t1),(c1,c1,t2),(c1,c1,t3),(c1,c1,t4),
    (c2,c1,t4),(c2,c2,t1),(c2,c2,t2),(c2,c2,t3),
    (c3,c1,t4),(c3,c2,t2),(c3,c3,t1),(c3,c3,t3),
    (c4,c1,t4),(c4,c2,t2),(c4,c4,t1),(c4,c4,t3)
]

print("=============")
for (c,cp,t) in relations:
    flag_i = True
    for atom_i in c.atoms:
        flag_j = False
        for atom_j in cp.atoms:
            if atomicImplication(net, atom_i, atom_j, t):
                flag_j = True
                break
        flag_i &= flag_j
    print(flag_i)

# result = True
# c = c1
# cp = c1
# t = t1
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c1
# cp = c1
# t = t2
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c1
# cp = c1
# t = t3
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c1
# cp = c1
# t = t4
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)


# result = True
# c = c2
# cp = c1
# t = t4
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c2
# cp = c2
# t = t1
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c2
# cp = c2
# t = t2
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c2
# cp = c2
# t = t3
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c3
# cp = c1
# t = t4
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c3
# cp = c2
# t = t2
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c3
# cp = c3
# t = t1
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c3
# cp = c3
# t = t3
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c4
# cp = c1
# t = t4
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c4
# cp = c2
# t = t2
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c4
# cp = c4
# t = t1
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)

# result = True
# c = c4
# cp = c4
# t = t3
# for aj in cp.atoms:
#     flag = False
#     for ai in c.atoms:
#         if atomicImplication(net, ai, aj, t):
#             flag = True
#             break
#     result &= flag
# print(result)