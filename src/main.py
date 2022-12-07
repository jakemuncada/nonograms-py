import os
import sys
import json
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

def main(args: list[str]):
    """Main function."""

    try:
        puzzle_idx = int(args[1]) if len(args) > 1 and args[1].isnumeric() else 0

        # Open a sample puzzle.
        with open('./src/data/puzzles.json', 'r') as f:
            data = json.load(f)
        puzzle = Puzzle.from_json(data[puzzle_idx])

        puzzle.left_clues_ticks[3][-1] = True
        puzzle.left_clues_ticks[3][-2] = True
        puzzle.left_clues_ticks[4][-2] = True
        puzzle.left_clues_ticks[5][-1] = True
        puzzle.left_clues_ticks[6][-3] = True

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

    if is_lmb and is_rmb:
        renderer.end_draft()

    elif is_lmb:
        if renderer.get_actual_board_rect().collidepoint(curr_x, curr_y):
            row_idx, col_idx = renderer.screen_coord_to_cell_idx(curr_x, curr_y)
            if renderer.puzzle.is_board_cell_idx_valid(row_idx, col_idx):
                curr_symbol = renderer.puzzle.board[row_idx][col_idx]
                if curr_symbol == ' ':
                    new_symbol = '.'
                elif curr_symbol == '.':
                    new_symbol = 'x'
                elif curr_symbol == 'x':
                    new_symbol = ' '
                renderer.start_draft(row_idx, col_idx, new_symbol)

        elif renderer.get_actual_top_clues_rect().collidepoint(curr_x, curr_y):
            row_idx, col_idx = renderer.screen_coord_to_top_clues_idx(curr_x, curr_y)
            if renderer.puzzle.is_top_clues_cell_idx_valid(row_idx, col_idx):
                tick_flag = not renderer.puzzle.top_clues_ticks[row_idx][col_idx]
                renderer.start_top_clue_toggling(row_idx, col_idx, tick_flag)

        elif renderer.get_actual_left_clues_rect().collidepoint(curr_x, curr_y):
            pass

    elif is_mmb:
        renderer.start_drag(curr_x, curr_y)

    renderer.update_symbols()
    renderer.render()

def handle_mouse_up(event: pygame.event.Event, renderer: Renderer) -> None:
    """
    Handle mouse up event.
    """
    is_lmb, is_mmb, is_rmb = pygame.mouse.get_pressed(3)

    if not is_lmb:
        if renderer.is_drafting:
            for row_idx, col_idx in renderer.get_draft_cell_indices():
                renderer.puzzle.board[row_idx][col_idx] = renderer.draft_symbol
            renderer.end_draft()

        if renderer.is_toggling_top_clues:
            for row_idx, col_idx in renderer.get_clues_toggle_cell_indices():
                renderer.puzzle.top_clues_ticks[row_idx][col_idx] = renderer.clue_tick_flag
            renderer.end_clue_toggling()

    if not is_mmb:
        renderer.end_drag()

    renderer.update_symbols()
    renderer.update_clues()
    renderer.render()

def handle_mouse_move(event: pygame.event.Event, renderer: Renderer) -> None:
    """
    Handle mouse move event.
    """
    is_lmb, is_mmb, is_rmb = pygame.mouse.get_pressed(3)
    curr_x, curr_y = pygame.mouse.get_pos()

    if is_lmb and renderer.is_drafting:
        row_idx, col_idx = renderer.screen_coord_to_cell_idx(curr_x, curr_y)
        if renderer.puzzle.is_board_cell_idx_valid(row_idx, col_idx):
           renderer.update_draft(row_idx, col_idx)
           renderer.update_symbols(mode='draft')
           renderer.render()

    if is_lmb and renderer.is_toggling_top_clues:
        row_idx, col_idx = renderer.screen_coord_to_top_clues_idx(curr_x, curr_y)
        if renderer.puzzle.is_top_clues_cell_idx_valid(row_idx, col_idx):
            renderer.update_clue_toggling(row_idx, col_idx)
            renderer.update_clues()
            renderer.render()

    if is_mmb and renderer.is_dragging:
        renderer.update_drag(curr_x, curr_y)
        renderer.render()

def handle_mouse_wheel(event: pygame.event.Event, renderer: Renderer) -> None:
    """
    Handle mouse wheel event.
    """
    value = 2
    if pygame.key.get_mods() & pygame.KMOD_CTRL:
        # Zoom in/out faster if CTRL key is pressed.
        value = 6

    if event.y > 0:
        renderer.zoom(value)
    elif event.y < 0:
        renderer.zoom(-value)

    renderer.initialize_surfaces()
    renderer.render()
