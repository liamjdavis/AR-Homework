from typing import List, TextIO
import sys


class SudokuEncoder:
    def __init__(self) -> None:
        self.size = 9
        self.clauses: List[List[int]] = []
        self.num_clauses = 0

    def _add_clause(self, clause: List[int]) -> None:
        """Add a clause and increment clause counter"""
        self.clauses.append(clause)
        self.num_clauses += 1

    def get_var(self, row: int, col: int, num: int) -> int:
        """Convert (row, col, num) to DIMACS variable number"""
        return row * 81 + col * 9 + num

    def encode_cell_constraints(self) -> None:
        """Each cell must contain exactly one number"""
        for row in range(self.size):
            for col in range(self.size):
                # At least one number in each cell
                self._add_clause([self.get_var(row, col, num) for num in range(1, 10)])
                
                # At most one number in each cell
                for num1 in range(1, 10):
                    for num2 in range(num1 + 1, 10):
                        self._add_clause(
                            [-self.get_var(row, col, num1), -self.get_var(row, col, num2)]
                        )

    def encode_row_constraints(self) -> None:
        """Each number must appear exactly once in each row"""
        for row in range(self.size):
            for num in range(1, 10):
                self._add_clause([self.get_var(row, col, num) for col in range(self.size)])

    def encode_col_constraints(self) -> None:
        """Each number must appear exactly once in each column"""
        for col in range(self.size):
            for num in range(1, 10):
                self._add_clause([self.get_var(row, col, num) for row in range(self.size)])

    def encode_block_constraints(self) -> None:
        """Each number must appear exactly once in each 3x3 block"""
        for block_row in range(3):
            for block_col in range(3):
                for num in range(1, 10):
                    self._add_clause(
                        [
                            self.get_var(block_row * 3 + i, block_col * 3 + j, num)
                            for i in range(3)
                            for j in range(3)
                        ]
                    )

    def encode_initial_values(self, puzzle: List[List[int]]) -> None:
        """Encode the initial values from the puzzle"""
        for row in range(self.size):
            for col in range(self.size):
                if puzzle[row][col] != 0:
                    self._add_clause([self.get_var(row, col, puzzle[row][col])])

    def write_dimacs(self, output_file: TextIO) -> None:
        """Write the CNF formula in DIMACS format"""
        output_file.write(f"c Encoded Sudoku puzzle\n")
        output_file.write(f"p cnf {self.size ** 3} {self.num_clauses}\n")
        for clause in self.clauses:
            output_file.write(" ".join(map(str, clause)) + " 0\n")

    @staticmethod
    def validate_puzzle(puzzle: List[List[int]]) -> bool:
        """Validate puzzle"""
        if len(puzzle) != 9:
            return False
        return all(len(row) == 9 and all(0 <= x <= 9 for x in row) for row in puzzle)

    def encode_puzzle(self, puzzle: List[List[int]], output_path: str) -> bool:
        """Encode sudoku to DIMACS CNF"""
        if not self.validate_puzzle(puzzle):
            print("Error: Invalid puzzle format. Must be 9x9 with values 0-9")
            return False

        self.encode_cell_constraints()
        self.encode_row_constraints()
        self.encode_col_constraints()
        self.encode_block_constraints()
        self.encode_initial_values(puzzle)

        with open(output_path, 'w') as f:
            self.write_dimacs(f)
        return True


if __name__ == "__main__":
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    encoder = SudokuEncoder()
    
    if encoder.encode_puzzle(puzzle, "output.cnf"):
        print("Successfully encoded puzzle to output.cnf")
    else:
        print("Failed to encode puzzle")