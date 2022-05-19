import numpy as np
import time
from z3 import *
from objects.Net import Net
from tools.reader import *
from tasks.reachability import *
from tasks.separators import *


path = "./nets/homemade/mine-1"
net = createNet(path+".lola")
m = createMarking(net, path+".formula")
start = time.time()
answer = isReachable(net, m)
stop = time.time()
print("Output:", answer)
print("Time elapsed:", stop-start)