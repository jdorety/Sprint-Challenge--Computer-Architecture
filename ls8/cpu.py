"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [00000000] * 255
        self.reg = [00000000] * 8
        self.pc = 0
        self.stack = [0b0] * 255
        self.equal = 0b00000000
        self.HLT = 0b0001
        self.LDI = 0b0010
        self.PRN = 0b0111
        self.MUL = 0b0010
        self.ADD = 0b0000
        self.POP = 0b0110
        self.PUSH = 0b0101
        self.CALL = 0b0000
        self.RET = 0b0001
        self.CMP = 0b0111
        self.JMP = 0b0100
        self.JEQ = 0b0101
        self.JNE = 0b0110

    def ram_read(self, mar):
        mdr = self.ram[mar]
        return mdr

    def ram_write(self, mar, mdr):
        value = mdr
        self.ram[mar] = value

    def load(self, path):
        """Load a program into memory."""
        try:
            load_file = open(path, 'r')
            address = 0
            for line in load_file:
                split_line = line.split("#")
                possible_command = split_line[0]
                if len(possible_command) > 0:
                    possible_command = possible_command.strip()
                    if possible_command == "":
                        pass
                    else:
                        command = int(possible_command, 2)
                        self.ram[address] = command
                        address += 1
            load_file.close()
        except(FileNotFoundError):
            print("file not found")
        # For now, we've just hardcoded a program:

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            val_1 = self.reg[reg_a]
            val_2 = self.reg[reg_b]

            if val_1 < val_2:
                self.equal = 0b00000100
            elif val_1 > val_2:
                self.equal = 0b00000010
            else:
                self.equal = 0b00000001

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_CALL(self, reg_address):
        return_add = self.pc + 2

        self.reg[7] -= 1
        sp = self.reg[7]
        self.stack[sp] = return_add

        self.pc = self.reg[reg_address]

    def handle_LDI(self, reg_address, value):
        self.reg[reg_address] = value

    def handle_PRN(self, reg_address):
        print(self.reg[reg_address])

    def handle_POP(self, reg_address):
        sp = self.reg[7]
        self.reg[reg_address] = self.stack[sp]

        self.reg[7] += 1

    def handle_PUSH(self, reg_address):
        self.reg[7] -= 1
        sp = self.reg[7]
        self.stack[sp] = self.reg[reg_address]

    def handle_RET(self):
        sp = self.reg[7]
        return_add = self.stack[sp]

        self.reg[7] += 1

        self.pc = return_add

    def handle_JMP(self, register_address):
        self.pc = self.reg[register_address]

    def handle_JEQ(self, register_address):
        cmp_flag = self.equal
        equal = cmp_flag & 0b00000001
        if equal == 1:
            self.pc = self.reg[register_address]
        else:
            self.pc += 2

    def handle_JNE(self, register_address):
        cmp_flag = self.equal
        equal = cmp_flag & 0b00000001
        if equal == 0:
            self.pc = self.reg[register_address]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        running = True
        self.reg[7] = 0b11111111

        while running == True:
            ir = self.ram[self.pc]
            operands = (ir >> 6)
            function = ir & 0b00001111
            alu = (ir >> 5) & 0b001
            set_pc = (ir >> 4) & 0b0001


            if set_pc == 1:
                if function == self.CALL:
                    self.handle_CALL(self.ram[self.pc + 1])
                elif function == self.RET:
                    self.handle_RET()
                elif function == self.JMP:
                    self.handle_JMP(self.ram[self.pc + 1])
                elif function == self.JEQ:
                    self.handle_JEQ(self.ram[self.pc + 1])
                elif function == self.JNE:
                    self.handle_JNE(self.ram[self.pc + 1])

            else:
                if alu == 1:
                    if function == self.MUL:
                        self.alu("MUL", self.ram[self.pc + 1],
                                 self.ram[self.pc + 2])

                    elif function == self.ADD:
                        self.alu("ADD", self.ram[self.pc + 1],
                                 self.ram[self.pc + 2])

                    elif function == self.CMP:
                        self.alu("CMP", self.ram[self.pc + 1],
                                 self.ram[self.pc + 2])

                elif function == self.HLT:
                    running = False

                elif function == self.LDI:
                    self.handle_LDI(
                        self.ram[self.pc + 1], self.ram[self.pc + 2])

                elif function == self.PRN:
                    self.handle_PRN(self.ram[self.pc + 1])

                elif function == self.POP:
                    self.handle_POP(self.ram[self.pc + 1])

                elif function == self.PUSH:
                    self.handle_PUSH(self.ram[self.pc + 1])

                else:
                    print("ERROR")

                self.pc += (operands + 1)
