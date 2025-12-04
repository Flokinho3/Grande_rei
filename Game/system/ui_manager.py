"""
Gerenciador de interface do usuário
Responsabilidade: Coordenar desenho de caixas de texto, botões, títulos e diálogos
"""

import pygame
from .text_style import TextStyle
from .button import Button


class UIManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Compute responsive sizes based on screen height/width
        # Title font ~6% of height, dialogue ~3.5%, button ~2.8%
        title_size = max(18, int(self.screen_height * 0.06))
        dialogue_size = max(14, int(self.screen_height * 0.035))
        button_size = max(12, int(self.screen_height * 0.028))

        # Estilos de texto vitorianos (sizes computed responsively)
        self.title_style = TextStyle(size=title_size, color=(218, 165, 32))  # Dourado para títulos
        self.dialogue_style = TextStyle(size=dialogue_size, color=(255, 255, 255))  # Branco para diálogo
        self.button_style = TextStyle(size=button_size, color=(255, 255, 255))  # Branco para botões

        # Cores vitorianas
        self.background_color = (0, 0, 0)  # Preto
        self.text_box_color = (50, 50, 50, 200)  # Cinza escuro semi-transparente (slightly more opaque)
        self.text_box_border_color = (139, 69, 19)  # Marrom

    def draw_text_box(self, screen, text, x, y, width, height):
        # Desenha caixa de texto com borda vitoriana
        text_box_rect = pygame.Rect(x, y, width, height)
        # Border width scales with screen size but never too thin
        border_width = max(2, int(self.screen_width * 0.003))
        pygame.draw.rect(screen, self.text_box_border_color, text_box_rect, border_width)
        inner_rect = text_box_rect.inflate(-border_width * 2, -border_width * 2)
        # Fundo semi-transparente
        text_box_surf = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
        text_box_surf.fill(self.text_box_color)
        screen.blit(text_box_surf, inner_rect.topleft)
        return inner_rect  # Retorna retângulo interno para renderizar texto

    def create_buttons(self, options, start_y, button_width=300, button_height=40, spacing=10):
        # Compute responsive defaults if caller passed defaults
        if button_width == 300:
            # default to 35% of screen width capped
            button_width = min(int(self.screen_width * 0.35), 600)
        if button_height == 40:
            button_height = max(28, int(self.screen_height * 0.06))
        if spacing == 10:
            spacing = max(8, int(self.screen_height * 0.02))

        buttons = []
        for i, option in enumerate(options):
            x = (self.screen_width - button_width) // 2
            y = start_y + i * (button_height + spacing)
            button = Button(x, y, button_width, button_height, option['texto'], self.button_style)
            # Support multiple possible keys for the next scene id to be robust
            next_id = (
                option.get('cena')
                or option.get('proximo_id')
                or option.get('proximo')
                or option.get('next')
                or option.get('scene')
                or option.get('id')
            )
            if next_id is None:
                # Warn for easier debugging but still append None so caller can decide
                print(f"UIManager.create_buttons: option missing next-id keys for option: {option}")
            buttons.append((button, next_id, option))
        return buttons

    def draw_title(self, screen, title, y=50):
        title_surf = self.title_style.render(title)
        x = (self.screen_width - title_surf.get_width()) // 2
        screen.blit(title_surf, (x, y))

    def draw_speaker_label(self, screen, name, color, box_x, box_y):
        # Draw a small labeled badge at top-left touching the top of the text box
        # Position it just above the text box (y coordinate will be adjusted to sit above box_y)
        font = self.title_style.font
        name_surf = font.render(name, True, color)
        pad_x = 10
        pad_y = 6
        bg_w = name_surf.get_width() + pad_x * 2
        bg_h = name_surf.get_height() + pad_y * 2
        # Position the badge so its bottom edge touches the top of the text box
        label_y = box_y - bg_h
        bg_rect = pygame.Rect(box_x, label_y, bg_w, bg_h)
        # border
        pygame.draw.rect(screen, self.text_box_border_color, bg_rect, border_radius=6)
        # inner background (semi-transparent)
        inner = bg_rect.inflate(-4, -4)
        surf = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        # use same RGBA as text_box_color if available else fallback
        try:
            surf.fill(self.text_box_color)
        except Exception:
            surf.fill((50, 50, 50, 200))
        screen.blit(surf, inner.topleft)
        # Blit name text
        text_pos = (inner.x + pad_x // 2, inner.y + pad_y // 2)
        screen.blit(name_surf, text_pos)

    def draw_dialogue(self, screen, text, text_processor, characters, x=50, y=None, max_width=None, skip_pressed=False):
        if y is None:
            y = self.screen_height - 150
        # Usa o renderizador com quebra de linhas para garantir que o texto não saia da caixa
        # Definir padding e dimensões
        padding = 10
        if max_width is None:
            max_w = self.screen_width - x - padding - 30
        else:
            max_w = max_width
        # calcula altura de linha com base no tamanho da fonte
        line_height = self.dialogue_style.size + 6
        
        # Usar renderizador com efeitos especiais (tex_time, jump_text)
        finished, has_slow_text = text_processor.render_dialogue_with_effects(
            screen,
            text,
            self.dialogue_style.font,
            x,
            y,
            max_w,
            line_height,
            self.dialogue_style.color,
            characters,
            skip_pressed
        )
        
        return finished, has_slow_text

    def draw_item_notification(self, screen, item):
        """
        Desenha uma notificação de item adicionado no topo esquerdo da tela.
        item deve ter 'nome' e 'quantidade'.
        """
        if not item:
            return
            
        # Posição no topo esquerdo
        margin_x = 20
        margin_y = 20
        
        # Criar texto da notificação
        # Suporta tanto dicionário quanto string
        if isinstance(item, dict):
            nome = item.get('nome', 'Item')
            quantidade = item.get('quantidade', 1)
        else:
            nome = str(item)
            quantidade = 1
        notification_text = f"+{quantidade} {nome}"
        
        # Renderizar texto
        font = self.dialogue_style.font
        text_surf = font.render(notification_text, True, (218, 165, 32))  # Dourado
        
        # Dimensões da caixa de notificação
        pad_x = 15
        pad_y = 10
        box_width = text_surf.get_width() + pad_x * 2
        box_height = text_surf.get_height() + pad_y * 2
        
        # Desenhar fundo semi-transparente
        notification_rect = pygame.Rect(margin_x, margin_y, box_width, box_height)
        
        # Borda
        border_width = 2
        pygame.draw.rect(screen, (218, 165, 32), notification_rect, border_width, border_radius=5)  # Borda dourada
        
        # Fundo escuro semi-transparente
        inner_rect = notification_rect.inflate(-border_width * 2, -border_width * 2)
        bg_surf = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
        bg_surf.fill((30, 30, 30, 220))  # Preto semi-transparente
        screen.blit(bg_surf, inner_rect.topleft)
        
        # Desenhar texto centralizado
        text_x = notification_rect.x + pad_x
        text_y = notification_rect.y + pad_y
        screen.blit(text_surf, (text_x, text_y))