module alu (
  input logic [15:0] instruction,
  input logic [15:0] regA,
  input logic [15:0] regA_imm6,
  input logic [15:0] regA_imm8,
  input logic [15:0] regB,
  input logic carry,
  output logic [15:0] result
);
  
  // Declare
  logic is_imm_10;
  logic [5:0] imm6;
  logic [7:0] imm8;

  always_comb begin
    // Initialize
    is_imm_10 = instruction[10];  // imm bit is at position 10
    imm6 = instruction[5:0];
    imm8 = instruction[7:0];


    // Check if instruction is ADD, ADC, or SUB
    case (instruction[15:11])
      5'b10000: begin
        // ADD operation
        // uses imm6
        //$display("ADD: instr: %0h regA: %0h regB: %0h imm6: %0h", instruction, regA_imm6, regB, imm6);
        // TODO: set flags and 2complement
        if (is_imm_10 == 1) begin
          result = regA_imm6 + imm6;
        end else begin
          result = regA_imm6 + regB;
        end
      end

      5'b10001: begin
        // ADC operation
        // uses imm6

        // TODO: set flags and 2complement
        if (is_imm_10 == 1) begin
          result = regA_imm6 + imm6 + carry;
        end else begin
          result = regA_imm6 + regB + carry;
        end
      end

      5'b10010: begin
        // SUB operation
        // Implement your SUB logic here

        // TODO: set flags and 2complement
        if (is_imm_10 == 1) begin
          result = regA_imm6 - imm6;
        end else begin
          result = regA_imm6 - regB;
        end
      end

      5'b10011: begin
        // AND, OR, NOT, XOR, SLL, SRL and SRA operations

        case(instruction[10:8])
          3'b000: begin
            // AND
            result = regA & regB;
          end

          3'b001: begin
            // OR
            result = regA | regB;
          end

          3'b010: begin
            // NOT
            result = ~regA;
          end

          3'b011: begin
            // XOR
            result = regA ^ regB;
          end

          3'b100: begin
            // SLL
            result = regA << regB;
          end

          3'b101: begin
            // SRL
            result = regA >> regB;
          end

          3'b110: begin
            // SRA
            result = regA >>> regB;
          end

          default: begin
            // unknown
            result = 16'h0;
          end

        endcase
      end
      default: begin
        // Handle unknown instruction
        result = 16'h0;
      end
    endcase
  end

endmodule
