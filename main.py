import pygame
import sys
from Game.system.data_loader import DataLoader
from Game.system.character_loader import CharacterLoader
from Game.system.text_processor import TextProcessor
from Game.system.renderer import Renderer
from Game.system.game import Game

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
    scenes, scenes_order = data_loader.load_scenes('Game/data/script/Cap/Cap_1/EP_1.json')

    character_loader = CharacterLoader()
    characters, player_name = character_loader.load_characters()

    text_processor = TextProcessor()

    renderer = Renderer(screen, font, title_font, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY)
    renderer.text_processor = text_processor

    game = Game(scenes, scenes_order, characters, player_name, renderer, clock)
    game.run()

if __name__ == "__main__":
    main()
