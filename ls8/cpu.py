"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # This will hold our 256 bytes of memory
        self.ram = [0]*256

        # This is our program counter. It holds the address of the currently executing instruction
        self.pc = 0
        # This will hold out 8 general purpose registers
        self.reg = [0]*8
        # init the stack pointer
        self.reg[7] = 0xF4

        self.flag = 0

    def load(self):
        """Load a program into memory."""

        # address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        if len(sys.argv) != 2:
            print("not reading file")
            sys.exit(1)
        try:
            address = 0
            with open(sys.argv[1]) as files:
                for line in files:
                    split_line = line.split('#')
                    command = split_line[0].strip()
                    if command == '':
                        continue
                    num_command = int(command, 2)

                    self.ram[address] = num_command
                    address += 1
        except FileNotFoundError:
            print(f'{sys.argv[0]} {sys.argv[1]}file was not found')
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "CMP":
            if reg_a == reg_b:
                self.flag = 0b00000001
            elif reg_a < reg_b:
                self.flag = 0b00000100
            elif reg_a > reg_b:
                self.flag = 0b00000010

        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        # This will accept the address to read and return the value stored
        return self.ram[address]

    def ram_write(self, address, value):
        # This will accept the value to write, and the address to write it to
        self.reg[address] = value

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

    def run(self):
        """Run the CPU."""
        self.load()
        while self.pc < len(self.ram):
            command = self.ram[self.pc]
            HLT = 0b00000001
            operand1 = self.ram_read(self.pc+1)
            operand2 = self.ram_read(self.pc+2)

            # If our instruction register is equal to HLT (stop the CPU)
            if command == HLT:
                break

            if command == 0b10000010:
                # Execute our LDI function using our two operands as input parameters

                self.ram_write(operand1, operand2)

            if command == 0b01000111:
                # Execute our PRN function
                print(self.reg[operand1])

            if command == 0b10100010:  # multiplies the numbers of the indexes of the next 2 lines
                self.reg[operand1] *= self.reg[operand2]

            if command == 0b10100000:  # sum
                self.reg[operand1] += self.reg[operand2]

            if command == 0b01000101:  # Push
                self.reg[7] -= 1  # decrement stack pointer
                self.reg[7] &= 0xff

                # get the index
                reg_index = self.ram[self.pc+1]
                # get the value at the pointer's address
                value = self.reg[reg_index]
                self.ram[self.reg[7]] = value

            if command == 0b01000110:  # Pop
                # get the stack pointer
                sp = self.reg[7]
                # get register number to put value in
                reg = self.ram[self.pc+1]
                # use stack pointer to get the value
                value = self.ram[sp]
                # put the value into the given register
                self.reg[reg] = value

                self.reg[7] += 1

            # self.pc += command >> 6

            # self.pc += 1

            if command == 0b01010000:  # Call
                self.reg[7] -= 1
                sp = self.reg[7]
                self.ram[sp] = self.pc+1
                self.pc = self.reg[operand1]

            if command == 0b00010001:  # RET
                sp = self.reg[7]
                self.reg[7] += 1
                self.pc = self.ram[sp]

            if command != 0b01010000 and command != 0b01010100 and command != 0b01010101 and command != 0b01010110:
                self.pc += command >> 6
                self.pc += 1
