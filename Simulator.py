import sys

WORD = 32
MASK32 = 0xFFFFFFFF


DATA_START  = 0x00010000
DATA_END    = 0x0001007C   
STACK_START = 0x00000100   
STACK_END   = 0x0000017C   


def sext(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


def fmt32(value):
    v = value & MASK32
    return "0b" + format(v, "032b")


def validate_mem_access(addr, op, line_num):
    """
    Validates a memory access for alignment and region bounds.
    Includes line_num to identify which instruction in the input file failed.
    Returns (True, '') on success, or (False, error_message) on failure.
    """
    if addr % 4 != 0:
        return False, (f"Error: misaligned memory {op} at address "
                       f"0x{addr:08X} (not 4-byte aligned) at line {line_num}")

    in_stack = STACK_START <= addr <= STACK_END
    in_data  = DATA_START  <= addr <= DATA_END

    if not (in_stack or in_data):
        return False, (f"Error: invalid memory {op} at address "
                       f"0x{addr:08X} (outside valid memory regions) at line {line_num}")
    return True, ''


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
        self._halted = False         

    @staticmethod
    def bits(instr, hi, lo):
        width = hi - lo + 1
        return (instr >> lo) & ((1 << width) - 1)

    def _reg_write(self, rd, value):
        if rd != 0:
            self.reg[rd] = value & MASK32

    def _emit_trace(self):
        parts = [fmt32(self.pc)]
        for i in range(32):
            parts.append(fmt32(self.reg[i]))
        self.trace_lines.append(" ".join(parts) + " ")

    def _current_line_num(self):
        """Returns 1-based line number of the current instruction."""
        return (self.pc >> 2) + 1

    def _step(self):
        pc = self.pc
        if pc < 0 or (pc >> 2) >= len(self.instructions):
            print(f"Error: PC 0x{pc:08X} out of range", file=sys.stderr)
            return False

        instr = self.instructions[pc >> 2]
        opcode = self.bits(instr, 6, 0)

        
        if opcode == 0b0110011:
            funct3 = self.bits(instr, 14, 12)
            funct7 = self.bits(instr, 31, 25)
            rs1    = self.bits(instr, 19, 15)
            rs2    = self.bits(instr, 24, 20)
            rd     = self.bits(instr, 11,  7)
            v1 = self.reg[rs1]; v2 = self.reg[rs2]
            sv1 = sext(v1, 32); sv2 = sext(v2, 32)

            if   funct3 == 0b000 and funct7 == 0b0000000:
                result = (v1 + v2) & MASK32
            elif funct3 == 0b000 and funct7 == 0b0100000:
                result = (v1 - v2) & MASK32
            elif funct3 == 0b001:
                result = (v1 << (v2 & 0x1F)) & MASK32
            elif funct3 == 0b010:
                result = 1 if sv1 < sv2 else 0
            elif funct3 == 0b011:
                result = 1 if (v1 & MASK32) < (v2 & MASK32) else 0
            elif funct3 == 0b100:
                result = (v1 ^ v2) & MASK32
            elif funct3 == 0b101 and funct7 == 0b0000000:
                result = (v1 & MASK32) >> (v2 & 0x1F)
            elif funct3 == 0b101 and funct7 == 0b0100000:
                result = sext(v1, 32) >> (v2 & 0x1F)
                result = result & MASK32
            elif funct3 == 0b110:
                result = (v1 | v2) & MASK32
            elif funct3 == 0b111:
                result = (v1 & v2) & MASK32
            else:
                print(f"Unknown R-type funct3={funct3} funct7={funct7}", file=sys.stderr)
                result = 0
            self._reg_write(rd, result)
            self.pc += 4

        
        elif opcode == 0b0010011:
            funct3 = self.bits(instr, 14, 12)
            rs1    = self.bits(instr, 19, 15)
            rd     = self.bits(instr, 11,  7)
            imm    = sext(self.bits(instr, 31, 20), 12)
            v1     = self.reg[rs1]
            sv1    = sext(v1, 32)

            if   funct3 == 0b000:
                result = (v1 + imm) & MASK32
            elif funct3 == 0b010:
                result = 1 if sv1 < imm else 0
            elif funct3 == 0b011:
                uimm = imm & MASK32
                result = 1 if (v1 & MASK32) < uimm else 0
            elif funct3 == 0b100:
                result = (v1 ^ (imm & MASK32)) & MASK32
            elif funct3 == 0b110:
                result = (v1 | (imm & MASK32)) & MASK32
            elif funct3 == 0b111:
                result = (v1 & (imm & MASK32)) & MASK32
            elif funct3 == 0b001:
                shamt = self.bits(instr, 24, 20)
                result = (v1 << shamt) & MASK32
            elif funct3 == 0b101:
                shamt = self.bits(instr, 24, 20)
                funct7 = self.bits(instr, 31, 25)
                if funct7 == 0b0100000:
                    result = (sext(v1, 32) >> shamt) & MASK32
                else:
                    result = (v1 & MASK32) >> shamt
            else:
                result = 0
            self._reg_write(rd, result)
            self.pc += 4


        elif opcode == 0b0000011:
            funct3 = self.bits(instr, 14, 12)
            rs1    = self.bits(instr, 19, 15)
            rd     = self.bits(instr, 11,  7)
            imm    = sext(self.bits(instr, 31, 20), 12)
            addr   = (self.reg[rs1] + imm) & MASK32

            line_num = self._current_line_num()
            ok, err = validate_mem_access(addr, 'lw', line_num)
            if not ok:
                print(err, file=sys.stderr)
                self._halted = True
                return False

            if funct3 == 0b010:
                result = self.mem.load_word(addr)
            else:
                result = 0
            self._reg_write(rd, result)
            self.pc += 4

        
        elif opcode == 0b1100111:
            rs1 = self.bits(instr, 19, 15)
            rd  = self.bits(instr, 11,  7)
            imm = sext(self.bits(instr, 31, 20), 12)
            ret = (self.pc + 4) & MASK32
            target = ((self.reg[rs1] + imm) & ~1) & MASK32
            self._reg_write(rd, ret)
            self.pc = target

        
        elif opcode == 0b0100011:
            rs1    = self.bits(instr, 19, 15)
            rs2    = self.bits(instr, 24, 20)
            imm_hi = self.bits(instr, 31, 25)
            imm_lo = self.bits(instr, 11,  7)
            imm    = sext((imm_hi << 5) | imm_lo, 12)
            addr   = (self.reg[rs1] + imm) & MASK32

            line_num = self._current_line_num()
            ok, err = validate_mem_access(addr, 'sw', line_num)
            if not ok:
                print(err, file=sys.stderr)
                self._halted = True
                return False

            self.mem.store_word(addr, self.reg[rs2])
            self.pc += 4

        
        elif opcode == 0b1100011:
            funct3 = self.bits(instr, 14, 12)
            rs1    = self.bits(instr, 19, 15)
            rs2    = self.bits(instr, 24, 20)
            b12   = self.bits(instr, 31, 31)
            b11   = self.bits(instr,  7,  7)
            b10_5 = self.bits(instr, 30, 25)
            b4_1  = self.bits(instr, 11,  8)
            imm   = (b12 << 12) | (b11 << 11) | (b10_5 << 5) | (b4_1 << 1)
            imm   = sext(imm, 13)

            v1 = self.reg[rs1]; v2 = self.reg[rs2]
            sv1 = sext(v1, 32); sv2 = sext(v2, 32)

            
            if funct3 == 0b000 and rs1 == 0 and rs2 == 0 and imm == 0:
                self.pc += 4
                self._emit_trace()
                return False

            if   funct3 == 0b000: taken = (v1 == v2)
            elif funct3 == 0b001: taken = (v1 != v2)
            elif funct3 == 0b100: taken = (sv1 < sv2)
            elif funct3 == 0b101: taken = (sv1 >= sv2)
            elif funct3 == 0b110: taken = ((v1 & MASK32) < (v2 & MASK32))
            elif funct3 == 0b111: taken = ((v1 & MASK32) >= (v2 & MASK32))
            else: taken = False

            if taken:
                self.pc = (self.pc + imm) & MASK32
            else:
                self.pc += 4

        
        elif opcode == 0b0110111:
            rd  = self.bits(instr, 11,  7)
            imm = self.bits(instr, 31, 12) << 12
            self._reg_write(rd, imm & MASK32)
            self.pc += 4

        
        elif opcode == 0b0010111:
            rd  = self.bits(instr, 11,  7)
            imm = self.bits(instr, 31, 12) << 12
            result = (self.pc + imm) & MASK32
            self._reg_write(rd, result)
            self.pc += 4

        
        elif opcode == 0b1101111:
            rd     = self.bits(instr, 11, 7)
            b20    = self.bits(instr, 31, 31)
            b10_1  = self.bits(instr, 30, 21)
            b11    = self.bits(instr, 20, 20)
            b19_12 = self.bits(instr, 19, 12)
            imm    = (b20 << 20) | (b19_12 << 12) | (b11 << 11) | (b10_1 << 1)
            imm    = sext(imm, 21)
            ret    = (self.pc + 4) & MASK32
            self._reg_write(rd, ret)
            self.pc = (self.pc + imm) & MASK32

        else:
            print(f"Unknown opcode 0b{opcode:07b} at PC=0x{pc:08X}", file=sys.stderr)
            self.pc += 4

        return True

    def run(self):
        MAX_STEPS = 10_000_000
        for _ in range(MAX_STEPS):
            cont = self._step()
            self._emit_trace()
            if not cont:
                break
        else:
            print("Warning: max steps reached without halt", file=sys.stderr)

    def run_fixed(self):
        MAX_STEPS = 10_000_000
        for _ in range(MAX_STEPS):
            pc_before = self.pc
            if (pc_before >> 2) < len(self.instructions):
                instr = self.instructions[pc_before >> 2]
                opcode = self.bits(instr, 6, 0)
                if opcode == 0b1100011:
                    funct3 = self.bits(instr, 14, 12)
                    rs1 = self.bits(instr, 19, 15)
                    rs2 = self.bits(instr, 24, 20)
                    b12   = self.bits(instr, 31, 31)
                    b11   = self.bits(instr,  7,  7)
                    b10_5 = self.bits(instr, 30, 25)
                    b4_1  = self.bits(instr, 11,  8)
                    imm_raw = (b12<<12)|(b11<<11)|(b10_5<<5)|(b4_1<<1)
                    imm = sext(imm_raw, 13)
                    if funct3 == 0b000 and rs1 == 0 and rs2 == 0 and imm == 0:
                        self._emit_trace()
                        break
            cont = self._step()
            self._emit_trace()
            if not cont or self._halted:
                break
        else:
            print("Warning: max steps reached without halt", file=sys.stderr)

    def memory_dump(self):
        lines = []
        for i in range(self.DATA_SIZE):
            addr = self.DATA_BASE + i * 4
            val  = self.mem.load_word(addr)
            lines.append(f"0x{addr:08X}:{fmt32(val)}")
        return lines


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 Simulator.py <input_bin_file> <output_trace_file> [output_read_trace_file]",
              file=sys.stderr)
        sys.exit(1)

    input_file  = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(input_file, 'r') as f:
            raw_lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print(f"Error: cannot open input file {input_file}", file=sys.stderr)
        sys.exit(1)

    instructions = []
    for line in raw_lines:
        try:
            instructions.append(int(line, 2))
        except ValueError:
            print(f"Error: invalid binary line: {line}", file=sys.stderr)
            sys.exit(1)

    sim = Simulator(instructions)
    sim.run_fixed()

    mem_lines = sim.memory_dump()
    all_lines = sim.trace_lines + mem_lines

    with open(output_file, 'w') as f:
        f.write("\n".join(all_lines) + "\n")

    if len(sys.argv) >= 4:
        read_trace_file = sys.argv[3]
        with open(read_trace_file, 'w') as f:
            f.write("\n".join(all_lines) + "\n")


if __name__ == "__main__":
    main()
