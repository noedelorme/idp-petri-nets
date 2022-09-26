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

def runBenchmark(path, log=False):
    runReachability(path, log=log)
    runSeparator(path, log=log)




runBenchmark("./nets/unreachable/homemade/figure-1-esparza")
# runBenchmark("./nets/unreachable/homemade/figure-1a-haddad")
# runBenchmark("./nets/unreachable/homemade/bad-case-1")
# runBenchmark("./nets/unreachable/homemade/bad-case-2")
# runBenchmark("./nets/unreachable/homemade/bad-case-5")
# runBenchmark("./nets/unreachable/homemade/mine-6")
# runBenchmark("./nets/unreachable/homemade/mine-7")
# runBenchmark("./nets/unreachable/coverability/mist-pn/kanban")
# runBenchmark("./nets/unreachable/coverability/mist-pn/leabasicapproach")
# runBenchmark("./nets/unreachable/coverability/mist-pn/pncsacover")
# runBenchmark("./nets/unreachable/coverability/mist-pn/pncsasemiliv")
# runBenchmark("./nets/unreachable/coverability/soter/finite_leader__single_leader__depth_0")
# runBenchmark("./nets/unreachable/coverability/soter/firewall__no_pred_called_with_zero__depth_0")
# runBenchmark("./nets/unreachable/coverability/soter/howait__all_workers_finished_if_wait_over__depth_0")
# runBenchmark("./nets/unreachable/coverability/soter/howait__all_workers_finished_if_wait_over__depth_1")
# runBenchmark("./nets/unreachable/coverability/soter/howait__all_workers_finished_if_wait_over__depth_2")
# runBenchmark("./nets/unreachable/coverability/soter/safe_send__sending_to_non-pid__depth_0")
# runBenchmark("./nets/unreachable/coverability/soter/stutter__we_abhorr_as__depth_0")
# runBenchmark("./nets/unreachable/coverability/soter/stutter__we_abhorr_as__depth_1")
# runBenchmark("./nets/unreachable/coverability/soter/stutter__we_abhorr_as__depth_2")
# runBenchmark("./nets/unreachable/coverability/soter/unsafe_send__sending_to_non-pid__depth_0")
# runBenchmark("./nets/unreachable/coverability/soter/unsafe_send__sending_to_non-pid__depth_1")
# runBenchmark("./nets/unreachable/coverability/soter/unsafe_send__sending_to_non-pid__depth_2")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/Function_Pointer3_vs_satabs.2")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/lu-fig2_fixed_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/lu-fig2_fixed_vs_satabs.2")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/lu-fig2_fixed_vs_satabs.3")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/peterson_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/peterson_vs_satabs.2")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/pthread5_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/pthread5_vs_satabs.2")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/pthread5_vs_satabs.3")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/pthread5_vs_satabs.4")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/rand_cas_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/rand_lock_p0_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/rand_lock_p0_vs_satabs.2")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/rand_lock_p0_vs_satabs.3")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/simple_loop5_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/spin2003_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/spin2003_vs_satabs.2")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/stack_cas_p0_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/stack_cas_p0_vs_satabs.2")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/stack_cas_p0_vs_satabs.3")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/stack_lock_p0_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/stack_lock_p0_vs_satabs.2")
# runBenchmark("./nets/unreachable/coverability/wahl-kroening/szymanski_vs_satabs.1")
# runBenchmark("./nets/unreachable/coverability/bug-tracking/x0_PENDING_q3_buggy")


# runBenchmark("./nets/unreachable/coverability/wahl-kroening/simple_loop5_vs_satabs.2")
# runBenchmark("./nets/unreachable/sypet/joda17")

