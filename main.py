import numpy as np
from z3 import *
from net import Net
from reachability import *
from separators import *

if __name__ == "__main__": 
    myNet = Net("./nets/formated/mine-2.in")
    myNet.print()

    print(isFireable(myNet, myNet.transitions, myNet.marking, False))