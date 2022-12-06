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

    def __init__(self,
                 nrows: int,
                 ncols: int,
                 top_clues: list[list[int]] = None,
                 left_clues: list[list[int]] = None):

        if nrows <= 0 or ncols <= 0:
            logger.error(f'Invalid bleeping puzzle size: {nrows}x{ncols}')
            raise ValueError(f'Invalid bleeping puzzle size: {nrows}x{ncols}')
        
        if top_clues is not None:
            if len(top_clues) <= 0 or len(top_clues[0]) != ncols:
                logger.error(f'The top clues grid size is not bleeping valid: {top_clues}')
                raise ValueError('The top clues grid is not bleeping valid.')
            
            if not Puzzle.__is_2d_grid_rectangular(top_clues):
                logger.error(f'The top clues grid is not bleeping rectangular: {top_clues}')
                raise ValueError(f'The top clues grid is not bleeping rectangular.')

        if left_clues is not None:
            if len(left_clues) != nrows or len(left_clues[0]) <= 0:
                logger.error(f'The left clues grid size is not bleeping valid: {left_clues}')
                raise ValueError('The left clues grid is not bleeping valid.')

            if not Puzzle.__is_2d_grid_rectangular(left_clues):
                logger.error(f'The left clues grid is not bleeping rectangular: {left_clues}')
                raise ValueError(f'The left clues grid is not bleeping rectangular.')

        self.__nrows = nrows
        self.__ncols = ncols
        self.__top_clues_nrows = len(top_clues) if top_clues is not None else 0
        self.__top_clues_ncols = len(top_clues[0]) if top_clues is not None else 0
        self.__left_clues_nrows = len(left_clues) if left_clues is not None else 0
        self.__left_clues_ncols = len(left_clues[0]) if left_clues is not None else 0

        self.board: list[list[str]] = []
        """The puzzle board."""

        self.top_clues_grid: list[list[int]] = top_clues if top_clues is not None else []
        """The top clues grid."""
        self.left_clues_grid: list[list[int]] = left_clues if left_clues is not None else []
        """The left clues grid."""
        
        self.top_clues_ticks: list[list[bool]] = []
        """
        Grid of boolean values that specifies whether or not
        the clue number in the top clue grid is ticked/crossed off.
        """
        self.left_clues_ticks: list[list[bool]] = []
        """
        Grid of boolean values that specifies whether or not
        the clue number in the left clue grid is ticked/crossed off.
        """

        for _ in range(nrows):
            row = [ ' ' for _ in range(ncols) ]
            self.board.append(row)

        if top_clues is not None:
            for _ in range(self.__top_clues_nrows):
                row = [ False for _ in range(self.__top_clues_ncols) ]
                self.top_clues_ticks.append(row)

        if left_clues is not None:
            for _ in range(self.__left_clues_nrows):
                row = [ False for _ in range(self.__left_clues_ncols) ]
                self.left_clues_ticks.append(row)

    @classmethod
    def from_json(cls, json_data):
        """
        Instantiate a puzzle from json.
        """
        nrows: int = json_data['nrows']
        ncols: int = json_data['ncols']
        top_clues_str_list: list[str] = json_data['top_clues']
        left_clues_str_list: list[str] = json_data['left_clues']

        top_clues: list[list[int]] = None
        left_clues: list[list[int]] = None

        if top_clues_str_list is not None:
            top_clues = []
            for line in top_clues_str_list:
                clue_row = line.strip().split(' ')
                clue_row = list(x for x in clue_row if x != '')
                clue_row = list(map(int, clue_row))
                top_clues.append(clue_row)

        if left_clues_str_list is not None:
            left_clues = []
            for line in left_clues_str_list:
                clue_row = line.strip().split(' ')
                clue_row = list(x for x in clue_row if x != '')
                clue_row = list(map(int, clue_row))
                left_clues.append(clue_row)
        
        return cls(nrows, ncols, top_clues, left_clues)

    @property
    def nrows(self) -> int:
        """The number of rows in the puzzle."""
        return self.__nrows
        
    @property
    def ncols(self) -> int:
        """The number of columns in the puzzle."""
        return self.__ncols
        
    @property
    def top_clues_nrows(self) -> int:
        """The number of rows in the top clues grid."""
        return self.__top_clues_nrows
        
    @property
    def top_clues_ncols(self) -> int:
        """The number of cols in the top clues grid."""
        return self.__top_clues_ncols
        
    @property
    def left_clues_nrows(self) -> int:
        """The number of rows in the left clues grid."""
        return self.__left_clues_nrows
        
    @property
    def left_clues_ncols(self) -> int:
        """The number of cols in the left clues grid."""
        return self.__left_clues_ncols

    @staticmethod
    def __is_2d_grid_rectangular(grid: list[list[str]]) -> bool:
        """
        Returns true if the grid is rectangular, i.e. all rows have the same number of columns.
        Returns false otherwise.
        """
        if len(grid) == 0 or len(grid[0]) == 0:
            return False

        for row_idx in range(1, len(grid)):
            if len(grid[row_idx]) != len(grid[0]):
                return False

        return True

    def is_filled(self, row: int, col: int) -> bool:
        """
        Returns true if the specified cell is filled. Returns false otherwise.
        Also returns false if the specified cell is out of bounds.
        """
        if row < 0 or row >= self.nrows or col < 0 or col >= self.ncols:
            return False
        return self.board[row][col] == '.'

    def is_crossed(self, row: int, col: int) -> bool:
        """
        Returns true if the specified cell is crossed out. Returns false otherwise.
        Also returns false if the specified cell is out of bounds.
        """
        if row < 0 or row >= self.nrows or col < 0 or col >= self.ncols:
            return False
        return self.board[row][col] == 'x'

    def is_blank(self, row: int, col: int) -> bool:
        """
        Returns true if the specified cell is neither filled nor crossed out. Returns false otherwise.
        Also returns false if the specified cell is out of bounds.

        Note that cells containing other symbols will be treated as blank cells.
        """
        if row < 0 or row >= self.nrows or col < 0 or col >= self.ncols:
            return False
        return self.board[row][col] != '.' and self.board[row][col] != 'x'