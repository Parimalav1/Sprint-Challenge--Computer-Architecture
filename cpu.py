"""CPU functionality."""

import sys

ADD = 0b10100000
HLT = 0b00000001
LDI = 0b10000010
MUL = 0b10100010
PRN = 0b01000111
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001
SHL = 0b10101100
SHR = 0b10101101
MOD = 0b10100100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.pc = 0
        self.ir = 0
        self.mar = 0
        self.mdr = 0
        self.ram = [0] * 256
        self.sp = 256
        self.E = 0
        self.L = 0
        self.G = 0

    def ram_read(self, mar):
        self.mdr = self.ram[mar]
        return self.ram[mar]
    # memory data register- mdr(data)
    # memory address register- mar(address)

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def load(self, input_program=[]):
        """Load a program into memory."""
        address = 0
        if len(input_program) > 0:
            program = input_program
        else:
            program = [
                0b10000010, # LDI R0,8
                0b00000000,
                0b00001000,
                0b01000111, # PRN R0
                0b00000000,
                0b00000001, # HLT
            ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # Add an `ADDI` extension instruction to add an immediate value to a register
        # elif op == "ADDI":
            
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == 'CMP':
            self.E = 0
            self.L = 0
            self.G = 0
            if self.reg[reg_a] == self.reg[reg_b]:
                self.E = 1
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.L = 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.G = 1
            else:
                self.E = 0
        elif op == 'AND':
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == 'OR':
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == 'XOR':
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == 'NOT':
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == 'SHL':
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == 'SHR':
            self.reg[reg_a] >>= self.reg[reg_b]
        elif op == 'MOD':
            self.reg[reg_a] %= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def push_value(self, value):
        # pc-address, sp-register
        # decrement pc and copy the value
        self.sp -= 1
        top_of_stack = self.sp
        self.ram[top_of_stack] = value

    def pop_value(self):
        # Get value from top of stack & increment the pc
        top_of_stack = self.sp
        value = self.ram[top_of_stack]
        self.sp += 1
        return value

    def run(self):
        """Run the CPU."""
        halted = False
        while not halted:
            #self.trace()
            self.ir = self.ram_read(self.pc)
            if self.ir == ADD:
                operand1 = self.ram_read(self.pc + 1)
                operand2 = self.ram_read(self.pc + 2)
                self.alu('ADD', operand1, operand2)
                self.pc += 3
            elif self.ir == HLT:
                halted = True
            elif self.ir == LDI:
                operand1 = self.ram_read(self.pc + 1)
                operand2 = self.ram_read(self.pc + 2)
                self.reg[operand1] = operand2
                self.pc += 3
            elif self.ir == MUL:
                operand1 = self.ram_read(self.pc + 1)
                operand2 = self.ram_read(self.pc + 2)
                self.alu('MUL', operand1, operand2)
                self.pc += 3
            elif self.ir == PRN:
                operand1 = self.ram_read(self.pc + 1)
                print(self.reg[operand1])
                self.pc += 2

            elif self.ir == PUSH:
                # Decrement the stack pointer
                self.sp -= 1
                # Grab the value out of the given register
                reg_num = self.ram_read(self.pc + 1)
                value = self.reg[reg_num]  
                # Copy the value onto the stack
                top_of_stack = self.sp
                self.ram[top_of_stack] = value
                self.pc += 2

            elif self.ir == POP:
                # Get value from top of stack
                top_of_stack = self.sp
                value = self.ram[top_of_stack]
                reg_num = self.ram_read(self.pc + 1)
                self.reg[reg_num] = value
                # Increment the SP
                self.sp += 1
                self.pc += 2

            elif self.ir == CALL:
                return_add = self.pc + 2
                # Push it on the stack
                self.push_value(return_add)

                # Get subroutine address from register
                reg_num = self.ram_read(self.pc + 1)
                subroutine_add = self.reg[reg_num]
                self.pc = subroutine_add

            elif self.ir == RET:
                # Get return addr from top of stack
                return_add = self.pop_value()

                # Store it in the PC
                self.pc = return_add

            # _conditional jumps_ (AKA _conditional branching_)
            elif self.ir == JMP:
                # pc-address, sp-register, # JMP R2
                reg_num = self.ram_read(self.pc + 1)
                to_address = self.reg[reg_num]
                self.pc = to_address

            elif self.ir == JEQ:
                if self.E == 1:
                    reg_num = self.ram_read(self.pc + 1)
                    to_address = self.reg[reg_num]
                    self.pc = to_address
                else:
                    self.pc += 2
            
            elif self.ir == JNE:
                if self.E == 0:
                    reg_num = self.ram_read(self.pc + 1)
                    to_address = self.reg[reg_num]
                    self.pc = to_address
                else:
                    self.pc += 2
            
            elif self.ir == CMP:
                operand1 = self.ram_read(self.pc + 1)
                operand2 = self.ram_read(self.pc + 2)
                self.alu('CMP', operand1, operand2)
                self.pc += 3

            elif self.ir == AND:
                operand1 = self.ram_read(self.pc + 1)
                operand2 = self.ram_read(self.pc + 2)
                self.alu('AND', operand1, operand2)
                self.pc += 3

            elif self.ir == OR:
                operand1 = self.ram_read(self.pc + 1)
                operand2 = self.ram_read(self.pc + 2)
                self.alu('OR', operand1, operand2)
                self.pc += 3

            elif self.ir == XOR:
                operand1 = self.ram_read(self.pc + 1)
                operand2 = self.ram_read(self.pc + 2)
                self.alu('XOR', operand1, operand2)
                self.pc += 3

            elif self.ir == NOT:
                operand1 = self.ram_read(self.pc + 1)
                self.alu('NOT', operand1)
                self.pc += 2

            elif self.ir == SHL:
                operand1 = self.ram_read(self.pc + 1)
                operand2 = self.ram_read(self.pc + 2)
                self.alu('SHL', operand1, operand2)
                self.pc += 3

            elif self.ir == SHR:
                operand1 = self.ram_read(self.pc + 1)
                operand2 = self.ram_read(self.pc + 2)
                self.alu('SHR', operand1, operand2)
                self.pc += 3

            elif self.ir == MOD:
                if operand2 != 0:
                    operand1 = self.ram_read(self.pc + 1)
                    operand2 = self.ram_read(self.pc + 2)
                    self.alu('MOD', operand1, operand2)
                    self.pc += 3
                else:
                    print('Error')
                    halted = True

            else:
                print(f'unknown instruction {self.ir} at address {self.pc}')
                sys.exit(1)

