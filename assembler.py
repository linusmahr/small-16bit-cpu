# Define instruction mapping and register encoding based on design.txt
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

def parse_rbimm6b(operand):
  """Parse an rB/#imm6 operand (register or immediate in decimal or hex)."""
  if operand.startswith('R'):
    return format(int(register_map[operand]), '06d'), '0'  # Register
  elif operand.startswith('#'):
    imm_value = operand[1:]  # Remove the '#' prefix
    
    # Check if the value is in hex format
    if imm_value.startswith('0x'):
      imm_value = int_2c(imm_value, 6)  # Parse hex value
    else:
      imm_value = int(imm_value)  # Parse decimal value

    if imm_value < -(1 << 5) or imm_value >= (1 << 5):
      raise ValueError(f"Immediate value {imm_value} exceeds the allowed 6-bit range (-32 to 31).")
    
    return format(imm_value & 0x3F, '06b'), '1'  # Immediate with 6 bits
  else:
    raise ValueError(f"Unknown operand rB/#imm6: {operand}")
  
def parse_imm8b(operand):
  """Parse an #imm8 operand (register or immediate in decimal or hex)."""
  if operand.startswith('#'):
    imm_value = operand[1:]  # Remove the '#' prefix
    
    # Check if the value is in hex format
    if imm_value.startswith('0x'):
      # Convert from hex string using 2's complement
      imm_value = int_2c(imm_value, 8)
    else:
      # Parse as a regular integer, assuming decimal input
      imm_value = int(imm_value)
    
    # Ensure the value fits within the 8-bit range (-128 to 127 for signed 2's complement)
    if imm_value < -(1 << 7) or imm_value >= (1 << 7):
      raise ValueError(f"Immediate value {imm_value} exceeds the allowed 8-bit range (-128 to 127).")
    
    # Convert back to hex 2's complement and return the binary representation
    return format(imm_value & 0xFF, '08b')  # Format as 8-bit binary string
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
  
  if instruction in ['ADD', 'ADC', 'SUB']:
    rA = parse_reg(parts[1].rstrip(','))
    rbimm6, is_imm = parse_rbimm6b(parts[2])
    return f"{opcode}{is_imm}{rA}{rbimm6}"
  
  elif instruction in ['AND', 'OR', 'XOR', 'SLL', 'SRL', 'SRA']:
    rA = parse_reg(parts[1].rstrip(','))
    rB = parse_reg(parts[2])
    return f"{opcode}{rA}{rB}"
  
  elif instruction in ['SB', 'SW', 'LB', 'LW', 'MVL', 'MVH']:
    rA = parse_reg(parts[1].rstrip(','))
    imm8 = parse_imm8b(parts[2])
    return f"{opcode}{rA}{imm8}"
  
  elif instruction in ['MV']:
    rA = parse_reg(parts[1].rstrip(','))
    rB = parse_reg(parts[2])
    return f"{opcode}0000{rA}{rB}"
  
  elif instruction in ['SET', 'PUSH', 'POP']:
    rA = parse_reg(parts[1])
    return f"{opcode}{rA}"
  
  elif instruction in ['NOT']:
    rA = parse_reg(parts[1])
    return f"{opcode}{rA}0000"
  
  elif instruction in ['RET', 'NOP']:
    return f"{opcode}0000"
  
  elif instruction in ['CALL',
                       'BO', 'BO.Z', 'BO.NZ', 'BO.C', 'BO.V', 'BO.N', 'BO.P',
                       'BA', 'BA.Z', 'BA.NZ', 'BA.C', 'BA.V', 'BA.N', 'BA.P']:
    imm8 = parse_imm8b(parts[1])
    return f"{opcode}{imm8}"
  
  else:
    raise ValueError(f"opcode not supported: {opcode}")
  
def assembler_macro(line):
  """Handles assembler macros"""
  parts = line.split()
  if line.startswith('asm.call'):
    MVL = f"01001011{parts[1]}_l"
    MVH = f"01011011{parts[1]}_h"
    CALL = f"1100000100000000"
    binary_code = [MVL, MVH, CALL]
  elif line.startswith('asm.mv'):
    imm_value = parts[2][1:]
    if imm_value.startswith('0x'):
      imm_value = int_2c(imm_value, 16)
    else:
      imm_value = int(imm_value)
    if imm_value < -(1 << 15) or imm_value >= (1 << 15):
      raise ValueError(f"Immediate value {hex_2c(imm_value)} exceeds the allowed 16-bit range (0xFFFF).")
    rA = parse_reg(parts[1].rstrip(','))
    MVL = f"0100{rA}{format(imm_value & 0xFF, '08b')}"  # Lower 8 bits
    MVH = f"0101{rA}{format((imm_value >> 8) & 0xFF, '08b')}"  # Higher 8 bits
    binary_code = [MVL, MVH]
  return binary_code

