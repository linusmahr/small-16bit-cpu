import cpu, assembler

assembler.assemble_file('assembly.txt', 'binary.txt')

cpu = cpu.CPU()

# Reset the CPU
cpu.reset()
cpu.nop_rom()
cpu.nop_range(0xE00000, 0xFFFFFF)

# Load the program into memory starting at address 0
cpu.load_program_from_file('binary.txt')

# Run the CPU
cpu.run(ttl=0xFF)

# Check register and flag values
cpu.print_registers()
cpu.print_flags()

# Check register values with expected
cpu.evaluate_registers(output=True, halt=False, r1=9, r2=3)

# Check the result
result = cpu.read_word(0x400000)
print(f"Result stored in memory: {result}")  # Should print 8
