# disassembler.py

instruction_map = {
  'ADD':  '10000', 'ADC': '10001', 'SUB': '10010', 'AND': '10011000', 'OR': '10011001',
  'NOT':  '10011010', 'XOR': '10011011', 'SLL': '10011100', 'SRL': '10011101', 'SRA': '10011110',
  'LB':   '0010', 'LW': '0011', 'SB': '0110', 'SW': '0111', 'MV': '0001', 'MVL': '0100', 'MVH': '0101',
  'SET':  '110000000000', 'PUSH': '110000000010', 'POP': '110000000011', 'CALL': '11000001', 
  'RET':  '110000000001', 'NOP': '0000000000000',
  'BO':   '11100000', 'BO.Z': '11100001', 'BO.NZ': '11100010', 'BO.C': '11100011', 'BO.V': '11100100', 'BO.N': '11100101', 'BO.P': '11100110', 
  'BA':   '11110000', 'BA.Z': '11110001', 'BA.NZ': '11110010', 'BA.C': '11110011', 'BA.V': '11110100', 'BA.N': '11110101', 'BA.P': '11110110'
}

register_map = {
  'R1': '0000', 'R2': '0001', 'R3': '0010', 'R4': '0011', 'R5': '0100', 'R6': '0101', 
  'R7': '0110', 'R8': '0111', 'R9': '1000', 'R10': '1001', 'R11': '1010', 'R12': '1011',
  'R13': '1100', 'R14': '1101', 'R15': '1110', 'R16': '1111',
  'IO': '1011', 'LR': '1100', 'SP': '1101', 'PC': '1110', 'FL': '1111'
}

# Reverse mappings from binary to instruction and register names
instruction_map_reverse = {v: k for k, v in instruction_map.items()}
register_map_reverse = {v: k for k, v in register_map.items()}

def disassemble_instruction(binary_code):
    """Converts a binary machine code into assembly instruction."""
    # Convert hex string to binary string if input is in hex
    if binary_code.startswith('0x'):
        binary_code = format(int(binary_code, 16), '016b')
    
    # Ensure the binary code is 16 bits long
    if len(binary_code) != 16:
        raise ValueError("Invalid binary code length. Expected 16 bits.")

    # Extract opcode (first 5 bits)
    #opcode = binary_code[:5]

    # Handle different instruction types
    if binary_code[:5] in ['10000', '10001', '10010']:  # ADD, ADC, SUB
        is_imm = binary_code[5]
        rA = register_map_reverse[binary_code[6:10]]
        rbimm6 = binary_code[10:]
        if is_imm == '1':
            imm_value = int(rbimm6, 2)
            if imm_value & 0x20:  # Check if the 6th bit is set (negative number)
                imm_value = imm_value - 64  # Convert to negative
            return f"{instruction_map_reverse[binary_code[:5]]} {rA}, #{imm_value}"
        else:
            rB = register_map_reverse[rbimm6[2:]]
            return f"{instruction_map_reverse[binary_code[:5]]} {rA}, {rB}"

    elif binary_code[:5] == '10011':  # AND, OR, NOT, XOR, SLL, SRL, SRA
        sub_opcode = binary_code[5:8]
        rA = register_map_reverse[binary_code[8:12]]
        rB = register_map_reverse[binary_code[12:]]
        full_opcode = binary_code[:5] + sub_opcode
        if full_opcode == '10011010':  # NOT
            return f"{instruction_map_reverse[full_opcode]} {rA}"
        return f"{instruction_map_reverse[full_opcode]} {rA}, {rB}"

    elif binary_code[:4] in ['0010', '0011', '0110', '0111', '0100', '0101']:  # LB, LW, SB, SW, MVL, MVH
        rA = register_map_reverse[binary_code[4:8]]
        imm8 = int(binary_code[8:], 2)
        if imm8 & 0x80:  # Check if the 8th bit is set (negative number)
            imm8 = imm8 - 256  # Convert to negative
        return f"{instruction_map_reverse[binary_code[:4]]} {rA}, #{imm8}"

    elif binary_code[:4] == '0001':  # MV
        rA = register_map_reverse[binary_code[8:12]]
        rB = register_map_reverse[binary_code[12:]]
        return f"{instruction_map_reverse[binary_code[:4]]} {rA}, {rB}"

    elif binary_code[:12] in ['110000000000', '110000000010', '110000000011']:  # SET, PUSH, POP
        rA = register_map_reverse[binary_code[12:]]
        return f"{instruction_map_reverse[binary_code[:12]]} {rA}"

    elif binary_code[:12] == '110000000001':  # RET
        return instruction_map_reverse[binary_code[:12]]

    elif binary_code[:13] == '0000000000000':  # NOP
        return instruction_map_reverse[binary_code[:13]]

    elif binary_code[:5] in ['11000', '11100', '11110']:  # CALL, BO*, BA*
        imm8 = int(binary_code[8:], 2)
        if imm8 & 0x80:  # Check if the 8th bit is set (negative number)
            imm8 = imm8 - 256  # Convert to negative
        return f"{instruction_map_reverse[binary_code[:8]]} #{imm8}"

    else:
        return "Unknown instruction"

def disassemble_file(input_file, output_file):
    """Read binary code from input_file, convert to assembly, and write to output_file."""
    with open(input_file, 'r') as bin_file:
        binary_lines = bin_file.readlines()

    assembly_output = []
    for line in binary_lines:
        line = line.strip()
        if line:
            try:
                assembly_instruction = disassemble_instruction(line)
                assembly_output.append(assembly_instruction)
            except ValueError as e:
                assembly_output.append(f"Error: {str(e)}")

    with open(output_file, 'w') as asm_file:
        asm_file.write('\n'.join(assembly_output))
        print(f"Assembly code written to {output_file}")

# Example usage
if __name__ == "__main__":
    # Example: Disassemble a single instruction
    binary_code = "0100001111111111"
    print(disassemble_instruction(binary_code))

    # Uncomment the following lines to disassemble a file
    disassemble_file('binary.txt', 'disassembled.txt')