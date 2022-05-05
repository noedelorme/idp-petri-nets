from z3 import *
import numpy as np
from net import Net

if __name__ == "__main__": 
    myNet = Net("./nets/formated/mine-2.in")
    #print(myNet.isFireable(myNet.transitions))
    print(myNet.isReachable(myNet.marking))
    print(myNet.isReachable([1,1,1,1,0,0]))