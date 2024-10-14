import disassembler

class CPU:
  def __init__(self):
    # Memory
    self.memory = [0] * (0xFFFF + 1)  # 24-bit address space
    
    # Registers
    self.registers = [0] * 16  # R1 to R16
    
    # init sp
    self.sp = 0x9FFE  # Stack Pointer (24-bit), initialized to top of stack
    
    # init flags
    self.z = 0  # Zero
    self.n = 0  # Negative
    self.p = 0  # Positive
    self.c = 0  # Carry
    self.v = 0  # Overflow

  @property
  def io(self):
    return self.registers[0xB]
    
  @io.setter
  def io(self, value):
    self.registers[0xB] = value

  @property
  def lr(self):
    return self.registers[0xC]
    
  @lr.setter
  def lr(self, value):
    self.registers[0xC] = value

  @property
  def sp(self):
    return self.registers[0xD]
    
  @sp.setter
  def sp(self, value):
    self.registers[0xD] = value

  @property
  def pc(self):
    return self.registers[0xE]
    
  @pc.setter
  def pc(self, value):
    self.registers[0xE] = value
  
  @property
  def fl(self):
    return self.registers[0xF]
    
  @fl.setter
  def fl(self, value):
    self.registers[0xF] = value

  @property
  def z(self):
    return self.fl & 0x1
  
  @z.setter
  def z(self, value):
    if value:
      self.fl |= 1
    else:
      self.fl &= ~0 

  @property
  def n(self):
    return (self.fl>>1) & 0x1
  
  @n.setter
  def n(self, value):
    if value:
      self.fl |= (1<<1)
    else:
      self.fl &= ~(0<<1)

  @property
  def p(self):
    return (self.fl>>2) & 0x1
  
  @p.setter
  def p(self, value):
    if value:
      self.fl |= (1<<2)
    else:
      self.fl &= ~(0<<2)

  @property
  def c(self):
    return (self.fl>>3) & 0x1
  
  @c.setter
  def c(self, value):
    if value:
      self.fl |= (1<<3)
    else:
      self.fl &= ~(0<<3)

  @property
  def v(self):
    return (self.fl>>4) & 0x1
  
  @v.setter
  def v(self, value):
    if value:
      self.fl |= (1<<4)
    else:
      self.fl &= ~(0<<4)

  def reset(self):
    self.__init__()

  def load_program_from_file(self, filename, start_address=0):
    with open(filename, 'r') as file:
      for i, line in enumerate(file):
        # Remove any whitespace (like newlines)
        binary_instruction = line.strip()

        # Convert binary string to an integer
        instruction = int(binary_instruction, 2)

        # Extract the upper and lower bytes
        upper_byte = (instruction >> 8) & 0xFF  # Upper 8 bits
        lower_byte = instruction & 0xFF         # Lower 8 bits

        # Store the upper and lower bytes in consecutive memory locations
        self.memory[start_address + 2*i] = upper_byte
        self.memory[start_address + 2*i + 1] = lower_byte

  def fetch(self):
    instruction = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
    return instruction

  def decode_and_execute(self, instruction):
    self.pc += 2

    opcode = (instruction >> 12) & 0xF
    
    if opcode == 0b0010:  # LB
      ra = (instruction >> 8) & 0xF
      imm8 = instruction & 0xFF
      if imm8 & 0x80:  # If the highest bit (sign bit) is set
        imm8 -= 0x100  # Convert to negative two's complement
      address = self.io + imm8
      self.registers[ra] = self.read_byte(address)
    
    elif opcode == 0b0011:  # LW
      ra = (instruction >> 8) & 0xF
      imm8 = instruction & 0xFF
      if imm8 & 0x80:  # If the highest bit (sign bit) is set
        imm8 -= 0x100  # Convert to negative two's complement
      address = self.io + imm8
      if address % 2 != 0:
        raise ValueError("Access to an odd address is not allowed: 0x{:X}".format(address))
      self.registers[ra] = self.read_word(address)
  
    elif opcode == 0b0110:  # SB
      ra = (instruction >> 8) & 0xF
      imm8 = instruction & 0xFF
      if imm8 & 0x80:  # If the highest bit (sign bit) is set
        imm8 -= 0x100  # Convert to negative two's complement
      address = self.io + imm8
      self.write_byte(address, self.registers[ra])
    
    elif opcode == 0b0111:  # SW
      ra = (instruction >> 8) & 0xF
      imm8 = instruction & 0xFF
      if imm8 & 0x80:  # If the highest bit (sign bit) is set
        imm8 -= 0x100  # Convert to negative two's complement
      address = self.io + imm8
      if address % 2 != 0:
        raise ValueError("Access to an odd address is not allowed: 0x{:X}".format(address))
      self.write_word(address, self.registers[ra])
  
    elif opcode == 0b0001:  # MV
      ra = (instruction >> 4) & 0xF
      rb = instruction & 0xF
      self.registers[ra] = self.registers[rb]
    
    elif opcode == 0b0100: # MVL
      ra = (instruction >> 8) & 0xF
      imm8 = instruction & 0xFF
      self.registers[ra] = (self.registers[ra] & 0xFF00) | (imm8)
      
    elif opcode == 0b0101: # MVH
      ra = (instruction >> 8) & 0xF
      imm8 = instruction & 0xFF
      self.registers[ra] = (self.registers[ra] & 0x00FF) | (imm8 << 8)
    
    elif opcode == 0x8:  # Arithmetic operations ADD and ADC
      ra = (instruction >> 6) & 0xF
      rb = instruction & 0xF
      imm = instruction & 0x3F
      is_imm = (instruction >> 10) & 0x1
      
      if ((instruction >> 11) & 0x1) == 0x0:  # ADD
        b = imm if is_imm else self.registers[rb]
        self.registers[ra] = self.alu_add(self.registers[ra], b)
      elif ((instruction >> 11) & 0x1) == 0x1:  # ADC
        b = imm if is_imm else self.registers[rb]
        self.registers[ra] = self.alu_add(self.registers[ra], b, with_carry=True)

    elif opcode == 0x9: # Rest of Arithmetic operations
      subop = (instruction >> 8) & 0xF
      ra = (instruction >> 4) & 0xF
      rb = instruction & 0xF

      if (instruction >> 10) & 0x1:  # SUB
        ra = (instruction >> 6) & 0xF
        imm = instruction & 0x3F
        is_imm = (instruction >> 10) & 0x1
        b = imm if is_imm else self.registers[rb]
        self.registers[ra] = self.alu_sub(self.registers[ra], b)
      elif subop == 0x8:  # AND
        self.registers[ra] = self.alu_and(self.registers[ra], self.registers[rb])
      elif subop == 0x9:  # OR
        self.registers[ra] = self.alu_or(self.registers[ra], self.registers[rb])
      elif subop == 0xA:  # NOT
        self.registers[ra] = self.alu_not(self.registers[ra])
      elif subop == 0xB:  # XOR
        self.registers[ra] = self.alu_xor(self.registers[ra], self.registers[rb])
      elif subop == 0xC:  # SLL
        self.registers[ra] = self.alu_shift(self.registers[ra], self.registers[rb], 'left')
      elif subop == 0xD:  # SRL
        self.registers[ra] = self.alu_shift(self.registers[ra], self.registers[rb], 'right')
      elif subop == 0xE:  # SRA
        self.registers[ra] = self.alu_shift(self.registers[ra], self.registers[rb], 'right', arithmetic=True)
      
    elif opcode == 0xC:  # Control instructions
      if (instruction >> 8) & 0xF == 0x1: # CALL
        imm8 = instruction & 0xFF
        if imm8 & 0x80:  # If the highest bit (sign bit) is set
          imm8 -= 0x100  # Convert to negative two's complement
        self.lr = self.pc
        self.pc = self.io + imm8
      subop = (instruction >> 4) & 0xF
      if subop == 0x0:  # SET
        ra = instruction & 0xF
        self.set_flags(self.registers[ra])
      elif subop == 0x2:  # PUSH
        ra = instruction & 0xF
        self.sp -= 2
        self.write_word(self.sp, self.registers[ra])
      elif subop == 0x3:  # POP
        ra = instruction & 0xF
        self.registers[ra] = self.read_word(self.sp)
        self.sp += 2
      elif subop == 0x1:  # RET
        self.pc = self.lr

    elif opcode in [0xE, 0xF]:  # Jump instructions
      imm8 = instruction & 0xFF
      if imm8 & 0x80:  # If the highest bit (sign bit) is set
        imm8 -= 0x100  # Convert to negative two's complement
      condition = (instruction >> 8) & 0x7
      is_branch_offset = opcode == 0xE

      if instruction & 0x1:
        raise ValueError("Jumped to uneven address; not supported!")
      
      should_jump = False
      if condition == 0:  # Unconditional
        should_jump = True
      elif condition == 1 and self.z:  # Z
        should_jump = True
      elif condition == 2 and not self.z:  # NZ
        should_jump = True
      elif condition == 3 and self.c:  # C
        should_jump = True
      elif condition == 4 and self.v:  # V
        should_jump = True
      elif condition == 5 and self.n:  # N
        should_jump = True
      elif condition == 6 and self.p:  # P
        should_jump = True
          
      if should_jump:
        if is_branch_offset:
          self.pc += imm8
          if self.pc > 0xFFFF or self.pc < 0x0000:
            raise ValueError("PC out of range, jumped too far.")
          #self.pc += sign_extend(imm8, 8)
        else:
          self.pc = self.io + imm8
          #self.pc = self.read_word((self.registers[12] << 8) + imm8)
  
  def run(self, ttl = None):
    if ttl == None:
      ttl = 0xFFFF # Change for longer programs 
    while ttl > 0:
      instruction = self.fetch()
      self.decode_and_execute(instruction)

      ttl -= 1
      # halt condition
      if self.pc > 0xFFF4:
        print("\033[31m[halt]\033[0m reached 0xFFF4 with PC")
        break

    if ttl == 0:
      print("\033[31m[halt]\033[0m ttl decreased to 0")

  def read_byte(self, address):
    return self.memory[address] & 0xFF

  def read_word(self, address):
    return (self.memory[address] << 8) | self.memory[address + 1]

  def write_byte(self, address, value):
    self.memory[address] = value & 0xFF

  def write_word(self, address, value):
    self.memory[address] = (value >> 8) & 0xFF
    self.memory[address + 1] = value & 0xFF

  def alu_add(self, a, b, with_carry=False):
    result = a + b + (self.c if with_carry else 0)
    self.c = 1 if result > 0x7FFF else 0 # TODO: check carry
    self.v = 1 if (a ^ result) & (b ^ result) & 0x8000 else 0 #TODO: check line
    return result & 0xFFFF

  def alu_sub(self, a, b):
    result = a - b
    self.c = 0 if result > 0 else 1 # TODO: check carry
    self.v = 1 if (a ^ b) & (a ^ result) & 0x8000 else 0
    return result & 0xFFFF

  def alu_and(self, a, b):
    result = a & b
    return result

  def alu_or(self, a, b):
    result = a | b
    return result

  def alu_xor(self, a, b):
    result = a ^ b
    return result

  def alu_not(self, a):
    result = ~a & 0xFFFF
    return result

  def alu_shift(self, a, b, direction, arithmetic=False):
    if direction == 'left':
      result = (a << b) & 0xFFFF
    else:  # right shift
      if arithmetic and (a & 0x8000):
        result = ((a & 0xFFFF) >> b) | (~(0xFFFF >> b) & 0xFFFF)
      else:
        result = (a & 0xFFFF) >> b
    return result

  def set_flags(self, result):
    self.z = 1 if result == 0 else 0
    self.n = 1 if result & 0x8000 else 0
    self.p = 1 if not self.z and not self.n else 0

  def print_registers(self):
    print("\033[34m--- printing contents of registers ---\033[0m")
    for i, reg_name in enumerate(['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'IO', 'LR', 'SP', 'PC', 'FL']):
      value_dec = self.registers[i]       # Decimal value
      value_hex = hex(self.registers[i])  # Hexadecimal value
      print(f"{reg_name: <4}: {value_dec: >10}  {value_hex: >10}")

  def print_registers_dense(self):
    print("\033[34m--- printing contents of registers ---\033[0m")
    for i in range(0, 16, 4):  # Process 4 registers at a time
      line = ""
      for j in range(4):
        reg_name = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'IO', 'LR', 'SP', 'PC', 'FL'][i+j]
        value_dec = self.registers[i+j]
        value_hex = hex(self.registers[i+j])
        line += f"{reg_name: <4}: {value_dec: >10} {value_hex: >10}    "
      print(line)

  def print_flags(self):
    print("\033[34m--- printing flags ---\033[0m")  # Blue heading
    print(f"Z: {self.z}   N: {self.n}   P: {self.p}   C: {self.c}   V: {self.v}")

  def detect_register_changes(self, old_registers):
    changed_registers = []
    for i in range(14):
      if self.registers[i] != old_registers[i]:
        changed_registers.append(i)

    # only notify when PC changes to something other than +2 (or +0 when no execute during prompt)
    if self.pc != old_registers[14] + 2 and self.pc != old_registers[14]: 
      changed_registers.append(14)
    return changed_registers
  
  def detect_flag_changes(self, old_flags):
    changed_flags = []
    current_flags = {'z': self.z, 'n': self.n, 'p': self.p, 'c': self.c, 'v': self.v}
    for flag, old_value in old_flags.items():
      if current_flags[flag] != old_value:
        changed_flags.append(flag)
    return changed_flags

  def evaluate_registers(self, output = None, halt = None, r1 = None, r2 = None, r3 = None, r4 = None, r5 = None, r6 = None, r7 = None, r8 = None, r9 = None, r10 = None, r11 = None, io = None, lr = None, sp = None, pc = None, fl = None):
    error = False
    if output:
      print("--- start evaluation of registers ---")
    if r1 != None and r1 != self.registers[0x0]:
      error = True
      print(f"\033[31m[error]\033[0m R1 doesnt match: specified: {r1} -- actual: {self.registers[0x0]}")
    if r2 != None and r2 != self.registers[0x1]:
      error = True
      print(f"\033[31m[error]\033[0m R2 doesnt match: specified: {r2} -- actual: {self.registers[0x1]}")
    if r3 != None and r3 != self.registers[0x2]:
      error = True
      print(f"\033[31m[error]\033[0m R3 doesnt match: specified: {r3} -- actual: {self.registers[0x2]}")
    if r4 != None and r4 != self.registers[0x3]:
      error = True
      print(f"\033[31m[error]\033[0m R4 doesnt match: specified: {r4} -- actual: {self.registers[0x3]}")
    if r5 != None and r5 != self.registers[0x4]:
      error = True
      print(f"\033[31m[error]\033[0m R5 doesnt match: specified: {r5} -- actual: {self.registers[0x4]}")
    if r6 != None and r6 != self.registers[0x5]:
      error = True
      print(f"\033[31m[error]\033[0m R6 doesnt match: specified: {r6} -- actual: {self.registers[0x5]}")
    if r7 != None and r7 != self.registers[0x6]:
      error = True
      print(f"\033[31m[error]\033[0m R7 doesnt match: specified: {r7} -- actual: {self.registers[0x6]}")
    if r8 != None and r8 != self.registers[0x7]:
      error = True
      print(f"\033[31m[error]\033[0m R8 doesnt match: specified: {r8} -- actual: {self.registers[0x7]}")
    if r9 != None and r9 != self.registers[0x8]:
      error = True
      print(f"\033[31m[error]\033[0m R9 doesnt match: specified: {r9} -- actual: {self.registers[0x8]}")
    if r10 != None and r10 != self.registers[0x9]:
      error = True
      print(f"\033[31m[error]\033[0m R10 doesnt match: specified: {r10} -- actual: {self.registers[0x9]}")
    if r11 != None and r11 != self.registers[0xA]:
      error = True
      print(f"\033[31m[error]\033[0m R11 doesnt match: specified: {r11} -- actual: {self.registers[0xA]}")
    if io != None and io != self.io:
      error = True
      print(f"\033[31m[error]\033[0m IO doesnt match: specified: {io} -- actual: {self.io}")
    if lr != None and lr != self.lr:
      error = True
      print(f"\033[31m[error]\033[0m LR doesnt match: specified: {lr} -- actual: {self.lr}")
    if sp != None and sp != self.sp:
      error = True
      print(f"\033[31m[error]\033[0m SP doesnt match: specified: {sp} -- actual: {self.sp}")
    if pc != None and pc != self.pc:
      error = True
      print(f"\033[31m[error]\033[0m PC doesnt match: specified: {pc} -- actual: {self.pc}")
    if fl != None and fl != self.fl:
      error = True
      print(f"\033[31m[error]\033[0m FL doesnt match: specified: {fl} -- actual: {self.fl}")
    if error == False and output:
      print("\033[32m[passed]\033[0m no errors")
    if error and halt:
      raise ValueError("Invalid register content")
    return error
  
  def stepwise_run(self):
    cycle_count = 0
    print_changes = True

    changed_registers = []
    changed_flags = []

    while True:
      # Ask the user for input
      instruction = self.fetch()
      instruction_asm = disassembler.disassemble_instruction(hex(instruction))
      # maybe set width of disassembled instr higher
      user_input = input(f"PC: 0x{self.pc:04X}, instr: 0x{instruction:04X} ({instruction_asm:11}), Cycle: {cycle_count:03}. Enter # of instr to execute, (r/re)gisters, (f)lags, (t)oggle changes, (q)uit: ").strip()

      old_registers = self.registers[:]
      old_flags = {'z': self.z, 'n': self.n, 'p': self.p, 'c': self.c, 'v': self.v}

      if user_input == '':
        # Execute one instruction if input is empty
        self.decode_and_execute(instruction)
        cycle_count += 1  # Increment cycle count by 1
      elif user_input.isdigit():
        # Execute specified number of instructions
        for _ in range(int(user_input)):
          instruction = self.fetch()
          self.decode_and_execute(instruction)
          cycle_count += 1  # Increment cycle count by 1
          if self.pc > 0xFFF4:
            print("\033[31m[halt]\033[0m reached 0xFFF4 with PC")
            break
      elif user_input.lower() == 'r':
        # Print registers dense
        self.print_registers_dense()
      elif user_input.lower() == 're':
        #print registers extended
        self.print_registers()
      elif user_input.lower() == 'f':
        # Print flags
        self.print_flags()
      elif user_input == 'n':
        instruction = self.fetch()
        instruction_asm = disassembler.disassemble_instruction(hex(instruction))
        print(f"instr:\t{hex(instruction)} {instruction_asm}")
      elif user_input == 'l':
        self.pc -= 2
        instruction = self.fetch()
        instruction_asm = disassembler.disassemble_instruction(hex(instruction))
        self.pc += 2
        print(f"instr:\t{hex(instruction)} {instruction_asm}")
      elif user_input == 't':
        print_changes = not print_changes
        if print_changes:
          print("register and flag changes will now be printed")
        else:
          print("no more register and flag changes will be printed")
      elif user_input.lower() == 'q':
        # Quit the execution
        print("Execution halted by user.")
        break
      else:
        # Handle invalid input
        print("Invalid input. Please enter a number, 'r', 'f', or 'q'.")

      # Detect changes in registers and flags
      if print_changes:
        changed_registers = self.detect_register_changes(old_registers)
        changed_flags = self.detect_flag_changes(old_flags)

      # Print changed registers
      if changed_registers and print_changes:
        print("\033[33m--- Registers changed ---\033[0m")
        for reg in changed_registers:
          reg_name = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'IO', 'LR', 'SP', 'PC', 'FL'][reg]
          print(f"  {reg_name}: {self.registers[reg]} (0x{self.registers[reg]:X})")

      # Print changed flags
      if changed_flags and print_changes:
        print("\033[38;5;214m--- Flags changed ---\033[0m")
        for flag in changed_flags:
          print(f"  {flag.upper()} flag changed to {getattr(self, flag)}")

      # Optional halt condition (e.g., if PC reaches 0xFFF4)
      if self.pc > 0xFFF4:
        print("\033[31m[halt]\033[0m reached 0xFFF4 with PC")
        break


# Helper functions
def sign_extend(value, bits):
  sign_bit = 1 << (bits - 1)
  return (value & (sign_bit - 1)) - (value & sign_bit)