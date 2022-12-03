"""
Some useful utility functions for the renderer.
"""

import pygame
import src.constants as constants

def offset_rect(rect: pygame.Rect, amount: float) -> pygame.Rect:
    """
    Offset a rect by the specified amount and return the resulting rect.

    Offsetting will increase/decrease the boundaries of the rect by the specified amount.
    
    A positive value will decrease the boundaries of the rect while a negative value
    will increase the boundaries of the rect.

    Parameters:
        rect: The rect to be offset.
        amount: The offset value.

    Returns:
        A new Rect instance whose boundaries are offset from the original rect.
    """
    x = rect.x + amount
    y = rect.y + amount
    width = rect.width - (amount * 2)
    height = rect.height - (amount * 2)
    return pygame.Rect(x, y, width, height)


def calc_rects(
    board_cell_size: float,
    top_clues_cell_height: float,
    left_clues_cell_width: float,
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
    bdr_thick = constants.BORDER_THICKNESS
    bdr_thick2 = bdr_thick * 2

    board_border_thick_h = ((board_ncols - 1 + 4) * bdr_thick)
    board_border_thick_v = ((board_nrows - 1 + 4) * bdr_thick)
    top_clues_border_thick_v = ((top_clues_nrows - 1 + 4) * bdr_thick)
    left_clues_border_thick_h = ((left_clues_ncols - 1 + 4) * bdr_thick)

    total_border_thick_h = board_border_thick_h + left_clues_border_thick_h
    total_border_thick_v = board_border_thick_v + top_clues_border_thick_v

    board_cell_size_h = board_ncols * board_cell_size
    board_cell_size_v = board_nrows * board_cell_size
    top_clues_cell_size_v = top_clues_nrows * top_clues_cell_height
    left_clues_cell_size_h = left_clues_ncols * left_clues_cell_width

    total_cell_size_h = board_cell_size_h + left_clues_cell_size_h
    total_cell_size_v = board_cell_size_v + top_clues_cell_size_v

    parent_w = total_cell_size_h + total_border_thick_h - bdr_thick2
    parent_h = total_cell_size_v + total_border_thick_v - bdr_thick2
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
    top_clues_nrows: int,
    left_clues_ncols: int) -> float:
    """
    Calculate the cell size such that the puzzle fills the screen optimally.

    Parameters:
        board_nrows: The number of rows of the board.
        board_ncols: The number of columns of the board.
        top_clues_nrows: The number of rows of the top clues panel.
        left_clues_ncols: The number of columns of the left clues panel.

    Returns:
        The optimum cell size.
    """
    total_nrows = board_nrows + top_clues_nrows
    total_cols = board_ncols + left_clues_ncols

    board_border_thick_h = ((board_ncols - 1 + 4) * constants.BORDER_THICKNESS)
    board_border_thick_v = ((board_nrows - 1 + 4) * constants.BORDER_THICKNESS)
    top_clues_border_thick_v = ((top_clues_nrows - 1 + 2) * constants.BORDER_THICKNESS)
    left_clues_border_thick_h = ((left_clues_ncols - 1 + 2) * constants.BORDER_THICKNESS)

    total_border_thick_h = board_border_thick_h + left_clues_border_thick_h
    total_border_thick_v = board_border_thick_v + top_clues_border_thick_v

    h_margins = constants.SCREEN_LEFT_MARGIN + constants.SCREEN_RIGHT_MARGIN
    v_margins = constants.SCREEN_TOP_MARGIN + constants.SCREEN_BOTTOM_MARGIN
    usable_width = constants.SCREEN_WIDTH - h_margins
    usable_height = constants.SCREEN_HEIGHT - v_margins

    cell_width = (usable_width - total_border_thick_h) / total_cols
    cell_height = (usable_height - total_border_thick_v) / total_nrows

    return min(cell_width, cell_height)


def get_cell_rect(
    row: int,
    col: int,
    cell_width: float,
    cell_height: float,
    bdr: int) -> pygame.Rect:
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

    Returns:
        The rect of the specified cell.
    """
    x = (col * cell_width) + (col * bdr)
    y = (row * cell_height) + (row * bdr)
    width = cell_width
    height = cell_height
    return pygame.Rect(x, y, width, height)
