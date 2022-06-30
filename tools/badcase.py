# number of places: 2*size+2
# number of transitions: 3*size+1

size = 2
path = "./nets/reachability/homemade/bad-case-"+str(size)

with open(path+".lola", "a") as file:
    file.write("PLACE\n")
    first = "s0_2"
    file.write(first+",")
    for i in range(1,size+1):
        text = "s"+str(i)+"_1,s"+str(i)+"_2,"
        file.write(text)
    last = "s"+str(size+1)+"_1"
    file.write(last+";\n\n")

    file.write("MARKING\n")
    file.write(last+": 1;\n\n")

    for i in range(1, size+1):
        file.write("TRANSITION t"+str(i)+"_1\n")
        file.write("CONSUME s"+str(i-1)+"_2: 1, s"+str(i)+"_1: 1;\n")
        file.write("PRODUCE s"+str(i-1)+"_2: 1, s"+str(i)+"_2: 1;\n\n")

        file.write("TRANSITION t"+str(i)+"_2\n")
        file.write("CONSUME ;\n")
        file.write("PRODUCE s"+str(i)+"_1: 1, s"+str(i)+"_2: 1;\n\n")

        file.write("TRANSITION t"+str(i)+"_3\n")
        file.write("CONSUME s"+str(i)+"_2: 1;\n")
        file.write("PRODUCE ;\n\n")

    file.write("TRANSITION t"+str(size+1)+"_1\n")
    file.write("CONSUME s"+str(size)+"_2: 1, s"+str(size+1)+"_1: 1;\n")
    file.write("PRODUCE s"+str(size)+"_2: 1;\n\n")

with open(path+".formula", "a") as file:
    file.write("EF (")
    file.write("s0_2 = 0 AND ")
    for i in range(1,size+1):
        text = "s"+str(i)+"_1 = 0 AND s"+str(i)+"_2 = 0 AND "
        file.write(text)
    file.write("s"+str(size+1)+"_1 = 0)\n")