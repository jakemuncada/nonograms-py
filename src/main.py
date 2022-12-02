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
        __main()
    except KeyboardInterrupt:
        logger.info(f'Quitting nonograms...')
        console.info(f'Quitting nonograms...')
        pygame.quit()
        sys.exit()


def __main():
    """Main function."""

    puzzle = Puzzle(80, 80, [], [])
    renderer = Renderer(SCREEN)
    renderer.initialize_puzzle(puzzle)
    renderer.render()

    is_dragging = False

    # Loop forever
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info(f'Quitting nonograms...')
                console.info(f'Quitting nonograms...')
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                is_lmb, is_mmb, is_rmb = pygame.mouse.get_pressed(3)

                if is_mmb:
                    # If middle mouse is pressed, start dragging.
                    is_dragging = True
                    orig_x, orig_y = pygame.mouse.get_pos()
                    orig_pan_x, orig_pan_y = renderer.pan_delta

            elif event.type == pygame.MOUSEMOTION:
                is_lmb, is_mmb, is_rmb = pygame.mouse.get_pressed(3)

                if is_mmb and is_dragging:
                    curr_x, curr_y = pygame.mouse.get_pos()
                    delta_x = curr_x - orig_x
                    delta_y = curr_y - orig_y
                    new_pan_x = orig_pan_x + delta_x
                    new_pan_y = orig_pan_y + delta_y
                    renderer.set_pan(new_pan_x, new_pan_y)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                is_lmb, is_mmb, is_rmb = pygame.mouse.get_pressed(3)

                if not is_mmb:
                    is_dragging = False

            elif event.type == pygame.MOUSEWHEEL:
                value = 0.05
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Zoom in/out faster if CTRL key is pressed.
                    value = 0.15

                if event.y > 0:
                    renderer.inc_scaling_factor(value)
                elif event.y < 0:
                    renderer.inc_scaling_factor(-value)
