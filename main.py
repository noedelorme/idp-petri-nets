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

ans = checkLocallyClosedBiSeparator(net, sep, net.marking, m)
print(ans)



trans = [None, None, None, None]
for t in net.transitions:
    trans[t.id] = t
t1 = trans[0]
t2 = trans[1]
t3 = trans[2]
t4 = trans[3]


# c1 = sep.clauses[0]
# c2 = sep.clauses[1]
# c3 = sep.clauses[2]

# a11 = c1.atoms[0]
# a21 = c2.atoms[0]
# a22 = c2.atoms[1]
# a31 = c3.atoms[0]
# a32 = c3.atoms[1]
# a33 = c3.atoms[2]

# print("=============")
# print(atomicImplication(net, a31, a31, t1))
# print(atomicImplication(net, a31, a32, t1))
# print(atomicImplication(net, a31, a33, t1))
# print("=============")
# print(atomicImplication(net, a32, a31, t1))
# print(atomicImplication(net, a32, a32, t1))
# print(atomicImplication(net, a32, a33, t1))
# print("=============")
# print(atomicImplication(net, a33, a31, t1))
# print(atomicImplication(net, a33, a32, t1))
# print(atomicImplication(net, a33, a33, t1))


# relations = [
#     (c3,c1,t4),(c3,c2,t4),(c3,c3,t4),
# ]

# # Def of clause c t-implies clause cp according to the big formula
# print("=============")
# for (c,cp,t) in relations:
#     flag_i = True
#     for atom_i in c.atoms:
#         flag_j = False
#         for atom_j in cp.atoms:
#             if atomicImplication(net, atom_i, atom_j, t):
#                 flag_j = True
#                 break
#         flag_i &= flag_j
#     print(flag_i)

# Def of clause c t-implies clause cp according to 4.1
# print("=============")
# for (c,cp,t) in relations:
#     flag_j = True
#     for atom_j in cp.atoms:
#         flag_i = False
#         for atom_i in c.atoms:
#             if atomicImplication(net, atom_i, atom_j, t):
#                 flag_i = True
#                 break
#         flag_j &= flag_i
#     print(flag_j)

















c1 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1]), True)])
c2 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,-1]), np.array([0,0,0,1]), True)])
c3 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([0,0,0,0]), np.array([1,1,0,0]), True)])
c4 = Clause([Atom(np.array([0,0,0,1]), np.array([0,0,0,1])), Atom(np.array([1,1,0,0]), np.array([0,0,0,0])), Atom(np.array([0,0,-1,0]), np.array([0,0,-1,0]))])
form = Formula([c1,c2,c3,c4])

# ans = checkLocallyClosedBiSeparator(net, form, net.marking, m)
# print(ans)

# a44s = Atom(np.array([0,0,0,1]), np.array([0,0,0,1]), True)
# a44 = Atom(np.array([0,0,0,1]), np.array([0,0,0,1]))
# am44s = Atom(np.array([0,0,0,-1]), np.array([0,0,0,1]), True)
# a12ps = Atom(np.array([0,0,0,0]), np.array([1,1,0,0]), True)
# a12 = Atom(np.array([1,1,0,0]), np.array([0,0,0,0]))
# am3m3p = Atom(np.array([0,0,-1,0]), np.array([0,0,-1,0]))

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

# Def of clause c t-implies clause cp according to the big formula
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

# # Def of clause c t-implies clause cp according to 4.1
# print("=============")
# for (c,cp,t) in relations:
#     flag_j = True
#     for atom_j in cp.atoms:
#         flag_i = False
#         for atom_i in c.atoms:
#             if atomicImplication(net, atom_i, atom_j, t):
#                 flag_i = True
#                 break
#         flag_j &= flag_i
#     print(flag_j)