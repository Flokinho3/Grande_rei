import pygame

from Game.system.data_loader import DataLoader
from Game.system.character_loader import CharacterLoader
from Game.system.text_processor import TextProcessor
from Game.system.renderer import Renderer
from Game.system.game import Game

# Initialize Pygame
pygame.init()

# Screen dimensions
info = pygame.display.Info()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# Use current display resolution and open a fullscreen window
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Visual Novel")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Font
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 36)

# Clock
clock = pygame.time.Clock()

# Main
def main():
    data_loader = DataLoader()
    result = data_loader.load_scenes('Game/data/script/Cap/Cap_1/EP_1.json')
    if result is None:
        raise RuntimeError("DataLoader.load_scenes returned None; expected (scenes, scenes_order)")
    try:
        scenes, scenes_order = result
    except Exception as exc:
        raise RuntimeError(f"Unexpected return value from load_scenes: {exc}")

    character_loader = CharacterLoader()
    characters, player_name, player_data = character_loader.load_characters()

    text_processor = TextProcessor()

    renderer = Renderer(screen, font, title_font, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY)
    setattr(renderer, "text_processor", text_processor)

    game = Game(scenes, scenes_order, characters, player_name, player_data, renderer, clock, data_loader)
    game.run()

if __name__ == "__main__":
    main()
