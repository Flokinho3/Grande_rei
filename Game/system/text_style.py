"""
Classe para estilos de texto
Responsabilidade: Definir e aplicar estilos tipográficos (fontes, tamanhos, cores)
"""

import pygame
import os


class TextStyle:
    """Define estilos de texto no estilo vitoriano"""
    
    def __init__(self, font_path: str = None, size: int = 24, 
                 color: tuple = (255, 255, 255), bold: bool = False, 
                 italic: bool = False):
        """
        Cria um estilo de texto
        
        Args:
            font_path: Caminho para arquivo de fonte (usa serif se None)
            size: Tamanho da fonte em pixels
            color: Cor do texto como tupla RGB (padrão branco)
            bold: Se o texto deve ser negrito
            italic: Se o texto deve ser itálico
        """
        if font_path and os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, size)
        else:
            # Fallback para fonte serif padrão (Times New Roman para estilo vitoriano)
            self.font = pygame.font.SysFont('timesnewroman', size, bold, italic)
            
        self.color = color
        self.size = size
        self.bold = bold
        self.italic = italic
        
    def render(self, text: str, antialias: bool = True) -> pygame.Surface:
        """
        Renderiza texto com este estilo
        
        Args:
            text: Texto a renderizar
            antialias: Se deve usar anti-aliasing (padrão True)
            
        Returns:
            Surface do Pygame com o texto renderizado
        """
        return self.font.render(text, antialias, self.color)
        
    def get_text_size(self, text: str) -> tuple:
        """
        Calcula dimensões do texto renderizado
        
        Args:
            text: Texto a medir
            
        Returns:
            Tupla (largura, altura) em pixels
        """
        return self.font.size(text)
        
    def set_color(self, color: tuple):
        """
        Altera a cor do texto
        
        Args:
            color: Nova cor como tupla RGB
        """
        self.color = color
        
    def set_size(self, size: int):
        """
        Altera o tamanho da fonte (recria o objeto font)
        
        Args:
            size: Novo tamanho em pixels
        """
        self.size = size
        # Recria a fonte com novo tamanho
        self.font = pygame.font.SysFont('timesnewroman', size, self.bold, self.italic)
        
    def copy(self) -> 'TextStyle':
        """
        Cria uma cópia deste estilo
        
        Returns:
            Novo objeto TextStyle com as mesmas configurações
        """
        return TextStyle(
            font_path=None,
            size=self.size,
            color=self.color,
            bold=self.bold,
            italic=self.italic
        )
        
    @staticmethod
    def create_victorian_title(size: int = 32) -> 'TextStyle':
        """
        Factory method: cria estilo para títulos vitorianos
        
        Args:
            size: Tamanho da fonte
            
        Returns:
            TextStyle configurado para títulos (dourado)
        """
        return TextStyle(size=size, color=(218, 165, 32), bold=True)
        
    @staticmethod
    def create_victorian_dialogue(size: int = 20) -> 'TextStyle':
        """
        Factory method: cria estilo para diálogos vitorianos
        
        Args:
            size: Tamanho da fonte
            
        Returns:
            TextStyle configurado para diálogos (branco)
        """
        return TextStyle(size=size, color=(255, 255, 255))
        
    @staticmethod
    def create_victorian_button(size: int = 18) -> 'TextStyle':
        """
        Factory method: cria estilo para botões vitorianos
        
        Args:
            size: Tamanho da fonte
            
        Returns:
            TextStyle configurado para botões (branco)
        """
        return TextStyle(size=size, color=(255, 255, 255))
