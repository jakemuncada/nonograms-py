"""
The nonogram puzzle model.
"""

import logging


logger = logging.getLogger(__name__)
console = logging.getLogger('console')


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
    def from_json(cls, json_data):
        """
        Instantiate a puzzle from json.
        """
        nrows: int = json_data['nrows']
        ncols: int = json_data['ncols']
        left_clues_str_list: list[str] = json_data['left_clues']
        top_clues_str_list: list[str] = json_data['top_clues']

        if len(left_clues_str_list) != nrows:
            logger.error(f'Failed to instantiate puzzle from json, '
                         f'the left clues list has {len(left_clues_str_list)} while nrows is {nrows}.')
                         
        if len(top_clues_str_list) != ncols:
            logger.error(f'Failed to instantiate puzzle from json, '
                         f'the top clues list has {len(top_clues_str_list)} while ncols is {ncols}.')

        row_clues: list[list[int]] = []
        col_clues: list[list[int]] = []

        for clue_str in left_clues_str_list:
            row: list[int] = []
            for clue_val_str in clue_str.strip().split(' '):
                clue_val = int(clue_val_str)
                if clue_val > 0:
                    row.insert(0, clue_val)
            row_clues.append(row)
            
        grid: list[list[int]] = []
        for clue_str in top_clues_str_list:
            clues = list(map(int, clue_str.strip().split(' ')))
            grid.append(clues)
        
        grid_nrows = len(grid)
        grid_ncols = len(grid[0])
        for c in range(grid_ncols):
            clues = []
            for r in range(grid_nrows - 1, -1, -1):
                num = grid[r][c]
                if num <= 0:
                    break
                clues.append(num)
            col_clues.append(clues)
        
        return cls(nrows, ncols, row_clues, col_clues)

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