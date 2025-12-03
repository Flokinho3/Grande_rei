"""
Renderizador de cenas
Responsabilidade: Orquestrar a renderização completa de uma cena (background, sprites, UI)
"""

import pygame
import re
import os

from .ui_manager import UIManager
from .sprite_manager import SpriteManager
from .background_manager import BackgroundManager


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
        
        # Sistema de sprites
        sprite_base_path = os.path.join('Game', 'data', 'script', 'imgs', 'NPC')
        self.sprite_manager = SpriteManager(screen_width, screen_height, sprite_base_path)
        
        # Sistema de backgrounds
        self.background_manager = BackgroundManager(screen_width, screen_height)

    def display_scene(self, scene, player_name, text_index, characters, text_processor, buttons=None, sprite_manager=None, item_notification=None, condition_evaluator=None):
        # Always clear the screen with background color first
        self.screen.fill(self.ui_manager.background_color)

        # Background image usando BackgroundManager
        if 'img_fundo' in scene and scene['img_fundo']:
            self.background_manager.render_background(
                self.screen, 
                scene['img_fundo'], 
                fit_mode='fit'
            )

        # Character sprites (after background, before text box) - usando novo sistema
        if sprite_manager:
            sprite_manager.update()
            sprite_manager.render(self.screen)

        # Title
        title = text_processor.replace_placeholders(scene['titulo'], player_name, characters)
        self.ui_manager.draw_title(self.screen, title)

        # Text box and dialogue (responsive layout)
        margin_x = int(self.screen_width * 0.04)
        margin_y = int(self.screen_height * 0.03)
        box_width = self.screen_width - margin_x * 2
        box_height = max(int(self.screen_height * 0.20), 120)
        box_x = margin_x
        box_y = self.screen_height - box_height - margin_y
        text_box_inner = self.ui_manager.draw_text_box(self.screen, "", box_x, box_y, box_width, box_height)
        if text_index > 0:
            line = scene['texto'][text_index - 1]
            replaced_line = text_processor.replace_placeholders(line, player_name, characters)
            # Detect a leading speaker token in curly braces, e.g. "{Yuno}: Hello" or "{nome_player}:..."
            speaker_name = None
            speaker_color = None
            m = re.match(r"^\{([^}]+)\}\s*:?\s*(.*)$", replaced_line)
            if m:
                token = m.group(1)
                # If token refers to player name variants, use player_name
                if token.lower() in ('nome_jogador', 'nome_player', 'player_name'):
                    speaker_name = player_name
                else:
                    # Try to map normalized token to a character name
                    norm = re.sub(r'[^a-z0-9]', '_', token.lower())
                    norm_map = {}
                    for name in characters:
                        n = re.sub(r'[^a-z0-9]', '_', name.lower())
                        norm_map[n] = name
                    if norm in norm_map:
                        speaker_name = norm_map[norm]
                # The rest of the line after the token becomes the dialogue
                replaced_line = m.group(2)
                if speaker_name:
                    speaker_color = characters.get(speaker_name, {}).get('color')
                    # Draw speaker label above text box (touching the top edge)
                    if speaker_color:
                        self.ui_manager.draw_speaker_label(self.screen, speaker_name, speaker_color, box_x, box_y)
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
                # Filtra opções baseado em condições
                opcoes_filtradas = scene['opcoes']
                if condition_evaluator:
                    opcoes_filtradas = condition_evaluator.filter_options_by_conditions(scene['opcoes'])
                    if len(opcoes_filtradas) < len(scene['opcoes']):
                        print(f"[RENDERER] Opções filtradas: {len(scene['opcoes'])} -> {len(opcoes_filtradas)}")
                
                # start roughly above the text box, centered vertically between top and text box
                available_bottom = box_y
                total_h = len(opcoes_filtradas) * int(self.ui_manager.screen_height * 0.06)
                start_y = max(available_bottom // 2 - total_h // 2, int(self.screen_height * 0.15))
                buttons = self.ui_manager.create_buttons(opcoes_filtradas, start_y)

            # Desenha os botões atuais (se houver)
            if buttons:
                for button, _ in buttons:
                    button.draw(self.screen)

        # Desenhar notificação de item se houver
        if item_notification:
            self.ui_manager.draw_item_notification(self.screen, item_notification)

        pygame.display.flip()
        return buttons

    def draw_buttons(self, buttons):
        for button, _ in buttons:
            button.draw(self.screen)
        pygame.display.flip()