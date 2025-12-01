import pygame
import os
from .ui_manager import UIManager

class Renderer:
    def __init__(self, screen, font, title_font, screen_width, screen_height, white, black, gray):
        self.screen = screen
        self.font = font
        self.title_font = title_font
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.white = white
        self.black = black
        self.gray = gray
        self.ui_manager = UIManager(screen_width, screen_height)
        self.text_processor = None  # Will be set later

    def display_scene(self, scene, player_name, text_index, characters, text_processor, buttons=None):
        # Background - default to dark if no image
        bg_path = os.path.join('Game', 'data', 'imgs', scene['img_fundo'])
        if os.path.exists(bg_path):
            background = pygame.image.load(bg_path)
            background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill(self.ui_manager.background_color)  # Fundo escuro vitoriano

        # Title
        title = text_processor.replace_placeholders(scene['titulo'], player_name, characters)
        self.ui_manager.draw_title(self.screen, title)

        # Text box and dialogue
        text_box_inner = self.ui_manager.draw_text_box(self.screen, "", 30, self.screen_height - 180, 740, 140)
        if text_index > 0:
            line = scene['texto'][text_index - 1]
            replaced_line = text_processor.replace_placeholders(line, player_name, characters)
            # Passe também a largura útil da caixa interna para que o texto quebre corretamente
            self.ui_manager.draw_dialogue(
                self.screen,
                replaced_line,
                text_processor,
                characters,
                text_box_inner.x + 10,
                text_box_inner.y + 10,
                text_box_inner.width - 20
            )

        # Options as Victorian buttons
        if 'opcoes' in scene and text_index >= len(scene['texto']):
            # Se não houver buttons passados, crie novos
            if buttons is None:
                start_y = (self.screen_height // 2) - (len(scene['opcoes']) * 50) // 2
                buttons = self.ui_manager.create_buttons(scene['opcoes'], start_y)

            # Desenha os botões atuais (se houver)
            if buttons:
                for button, _ in buttons:
                    button.draw(self.screen)

        pygame.display.flip()
        return buttons

    def draw_buttons(self, buttons):
        for button, _ in buttons:
            button.draw(self.screen)
        pygame.display.flip()