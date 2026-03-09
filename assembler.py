import sys
# error function
def error(line):
    print("Error on line", line)
    sys.exit()

# this will read the file
def readfile(name):
    lines = []
    with open(name, "r") as f:
        for line in f:
            x = line.strip()
            if x != "":
                lines.append(x)

    return lines

# registers table and checking
registers = {
"zero":"00000","ra":"00001","sp":"00010","gp":"00011","tp":"00100",
"t0":"00101","t1":"00110","t2":"00111",
"s0":"01000","fp":"01000","s1":"01001",
"a0":"01010","a1":"01011","a2":"01100","a3":"01101",
"a4":"01110","a5":"01111","a6":"10000","a7":"10001",
"s2":"10010","s3":"10011","s4":"10100","s5":"10101",
"s6":"10110","s7":"10111","s8":"11000","s9":"11001",
"s10":"11010","s11":"11011",
"t3":"11100","t4":"11101","t5":"11110","t6":"11111"
}

def checkreg(r,line):
    if r not in registers:
        error(line)

# convert num into binary
def binary(num,bits):
    n = int(num)

    if n < 0:
        n = (1 << bits) + n

    b = bin(n)[2:]
    return b.zfill(bits)

# this func will check immediate range
def checkimm(num,bits,line):

    n = int(num)
    low = -(2**(bits-1))
    high = (2**(bits-1)) - 1

    if n < low or n > high:
        error(line)

# opcode table
opcode = {
"add":"0110011","sub":"0110011","slt":"0110011","sltu":"0110011",
"xor":"0110011","sll":"0110011","srl":"0110011","or":"0110011","and":"0110011",
"lw":"0000011","addi":"0010011","sltiu":"0010011","jalr":"1100111",
"sw":"0100011",
"beq":"1100011","bne":"1100011","blt":"1100011",
"bge":"1100011","bltu":"1100011","bgeu":"1100011",
"lui":"0110111","auipc":"0010111",
"jal":"1101111"
}

funct3 = {

"add":"000","sub":"000","slt":"010","sltu":"011",
"xor":"100","sll":"001","srl":"101","or":"110","and":"111",
"lw":"010","addi":"000","sltiu":"011","jalr":"000",
"sw":"010",
"beq":"000","bne":"001","blt":"100",
"bge":"101","bltu":"110","bgeu":"111"
}

funct7 = {
    "add":"0000000", "sub":"0100000", "slt":"0000000", 
    "sltu":"0000000", "xor":"0000000", "srl":"0000000", 
    "and":"0000000", "or":"0000000"}


# instruction grp
rtype = ["add","sub","slt","sltu","xor","sll","srl","or","and"]

itype = ["lw","addi","sltiu","jalr"]

stype = ["sw"]

btype = ["beq","bne","blt","bge","bltu","bgeu"]

utype = ["lui","auipc"]

jtype = ["jal"]


# input
inputfile = sys.argv[1]
outputfile = sys.argv[2]

program = readfile(inputfile)

#lable detection
labeltable = {}
address = 0

for i,line in enumerate(program):

    if ":" in line:
        label,inst = line.split(":",1)
        labeltable[label.strip()] = address
        program[i] = inst.strip()

    else:
        program[i] = line.strip()

    address += 4
program = [x for x in program if x != ""]


# checking virtual halt
halt_found = False

for i,line in enumerate(program):
    temp = line.replace(","," ")
    parts = temp.split()
    if len(parts) == 4:

        if parts[0]=="beq" and parts[1]=="zero" and parts[2]=="zero":
            try:
                if int(parts[3]) == 0:
                    halt_found = True
                    if i != len(program)-1:
                        error(i+1)
            except:
                pass
if not halt_found:
    error(len(program))


# parsing loop
output = []
pc = 0

for lineno,line in enumerate(program,1):
    line = line.replace(","," ")
    line = line.replace("("," ")
    line = line.replace(")"," ")

    parts = line.split()
    if len(parts) == 0:
        continue

    op = parts[0]
    # R-type encoding
    if op in rtype:

        if len(parts)!=4:
            error(lineno)

        checkreg(parts[1],lineno)
        checkreg(parts[2],lineno)
        checkreg(parts[3],lineno)
        rd = registers[parts[1]]
        rs1 = registers[parts[2]]
        rs2 = registers[parts[3]]

        inst = funct7[op] + rs2 + rs1 + funct3[op] + rd + opcode[op]

        output.append(inst)


    # I-type encoding
    elif op in itype:
        if len(parts)!=4:
            error(lineno)

        if op=="lw":
            checkreg(parts[1],lineno)
            checkreg(parts[3],lineno)

            checkimm(parts[2],12,lineno)
            rd = registers[parts[1]]
            rs1 = registers[parts[3]]
            imm = binary(parts[2],12)

        else:
            checkreg(parts[1],lineno)
            checkreg(parts[2],lineno)

            checkimm(parts[3],12,lineno)

            rd = registers[parts[1]]
            rs1 = registers[parts[2]]
            imm = binary(parts[3],12)
        inst = imm + rs1 + funct3[op] + rd + opcode[op]

        output.append(inst)


    # S-type encoding
    elif op in stype:

        if len(parts)!=4:
            error(lineno)
        checkreg(parts[1],lineno)
        checkreg(parts[3],lineno)

        checkimm(parts[2],12,lineno)

        rs2 = registers[parts[1]]
        rs1 = registers[parts[3]]
        imm = binary(parts[2],12)
        inst = imm[0:7] + rs2 + rs1 + funct3[op] + imm[7:12] + opcode[op]

        output.append(inst)


    # B-type encoding
    elif op in btype:

        if len(parts)!=4:
            error(lineno)
        checkreg(parts[1],lineno)
        checkreg(parts[2],lineno)

        if parts[3] in labeltable:
            offset = labeltable[parts[3]] - pc
        else:
            offset = int(parts[3])
        checkimm(offset,13,lineno)
        imm = binary(offset,13)
        inst = (imm[0] + imm[2:8] + registers[parts[2]] + registers[parts[1]] + funct3[op] + imm[8:12] + imm[1] + opcode[op])

        output.append(inst)


    # U-type encoding
    elif op in utype:

        if len(parts)!=3:
            error(lineno)
        checkreg(parts[1],lineno)
        checkimm(parts[2],20,lineno)

        rd = registers[parts[1]]
        imm = binary(parts[2],20)
        inst = imm + rd + opcode[op]

        output.append(inst)
    # J-type encoding
    elif op in jtype:
        if len(parts)!=3:
            error(lineno)
        checkreg(parts[1],lineno)

        if parts[2] in labeltable:
            offset = labeltable[parts[2]] - pc
        else:
            offset = int(parts[2])
        imm = binary(offset,21)
        inst = imm[0] + imm[10:20] + imm[9] + imm[1:9] + registers[parts[1]] + opcode[op]

        output.append(inst)
    else:
        error(lineno)
        
    pc += 4

# this will create output file
with open(outputfile,"w") as O:
    for inst in output:
        O.write(inst + "\n")