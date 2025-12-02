"""
Classe de botão interativo
Responsabilidade: Renderizar e gerenciar interações com botões (hover, cliques)
"""

import pygame
from .text_style import TextStyle


class Button:
    """Botão interativo no estilo vitoriano"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 text_style: TextStyle, 
                 normal_color: tuple = (139, 69, 19),
                 hover_color: tuple = (160, 82, 45),
                 border_color: tuple = (218, 165, 32),
                 border_width: int = 3):
        """
        Cria um botão estilo vitoriano
        
        Args:
            x: Posição X do botão
            y: Posição Y do botão
            width: Largura do botão
            height: Altura do botão
            text: Texto a exibir no botão
            text_style: Estilo do texto (objeto TextStyle)
            normal_color: Cor de fundo normal (marrom escuro)
            hover_color: Cor de fundo ao passar mouse (marrom claro)
            border_color: Cor da borda (dourado)
            border_width: Espessura da borda em pixels
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_style = text_style
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.border_width = border_width
        self.hovered = False
        
    def draw(self, screen: pygame.Surface):
        """
        Renderiza o botão na tela
        
        Args:
            screen: Surface da tela onde desenhar
        """
        # Desenha borda dourada
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        
        # Desenha fundo (cor depende do hover)
        inner_rect = self.rect.inflate(-self.border_width * 2, -self.border_width * 2)
        color = self.hover_color if self.hovered else self.normal_color
        pygame.draw.rect(screen, color, inner_rect)
        
        # Desenha texto centralizado
        text_surf = self.text_style.render(self.text)
        text_x = self.rect.x + (self.rect.width - text_surf.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        screen.blit(text_surf, (text_x, text_y))
        
    def update_hover(self, mouse_pos: tuple):
        """
        Atualiza estado de hover baseado na posição do mouse
        
        Args:
            mouse_pos: Tupla (x, y) com posição do mouse
        """
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos: tuple, event: pygame.event.Event) -> bool:
        """
        Verifica se o botão foi clicado
        
        Args:
            mouse_pos: Tupla (x, y) com posição do mouse
            event: Evento do Pygame
            
        Returns:
            True se o botão foi clicado, False caso contrário
        """
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                self.rect.collidepoint(mouse_pos))
                
    def set_position(self, x: int, y: int):
        """
        Altera a posição do botão
        
        Args:
            x: Nova posição X
            y: Nova posição Y
        """
        self.rect.x = x
        self.rect.y = y
        
    def set_text(self, text: str):
        """
        Altera o texto do botão
        
        Args:
            text: Novo texto a exibir
        """
        self.text = text
        
    def set_enabled(self, enabled: bool):
        """
        Habilita ou desabilita o botão (visual)
        
        Args:
            enabled: True para habilitar, False para desabilitar
        """
        if not enabled:
            # Escurece as cores quando desabilitado
            self.normal_color = (80, 40, 10)
            self.hover_color = (80, 40, 10)
        else:
            # Restaura cores originais
            self.normal_color = (139, 69, 19)
            self.hover_color = (160, 82, 45)
            
    def get_rect(self) -> pygame.Rect:
        """
        Retorna o retângulo do botão
        
        Returns:
            Objeto pygame.Rect com posição e dimensões
        """
        return self.rect
