import os
import sys
import pygame
import logging

from src.puzzle import Puzzle
from src.renderer import Renderer
import src.constants as constants


logger = logging.getLogger(__name__)
console = logging.getLogger('console')


####################################################################################################
#  INITIALIZATION
####################################################################################################

os.environ['SDL_VIDEO_WINDOW_POS'] = f"{constants.SCREEN_X},{constants.SCREEN_Y}"
pygame.init()
SCREEN: pygame.Surface = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Nonograms")


####################################################################################################
#  MAIN
####################################################################################################

def main():
    """Main function."""

    try:
        puzzle = Puzzle.get_sample()
        renderer = Renderer(SCREEN)
        renderer.initialize_puzzle(puzzle)
        renderer.render()

        # Loop forever
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.info(f'Quitting nonograms...')
                    console.info(f'Quitting nonograms...')
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    handle_mouse_down(event, renderer)

                elif event.type == pygame.MOUSEMOTION:
                    handle_mouse_move(event, renderer)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    handle_mouse_up(event, renderer)

                elif event.type == pygame.MOUSEWHEEL:
                    handle_mouse_wheel(event, renderer)

    except KeyboardInterrupt:
        logger.info(f'Quitting nonograms...')
        console.info(f'Quitting nonograms...')
        pygame.quit()
        sys.exit()

def handle_mouse_down(event: pygame.event.Event, renderer: Renderer) -> None:
    """
    Handle mouse down event.
    """
    is_lmb, is_mmb, is_rmb = pygame.mouse.get_pressed(3)
    curr_x, curr_y = pygame.mouse.get_pos()

    if is_lmb:
        row_idx, col_idx = renderer.screen_to_board_coords(curr_x, curr_y)
        if (row_idx >= 0 and row_idx < renderer.puzzle.nrows and 
            col_idx >= 0 and col_idx < renderer.puzzle.ncols):
           renderer.start_draft(row_idx, col_idx, '.')

    if is_mmb:
        renderer.start_drag(curr_x, curr_y)

    renderer.render()

def handle_mouse_up(event: pygame.event.Event, renderer: Renderer) -> None:
    """
    Handle mouse up event.
    """
    is_lmb, is_mmb, is_rmb = pygame.mouse.get_pressed(3)

    if not is_lmb:
        if renderer.is_drafting:
            for row_idx, col_idx in renderer.get_draft_cell_coords():
                renderer.puzzle.board[row_idx][col_idx] = renderer.draft_symbol
        renderer.end_draft()

    if not is_mmb:
        renderer.end_drag()

    renderer.render()

def handle_mouse_move(event: pygame.event.Event, renderer: Renderer) -> None:
    """
    Handle mouse move event.
    """
    is_lmb, is_mmb, is_rmb = pygame.mouse.get_pressed(3)
    curr_x, curr_y = pygame.mouse.get_pos()

    if is_lmb and renderer.is_drafting:
        row_idx, col_idx = renderer.screen_to_board_coords(curr_x, curr_y)
        if (row_idx >= 0 and row_idx < renderer.puzzle.nrows and 
            col_idx >= 0 and col_idx < renderer.puzzle.ncols):
           renderer.update_draft(row_idx, col_idx)
           renderer.render()

    if is_mmb and renderer.is_dragging:
        renderer.update_drag(curr_x, curr_y)
        renderer.render()

def handle_mouse_wheel(event: pygame.event.Event, renderer: Renderer) -> None:
    """
    Handle mouse wheel event.
    """
    value = 0.05
    if pygame.key.get_mods() & pygame.KMOD_CTRL:
        # Zoom in/out faster if CTRL key is pressed.
        value = 0.15

    if event.y > 0:
        renderer.inc_scaling_factor(value)
    elif event.y < 0:
        renderer.inc_scaling_factor(-value)

    renderer.initialize_surfaces()
    renderer.render()
