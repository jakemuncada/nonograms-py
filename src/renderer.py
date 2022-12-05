"""
Module for rendering the game to the screen.
"""

import pygame
import logging
import pygame.gfxdraw
from typing import Optional

from src.coord import Coord
from src.puzzle import Puzzle
import src.colors as colors
import src.constants as constants
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
        """The list of fonts."""
        self.__fonts.append(pygame.font.SysFont('consolas', 6))
        self.__fonts.append(pygame.font.SysFont('consolas', 10))
        self.__fonts.append(pygame.font.SysFont('consolas', 13))
        self.__fonts.append(pygame.font.SysFont('consolas', 16))
        self.__fonts.append(pygame.font.SysFont('consolas', 20))
        self.__fonts.append(pygame.font.SysFont('consolas', 24))
        self.__fonts.append(pygame.font.SysFont('consolas', 28))
        self.__fonts.append(pygame.font.SysFont('consolas', 32))
        self.__fonts.append(pygame.font.SysFont('consolas', 36))

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
        self.__pan_orig_xy: Coord = None
        self.__pan_orig_delta: Coord = None
        self.is_dragging = False

        self.draft_start_cell: Coord = None
        self.draft_end_cell: Coord = None
        self.draft_symbol = '.'
        self.is_drafting = False

        self.cell_bdr = 1
        """The cell border thickness."""
        self.outer_bdr = self.cell_bdr * 2
        """The outer border thickness."""

        self.board_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.top_clues_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.left_clues_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.parent_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

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
        top_clues_nrows = self.puzzle.max_col_clues
        left_clues_ncols = self.puzzle.max_row_clues

        # Calculate the optimum cell size where the puzzle fills the screen.
        optimum_cell_size = utils.calc_optimum_cell_size(nrows, ncols,
            self.cell_bdr, self.outer_bdr, top_clues_nrows, left_clues_ncols)

        # Clamp the minimum zoom amount.
        min_zoom_amt = Renderer.MINIMUM_CELL_SIZE - optimum_cell_size
        self.__cell_size_zoom_amt = max(min_zoom_amt, self.__cell_size_zoom_amt)
        # Then, apply the magnification (zoom in/out).
        self.cell_size = optimum_cell_size + self.__cell_size_zoom_amt

        # Ensure that cell_size is EVEN.
        self.cell_size = self.cell_size if self.cell_size % 2 == 0 else self.cell_size - 1

        console.info(f'Reinitializing board, cell size is {self.cell_size}.')

        # Get the sizes and positions of the board, and the clues panels.
        board_rect, top_clues_rect, left_clues_rect, parent_rect = utils.calc_rects(
            self.cell_size, self.cell_size, self.cell_size, self.cell_bdr, self.outer_bdr,
            nrows, ncols, top_clues_nrows, left_clues_ncols)

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
            self.cell_size, self.cell_bdr, None, self.outer_bdr)
        self.__draw_cell_borders(self.top_clues_surface, top_clues_nrows, ncols,
            self.cell_size, self.cell_bdr, None, self.outer_bdr)
        self.__draw_cell_borders(self.left_clues_surface, nrows, left_clues_ncols,
            self.cell_size, self.cell_bdr, None, self.outer_bdr)

        # Draw the clue numbers.
        self.__draw_top_clues_numbers()
        self.__draw_left_clues_numbers()

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

    def is_coord_in_board(self, coord_x: float, coord_y: float) -> bool:
        """
        Returns true if the specified coordinate is inside the board rect.
        Returns false otherwise.
        """
        board_rect = self.get_actual_board_rect()
        board_rect.inflate_ip(self.outer_bdr * -2, self.outer_bdr * -4)
        return board_rect.collidepoint(coord_x, coord_y)

    def screen_to_board_coords(self, screen_x: float, screen_y: float) -> tuple[int, int]:
        """
        Convert a point in the screen coordinates to its board coordinates,
        i.e. the board row index and column index.
        """
        board_rect = self.get_actual_board_rect()
        board_rect.inflate_ip(self.outer_bdr * -2, self.outer_bdr * -2)

        row_idx = (screen_y - board_rect.y) // (self.cell_size + self.cell_bdr)
        col_idx = (screen_x - board_rect.x) // (self.cell_size + self.cell_bdr)
        return int(row_idx), int(col_idx)

    def get_draft_cell_coords(self) -> list[tuple[int, int]]:
        """
        Get the row/col indices of the draft cells.
        """
        cells = []
        if not self.is_drafting:
            return cells
        
        if self.draft_start_cell is None or self.draft_end_cell is None:
            logger.error('Draft start/end cell is None during draft mode.')
            return cells
        
        # If the draft is vertical.
        if self.draft_start_cell.x == self.draft_end_cell.x:
            x = self.draft_start_cell.x
            min_y = min(self.draft_start_cell.y, self.draft_end_cell.y)
            max_y = max(self.draft_start_cell.y, self.draft_end_cell.y)
            for y in range(min_y, max_y + 1):
                cells.append((x, y))
        
        # Else if the draft is horizontal.
        elif self.draft_start_cell.y == self.draft_end_cell.y:
            y = self.draft_start_cell.y
            min_x = min(self.draft_start_cell.x, self.draft_end_cell.x)
            max_x = max(self.draft_start_cell.x, self.draft_end_cell.x)
            for x in range(min_x, max_x + 1):
                cells.append((x, y))

        # Else if the draft is neither vertical nor horizontal.
        else:
            logger.error(f'The draft start cell ({tuple(self.draft_start_cell)}) and '
                         f'the draft end cell ({tuple(self.draft_end_cell)}) are not aligned.')

        return cells     

    ################################################################################################
    # USER INTERACTION METHODS
    ################################################################################################

    def start_drag(self, curr_x: float, curr_y: float) -> None:
        """
        Start dragging.
        """
        self.__pan_orig_xy = Coord((curr_x, curr_y))
        self.__pan_orig_delta = self.pan_delta
        self.is_dragging = True

    def update_drag(self, curr_x: float, curr_y: float) -> None:
        """
        Update the pan delta.
        """
        orig_x, orig_y = self.__pan_orig_xy
        delta_x = curr_x - orig_x
        delta_y = curr_y - orig_y
        self.__pan_delta = self.__pan_orig_delta.move((delta_x, delta_y))

    def end_drag(self) -> None:
        """
        End the drag.
        """
        self.__pan_orig_xy = None
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
        self.draft_start_cell = Coord((row_idx, col_idx))
        self.draft_end_cell = Coord((row_idx, col_idx))
        self.draft_symbol = symbol
        self.is_drafting = True

    def update_draft(self, row_idx: int, col_idx: int) -> None:
        """
        Continue drafting, updating the current draft cells.

        Drafting is editing the puzzle symbols
        but the changes have not yet been finalized.
        """
        vertical_len = abs(self.draft_start_cell.x - row_idx)
        horizontal_len = abs(self.draft_start_cell.y - col_idx)
        if horizontal_len >= vertical_len:
            self.draft_end_cell = Coord((self.draft_start_cell.x, col_idx))
        else:
            self.draft_end_cell = Coord((row_idx, self.draft_start_cell.y))

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
        self.symbol_surface.fill(colors.PUZZLE_BG)
        self.__render_symbols()
        self.__render_draft()

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

    def __render_symbols(self) -> None:
        """
        Render the symbols onto the symbols surface.
        """
        for row_idx, board_row in enumerate(self.puzzle.board):
            for col_idx, symbol in enumerate(board_row):
                self.__render_symbol(row_idx, col_idx, symbol, colors.MAIN_SYMBOL)

    def __render_draft(self) -> None:
        """
        Render the draft symbols onto the symbols surface.
        Only renders the draft if `is_drafting` is true.
        """
        for row_idx, col_idx in self.get_draft_cell_coords():
            if self.draft_symbol == ' ':
                new_symbol = self.puzzle.board[row_idx][col_idx]
            else:
                new_symbol = self.draft_symbol
            self.__render_symbol(row_idx, col_idx, new_symbol, colors.DRAFT_SYMBOL)

    def __render_symbol(self, row_idx: int, col_idx: int,
        symbol: str, color: tuple = colors.MAIN_SYMBOL) -> Optional[pygame.Rect]:
        """
        Render a symbol on the symbols surface.
        """
        if symbol == ' ':
            return None

        if self.cell_size <= 6:
            offset_amount = 0
        elif self.cell_size < 18:
            offset_amount = 1
        elif self.cell_size < 28:
            offset_amount = 2
        elif self.cell_size < 50:
            offset_amount = 3
        else:
            offset_amount = int(self.cell_size * 0.06)

        offset_x = offset_amount + self.outer_bdr
        offset_y = offset_amount + self.outer_bdr
        offset_w = offset_amount * -2
        offset_h = offset_amount * -2

        cell_rect_offset = (offset_x, offset_y, offset_w, offset_h)
        symbol_rect = utils.get_cell_rect(row_idx, col_idx,
            self.cell_size, self.cell_size, self.cell_bdr, cell_rect_offset)

        if symbol == ' ':
            return pygame.draw.rect(self.symbol_surface, colors.PUZZLE_BG, symbol_rect)

        if symbol == '.':
            return pygame.draw.rect(self.symbol_surface, color, symbol_rect)

        if symbol == 'x':
            pygame.draw.rect(self.symbol_surface, colors.PUZZLE_BG, symbol_rect)
            line_w = 2

            p1, p2 = symbol_rect.topleft, symbol_rect.bottomright
            p2 = p2[0] - line_w / 2, p2[1]

            p1b = p1[0] + 1,    p1[1]
            p1c = p1[0],        p1[1] + 1
            p2b = p2[0],        p2[1] - 1
            p2c = p2[0] - 1,    p2[1]

            pygame.draw.aaline(self.symbol_surface, color, p1, p2, 0)
            pygame.draw.aaline(self.symbol_surface, color, p1b, p2b, 0)
            pygame.draw.aaline(self.symbol_surface, color, p1c, p2c, 0)

            p1, p2 = symbol_rect.bottomleft, symbol_rect.topright
            p2 = p2[0] - line_w / 2, p2[1]

            p1b = p1[0] + 1,    p1[1]
            p1c = p1[0],        p1[1] - 1
            p2b = p2[0],        p2[1] + 1
            p2c = p2[0] - 1,    p2[1]

            pygame.draw.aaline(self.symbol_surface, color, p1, p2, 0)
            pygame.draw.aaline(self.symbol_surface, color, p1b, p2b, 0)
            pygame.draw.aaline(self.symbol_surface, color, p1c, p2c, 0)
            
            return symbol_rect
        
        logger.error(f'Cannot render unknown symbol: {symbol}')
        return None

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
                  If not specified, the border will be drawn on the outer edges of the given surface.
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
        thickness: int,
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
            thickness: The border thickness.
            rect: The rect where the cells are found, not including outer border.
                  If not specified, the whole surface will be treated as the rect.
            offset_outer_bdr: How many pixels to offset from the outer border.
            color: The line color.
        """
        if rect is None:
            rect = pygame.Rect(0, 0, surface.get_width(), surface.get_height())

        if offset_outer_bdr > 0:
            rect = pygame.Rect(
                rect.x + offset_outer_bdr,
                rect.y + offset_outer_bdr,
                rect.width - offset_outer_bdr * 2,
                rect.height - offset_outer_bdr * 2)

        # Draw horizontal cell borders.
        for i in range(thickness):
            for row_idx in range(nrows - 1):
                y = rect.y
                y += (cell_size + thickness) * row_idx   # Skip the previous rows.
                y += i                             # Skip the previously drawn borders.
                y += cell_size                     # Draw the line below the current row.
                p1 = (rect.x, y)
                p2 = (rect.x + rect.width + 0.5, y)
                pygame.draw.line(surface, color, p1, p2, 1)

        # Draw vertical cell borders.
        for i in range(thickness):
            for col_idx in range(ncols - 1):
                x = rect.x
                x += (cell_size + thickness) * col_idx  # Skip the previous columns.
                x += i                                  # Skip the previously drawn borders.
                x += cell_size                     # Draw the line to the right of the current column.
                p1 = (x, rect.y)
                p2 = (x, rect.y + rect.height + 0.5)
                pygame.draw.line(surface, color, p1, p2, 1)

    def __draw_top_clues_numbers(self) -> None:
        """
        Draw the top clues cell numbers.
        """
        render_list: list[tuple[pygame.Surface, pygame.Rect]] = []
        font = self.__get_font(self.cell_size, self.cell_size)

        cell_rect_offset = (self.outer_bdr, self.outer_bdr, 0, 0)

        for col_idx in range(len(self.puzzle.col_clues)):
            clues = self.puzzle.col_clues[col_idx]
            for row_idx in range(len(clues)):
                r_idx = self.puzzle.max_col_clues - row_idx - 1
                num = clues[row_idx]
                cell_rect = utils.get_cell_rect(r_idx, col_idx, self.cell_size, self.cell_size, 
                    self.cell_bdr, cell_rect_offset)
                text_surface = font.render(str(num), True, colors.CLUES_TEXT)
                text_rect = text_surface.get_rect()
                x = cell_rect.centerx - text_rect.centerx
                y = cell_rect.centery - text_rect.centery + (text_rect.height / 12)
                draw_rect = pygame.Rect(x, y, text_rect.width, text_rect.height)
                render_list.append((text_surface, draw_rect))

        self.top_clues_surface.blits(render_list)

    def __draw_left_clues_numbers(self) -> None:
        """
        Draw the left clues cell numbers.
        """
        render_list: list[tuple[pygame.Surface, pygame.Rect]] = []
        font = self.__get_font(self.cell_size, self.cell_size)

        cell_rect_offset = (self.outer_bdr, self.outer_bdr, 0, 0)

        for row_idx in range(len(self.puzzle.row_clues)):
            clues = self.puzzle.row_clues[row_idx]
            for col_idx in range(len(clues)):
                c_idx = self.puzzle.max_row_clues - col_idx - 1
                num = clues[col_idx]
                cell_rect = utils.get_cell_rect(row_idx, c_idx, self.cell_size,
                    self.cell_size, self.cell_bdr, cell_rect_offset)
                text_surface = font.render(str(num), True, colors.CLUES_TEXT)
                text_rect = text_surface.get_rect()
                x = cell_rect.centerx - text_rect.centerx
                y = cell_rect.centery - text_rect.centery + (text_rect.height / 12)
                draw_rect = pygame.Rect(x, y, text_rect.width, text_rect.height)
                render_list.append((text_surface, draw_rect))

        self.left_clues_surface.blits(render_list)

    def __get_font(self, cell_width: float, cell_height: float) -> pygame.font.Font:
        """
        Get the optimal font for the cell with the given size.
        """
        mini = min(cell_width, cell_height)
        if mini >= 45:
            return self.__fonts[-1]
        if mini >= 42:
            return self.__fonts[-2]
        if mini >= 38:
            return self.__fonts[-3]
        if mini >= 34:
            return self.__fonts[-4]
        if mini >= 30:
            return self.__fonts[-5]
        if mini >= 27:
            return self.__fonts[-6]
        if mini >= 22:
            return self.__fonts[-7]
        if mini >= 12:
            return self.__fonts[-8]
        return self.__fonts[-9]