def replace_labels(binary_output, labels):
  """Replaces labels @sth_l and _h"""
  updated_lines = []  # This will store the modified lines

  for line in binary_output:
    if '@' in line:
      # Split the line at the '@' symbol
      parts = line.split('@')
      binary_part = parts[0]  # The part before '@'
      name_with_suffix = parts[1]  # The part after '@' (e.g., "multiply_l")

      # Extract the label name (everything before the '_')
      label_name, suffix = name_with_suffix.split('_')

      # Look up the 16-bit binary value from the labels dictionary
      if label_name in labels:
        address_16bit = labels[label_name]  # 16-bit binary value from the dictionary

        # Extract the lower 8 bits and higher 8 bits
        lower_8_bits = address_16bit[8:]  # Last 8 bits
        higher_8_bits = address_16bit[:8]  # First 8 bits

        # Replace @name_l or @name_h with the corresponding bits
        if suffix == 'l':
          updated_line = binary_part + lower_8_bits
        elif suffix == 'h':
          updated_line = binary_part + higher_8_bits

        updated_lines.append(updated_line)
      else:
          # If the label is not found in the dictionary, leave the line unchanged
          updated_lines.append(line)
          raise ValueError(f"Cannot find label {label_name}")
    else:
        # If there's no '@', just add the line as is
        updated_lines.append(line)
  return updated_lines

def assemble_file(input_file, output_file):
  """Read assembly code from input_file, convert to binary, and write to output_file."""
  with open(input_file, 'r') as asm_file:
    lines = asm_file.readlines()

  binary_output = []
  labels = {}
  
  for line in lines:
    line = line.strip()

    if line.startswith('asm.stop'):
      break

    elif line.startswith('@'):     # Adds labels to the dictionary
      label = line[1:]
      address = format(len(binary_output)*2, '016b')  # Format address as 16-bit binary
      if label in labels:
        raise ValueError(f"Label '{label}' already exists in the dictionary.")
      labels[label] = address

    # Translate the lines, ignore empty lines, comments and asm instructions
    elif line and not line.startswith('#') and not line.startswith('asm'):
      binary_code = assemble_instruction(line)
      if binary_code:
        binary_output.append(binary_code)

    elif line.startswith('asm'):
      binary_code = assembler_macro(line)
      if binary_code:
        binary_output.extend(binary_code)

  # Replace labels with their proper addresses
  binary_output = replace_labels(binary_output, labels)

  with open(output_file, 'w') as bin_file:
    bin_file.write('\n'.join(binary_output))
    #print(f"Binary code written to {output_file}")

def hex_2c(n, bits=8):
    # Calculate the minimum and maximum allowable values for the given number of bits
    min_val = -(1 << (bits - 1))
    max_val = (1 << (bits - 1)) - 1
    
    # Check if the value is within the range of the 2's complement for the given bits
    if n < min_val or n > max_val:
        raise ValueError(f"Value {n} is out of range for {bits}-bit 2's complement")
    
    # Perform the 2's complement conversion
    hex_value = hex((n + (1 << bits)) % (1 << bits))
    return '0x' + hex_value[2:].upper()


def int_2c(hex_str, bits=8):
    # Convert hex string to an integer
    n = int(hex_str, 16)
    
    # Calculate the maximum allowable value for the given number of bits
    max_val = (1 << bits) - 1
    
    # Check if the value exceeds the maximum for the given number of bits
    if n > max_val:
        raise ValueError(f"Value {hex_str} is out of range for {bits}-bit 2's complement")
    
    # Check if the number is negative by examining the most significant bit
    if n & (1 << (bits - 1)):
        # If the number is negative, convert it from 2's complement
        n = n - (1 << bits)
    
    return n

# Example usage
if __name__ == "__main__":
  assemble_file('assembly.txt', 'binary.txt')