import pygame
import os

class TextStyle:
    def __init__(self, font_path=None, size=24, color=(255, 255, 255), bold=False, italic=False):
        """
        Classe para definir estilos de texto no estilo vitoriano.
        - font_path: caminho para a fonte (serif para vitoriano)
        - size: tamanho da fonte
        - color: cor do texto (padrão branco)
        - bold/italic: estilos
        """
        if font_path and os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, size)
        else:
            # Fallback para fonte serif padrão
            self.font = pygame.font.SysFont('timesnewroman', size, bold, italic)
        self.color = color
        self.size = size

    def render(self, text, antialias=True):
        return self.font.render(text, antialias, self.color)

class Button:
    def __init__(self, x, y, width, height, text, text_style, normal_color=(139, 69, 19), hover_color=(160, 82, 45), border_color=(218, 165, 32), border_width=3):
        """
        Botão no estilo vitoriano: bordas douradas, cores escuras.
        - normal_color: marrom escuro
        - hover_color: marrom mais claro
        - border_color: dourado
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_style = text_style
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.border_width = border_width
        self.hovered = False

    def draw(self, screen):
        # Desenha borda dourada
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        # Desenha fundo
        inner_rect = self.rect.inflate(-self.border_width*2, -self.border_width*2)
        color = self.hover_color if self.hovered else self.normal_color
        pygame.draw.rect(screen, color, inner_rect)
        # Desenha texto centralizado
        text_surf = self.text_style.render(self.text)
        text_x = self.rect.x + (self.rect.width - text_surf.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        screen.blit(text_surf, (text_x, text_y))

    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos)

class UIManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Estilos de texto vitorianos
        self.title_style = TextStyle(size=36, color=(218, 165, 32))  # Dourado para títulos
        self.dialogue_style = TextStyle(size=24, color=(255, 255, 255))  # Branco para diálogo
        self.button_style = TextStyle(size=20, color=(255, 255, 255))  # Branco para botões
        # Cores vitorianas
        self.background_color = (0, 0, 0)  # Preto
        self.text_box_color = (50, 50, 50, 180)  # Cinza escuro semi-transparente
        self.text_box_border_color = (139, 69, 19)  # Marrom

    def draw_text_box(self, screen, text, x, y, width, height):
        # Desenha caixa de texto com borda vitoriana
        text_box_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, self.text_box_border_color, text_box_rect, 5)  # Borda marrom grossa
        inner_rect = text_box_rect.inflate(-10, -10)
        # Fundo semi-transparente
        text_box_surf = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
        text_box_surf.fill(self.text_box_color)
        screen.blit(text_box_surf, inner_rect.topleft)
        return inner_rect  # Retorna retângulo interno para renderizar texto

    def create_buttons(self, options, start_y, button_width=300, button_height=40, spacing=10):
        buttons = []
        for i, option in enumerate(options):
            x = (self.screen_width - button_width) // 2
            y = start_y + i * (button_height + spacing)
            button = Button(x, y, button_width, button_height, option['texto'], self.button_style)
            buttons.append((button, option['cena']))
        return buttons

    def draw_title(self, screen, title, y=50):
        title_surf = self.title_style.render(title)
        x = (self.screen_width - title_surf.get_width()) // 2
        screen.blit(title_surf, (x, y))

    def draw_dialogue(self, screen, text, text_processor, characters, x=50, y=None, max_width=None):
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
        text_processor.render_wrapped_colored_text(
            screen,
            text,
            self.dialogue_style.font,
            x,
            y,
            max_w,
            line_height,
            self.dialogue_style.color,
            characters
        )