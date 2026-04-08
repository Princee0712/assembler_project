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
