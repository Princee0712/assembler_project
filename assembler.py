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
   
   "a0" : "01010", "a1" : "01011", "a2" : "01100", "a3" : "01101", "a4" : "01110", "a5" : "01111", 
   "a6" : "10000", "a7" : "10001", 
   
   "fp" : "01000", "s0" : "01000", "s1" : "01001", "s2" : "10010", "s3" : "10011", "s4" : "10100", "s5" : "10101", "s6" : "10110", 
   "s7" : "10111", "s8" : "11000", "s9" : "11001", "s10" : "11010", "s11" : "11011", 
}

def checkreg(r,line):
    if r not in registers:
        error(line)
        
        
# opcode table

opcode = {
    "add": "0110011", "sub": "0110011", "slt": "0110011", "sltu": "0110011", "xor": "0110011", 
    "sll": "0110011", "srl": "0110011", "or": "0110011", "and": "0110011",
    "sw": "0100011", "lw": "0000011",
    "addi": "0010011", "sltiu": "0010011", "jalr": "1100111",
    "beq": "1100011", "bne": "1100011", 
    "blt": "1100011", "bge": "1100011", "bltu": "1100011", "bgeu": "1100011", "lui": "0110111", 
    "auipc": "0010111", "jal": "1101111"
     
}

funct3 = {
    "add":"000", "sub":"000", "slt":"010", "sltu":"011", 
    "xor":"100", "sll":"001", "srl":"101", "or":"110", 
    "and":"111", "lw":"010", "addi":"000", "sltiu":"011", 
    "jalr":"000", "sw":"010", "beq":"000", "bne":"001", 
    "blt":"100", "bge":"101", "bltu":"110", "bgeu":"111", 
}

funct7 = {
    "add":"0000000", "sub":"0100000", "slt":"0000000", 
    "sltu":"0000000", "xor":"0000000", "srl":"0000000", 
    "and":"0000000", "or":"0000000"
}

# instruction groups

allinst = ["add","sub","slt","sltu","xor",
           "sll","srl","or","and","addi",
          "sltiu","jalr","sw","beq","bne",
          "blt","bge","bltu","bgeu","lw",
         "lui","auipc","jal"]

rtype = ["add","sub","slt","sltu","xor","sll","srl","or","and"]

itype = ["lw","addi","sltiu","jalr"]

stype = ["sw"]

btype = ["beq","bne","blt","bge","bltu","bgeu"]

utype = ["lui","auipc"]

jtype = ["jal"]

# Assembler loop
output = []
pc = 0 
for lineno, line in enumerate(program,1):
    x = line.replace(" ", ",")
    x = x.replace("(",",")
    x = x.replace(")", "")
    
    parts = x.split(",")
    op = parts[0]
    
    if op not in allinst:
    error(lineno)