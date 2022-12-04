"""
The nonogram puzzle model.
"""

class Puzzle:
    """
    The nonogram puzzle model.
    """

    def __init__(self, nrows: int, ncols: int, row_clues: list[list[int]], col_clues: list[list[int]]):
        if nrows == 0 or ncols == 0:
            raise ValueError('The number of rows/columns must not be zero.')
        self.__nrows = nrows
        self.__ncols = ncols

        self.board: list[list[str]] = []
        for _ in range(nrows):
            row = [ ' ' for _ in range(ncols) ]
            self.board.append(row)

        self.row_clues: list[list[int]] = row_clues
        # Count the maximum clues that a row can have.
        max_clues = 0
        for row in self.row_clues:
            clue_count = len(row)
            max_clues = max(max_clues, clue_count)
        self.__max_row_clues = max_clues

        self.col_clues: list[list[int]] = col_clues
        # Count the maximum clues that a column can have.
        max_clues = 0
        for col in self.col_clues:
            clue_count = len(col)
            max_clues = max(max_clues, clue_count)
        self.__max_col_clues = max_clues

    @classmethod
    def get_sample(cls):
        """
        Get a sample puzzle.
        """
        row_clues = [
            [1, 1, 1],
            [4, 2],
            [5, 1, 1, 3],
            [4, 2],
            [5, 1, 3],
            [5, 1, 3],
            [4, 4],
            [1, 6, 3],
            [1, 4, 2],
            [3, 5],
            [3, 5, 1],
            [3, 4, 1],
            [4, 5],
            [11],
            [7],
        ]

        col_clues = [
            [1, 5],
            [2, 7],
            [2, 7],
            [4, 1, 2],
            [6, 1],
            [6, 1, 1],
            [2, 5, 2],
            [2, 4, 1],
            [2, 4, 1],
            [2, 4, 2],
            [3, 8],
            [3, 1, 6],
            [5, 5],
            [4, 4],
            [2, 1, 1],
        ]

        puzzle = cls(15, 15, row_clues, col_clues)
        return puzzle

    @property
    def nrows(self) -> int:
        """The number of rows in the puzzle."""
        return self.__nrows
        
    @property
    def ncols(self) -> int:
        """The number of columns in the puzzle."""
        return self.__ncols

    @property
    def max_row_clues(self) -> int:
        """The maximum number of clues that a row can have."""
        return self.__max_row_clues

    @property
    def max_col_clues(self) -> int:
        """The maximum number of clues that a column can have."""
        return self.__max_col_clues

    def is_cell_filled(self, row: int, col: int) -> bool:
        """
        Returns true if the specified cell is filled. Returns false otherwise.
        Also returns false if the specified cell is out of bounds.
        """
        if row < 0 or row >= self.nrows or col < 0 or col >= self.ncols:
            return False
        return self.board[row][col] == '.'

    def is_cell_crossed(self, row: int, col: int) -> bool:
        """
        Returns true if the specified cell is crossed out. Returns false otherwise.
        Also returns false if the specified cell is out of bounds.
        """
        if row < 0 or row >= self.nrows or col < 0 or col >= self.ncols:
            return False
        return self.board[row][col] == 'x'

    def is_cell_blank(self, row: int, col: int) -> bool:
        """
        Returns true if the specified cell is neither filled nor crossed out. Returns false otherwise.
        Also returns false if the specified cell is out of bounds.

        Note that cells containing other symbols will be treated as blank cells.
        """
        if row < 0 or row >= self.nrows or col < 0 or col >= self.ncols:
            return False
        return self.board[row][col] != '.' and self.board[row][col] != 'x'