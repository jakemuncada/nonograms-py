"""
Module for rendering the game to the screen.
"""

import pygame
import logging

from src.coord import Coord
from src.puzzle import Puzzle
import src.constants as constants
import src.utils.render_utils as utils


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (138, 94, 56)

logger = logging.getLogger(__name__)
console = logging.getLogger('console')


class Renderer:
    """
    Renders the game to the screen.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self.__screen = screen
        self.__screen.fill(BROWN)

        self.puzzle: Puzzle = None
        self.total_rows: int = 0
        self.total_cols: int = 0

        self.cell_width: float = 0.0
        self.cell_height: float = 0.0

        self.__scale_factor: float = 1.0
        self.__pan_delta: Coord = Coord((0, 0))

        self.board_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.top_clues_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.left_clues_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

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
        self.__initialize_board_surface()

    def __initialize_board_surface(self) -> None:
        """
        Initialize the board surface.
        """
        nrows = self.puzzle.nrows
        ncols = self.puzzle.ncols
        top_clues_nrows = self.puzzle.max_col_clues
        left_clues_ncols = self.puzzle.max_row_clues

        # Calculate the optimum cell size where the puzzle fills the screen.
        optimum_cell_size = utils.calc_optimum_cell_size(nrows, ncols, top_clues_nrows, left_clues_ncols)
        # Then, apply the scaling factor, i.e. magnification.
        self.cell_size = optimum_cell_size * self.__scale_factor

        board_rect, top_clues_rect, left_clues_rect, parent_rect = utils.calc_rects(
            self.cell_size, self.cell_size, self.cell_size,
            nrows, ncols, top_clues_nrows, left_clues_ncols)

        self.board_rect = board_rect
        self.top_clues_rect = top_clues_rect
        self.left_clues_rect = left_clues_rect
        self.parent_rect = parent_rect

        self.board_surface = pygame.Surface((board_rect.width, board_rect.height))
        self.board_surface.fill(WHITE)

        self.top_clues_surface = pygame.Surface((top_clues_rect.width, top_clues_rect.height))
        self.top_clues_surface.fill(WHITE)

        self.left_clues_surface = pygame.Surface((left_clues_rect.width, left_clues_rect.height))
        self.left_clues_surface.fill(WHITE)


        _, _, width, height = self.board_rect
        bdr = constants.BORDER_THICKNESS

        # Draw board outer borders.
        for i in range(constants.BORDER_THICKNESS * 2):
            top_1 = (0, i)
            top_2 = (width + bdr, i)
            right_1 = (width - (i + 1), 0)
            right_2 = (width - (i + 1), height + bdr)
            bot_1 = (0, height - (i + 1))
            bot_2 = (width + bdr, height - (i + 1))
            left_1 = (i, 0)
            left_2 = (i, height + bdr)
            pygame.draw.line(self.board_surface, BLACK, top_1, top_2, 1)
            pygame.draw.line(self.board_surface, BLACK, right_1, right_2, 1)
            pygame.draw.line(self.board_surface, BLACK, bot_1, bot_2, 1)
            pygame.draw.line(self.board_surface, BLACK, left_1, left_2, 1)

        # Draw horizontal cell borders.
        for i in range(constants.BORDER_THICKNESS):
            for row_idx in range(self.puzzle.nrows - 1):
                y = bdr * 2                             # Skip the top border.
                y += (self.cell_size + bdr) * row_idx   # Skip the previous rows.
                y += i                                  # Skip the previously drawn borders.
                y += self.cell_size                     # Draw the line below the current row.
                p1 = (0, y)
                p2 = (width + bdr, y)
                pygame.draw.line(self.board_surface, BLACK, p1, p2, 1)

        # Draw vertical cell borders.
        for i in range(constants.BORDER_THICKNESS):
            for col_idx in range(self.puzzle.ncols - 1):
                x = bdr * 2                             # Skip the left border.
                x += (self.cell_size + bdr) * col_idx   # Skip the previous columns.
                x += i                                  # Skip the previously drawn borders.
                x += self.cell_size                     # Draw the line to the right of the current column.
                p1 = (x, 0)
                p2 = (x, height + bdr)
                pygame.draw.line(self.board_surface, BLACK, p1, p2, 1)

    def __initialize_top_clues_surface(self) -> None:
        """
        Initialize the top clues panel surface.

        Note that the board surface must already be initialized.
        """
        width = self.board_rect.width
        height = utils.calc_clues_panel_dimension(self.cell_size, self.puzzle.max_col_clues)
        left = self.board_rect.left
        top = self.board_rect.top - height

        self.top_clues_rect = pygame.Rect(left, top, width, height)

        self.top_clues_surface = pygame.Surface((width, height))
        self.top_clues_surface.fill(WHITE)

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

    def render(self) -> None:
        """
        Render the current puzzle.
        """
        board_x = self.board_rect.x + self.__pan_delta.x
        board_y = self.board_rect.y + self.__pan_delta.y
        self.screen.blit(self.board_surface, (board_x, board_y))

        top_clues_y = self.top_clues_rect.y + self.__pan_delta.y
        self.screen.blit(self.top_clues_surface, (board_x, top_clues_y))

        pygame.display.update()
