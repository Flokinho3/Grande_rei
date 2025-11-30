import pygame
import json
import os
import sys

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

# Load JSON data
def load_data():
    with open('Game/data/script/Cap/Cap_1/EP_1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    scenes = {scene['id']: scene for scene in data['EP_1']}
    return scenes

# Replace placeholders
def replace_placeholders(text, player_name="Jogador"):
    return text.replace("[nome_jogador]", player_name).replace("[mencao]", "mencao")

# Display scene
def display_scene(scene, player_name, text_index):
    # Background
    bg_path = os.path.join('Game', 'data', 'imgs', scene['img_fundo'])
    if os.path.exists(bg_path):
        background = pygame.image.load(bg_path)
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(background, (0, 0))
    else:
        screen.fill(WHITE)

    # Title
    title_text = title_font.render(replace_placeholders(scene['titulo'], player_name), True, BLACK)
    screen.blit(title_text, (50, 50))

    # Text lines
    y_offset = 100
    for i in range(text_index):
        line = scene['texto'][i]
        text = font.render(replace_placeholders(line, player_name), True, BLACK)
        screen.blit(text, (50, y_offset))
        y_offset += 30

    # Options only if all text shown
    buttons = []
    if text_index >= len(scene['texto']):
        y_offset = y_offset + 20
        for option in scene['opcoes']:
            button_rect = pygame.Rect(50, y_offset, 300, 40)
            pygame.draw.rect(screen, GRAY, button_rect)
            option_text = font.render(option['texto'], True, BLACK)
            screen.blit(option_text, (60, y_offset + 10))
            buttons.append((button_rect, option['cena']))
            y_offset += 50

    pygame.display.flip()
    return buttons

# Main loop
def main():
    scenes = load_data()
    current_scene_id = "1"  # Start with first scene
    player_name = "Jogador"  # Default name, can be input later
    current_text_index = 0

    running = True
    while running:
        scene = scenes.get(current_scene_id)
        if not scene:
            print("Scene not found:", current_scene_id)
            running = False
            continue

        buttons = display_scene(scene, player_name, current_text_index)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if current_text_index < len(scene['texto']):
                        current_text_index += 1
            elif event.type == pygame.MOUSEBUTTONDOWN and buttons:
                mouse_pos = pygame.mouse.get_pos()
                for button_rect, next_scene in buttons:
                    if button_rect.collidepoint(mouse_pos):
                        current_scene_id = next_scene
                        current_text_index = 0
                        break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
