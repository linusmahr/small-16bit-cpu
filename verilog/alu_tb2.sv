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

  // Test case arrays
  logic [15:0] test_instructions [];
  logic [15:0] test_regA [];
  logic [15:0] test_regA_imm6 [];
  logic [15:0] test_regA_imm8 [];
  logic [15:0] test_regB [];
  logic test_carry [];
  logic [15:0] test_expected_results [];
  string test_names [];

  integer num_tests;

  // Initialize test cases
  initial begin
    // Define the number of test cases
    num_tests = 13;

    // Allocate arrays
    test_instructions = new[num_tests];
    test_regA = new[num_tests];
    test_regA_imm6 = new[num_tests];
    test_regA_imm8 = new[num_tests];
    test_regB = new[num_tests];
    test_carry = new[num_tests];
    test_expected_results = new[num_tests];
    test_names = new[num_tests];

    // Initialize test cases
    test_instructions = '{
      16'b1000000000000001, 16'b1000000000100001, 16'b1000100000000001,
      16'b1000100000100001, 16'b1001000000000001, 16'b1001000000100001,
      16'b1001100000000000, 16'b1001100001000000, 16'b1001100010000000,
      16'b1001100011000000, 16'b1001100100000000, 16'b1001100101000000,
      16'b1001100110000000
    };

    test_regA = '{
      16'd10, 16'd10, 16'd10, 16'd10, 16'd10, 16'd10,
      16'd10, 16'd10, 16'd10, 16'd10, 16'd10, 16'd10, 16'hFFF0
    };

    test_regA_imm6 = '{
      16'd10, 16'd10, 16'd10, 16'd10, 16'd10, 16'd10,
      16'd10, 16'd10, 16'd10, 16'd10, 16'd10, 16'd10, 16'hFFF0
    };

    test_regA_imm8 = '{
      16'd10, 16'd10, 16'd10, 16'd10, 16'd10, 16'd10,
      16'd10, 16'd10, 16'd10, 16'd10, 16'd10, 16'd10, 16'hFFF0
    };

    test_regB = '{
      16'd5, 16'd0, 16'd5, 16'd0, 16'd5, 16'd0,
      16'd5, 16'd5, 16'd5, 16'd5, 16'd2, 16'd1, 16'd1
    };

    test_carry = '{
      1'b0, 1'b0, 1'b1, 1'b1, 1'b0, 1'b0,
      1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0
    };

    test_expected_results = '{
      16'd15, 16'd11, 16'd16, 16'd12, 16'd5, 16'd9,
      16'd0, 16'd15, 16'hFFF5, 16'd15, 16'd40, 16'd5, 16'hFFF8
    };

    test_names = '{
      "ADD without immediate", "ADD with immediate", "ADC without immediate",
      "ADC with immediate", "SUB without immediate", "SUB with immediate",
      "AND", "OR", "NOT", "XOR", "SLL", "SRL", "SRA"
    };

    run_tests();
  end

  task run_tests();
    for (int i = 0; i < num_tests; i++) begin
      // Apply inputs
      instruction = test_instructions[i];
      regA = test_regA[i];
      regA_imm6 = test_regA_imm6[i];
      regA_imm8 = test_regA_imm8[i];
      regB = test_regB[i];
      carry = test_carry[i];

      // Wait for combinational logic to settle
      #10;

      // Check result
      if (result === test_expected_results[i]) begin
        $display("Test Case %0d (%s): PASSED", i, test_names[i]);
      end else begin
        $display("Test Case %0d (%s): FAILED. Expected %0h, Got %0h", i, test_names[i], test_expected_results[i], result);
      end
    end

    $finish;
  endtask

endmodule