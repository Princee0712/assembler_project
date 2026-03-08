import sys

def readfile(name):
    lines = []
    with open (name, "r") as f :
        for i in f :
            x = i.strip()
            if x != "":
                lines.append(x)
    return lines 

def error(line):
    print ("Error on line", line)
    sys.exit()

inputfile = sys.argv[1]
outputfile = sys.argv[2]
program = readfile(inputfile)

# convert num into binary
def binary(num,bit):
    n = int(num)
    if n < 0
        n = (1<<bit)+n
    b = bin(n)[2:]
    return b.zfill(bit)

# checking immediate range
 def checkimm(num, bit, line):
     n = int(num)
     low = -(2**(bit-1))
     high = (2**(bit-1))-1
     
     if n < low or n > high:
         error(line)

# halt validation
haltcount = 0
 for i , line in enumerate(program,1):
     clean = line.replace(" ", "")
     if clean == "beqzero,zero,0":
         haltcount +=1
     if clean =="beqzero,zero,0" and i != len(program):
         error(i)
     if haltcount == 0:
         error (len(program))
          