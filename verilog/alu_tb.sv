`timescale 1ns / 1ps

module alu_tb();

  // Inputs
  logic [15:0] instruction;
  logic [15:0] regA;
  logic [15:0] regA_imm6;
  logic [15:0] regA_imm8;
  logic [15:0] regB;
  logic carry;

  // Outputs
  logic [15:0] result;

  // Instantiate the Unit Under Test (UUT)
  alu uut (
    .instruction(instruction),
    .regA(regA),
    .regA_imm6(regA_imm6),
    .regA_imm8(regA_imm8),
    .regB(regB),
    .carry(carry),
    .result(result)
  );

  // Test case structure
  typedef struct {
    logic [15:0] instruction;
    logic [15:0] regA;
    logic [15:0] regA_imm6;
    logic [15:0] regA_imm8;
    logic [15:0] regB;
    logic carry;
    logic [15:0] expected_result;
    string test_name;
  } TestCase;

  TestCase test_cases[];

  // Initialize test cases
  initial begin
    test_cases = '{
      '{16'b1000000000000001, 16'd5, 16'd10, 16'd5, 16'd5, 1'b0, 16'd15, "ADD without immediate"},
      '{16'b1000000000000001, 16'd5, 16'd10, 16'd5, 16'd5, 1'b1, 16'd15, "ADD without immediate"},
      '{16'b1000000011000101, 16'd22, 16'd99, 16'd11, 16'd177, 1'b0, 16'd276, "ADD without immediate"},
      '{16'b1000010000100000, 16'd10, 16'd10, 16'd10, 16'd0, 1'b0, 16'd42, "ADD with immediate"},
      '{16'b1000010000100000, 16'd10, 16'd10, 16'd10, 16'd0, 1'b1, 16'd42, "ADD with immediate"},
      '{16'b1000100000000001, 16'd10, 16'd10, 16'd10, 16'd5, 1'b1, 16'd16, "ADC without immediate"},
      '{16'b1000100000100001, 16'd10, 16'd10, 16'd10, 16'd0, 1'b1, 16'd12, "ADC with immediate"},
      '{16'b1001000000000001, 16'd10, 16'd10, 16'd10, 16'd5, 1'b0, 16'd5, "SUB without immediate"},
      '{16'b1001000000100001, 16'd10, 16'd10, 16'd10, 16'd0, 1'b0, 16'd9, "SUB with immediate"},
      '{16'b1001100000000000, 16'd10, 16'd10, 16'd10, 16'd5, 1'b0, 16'd0, "AND"},
      '{16'b1001100001000000, 16'd10, 16'd10, 16'd10, 16'd5, 1'b0, 16'd15, "OR"},
      '{16'b1001100010000000, 16'd10, 16'd10, 16'd10, 16'd5, 1'b0, 16'hFFF5, "NOT"},
      '{16'b1001100011000000, 16'd10, 16'd10, 16'd10, 16'd5, 1'b0, 16'd15, "XOR"},
      '{16'b1001100100000000, 16'd10, 16'd10, 16'd10, 16'd2, 1'b0, 16'd40, "SLL"},
      '{16'b1001100101000000, 16'd10, 16'd10, 16'd10, 16'd1, 1'b0, 16'd5, "SRL"},
      '{16'b1001100110000000, 16'hFFF0, 16'hFFF0, 16'hFFF0, 16'd1, 1'b0, 16'hFFF8, "SRA"}
    };

    run_tests();
  end

  task run_tests();
    foreach (test_cases[i]) begin
      // Apply inputs
      instruction = test_cases[i].instruction;
      regA = test_cases[i].regA;
      regA_imm6 = test_cases[i].regA_imm6;
      regA_imm8 = test_cases[i].regA_imm8;
      regB = test_cases[i].regB;
      carry = test_cases[i].carry;

      // Wait for combinational logic to settle
      #10;

      // Check result
      if (result === test_cases[i].expected_result) begin
        $display("Test Case %0d (%s): PASSED", i, test_cases[i].test_name);
      end else begin
        $display("Test Case %0d (%s): FAILED. Expected %0h (%0d), Got %0h (%0d)", i, test_cases[i].test_name, test_cases[i].expected_result, test_cases[i].expected_result, result, result);
      end
    end

    $finish;
  endtask

endmodule