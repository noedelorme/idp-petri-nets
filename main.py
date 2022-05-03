from z3 import * 
from net import Net

if __name__ == "__main__": 
    myNet = Net("./nets/formated/mine-2.in")
    print(myNet.isFireable(myNet.transitions))