"""
Module for rendering the game to the screen.
"""

import pygame
import logging
from typing import Optional

from src.coord import Coord
from src.puzzle import Puzzle
import src.constants as constants
import src.utils.render_utils as utils


BLACK = (0, 0, 0)
GRAY = (144, 144, 144)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BROWN = (138, 94, 56)
LIGHT_BROWN = (217, 183, 165)

logger = logging.getLogger(__name__)
console = logging.getLogger('console')


class Renderer:
    """
    Renders the game to the screen.
    """

    FLAG_BORDER_NONE = 0
    FLAG_BORDER_TOP = 1 << 0
    FLAG_BORDER_RIGHT = 1 << 1
    FLAG_BORDER_BOT = 1 << 2
    FLAG_BORDER_LEFT = 1 << 3
    FLAG_BORDER_ALL = FLAG_BORDER_TOP | FLAG_BORDER_LEFT | FLAG_BORDER_RIGHT | FLAG_BORDER_BOT

    def __init__(self, screen: pygame.Surface) -> None:
        self.__screen = screen
        self.__screen.fill(BROWN)

        self.__fonts: list[pygame.font.Font] = []
        self.__fonts.append(pygame.font.SysFont('consolas', 10))
        self.__fonts.append(pygame.font.SysFont('consolas', 13))
        self.__fonts.append(pygame.font.SysFont('consolas', 16))
        self.__fonts.append(pygame.font.SysFont('consolas', 20))
        self.__fonts.append(pygame.font.SysFont('consolas', 24))
        self.__fonts.append(pygame.font.SysFont('consolas', 28))
        self.__fonts.append(pygame.font.SysFont('consolas', 32))
        self.__fonts.append(pygame.font.SysFont('consolas', 36))

        self.puzzle: Puzzle = None
        self.total_rows: int = 0
        self.total_cols: int = 0

        self.cell_size: float = 0.0

        self.__scale_factor: float = 1.0
        self.__pan_delta: Coord = Coord((0, 0))

        self.bdr_thick = constants.BORDER_THICKNESS

        self.board_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.top_clues_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.left_clues_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.parent_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        self.board_surface: pygame.Surface = None
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
        
    @property
    def scale_factor(self) -> Coord:
        """The pan delta."""
        return self.__scale_factor

    ################################################################################################
    # INITIALIZATION METHODS
    ################################################################################################

    def initialize_puzzle(self, puzzle: Puzzle) -> None:
        """
        Initialize the puzzle to be displayed.
        """
        logger.info(f'Initializing {puzzle.nrows}x{puzzle.ncols} puzzle...')
        self.puzzle = puzzle
        self.total_rows = puzzle.nrows + puzzle.max_row_clues
        self.total_cols = puzzle.ncols + puzzle.max_col_clues
        self.__initialize_puzzle_surfaces()

    def __initialize_puzzle_surfaces(self) -> None:
        """
        Initialize all the puzzle surfaces.
        """
        self.__initialize_surfaces()

    def __initialize_surfaces(self) -> None:
        """
        Initialize the board surface.
        """
        nrows = self.puzzle.nrows
        ncols = self.puzzle.ncols
        top_clues_nrows = self.puzzle.max_col_clues
        left_clues_ncols = self.puzzle.max_row_clues
        bdr_thick = constants.BORDER_THICKNESS
        bdr_thick2 = bdr_thick * 2

        # Calculate the optimum cell size where the puzzle fills the screen.
        optimum_cell_size = utils.calc_optimum_cell_size(nrows, ncols, top_clues_nrows, left_clues_ncols)
        # Then, apply the scaling factor, i.e. magnification.
        self.cell_size = optimum_cell_size * self.__scale_factor

        # Get the sizes and positions of the board, and the clues panels.
        board_rect, top_clues_rect, left_clues_rect, parent_rect = utils.calc_rects(
            self.cell_size, self.cell_size, self.cell_size,
            nrows, ncols, top_clues_nrows, left_clues_ncols)

        # Save the calculated values to their respective properties.
        self.board_rect = board_rect
        self.top_clues_rect = top_clues_rect
        self.left_clues_rect = left_clues_rect
        self.parent_rect = parent_rect

        # Create the board surface.
        self.board_surface = pygame.Surface((board_rect.width, board_rect.height))
        self.board_surface.fill(WHITE)

        # Create the top clues panel surface.
        self.top_clues_surface = pygame.Surface((top_clues_rect.width, top_clues_rect.height))
        self.top_clues_surface.fill(LIGHT_BROWN)

        # Create the left clues panel surface.
        self.left_clues_surface = pygame.Surface((left_clues_rect.width, left_clues_rect.height))
        self.left_clues_surface.fill(LIGHT_BROWN)

        # Draw the outer borders.
        self.__draw_rect_borders(self.board_surface, bdr_thick * 2)
        self.__draw_rect_borders(self.top_clues_surface, bdr_thick * 2)
        self.__draw_rect_borders(self.left_clues_surface, bdr_thick * 2)

        # Draw the cell borders.
        self.__draw_cell_borders(self.board_surface, nrows, ncols, self.cell_size, bdr_thick, None, bdr_thick2)
        self.__draw_cell_borders(self.top_clues_surface, top_clues_nrows, ncols, self.cell_size, bdr_thick, None, bdr_thick2)
        self.__draw_cell_borders(self.left_clues_surface, nrows, left_clues_ncols, self.cell_size, bdr_thick, None, bdr_thick2)

        # Draw the clue numbers.
        self.__draw_top_clues_numbers()
        self.__draw_left_clues_numbers()

    ################################################################################################
    # USER INTERACTION METHODS
    ################################################################################################

    def set_pan(self, new_pan_x: float, new_pan_y: float) -> None:
        """
        Set the new pan delta. Rerenders the whole screen.
        """
        self.__pan_delta = Coord((new_pan_x, new_pan_y))
        self.__screen.fill(BROWN)
        self.render()

    def set_scaling_factor(self, new_scale: float) -> None:
        """
        Set the new scaling factor. Rerenders the whole screen.
        """
        new_scale = max(new_scale, 0.5)
        new_scale = min(new_scale, 3.0)
        self.__scale_factor = new_scale

        self.__screen.fill(BROWN)
        self.__initialize_puzzle_surfaces()
        self.render()

    def inc_scaling_factor(self, value: float) -> None:
        """
        Decrement the current scaling factor by the specified value.
        Negative values will decrement it.
        """
        self.set_scaling_factor(self.scale_factor + value)

    ################################################################################################
    # RENDER METHOD
    ################################################################################################

    def render(self) -> None:
        """
        Render the current puzzle.
        """
        render_list: list[tuple[pygame.Surface, pygame.Rect]] = []

        board_x = self.parent_rect.x + self.board_rect.x + self.__pan_delta.x
        board_y = self.parent_rect.y + self.board_rect.y + self.__pan_delta.y
        board_rect = self.board_surface.get_rect().move(board_x, board_y)
        render_list.append((self.board_surface, board_rect))

        top_clues_y = self.parent_rect.y + self.top_clues_rect.y + self.__pan_delta.y
        top_clues_rect = self.top_clues_surface.get_rect().move(board_x, top_clues_y)
        render_list.append((self.top_clues_surface, top_clues_rect))

        left_clues_x = self.parent_rect.x + self.left_clues_rect.x + self.__pan_delta.x
        left_clues_rect = self.left_clues_surface.get_rect().move(left_clues_x, board_y)
        render_list.append((self.left_clues_surface, left_clues_rect))

        self.screen.blits(render_list)
        pygame.display.update()

    ################################################################################################
    # DRAW HELPER METHODS
    ################################################################################################

    def __draw_rect_borders(self, surface: pygame.Surface, thickness: int,
        rect: Optional[pygame.Rect] = None, flags: int = FLAG_BORDER_ALL, color: tuple = BLACK) -> None:
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
            if flags & Renderer.FLAG_BORDER_TOP:
                p1 = (0, i)
                p2 =  (rect.width - 0.5, i)
                pygame.draw.line(surface, color, p1, p2, 1)
            
            if flags & Renderer.FLAG_BORDER_RIGHT:
                p1 = (rect.width - (i + 1), 0)
                p2 = (rect.width - (i + 1), rect.height - 0.5)
                pygame.draw.line(surface, color, p1, p2, 1)
                
            if flags & Renderer.FLAG_BORDER_BOT:
                p1 = (0, rect.height - (i + 1))
                p2 = (rect.width - 0.5, rect.height - (i + 1))
                pygame.draw.line(surface, color, p1, p2, 1)

            if flags & Renderer.FLAG_BORDER_LEFT:
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
        color: tuple = BLACK) -> None:
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

        for col_idx in range(len(self.puzzle.col_clues)):
            clues = self.puzzle.col_clues[col_idx]
            for row_idx in range(len(clues)):
                r_idx = self.puzzle.max_col_clues - row_idx - 1
                num = clues[row_idx]
                cell_rect = utils.get_cell_rect(r_idx, col_idx, self.cell_size, self.cell_size, self.bdr_thick)
                cell_rect = cell_rect.move(self.bdr_thick * 2, self.bdr_thick * 2)
                # pygame.draw.rect(self.top_clues_surface, RED, cell_rect, 1)
                text_surface = font.render(str(num), True, BLACK)
                text_rect = text_surface.get_rect()
                x = cell_rect.centerx - text_rect.centerx
                y = cell_rect.centery - text_rect.centery + (text_rect.height / 12)
                draw_rect = pygame.Rect(x, y, text_rect.width, text_rect.height)
                # pygame.draw.rect(self.top_clues_surface, GRAY, draw_rect)
                render_list.append((text_surface, draw_rect))

        self.top_clues_surface.blits(render_list)

    def __draw_left_clues_numbers(self) -> None:
        """
        Draw the left clues cell numbers.
        """
        render_list: list[tuple[pygame.Surface, pygame.Rect]] = []
        font = self.__get_font(self.cell_size, self.cell_size)

        for row_idx in range(len(self.puzzle.row_clues)):
            clues = self.puzzle.row_clues[row_idx]
            for col_idx in range(len(clues)):
                c_idx = self.puzzle.max_row_clues - col_idx - 1
                num = clues[col_idx]
                cell_rect = utils.get_cell_rect(row_idx, c_idx, self.cell_size, self.cell_size, self.bdr_thick)
                cell_rect = cell_rect.move(self.bdr_thick * 2, self.bdr_thick * 2)
                # pygame.draw.rect(self.top_clues_surface, RED, cell_rect, 1)
                text_surface = font.render(str(num), True, BLACK)
                text_rect = text_surface.get_rect()
                x = cell_rect.centerx - text_rect.centerx
                y = cell_rect.centery - text_rect.centery + (text_rect.height / 12)
                draw_rect = pygame.Rect(x, y, text_rect.width, text_rect.height)
                # pygame.draw.rect(self.top_clues_surface, GRAY, draw_rect)
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
        return self.__fonts[-8]
