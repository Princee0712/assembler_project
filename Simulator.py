import sys

WORD = 32
MASK32 = 0xFFFFFFFF

def sext(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def fmt32(value):
    v = value & MASK32
    return "0b" + format(v, "032b")

class Memory:
    def __init__(self):
        self._mem = {}

    def load_word(self, addr):
        addr = addr & MASK32
        aligned = addr & ~3
        return self._mem.get(aligned, 0) & MASK32

    def store_word(self, addr, value):
        addr = addr & MASK32
        aligned = addr & ~3
        self._mem[aligned] = value & MASK32
        
class Simulator:

    DATA_BASE  = 0x00010000
    DATA_SIZE  = 32
    STACK_INIT = 0x0000017C

    def __init__(self, instructions):
        self.instructions = instructions
        self.reg = [0] * 32
        self.reg[2] = self.STACK_INIT
        self.pc = 0
        self.mem = Memory()
        self.trace_lines = []
