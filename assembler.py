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


# label detection
labletable = {}
address = 0 
for i, line in enumerate(program):
    if ":" in line:
        parts = line.split(":", 1)
        label = part[0].strip()
        inst = parts[1].strip()
        
        labletable[label] = address
        program[i] = inst 
    address += 4
    

# register table and check function

registers = {
   "zero" : "00000", "ra" : "00001", "sp" : "00010", "tp" : "00100",
   "gp" : "00011", "t0" : "00101", "t1" : " 00110", "t2" : "00111",
   "t3" : "11100" , "t4" : "11101" , "t5" : " 11110", "t6" : "11111",
   
   "a0" : "01010", "a1" : "01011", "a2" : "01100", "a3" : "01101", "a4" : "01110", "a5" : "", 
   "a6" : "10000", "a7" : "10001", 
   
   "fp" : "01000", "s0" : "01000", "s1" : "01001", "s2" : "10010", "s3" : "10011", "s4" : "10100", "s5" : "10101", "s6" : "10110", 
   "s7" : "10111", "s8" : "11000", "s9" : "11001", "s10" : "11010", "s11" : "11011", 
}

def checkreg(r,line):
    if r not in registers:
        error(line)
        
        
# opcode
