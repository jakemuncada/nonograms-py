"""
Some useful utility functions for the renderer.
"""

import pygame
import src.constants as constants



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
    board_border_thick_h = ((board_ncols - 1 + 4) * constants.BORDER_THICKNESS)
    board_border_thick_v = ((board_nrows - 1 + 4) * constants.BORDER_THICKNESS)
    top_clues_border_thick_v = ((top_clues_nrows - 1 + 2) * constants.BORDER_THICKNESS)
    left_clues_border_thick_h = ((left_clues_ncols - 1 + 2) * constants.BORDER_THICKNESS)

    total_border_thick_h = board_border_thick_h + left_clues_border_thick_h
    total_border_thick_v = board_border_thick_v + top_clues_border_thick_v

    board_cell_size_h = board_ncols * board_cell_size
    board_cell_size_v = board_nrows * board_cell_size
    top_clues_cell_size_v = top_clues_nrows * top_clues_cell_height
    left_clues_cell_size_h = left_clues_ncols * left_clues_cell_width

    total_cell_size_h = board_cell_size_h + left_clues_cell_size_h
    total_cell_size_v = board_cell_size_v + top_clues_cell_size_v

    parent_w = total_cell_size_h + total_border_thick_h
    parent_h = total_cell_size_v + total_border_thick_v
    parent_x = constants.SCREEN_HALF_WIDTH - (parent_w / 2)
    parent_y = constants.SCREEN_HALF_HEIGHT - (parent_h / 2)
    parent_rect = pygame.Rect(parent_x, parent_y, parent_w, parent_h)

    board_w = board_border_thick_h + board_cell_size_h
    board_h = board_border_thick_v + board_cell_size_v
    board_x = parent_w - board_w
    board_y = parent_h - board_h
    board_rect = pygame.Rect(board_w, board_h, board_x, board_y)

    top_clues_w = board_w
    top_clues_h = top_clues_border_thick_v + top_clues_cell_size_v
    top_clues_x = board_x
    top_clues_y = 0
    top_clues_rect = pygame.Rect(top_clues_w, top_clues_h, top_clues_x, top_clues_y)

    left_clues_w = left_clues_border_thick_h + left_clues_cell_size_h
    left_clues_h = board_h
    left_clues_x = 0
    left_clues_y = board_y
    left_clues_rect = pygame.Rect(left_clues_w, left_clues_h, left_clues_x, left_clues_y)

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





















def calc_borders_thickness(nrows: int, ncols: int) -> tuple[float, float]:
    """
    Calculate the total border thickness for both horizontal and vertical borders.

    The total border thickness includes the following:
        - Two border width's worth of outer border on the one side.
        - All the inner borders (between the cells).
        - And another two border width's worth of outer border on the other side.

    Parameters:
        nrows: The number of rows.
        ncols: The number of columns.

    Returns:
        A tuple containing the horizontal borders thickness
        and the vertical borders thickness respectively.
    """
    hborders_count = (ncols - 1) + 4
    vborders_count = (nrows - 1) + 4
    hborders_thickness = hborders_count * constants.BORDER_THICKNESS
    vborders_thickness = vborders_count * constants.BORDER_THICKNESS
    return hborders_thickness, vborders_thickness



def calc_board_rect(cell_size: float, nrows: int, ncols: int) -> pygame.Rect:
    """
    Calculate the board rect.

    Parameters:
        cell_size: The size of the cells in pixels.
        nrows: The number of rows in the puzzle.
        ncols: The number of columns in the puzzle.

    Returns:
        The board rect, which specifies the position and size of the board.
    """
    borders_h, borders_v = calc_borders_thickness(nrows, ncols)
    board_width = (cell_size * ncols) + borders_h
    board_height = (cell_size * nrows) + borders_v
    board_x = constants.SCREEN_HALF_WIDTH - (board_width / 2)
    board_y = constants.SCREEN_HALF_HEIGHT - (board_width / 2)
    return pygame.Rect(board_x, board_y, board_width, board_height)

def calc_top_clues_rect(cell_size: float, nrows: int, ncols: int) -> pygame.Rect:
    """
    """
    # borders_h, borders_v = calc_borders_thickness(nrows, ncols)
    # width = (cell_size * ncols) + borders_h
    # height = (cell_size * nrows) + borders_v - (constants.BORDER_THICKNESS * 2)
    # board_x = constants.SCREEN_HALF_WIDTH - (board_width / 2)

    # width = (cell_size * ncols) + hborders_thickness
    # height = utils.calc_clues_panel_dimension(self.cell_size, self.puzzle.max_col_clues)
    # left = self.board_rect.left
    # top = self.board_rect.top - height

def calc_clues_panel_dimension(cell_size: float, max_clues: int) -> float:
    """
    Calculate either the width/height dimension of the left/top clues panel,
    depending on the given parameters.

    Parameters:
        cell_size: The size of the cells in pixels.
        max_clues: The maximum number of clues.

    Returns:
        Either the width of the left clues panel or the height of the top clues panel.
    """
    nborders = (max_clues - 1) + 2
    borders_thickness = nborders * constants.BORDER_THICKNESS
    return (cell_size * max_clues) + borders_thickness