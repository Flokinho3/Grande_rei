import pygame
import re

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

    def display_scene(self, scene, player_name, text_index, characters, text_processor, buttons=None, current_sprite=None, item_notification=None):
        # Always clear the screen with background color first
        self.screen.fill(self.ui_manager.background_color)

        # Background image if available
        bg_path = os.path.join('Game', 'data', 'script', 'imgs', scene['img_fundo'])
        if os.path.exists(bg_path):
            background = pygame.image.load(bg_path)
            # Scale background to fit screen while keeping aspect ratio
            bg = background = pygame.image.load(bg_path).convert()
            bw, bh = bg.get_size()
            # compute scale factor to fit entirely
            scale = min(self.screen_width / bw, self.screen_height / bh)
            new_size = (int(bw * scale), int(bh * scale))
            background = pygame.transform.scale(bg, new_size)
            # center the image
            x = (self.screen_width - new_size[0]) // 2
            y = (self.screen_height - new_size[1]) // 2
            self.screen.blit(background, (x, y))

        # Character sprite (after background, before text box)
        print(f"[DEBUG RENDERER] current_sprite: {current_sprite}")
        print(f"[DEBUG RENDERER] characters disponíveis: {list(characters.keys()) if characters else 'None'}")
        
        # Normalize sprite name to match character names (case-insensitive)
        actual_sprite_name = None
        if current_sprite:
            sprite_lower = current_sprite.lower()
            for char_name in characters.keys():
                if char_name.lower() == sprite_lower:
                    actual_sprite_name = char_name
                    break
        
        if actual_sprite_name and actual_sprite_name in characters:
            char_data = characters[actual_sprite_name]
            print(f"[DEBUG RENDERER] Dados do personagem {actual_sprite_name}: {char_data}")
            if 'img' in char_data and char_data['img']:
                img_path = os.path.join('Game', 'data', 'script', 'imgs', 'NPC', char_data['img'])
                print(f"[DEBUG RENDERER] Caminho da imagem: {img_path}")
                print(f"[DEBUG RENDERER] Arquivo existe? {os.path.exists(img_path)}")
                if os.path.exists(img_path):
                    sprite = pygame.image.load(img_path).convert_alpha()
                    sw, sh = sprite.get_size()
                    # Scale sprite to reasonable size (max 30% of screen width, 60% of height)
                    max_sprite_width = int(self.screen_width * 0.30)
                    max_sprite_height = int(self.screen_height * 0.60)
                    scale = min(max_sprite_width / sw, max_sprite_height / sh, 1.0) if sw > 0 and sh > 0 else 1.0
                    new_sprite_size = (int(sw * scale), int(sh * scale))
                    sprite = pygame.transform.scale(sprite, new_sprite_size)
                    # Position on left side, bottom aligned
                    sprite_x = int(self.screen_width * 0.05)  # 5% from left edge
                    sprite_y = self.screen_height - new_sprite_size[1] - int(self.screen_height * 0.25)  # Above text box area
                    print(f"[DEBUG RENDERER] Desenhando sprite em ({sprite_x}, {sprite_y}), tamanho {new_sprite_size}")
                    self.screen.blit(sprite, (sprite_x, sprite_y))
                else:
                    print(f"[DEBUG RENDERER] ERRO: Arquivo de imagem não encontrado!")
            else:
                print(f"[DEBUG RENDERER] Personagem {actual_sprite_name} não tem campo 'img' ou está vazio")
        elif current_sprite:
            print(f"[DEBUG RENDERER] AVISO: sprite '{current_sprite}' não encontrado em characters (disponíveis: {list(characters.keys())})")

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
                # start roughly above the text box, centered vertically between top and text box
                available_bottom = box_y
                total_h = len(scene['opcoes']) * int(self.ui_manager.screen_height * 0.06)
                start_y = max(available_bottom // 2 - total_h // 2, int(self.screen_height * 0.15))
                buttons = self.ui_manager.create_buttons(scene['opcoes'], start_y)

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