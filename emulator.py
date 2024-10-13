import cpu, assembler

assembler.assemble_file('assembly.txt', 'binary.txt')

cpu = cpu.CPU()

# Reset the CPU
cpu.reset()

# Load the program into memory starting at address 0
cpu.load_program_from_file('binary.txt')

# Run the CPU
# cpu.run(ttl=0xFF)
cpu.stepwise_run()

# Check register and flag values
cpu.print_registers_dense()
cpu.print_flags()

# Check register values with expected
#cpu.evaluate_registers(output=True, halt=False, r1=8, r2=3, r3=0x1234)
cpu.evaluate_registers(output=True, halt=False, r1=25, r2=5, r3=5, r4=10)


# Check the result
result = cpu.read_word(0x4000)
print(f"Result stored in memory: {result}")  # Should print 8
