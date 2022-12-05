"""
Some useful utility functions for the renderer.
"""

import pygame
from typing import Optional, Union
import src.constants as constants

def calc_rects(
    board_cell_size: float,
    top_clues_cell_height: float,
    left_clues_cell_width: float,
    cell_bdr: int,
    outer_bdr: int,
    board_nrows: int,
    board_ncols: int, 
    top_clues_nrows: int,
    left_clues_ncols: int) -> \
    tuple[pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect]:
    """
    Calculate the sizes and positions of the board, the top and left clues panels,
    and the parent rect that contains the above rects.

    The positions of the board and clues panels are relative to their parent rect.

    Parameters:
        board_cell_size: The size of the cells of the board.
        top_clues_cell_height: The height of the cells of the top clues panel.
        left_clues_cell_width: The width of the cells of the left clues panel.
        cell_bdr: The thickness of the border between the cells.
        outer_bdr: The thickness of the border surrounding the board.
        board_nrows: The number of rows of the board.
        board_ncols: The number of columns of the board.
        top_clues_nrows: The number of rows of the top clues panel.
        left_clues_ncols: The number of columns of the left clues panel.

    Returns:
        The sizes and positions of the following as a tuple:
        - The size and position of the board.
        - The size and position of the top clues panel.
        - The size and position of the left clues panel.
        - The size and position of the parent rect that contains the above.
    """
    board_border_thick_h = ((board_ncols - 1) * cell_bdr) + (outer_bdr * 2)
    board_border_thick_v = ((board_nrows - 1) * cell_bdr) + (outer_bdr * 2)
    top_clues_border_thick_v = ((top_clues_nrows - 1) * cell_bdr) + (outer_bdr * 2)
    left_clues_border_thick_h = ((left_clues_ncols - 1) * cell_bdr) + (outer_bdr * 2)

    total_border_thick_h = board_border_thick_h + left_clues_border_thick_h
    total_border_thick_v = board_border_thick_v + top_clues_border_thick_v

    board_cell_size_h = board_ncols * board_cell_size
    board_cell_size_v = board_nrows * board_cell_size
    top_clues_cell_size_v = top_clues_nrows * top_clues_cell_height
    left_clues_cell_size_h = left_clues_ncols * left_clues_cell_width

    total_cell_size_h = board_cell_size_h + left_clues_cell_size_h
    total_cell_size_v = board_cell_size_v + top_clues_cell_size_v

    parent_w = total_cell_size_h + total_border_thick_h - outer_bdr
    parent_h = total_cell_size_v + total_border_thick_v - outer_bdr
    parent_x = constants.SCREEN_HALF_WIDTH - (parent_w / 2)
    parent_y = constants.SCREEN_HALF_HEIGHT - (parent_h / 2)
    parent_rect = pygame.Rect(parent_x, parent_y, parent_w, parent_h)

    board_w = board_border_thick_h + board_cell_size_h
    board_h = board_border_thick_v + board_cell_size_v
    board_x = parent_w - board_w
    board_y = parent_h - board_h
    board_rect = pygame.Rect(board_x, board_y, board_w, board_h)

    top_clues_w = board_w
    top_clues_h = top_clues_border_thick_v + top_clues_cell_size_v
    top_clues_x = board_x
    top_clues_y = 0
    top_clues_rect = pygame.Rect(top_clues_x, top_clues_y, top_clues_w, top_clues_h)

    left_clues_w = left_clues_border_thick_h + left_clues_cell_size_h
    left_clues_h = board_h
    left_clues_x = 0
    left_clues_y = board_y
    left_clues_rect = pygame.Rect(left_clues_x, left_clues_y, left_clues_w, left_clues_h)

    return board_rect, top_clues_rect, left_clues_rect, parent_rect


def calc_optimum_cell_size(
    board_nrows: int,
    board_ncols: int,
    cell_bdr: int,
    outer_bdr: int,
    top_clues_nrows: int,
    left_clues_ncols: int) -> int:
    """
    Calculate the cell size such that the puzzle fills the screen optimally.

    Parameters:
        board_nrows: The number of rows of the board.
        board_ncols: The number of columns of the board.
        cell_bdr: The thickness of the border between the cells.
        outer_bdr: The thickness of the border surrounding the board.
        top_clues_nrows: The number of rows of the top clues panel.
        left_clues_ncols: The number of columns of the left clues panel.

    Returns:
        The optimum cell size.
    """
    total_nrows = board_nrows + top_clues_nrows
    total_cols = board_ncols + left_clues_ncols

    board_border_thick_h = ((board_ncols - 1) * cell_bdr) + (outer_bdr * 2)
    board_border_thick_v = ((board_nrows - 1) * cell_bdr) + (outer_bdr * 2)
    top_clues_border_thick_v = ((top_clues_nrows - 1) * cell_bdr) + outer_bdr
    left_clues_border_thick_h = ((left_clues_ncols - 1) * cell_bdr) + outer_bdr

    total_border_thick_h = board_border_thick_h + left_clues_border_thick_h
    total_border_thick_v = board_border_thick_v + top_clues_border_thick_v

    h_margins = constants.SCREEN_LEFT_MARGIN + constants.SCREEN_RIGHT_MARGIN
    v_margins = constants.SCREEN_TOP_MARGIN + constants.SCREEN_BOTTOM_MARGIN
    usable_width = constants.SCREEN_WIDTH - h_margins
    usable_height = constants.SCREEN_HEIGHT - v_margins

    cell_width = (usable_width - total_border_thick_h) / total_cols
    cell_height = (usable_height - total_border_thick_v) / total_nrows

    cell_width = max(2, int(cell_width))
    cell_height = max(2, int(cell_height))

    return min(cell_width, cell_height)


def get_cell_rect(
    row: int,
    col: int,
    cell_width: float,
    cell_height: float,
    bdr: int,
    offset: Optional[Union[pygame.Rect, tuple[float, float, float, float]]] = None
    ) -> pygame.Rect:
    """
    Get the rect of the specified cell.

    This rect is relative to the rect whose (0, 0) coordinate
    is at the upper left grid corner.

    Parameters:
        row: The specified cell's row index.
        col: The specified cell's column index.
        cell_width: The cell width.
        cell_height: The cell height.
        bdr: The border thickness.
        offset: Optional offset amount to offset the
                x, y, width, and height of the resulting rect.

    Returns:
        The rect of the specified cell.
    """
    x = (col * cell_width) + (col * bdr)
    y = (row * cell_height) + (row * bdr)
    width = cell_width
    height = cell_height

    if offset is not None:
        offset_x, offset_y, offset_w, offset_h = offset
    else:
        offset_x, offset_y, offset_w, offset_h = 0, 0, 0, 0

    return pygame.Rect(x + offset_x, y + offset_y,
        width + offset_w, height + offset_h)