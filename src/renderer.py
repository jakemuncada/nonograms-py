"""
Module for rendering the game to the screen.
"""

# TODO
# Refactor the Renderer to only strictly handle rendering stuff.
# Create another class (maybe called Controller) to handle the logic stuff?

import pygame
import logging
from typing import Optional
from functools import lru_cache

from src.coord import Coord
from src.cell_idx import CellIdx
from src.puzzle import Puzzle
import src.colors as colors
import src.utils.render_utils as utils


logger = logging.getLogger(__name__)
console = logging.getLogger('console')


class Renderer:
    """
    Renders the game to the screen.
    """

    MINIMUM_CELL_SIZE = 4

    def __init__(self, screen: pygame.Surface) -> None:
        self.__screen = screen
        """The main screen surface."""
        self.__screen.fill(colors.MAIN_BG)

        self.__fonts: list[pygame.font.Font] = []
        """The list of available fonts."""
        self.__fonts.append(pygame.font.SysFont('consolas', 40))
        self.__fonts.append(pygame.font.SysFont('consolas', 36))
        self.__fonts.append(pygame.font.SysFont('consolas', 32))
        self.__fonts.append(pygame.font.SysFont('consolas', 28))
        self.__fonts.append(pygame.font.SysFont('consolas', 24))
        self.__fonts.append(pygame.font.SysFont('consolas', 20))
        self.__fonts.append(pygame.font.SysFont('consolas', 18))
        self.__fonts.append(pygame.font.SysFont('consolas', 16))
        self.__fonts.append(pygame.font.SysFont('consolas', 14))
        self.__fonts.append(pygame.font.SysFont('consolas', 12))
        self.__fonts.append(pygame.font.SysFont('consolas', 10))
        self.__fonts.append(pygame.font.SysFont('consolas', 8))
        self.__fonts.append(pygame.font.SysFont('consolas', 6))
        self.__fonts.append(pygame.font.SysFont('consolas', 4))

        self.puzzle: Puzzle = None
        """The puzzle object."""

        self.cell_size: int = 0
        """The current size of the cell in pixels, including the zoom amount."""
        self.__cell_size_zoom_amt: int = 0
        """
        The current zoom amount. Positive values increase the cell size
        while negative values decrease it.
        """

        self.__pan_delta: Coord = Coord((0, 0))
        """The amount by which the whole puzzle is panned."""
        self.__pan_orig_coord: Coord = None
        """The original screen coordinates where the drag event originated."""
        self.__pan_orig_delta: Coord = None
        """The original pan delta when then drag event started."""
        self.is_dragging = False
        """True if the puzzle is currently being dragged."""

        self.draft_start_cell: CellIdx = None
        """The cell index where the draft started."""
        self.draft_end_cell: CellIdx = None
        """The cell index where the draft ends. Must be orthogonal to the start cell."""
        self.draft_symbol = '.'
        """The symbol currently being drafted."""
        self.is_drafting = False
        """True if the puzzle is currently being drafted."""

        self.toggle_clue_start_cell: CellIdx = None
        """The cell index where the clue toggling started."""
        self.toggle_clue_end_cell: CellIdx = None
        """The cell index where the clue toggling ends."""
        self.clue_cross_flag = True
        """When true, the clues will be crossed out. When false, the clues will be uncrossed."""
        self.is_toggling_top_clues = False
        """True if the top clues are currently being toggled."""
        self.is_toggling_left_clues = False
        """True if the left clues are currently being toggled."""

        self.cell_bdr = 1
        """The cell border thickness."""
        self.outer_bdr = self.cell_bdr * 2
        """The outer border thickness."""
        self.sep_bdr = self.cell_bdr * 2
        """The thickness of the separator border every 5 rows/cols."""

        self.board_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.top_clues_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.left_clues_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.parent_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        self.__cell_rect_memo: dict[tuple[int, int], pygame.Rect] = {}
        """Memoization dictionary for storing the rects of each cell. Key is the row-col index."""

        self.board_surface: pygame.Surface = None
        """The base board surface that contains the base grid."""

        self.symbol_surface: pygame.Surface = None
        """The board surface that contains the symbols."""

        self.left_clues_surface: pygame.Surface = None
        """The left clues panel."""

        self.top_clues_surface: pygame.Surface = None
        """The left clues panel."""

    @property
    def screen(self) -> pygame.Surface:
        """The display screen."""
        return self.__screen

    @property
    def pan_delta(self) -> Coord:
        """The pan delta."""
        return self.__pan_delta

    ################################################################################################
    # INITIALIZATION METHODS
    ################################################################################################

    def initialize_puzzle(self, puzzle: Puzzle) -> None:
        """
        Initialize the puzzle to be displayed.
        """
        logger.info(f'Initializing {puzzle.nrows}x{puzzle.ncols} puzzle...')
        self.puzzle = puzzle
        self.initialize_surfaces()

    def initialize_surfaces(self) -> None:
        """
        Initialize the board surface.
        """
        nrows = self.puzzle.nrows
        ncols = self.puzzle.ncols
        top_nrows = self.puzzle.top_clues_nrows
        left_ncols = self.puzzle.left_clues_ncols

        self.__cell_rect_memo = {}

        # Calculate the optimum cell size where the puzzle fills the screen.
        optimum_cell_size = utils.calc_optimum_cell_size(nrows, ncols,
            self.cell_bdr, self.outer_bdr, self.sep_bdr, top_nrows, left_ncols)

        # Clamp the minimum zoom amount.
        min_zoom_amt = Renderer.MINIMUM_CELL_SIZE - optimum_cell_size
        self.__cell_size_zoom_amt = max(min_zoom_amt, self.__cell_size_zoom_amt)
        # Then, apply the magnification (zoom in/out).
        self.cell_size = optimum_cell_size + self.__cell_size_zoom_amt

        # Ensure that cell_size is EVEN.
        self.cell_size = self.cell_size if self.cell_size % 2 == 0 else self.cell_size - 1

        cellsz = self.cell_size
        console.info(f'Reinitializing board, cell size is {cellsz}.')

        # Get the sizes and positions of the board, and the clues panels.
        board_rect, top_clues_rect, left_clues_rect, parent_rect = utils.calc_rects(
            cellsz, cellsz, cellsz, self.cell_bdr, self.outer_bdr,
            self.sep_bdr, nrows, ncols, top_nrows, left_ncols)

        # Save the calculated values to their respective properties.
        self.board_rect = board_rect
        self.top_clues_rect = top_clues_rect
        self.left_clues_rect = left_clues_rect
        self.parent_rect = parent_rect

        # Create the board surface.
        self.board_surface = pygame.Surface((board_rect.width, board_rect.height))
        self.board_surface.fill(colors.PUZZLE_BG)

        # Create the symbols surface.
        self.symbol_surface = pygame.Surface((board_rect.width, board_rect.height))
        pygame.Surface.set_colorkey(self.symbol_surface, colors.PUZZLE_BG)
        self.symbol_surface.fill(colors.PUZZLE_BG)

        # Create the top clues panel surface.
        self.top_clues_surface = pygame.Surface((top_clues_rect.width, top_clues_rect.height))
        self.top_clues_surface.fill(colors.CLUES_BG)

        # Create the left clues panel surface.
        self.left_clues_surface = pygame.Surface((left_clues_rect.width, left_clues_rect.height))
        self.left_clues_surface.fill(colors.CLUES_BG)

        # Draw the outer borders.
        self.__draw_rect_borders(self.board_surface, self.outer_bdr)
        self.__draw_rect_borders(self.top_clues_surface, self.outer_bdr)
        self.__draw_rect_borders(self.left_clues_surface, self.outer_bdr)

        # Draw the cell borders.
        self.__draw_cell_borders(self.board_surface, nrows, ncols,
            cellsz, self.cell_bdr, self.sep_bdr, True, True, None, self.outer_bdr)
        self.__draw_cell_borders(self.top_clues_surface, top_nrows, ncols,
            cellsz, self.cell_bdr, self.sep_bdr, False, True, None, self.outer_bdr)
        self.__draw_cell_borders(self.left_clues_surface, nrows, left_ncols,
            cellsz, self.cell_bdr, self.sep_bdr, True, False, None, self.outer_bdr)

        # Draw the clue numbers.
        self.update_clues()

        # Draw the symbols.
        self.update_symbols()

    ################################################################################################
    # COORDINATE & RECT GETTER METHODS
    ################################################################################################

    def get_actual_board_rect(self) -> pygame.Rect:
        """
        Get the actual board rect relative to the screen,
        after adjusting for the parent rect and the pan delta.
        
        Note that `self.board_rect` is the rect relative to `self.parent_rect`,
        so its actual position needs to be adjusted.
        """
        board_x = self.parent_rect.x + self.board_rect.x + self.__pan_delta.x
        board_y = self.parent_rect.y + self.board_rect.y + self.__pan_delta.y
        board_rect = self.board_surface.get_rect().move(board_x, board_y)
        return board_rect

    def get_board_cell_rect(self, row_idx: int, col_idx: int) -> pygame.Rect:
        """
        Get the rect surrounding the specified cell. The rect is relative to the board.
        """
        if (row_idx, col_idx) in self.__cell_rect_memo:
            return self.__cell_rect_memo[(row_idx, col_idx)]

        offset = (self.outer_bdr, self.outer_bdr, 0, 0)
        cell_rect = utils.get_cell_rect(row_idx, col_idx, self.cell_size,
            self.cell_size, self.cell_bdr, self.sep_bdr, offset)
        
        self.__cell_rect_memo[(row_idx, col_idx)] = cell_rect
        return cell_rect

    def is_coord_in_board(self, coord_x: float, coord_y: float) -> bool:
        """
        Returns true if the specified coordinate is inside the board rect.
        Returns false otherwise.
        """
        board_rect = self.get_actual_board_rect()
        board_rect.inflate_ip(self.outer_bdr * -2, self.outer_bdr * -4)
        return board_rect.collidepoint(coord_x, coord_y)

    def screen_coord_to_cell_idx(self, screen_x: float, screen_y: float) -> CellIdx:
        """
        Convert a point in the screen coordinates to its board coordinates,
        i.e. the board row index and column index.
        """
        # Get the board rect. Remove the outer borders.
        board_rect = self.get_actual_board_rect()
        board_rect.inflate_ip(self.outer_bdr * -2, self.outer_bdr * -2)
        
        return CellIdx(utils.screen_coord_to_cell_idx(screen_x, screen_y,
            board_rect, self.cell_size, self.cell_bdr, self.sep_bdr))

    def get_draft_cell_indices(self) -> list[CellIdx]:
        """
        Get the row/col indices of the draft cells.
        """
        cells: list[CellIdx] = []
        if not self.is_drafting:
            return cells
        
        if self.draft_start_cell is None or self.draft_end_cell is None:
            logger.error('Draft start/end cell is None during draft mode.')
            return cells
        
        # If the draft is vertical.
        if self.draft_start_cell.col == self.draft_end_cell.col:
            col = self.draft_start_cell.col
            min_row = min(self.draft_start_cell.row, self.draft_end_cell.row)
            max_row = max(self.draft_start_cell.row, self.draft_end_cell.row)
            for row in range(min_row, max_row + 1):
                cells.append(CellIdx(row, col))
        
        # Else if the draft is horizontal.
        elif self.draft_start_cell.row == self.draft_end_cell.row:
            row = self.draft_start_cell.row
            min_col = min(self.draft_start_cell.col, self.draft_end_cell.col)
            max_col = max(self.draft_start_cell.col, self.draft_end_cell.col)
            for col in range(min_col, max_col + 1):
                cells.append(CellIdx(row, col))

        # Else if the draft is neither vertical nor horizontal.
        else:
            logger.error(f'The draft start cell ({tuple(self.draft_start_cell)}) and '
                         f'the draft end cell ({tuple(self.draft_end_cell)}) are not aligned.')

        return cells

    def get_draft_start_ortho_cells(self) -> list[CellIdx]:
        """
        Get the row/col indices of the cells that are orthogonal to the draft start cell,
        including the draft start cell itself.
        """
        cells = []
        if not self.is_drafting:
            return cells
        
        if self.draft_start_cell is None or self.draft_end_cell is None:
            logger.error('Draft start cell is None during draft mode.')
            return cells

        for row_idx in range(self.puzzle.nrows):
            cells.append((row_idx, self.draft_start_cell.col))

        for col_idx in range(self.puzzle.ncols):
            cells.append((self.draft_start_cell.row, col_idx))

        return cells

    ################################################################################################
    # USER INTERACTION METHODS
    ################################################################################################

    def start_drag(self, curr_x: float, curr_y: float) -> None:
        """
        Start dragging.
        """
        self.__pan_orig_coord = Coord((curr_x, curr_y))
        self.__pan_orig_delta = self.pan_delta
        self.is_dragging = True

    def update_drag(self, curr_x: float, curr_y: float) -> None:
        """
        Update the pan delta.
        """
        orig_x, orig_y = self.__pan_orig_coord
        delta_x = curr_x - orig_x
        delta_y = curr_y - orig_y
        self.__pan_delta = self.__pan_orig_delta.move((delta_x, delta_y))

    def end_drag(self) -> None:
        """
        End the drag.
        """
        self.__pan_orig_coord = None
        self.__pan_orig_delta = None
        self.is_dragging = False

    def zoom(self, value: int) -> None:
        """
        Zoom in/out by the specified value.
        Positive values zoom out. Negative values zoom in.
        """
        value = value if value % 2 == 0 else value - 1
        self.__cell_size_zoom_amt += value

    def start_draft(self, row_idx: int, col_idx: int, symbol: str) -> None:
        """
        Start the draft.
        
        Drafting is editing the puzzle symbols
        but the changes have not yet been finalized.
        """
        self.draft_start_cell = CellIdx(row_idx, col_idx)
        self.draft_end_cell = CellIdx(row_idx, col_idx)
        self.draft_symbol = symbol
        self.is_drafting = True

    def update_draft(self, row_idx: int, col_idx: int) -> None:
        """
        Continue drafting, updating the current draft cells.

        Drafting is editing the puzzle symbols
        but the changes have not yet been finalized.
        """
        vertical_len = abs(self.draft_start_cell.row - row_idx)
        horizontal_len = abs(self.draft_start_cell.col - col_idx)
        if horizontal_len >= vertical_len:
            self.draft_end_cell = CellIdx(self.draft_start_cell.row, col_idx)
        else:
            self.draft_end_cell = CellIdx(row_idx, self.draft_start_cell.col)

    def end_draft(self) -> None:
        """
        Finalize the draft.
        """
        self.draft_start_pt = None
        self.draft_symbol = ' '
        self.is_drafting = False

    ################################################################################################
    # RENDER METHOD
    ################################################################################################

    def render(self) -> None:
        """
        Render the current puzzle.
        """
        render_list: list[tuple[pygame.Surface, pygame.Rect]] = []

        board_rect = self.get_actual_board_rect()
        render_list.append((self.board_surface, board_rect))
        render_list.append((self.symbol_surface, board_rect))

        top_clues_y = self.parent_rect.y + self.top_clues_rect.y + self.__pan_delta.y
        top_clues_rect = self.top_clues_surface.get_rect().move(board_rect.x, top_clues_y)
        render_list.append((self.top_clues_surface, top_clues_rect))

        left_clues_x = self.parent_rect.x + self.left_clues_rect.x + self.__pan_delta.x
        left_clues_rect = self.left_clues_surface.get_rect().move(left_clues_x, board_rect.y)
        render_list.append((self.left_clues_surface, left_clues_rect))

        self.screen.fill(colors.MAIN_BG)
        self.screen.blits(render_list)
        pygame.display.update()

    def update_symbols(self, mode: str = 'all') -> None:
        """
        Updates the symbols. Draws the symbols and the draft symbols onto the symbols surface.

        The `mode` parameter can be set to:
        - `all`: All cells will be updated.
        - `draft`: Only the draft cells will be updated.
        """
        mode = mode.lower()
        if mode not in ('all', 'draft'):
            msg = f'Update symbols mode "{mode}" is not supported. Mode will be set to "all".'
            logger.warning(msg)
            console.warning(msg)
            mode = 'all'

        # If the mode is ALL, update the current symbols of all the cells.
        if mode == 'all':
            self.symbol_surface.fill(colors.PUZZLE_BG)
            for row_idx, board_row in enumerate(self.puzzle.board):
                for col_idx, symbol in enumerate(board_row):
                    cell_rect = self.get_board_cell_rect(row_idx, col_idx)
                    self.__draw_symbol(self.symbol_surface, cell_rect, self.cell_size, symbol,
                        colors.MAIN_SYMBOL, erase_cell=False)

        # If the mode is DRAFT, redraw the current symbols of only the cells
        # that are orthogonal to the start draft cell.
        elif mode == 'draft':
            for row_idx, col_idx in self.get_draft_start_ortho_cells():
                symbol = self.puzzle.board[row_idx][col_idx]
                cell_rect = self.get_board_cell_rect(row_idx, col_idx)
                self.__draw_symbol(self.symbol_surface, cell_rect,
                    self.cell_size, symbol, colors.MAIN_SYMBOL)
        
        # Then, regardless of the mode, render the draft symbols (but only if currently drafting).
        if self.is_drafting:
            for row_idx, col_idx in self.get_draft_cell_indices():
                if self.draft_symbol == ' ':
                    new_symbol = self.puzzle.board[row_idx][col_idx]
                else:
                    new_symbol = self.draft_symbol
                
                cell_rect = self.get_board_cell_rect(row_idx, col_idx)
                self.__draw_symbol(self.symbol_surface, cell_rect, self.cell_size,
                    new_symbol, colors.DRAFT_SYMBOL)

    def update_clues(self, mode: str = 'all') -> None:
        """
        Updates the symbols. Draws the symbols and the draft symbols onto the symbols surface.

        The `mode` parameter can be set to:
        - `all`: All clue cells will be updated.
        - `top`: Only the top clues will be updated.
        - `left`: Only the left clues will be updated.
        """
        mode = mode.lower()
        if mode not in ('all', 'top', 'left'):
            msg = f'Update clues mode "{mode}" is not supported. Mode will be set to "all".'
            logger.warning(msg)
            console.warning(msg)
            mode = 'all'

        sz = self.cell_size
        top_clues_flag = mode in ('all', 'top')
        left_clues_flag = mode in ('all', 'left')

        if top_clues_flag:
            surface = self.top_clues_surface
            grid = self.puzzle.top_clues_grid
            ticks = self.puzzle.top_clues_ticks
            self.__draw_clues_numbers(surface, grid, ticks, sz, sz, 
                self.outer_bdr, self.cell_bdr, self.sep_bdr, colors.BLACK)
        
        if left_clues_flag:
            surface = self.left_clues_surface
            grid = self.puzzle.left_clues_grid
            ticks = self.puzzle.left_clues_ticks
            self.__draw_clues_numbers(surface, grid, ticks, sz, sz, 
                self.outer_bdr, self.cell_bdr, self.sep_bdr, colors.BLACK)

    ################################################################################################
    # DRAW HELPER METHODS
    ################################################################################################

    def __draw_rect_borders(self, surface: pygame.Surface, thickness: int,
        rect: Optional[pygame.Rect] = None, color: tuple = colors.BORDER) -> None:
        """
        Draw the borders with size and position of the given rect.

        Parameters:
            surface: The surface to draw on.
            thickness: The border thickness.
            rect: The rect that dictates the size and position of the border/s to draw.
                  If not specified, the border will be drawn on the outer edges
                  of the given surface.
            flags: The flag that dictates which border side/s to draw.
                   If not specified, borders on all sides will be drawn.
            color: The border color.
        """
        if rect is None:
            rect = pygame.Rect(0, 0, surface.get_width(), surface.get_height())

        for i in range(thickness):
            # Draw the TOP border.
            p1 = (0, i)
            p2 =  (rect.width - 0.5, i)
            pygame.draw.line(surface, color, p1, p2, 1)
            
            # Draw the RIGHT border.
            p1 = (rect.width - (i + 1), 0)
            p2 = (rect.width - (i + 1), rect.height - 0.5)
            pygame.draw.line(surface, color, p1, p2, 1)
                
            # Draw the BOTTOM border.
            p1 = (0, rect.height - (i + 1))
            p2 = (rect.width - 0.5, rect.height - (i + 1))
            pygame.draw.line(surface, color, p1, p2, 1)

            # Draw the LEFT border.
            p1 = (i, 0)
            p2 = (i, rect.height - 0.5)
            pygame.draw.line(surface, color, p1, p2, 1)

    def __draw_cell_borders(self,
        surface: pygame.Surface,
        nrows: int,
        ncols: int,
        cell_size: float,
        cell_bdr: int,
        sep_bdr: int,
        sep_h: bool,
        sep_v: bool,
        rect: Optional[pygame.Rect] = None,
        offset_outer_bdr: Optional[float] = 0,
        color: tuple = colors.BORDER) -> None:
        """
        Draw the cell borders.

        Parameters:
            surface: The surface to draw on.
            nrows: The number of rows.
            ncols: The number of columns.
            cell_size: The cell size.
            cell_bdr: The cell border thickness.
            rect: The rect where the cells are found, not including outer border.
                  If not specified, the whole surface will be treated as the rect.
            offset_outer_bdr: How many pixels to offset from the outer border.
            color: The line color.
        """
        if rect is None:
            rect = pygame.Rect(0, 0, surface.get_width(), surface.get_height())

        if sep_bdr < cell_bdr:
            logger.warning(f'The separator border ({sep_bdr}) is smaller '
                           f'than the cell border ({cell_bdr}).')
            sep_h, sep_v = False, False

        if offset_outer_bdr > 0:
            rect = pygame.Rect(
                rect.x + offset_outer_bdr,
                rect.y + offset_outer_bdr,
                rect.width - offset_outer_bdr * 2,
                rect.height - offset_outer_bdr * 2)

        # Draw horizontal cell borders.
        for i in range(cell_bdr):
            for row_idx in range(nrows - 1):
                y = rect.y
                y += (cell_size + cell_bdr) * row_idx   # Skip the previous rows.
                y += (row_idx // 5) * (sep_bdr - cell_bdr) # Skip previous sep borders.
                y += i                          # Skip the previously drawn borders.
                y += cell_size                  # Draw the line below the current row.
                p1 = (rect.x, y)
                p2 = (rect.x + rect.width + 0.5, y)
                pygame.draw.line(surface, color, p1, p2, 1)

                if sep_h and (row_idx != nrows - 1) and (row_idx + 1) % 5 == 0:
                    for sep_idx in range(sep_bdr - cell_bdr):
                        p1 = (rect.x, y + sep_idx + 1)
                        p2 = (rect.x + rect.width + 0.5, y + sep_idx + 1)
                        pygame.draw.line(surface, color, p1, p2, 1)

        # Draw vertical cell borders.
        for i in range(cell_bdr):
            for col_idx in range(ncols - 1):
                x = rect.x
                x += (cell_size + cell_bdr) * col_idx  # Skip the previous columns.
                x += (col_idx // 5) * (sep_bdr - cell_bdr) # Skip previous sep borders.
                x += i                          # Skip the previously drawn borders.
                x += cell_size                  # Draw the line to the right of the current column.
                p1 = (x, rect.y)
                p2 = (x, rect.y + rect.height + 0.5)
                pygame.draw.line(surface, color, p1, p2, 1)
                
                if sep_v and (col_idx != ncols - 1) and (col_idx + 1) % 5 == 0:
                    for sep_idx in range(sep_bdr - cell_bdr):
                        p1 = (x + sep_idx + 1, rect.y)
                        p2 = (x + sep_idx + 1, rect.y + rect.height + 0.5)
                        pygame.draw.line(surface, color, p1, p2, 1)

    def __draw_clues_numbers(self, surface: pygame.Surface, grid: list[list[int]],
        ticks: list[list[int]], cell_width: float, cell_height: float, outer_bdr: int,
        cell_bdr: int, sep_bdr: int, color: tuple) -> None:
        """
        Draw the clue numbers.
        """
        font_render_list: list[tuple[pygame.Surface, pygame.Rect]] = []
        tick_render_list: list[tuple[pygame.Surface, pygame.Rect]] = []
        font = self.__get_font(min(cell_width, cell_height))

        cell_rect_offset = (outer_bdr, outer_bdr, 0, 0)

        for row_idx in range(len(grid)):
            for col_idx in range(len(grid[row_idx])):
                num = grid[row_idx][col_idx]
                if num <= 0:
                    continue
                cell_rect = utils.get_cell_rect(row_idx, col_idx, cell_width, cell_height,
                    cell_bdr, sep_bdr, cell_rect_offset)
                text_surface = font.render(str(num), True, color)
                text_rect = text_surface.get_rect()
                x = cell_rect.centerx - text_rect.centerx
                y = cell_rect.centery - text_rect.centery + (text_rect.height / 12)
                draw_rect = pygame.Rect(x, y, text_rect.width, text_rect.height)
                font_render_list.append((text_surface, draw_rect))

        surface.blits(font_render_list)

    def __draw_symbol(self, surface: pygame.Surface, cell_rect: pygame.Rect,
        cell_size: int, symbol: str, color: tuple, erase_cell: bool = True) -> None:
        """
        Render a symbol on the symbols surface.
        """
        if not erase_cell and symbol == ' ':
            return

        # Calculate the padding between the symbol and the cell borders.
        if cell_size <= 6:
            padding = 0
        elif cell_size < 18:
            padding = 1
        elif cell_size < 28:
            padding = 2
        elif cell_size < 50:
            padding = 3
        else:
            padding = int(cell_size * 0.06)

        # Get the rect that encloses the cell and the rect that encloses the symbol.
        symbol_rect = pygame.Rect(cell_rect.x + padding,
                                  cell_rect.y + padding,
                                  cell_rect.width + padding * -2,
                                  cell_rect.height + padding * -2)

        # Erase the current symbol if the flag is set.
        if erase_cell:
            pygame.draw.rect(surface, colors.PUZZLE_BG, cell_rect)

        if symbol == ' ':
            # Do nothing for BLANK cells.
            pass

        elif symbol == '.':
            pygame.draw.rect(surface, color, symbol_rect)

        elif symbol == 'x':
            blend = 1 if color == colors.DRAFT_SYMBOL else 0
            
            tl = cell_rect.topleft
            tr = (tl[0] + cell_size, tl[1] - 1)
            bl = (tl[0] - 1, tl[1] + cell_size)
            br = (tr[0], bl[1])

            p1, p2 = tl, br
            p1b = p1[0] + 1,    p1[1]
            p1c = p1[0],        p1[1] + 1
            p2b = p2[0],        p2[1] - 1
            p2c = p2[0] - 1,    p2[1]

            pygame.draw.aaline(surface, color, p1, p2, blend)
            if cell_size > 20:
                pygame.draw.aaline(surface, color, p1b, p2b, 1)
                pygame.draw.aaline(surface, color, p1c, p2c, 1)

            p1, p2 = bl, tr
            p1b = p1[0] + 1,    p1[1]
            p1c = p1[0],        p1[1] - 1
            p2b = p2[0],        p2[1] + 1
            p2c = p2[0] - 1,    p2[1]

            pygame.draw.aaline(surface, color, p1, p2, blend)
            if cell_size > 20:
                pygame.draw.aaline(surface, color, p1b, p2b, 1)
                pygame.draw.aaline(surface, color, p1c, p2c, 1)

        else:
            logger.error(f'Cannot render unknown symbol: {symbol}')

    @lru_cache
    def __get_font(self, cell_size: int) -> pygame.font.Font:
        """
        Get the optimal font for the cell with the given size.
        """
        padding = 2
        for font in self.__fonts:
            w, h = font.size('99')
            if w + padding < cell_size and h + padding < cell_size:
                return font
        return self.__fonts[-1]
