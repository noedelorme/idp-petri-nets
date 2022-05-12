import numpy as np
from z3 import *
from net import Net
from reachability import *
from separators import *

if __name__ == "__main__":
    
    myNet = Net("./nets/formated/figure-1a-haddad.in")
    print(isReachable(myNet, np.array([0, 1, 0, 0])))

    # mine3 = Net("./nets/formated/mine-3.in")
    # print(isReachable(mine3, np.array([1.75, 0.75, 0.5, 0.5, 0, 1])))
    # print(isReachable(mine3, np.array([1.75, 0.75, 0, 0.5, 0.5, 0.5])))
    # print(isReachable(mine3, np.array([1.5, 0.5, 0.5, 0, 0.5, 0.5])))
    # print(isReachable(mine3, np.array([1.5, 0.5, 0.5, 0.5, 0.5, 0.5])))
    # print(isReachable(mine3, np.array([1.5, 0.5, 0.5, 0, 1.1, 0])))

    # mine4 = Net("./nets/formated/mine-4.in")
    # print(isReachable(mine4, np.array([1, 0, 2, 0.5, 0, 1])))
    # print(isReachable(mine4, np.array([1, 0, 1.5, 0.5, 0.5, 0.5])))
    # print(isReachable(mine4, np.array([1, 0, 1, 0.5, 1, 0])))

    # mine1 = Net("./nets/formated/mine-1.in")
    # print(isReachable(mine1, np.array([1, 1, 1, 2])))