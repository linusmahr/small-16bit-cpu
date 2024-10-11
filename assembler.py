# Define instruction mapping and register encoding based on design.txt
instruction_map = {
  'ADD':  '10000', 'ADC': '10001', 'SUB': '10010', 'AND': '10011000', 'OR': '10011001',
  'NOT':  '10011010', 'XOR': '10011011', 'SLL': '10011100', 'SRL': '10011101', 'SRA': '10011110',
  'LB':   '0000', 'LW': '0001', 'SB': '0010', 'SW': '0011', 'MV': '01000', 'MVL': '0101',
  'SET':  '110000000000', 'PUSH': '110000000010', 'POP': '110000000011', 'CALL': '11000001', 
  'RET':  '110000000001', 'NOP': '1100000000011',
  'BO':   '11100000', 'BO.Z': '11100001', 'BO.NZ': '11100010', 'BO.C': '11100011', 'BO.V': '11100100', 'BO.N': '11100101', 'BO.P': '11100110', 
  'BA':   '11110000', 'BA.Z': '11110001', 'BA.NZ': '11110010', 'BA.C': '11110011', 'BA.V': '11110100', 'BA.N': '11110101', 'BA.P': '11110110'
}

register_map = {
  'R1': '0000', 'R2': '0001', 'R3': '0010', 'R4': '0011', 'R5': '0100', 'R6': '0101', 
  'R7': '0110', 'R8': '0111', 'R9': '1000', 'R10': '1001', 'R11': '1010', 'R12': '1011',
  'R13': '1100', 'R14': '1101', 'R15': '1110', 'R16': '1111',
  'IO': '1011', 'LR': '1100', 'SP': '1101', 'PC': '1110', 'FL': '1111'
}

def parse_rbimm6b(operand):
  """Parse an rB/#imm6 operand (register or immediate in decimal or hex)."""
  if operand.startswith('R'):
    return format(int(register_map[operand]), '06b'), '0'  # Register
  elif operand.startswith('#'):
    imm_value = operand[1:]  # Remove the '#' prefix
    
    # Check if the value is in hex format
    if imm_value.startswith('0x'):
      imm_value = int(imm_value, 16)  # Parse hex value
    else:
      imm_value = int(imm_value)  # Parse decimal value
    
    return format(imm_value, '06b'), '1'  # Immediate with 6 bits
  else:
    raise ValueError(f"Unknown operand rB/#imm6: {operand}")
  
def parse_imm8b(operand):
  """Parse an #imm8 operand (register or immediate in decimal or hex)."""
  if operand.startswith('#'):
    imm_value = operand[1:]  # Remove the '#' prefix
    
    # Check if the value is in hex format
    if imm_value.startswith('0x'):
      imm_value = int(imm_value, 16)  # Parse hex value
    else:
      imm_value = int(imm_value)  # Parse decimal value
    
    return format(imm_value, '08b')  # Immediate with 6 bits
  else:
    raise ValueError(f"Unknown operand #imm8: {operand}")

def parse_reg(operand):
  """Parse a reg operand"""
  return register_map[operand]

def assemble_instruction(line):
  """Converts a line of assembly code into binary machine code."""
  parts = line.split()
  #print(parts)
  if len(parts) == 0:
    return None
  
  instruction = parts[0]
  opcode = instruction_map.get(instruction, None)
  if opcode is None:
    raise ValueError(f"Unknown instruction: {instruction}")
  
  if instruction in ['SB', 'SW']:  # Handle SB and SW instructions
    imm8 = parse_imm8b(parts[1].rstrip(','))
    rA = parse_reg(parts[2])
    return f"{opcode}{imm8}{rA}"
  
  elif instruction in ['ADD', 'ADC', 'SUB', 'MV']:
    rA = parse_reg(parts[1].rstrip(','))
    rbimm6, is_imm = parse_rbimm6b(parts[2])
    return f"{opcode}{is_imm}{rA}{rbimm6}"
  
  elif instruction in ['AND', 'OR', 'XOR', 'SLL', 'SRL', 'SRA']:
    rA = parse_reg(parts[1].rstrip(','))
    rB = parse_reg(parts[2])
    return f"{opcode}{rA}{rB}"
  
  elif instruction in ['LB', 'LW', 'MVL']:
    rA = parse_reg(parts[1].rstrip(','))
    imm8 = parse_imm8b(parts[2])
    return f"{opcode}{rA}{imm8}"
  
  elif instruction in ['SET', 'PUSH', 'POP']:
    rA = parse_reg(parts[1])
    return f"{opcode}{rA}"
  
  elif instruction in ['NOT']:
    rA = parse_reg(parts[1])
    return f"{opcode}{rA}0000"
  
  elif instruction in ['RET', 'NOP']:
    return f"{opcode}000"
  
  elif instruction in ['CALL',
                       'BO', 'BO.Z', 'BO.NZ', 'BO.C', 'BO.V', 'BO.N', 'BO.P',
                       'BA', 'BA.Z', 'BA.NZ', 'BA.C', 'BA.V', 'BA.N', 'BA.P']:
    imm8 = parse_imm8b(parts[1])
    return f"{opcode}{imm8}"
  
  else:
    raise ValueError(f"opcode not supported: {opcode}")

def assemble_file(input_file, output_file):
  """Read assembly code from input_file, convert to binary, and write to output_file."""
  with open(input_file, 'r') as asm_file:
    lines = asm_file.readlines()

  binary_output = []
  for line in lines:
    line = line.strip()
    if line and not line.startswith('#'):  # Ignore empty lines and comments
      binary_code = assemble_instruction(line)
      if binary_code:
        binary_output.append(binary_code)

  with open(output_file, 'w') as bin_file:
    bin_file.write('\n'.join(binary_output))
    #print(f"Binary code written to {output_file}")

# Example usage
assemble_file('assembly.txt', 'binary.txt')