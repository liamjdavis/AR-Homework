from typing import List, Optional, Tuple
from pysat.solvers import Solver
from pysat.formula import CNF


class DPLLSolver:
    def __init__(self) -> None:
        self.size = 9  # Changed to 9x9
        self.cnf = CNF()
        self.solver = Solver(name="glucose3")
        self.propagated_clauses = 0

    def _count_clause(self) -> None:
        self.propagated_clauses += 1

    def read_dimacs(self, filename: str) -> List[List[int]]:
        """Read Sudoku puzzle from DIMACS format file"""
        sudoku = [[0 for _ in range(9)] for _ in range(9)]
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('c') or line.startswith('p'):
                    continue
                nums = list(map(int, line.strip().split()))
                if len(nums) == 1 and nums[0] > 0:
                    # Convert DIMACS variable to row, col, num
                    var = nums[0] - 1
                    num = var % 9 + 1
                    col = (var // 9) % 9
                    row = var // 81
                    sudoku[row][col] = num
        return sudoku

    def write_dimacs(self, solution: List[List[int]], filename: str) -> None:
        """Write solution to DIMACS format file"""
        with open(filename, 'w') as f:
            f.write('c DPLL Sudoku Solution\n')
            f.write(f'p cnf {self.size * self.size * self.size} {len(self.cnf.clauses)}\n')
            for row in range(self.size):
                for col in range(self.size):
                    num = solution[row][col]
                    var = row * 81 + col * 9 + num
                    f.write(f'{var} 0\n')

    def get_var(self, row: int, col: int, num: int) -> int:
        """Convert row, col, num to DIMACS variable"""
        return row * 81 + col * 9 + num

    def add_sudoku_clauses(self, initial_grid: List[List[int]]) -> None:
        """Generate clauses for 9x9 Sudoku in DIMACS format"""
        # Cell constraints
        for row in range(9):
            for col in range(9):
                # At least one number in each cell
                self.cnf.append([self.get_var(row, col, num) for num in range(1, 10)])
                self._count_clause()

                # At most one number in each cell
                for num1 in range(1, 10):
                    for num2 in range(num1 + 1, 10):
                        self.cnf.append(
                            [-self.get_var(row, col, num1), -self.get_var(row, col, num2)]
                        )
                        self._count_clause()

        # Row constraints
        for row in range(9):
            for num in range(1, 10):
                self.cnf.append([self.get_var(row, col, num) for col in range(9)])
                self._count_clause()

        # Column constraints
        for col in range(9):
            for num in range(1, 10):
                self.cnf.append([self.get_var(row, col, num) for row in range(9)])
                self._count_clause()

        # 3x3 block constraints
        for block_row in range(3):
            for block_col in range(3):
                for num in range(1, 10):
                    self.cnf.append(
                        [
                            self.get_var(
                                block_row * 3 + i,
                                block_col * 3 + j,
                                num,
                            )
                            for i in range(3)
                            for j in range(3)
                        ]
                    )
                    self._count_clause()

        # Initial assignments
        for row in range(9):
            for col in range(9):
                if initial_grid[row][col] != 0:
                    num = initial_grid[row][col]
                    self.cnf.append([self.get_var(row, col, num)])
                    self._count_clause()

    def extract_solution(self, model: List[int]) -> List[List[int]]:
        """Extract solution from Glucose"""
        solution = [[0 for _ in range(9)] for _ in range(9)]
        for var in model:
            if var > 0:
                var -= 1
                num = var % 9 + 1
                col = (var // 9) % 9
                row = var // 81
                solution[row][col] = num
        return solution

    def solve(self, input_file: str, output_file: str) -> Optional[List[List[int]]]:
        """Solve Sudoku puzzle from DIMACS file and write solution"""
        initial_grid = self.read_dimacs(input_file)
        self.add_sudoku_clauses(initial_grid)
        self.solver.append_formula(self.cnf.clauses)

        try:
            if self.solver.solve():
                model = self.solver.get_model()
                solution = self.extract_solution(model)
                self.write_dimacs(solution, output_file)
                return solution
            return None
        except Exception as e:
            print(f"Error solving Sudoku: {e}")
            return None

if __name__ == "__main__":
    solver = DPLLSolver()
    solution = solver.solve("output.cnf", "solution.cnf")
    if solution:
        for row in solution:
            print(row)
    else:
        print("No solution exists.")