"""
Some useful utility functions for the renderer.
"""

import pygame
import src.constants as constants


def calc_borders_thickness(nrows: int, ncols: int) -> tuple[float, float]:
    """
    Calculate the total border thickness for both horizontal and vertical borders.

    Parameters:
        nrows: The number of rows in the puzzle.
        ncols: The number of columns in the puzzle.

    Returns:
        A tuple containing the horizontal borders thickness
        and the vertical borders thickness respectively.
    """
    hborders_count = (ncols - 1) + 4
    vborders_count = (nrows - 1) + 4
    hborders_thickness = hborders_count * constants.BORDER_THICKNESS
    vborders_thickness = vborders_count * constants.BORDER_THICKNESS
    return hborders_thickness, vborders_thickness

def calc_optimum_cell_size(nrows: int, ncols: int) -> float:
    """
    Calculate the cell size such that the puzzle fills the screen optimally.

    Parameters:
        nrows: The number of rows in the puzzle.
        ncols: The number of columns in the puzzle.

    Returns:
        The optimum cell size.
    """
    hborders_thickness, vborders_thickness = calc_borders_thickness(nrows, ncols)

    h_margins = constants.SCREEN_LEFT_MARGIN + constants.SCREEN_RIGHT_MARGIN
    v_margins = constants.SCREEN_TOP_MARGIN + constants.SCREEN_BOTTOM_MARGIN
    usable_width = constants.SCREEN_WIDTH - h_margins
    usable_height = constants.SCREEN_HEIGHT - v_margins

    cell_width = (usable_width - hborders_thickness) / ncols
    cell_height = (usable_height - vborders_thickness) / nrows

    return min(cell_width, cell_height)

def calc_board_rect(cell_size: float, nrows: int, ncols: int) -> pygame.Rect:
    """
    Calculate the board rect.

    Parameters:
        cell_size: The size in pixels of the cells.
        nrows: The number of rows in the puzzle.
        ncols: The number of columns in the puzzle.

    Returns:
        The board rect, which specifies the position and size of the board.
    """
    hborders_thickness, vborders_thickness = calc_borders_thickness(nrows, ncols)
    board_width = (cell_size * ncols) + hborders_thickness
    board_height = (cell_size * nrows) + vborders_thickness
    board_x = constants.SCREEN_HALF_WIDTH - (board_width / 2)
    board_y = constants.SCREEN_HALF_HEIGHT - (board_width / 2)
    return pygame.Rect(board_x, board_y, board_width, board_height)

