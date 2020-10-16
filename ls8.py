#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *
print('len(sys.argv):', len(sys.argv))
program = []
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()
    for line in lines:
        line = line.split('#')[0].strip()
        if len(line) > 0:
            instruction = int(line, 2)
            program.append(instruction)
cpu = CPU()

cpu.load(program)
cpu.run()