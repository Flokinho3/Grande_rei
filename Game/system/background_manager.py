"""
Gerenciador de backgrounds (imagens de fundo)
Responsabilidade: Carregar, escalar e renderizar imagens de fundo das cenas
"""

import pygame
import os
from typing import Optional, Tuple


class BackgroundManager:
    """Gerencia renderização de imagens de fundo"""
    
    def __init__(self, screen_width: int, screen_height: int, images_dir: str = None):
        """
        Inicializa o gerenciador de backgrounds
        
        Args:
            screen_width: Largura da tela em pixels
            screen_height: Altura da tela em pixels
            images_dir: Diretório base onde estão as imagens de fundo
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.images_dir = images_dir or os.path.join('Game', 'data', 'script', 'imgs')
        self._cache = {}  # Cache de imagens carregadas {filename: surface}
        
    def load_background(self, filename: str) -> Optional[pygame.Surface]:
        """
        Carrega uma imagem de fundo, usando cache quando disponível
        
        Args:
            filename: Nome do arquivo de imagem (relativo ao images_dir)
            
        Returns:
            Surface do Pygame com a imagem ou None se falhar
        """
        if not filename:
            return None
            
        # Verifica cache primeiro
        if filename in self._cache:
            return self._cache[filename]
            
        # Carrega do disco
        full_path = os.path.join(self.images_dir, filename)
        if not os.path.exists(full_path):
            print(f"[BACKGROUND_MANAGER] AVISO: Imagem não encontrada: {full_path}")
            return None
            
        try:
            surface = pygame.image.load(full_path).convert()
            self._cache[filename] = surface
            print(f"[BACKGROUND_MANAGER] Imagem carregada: {filename}")
            return surface
        except Exception as e:
            print(f"[BACKGROUND_MANAGER] ERRO ao carregar imagem {filename}: {e}")
            return None
            
    def scale_to_fit(self, surface: pygame.Surface) -> Tuple[pygame.Surface, Tuple[int, int]]:
        """
        Escala uma surface para caber na tela mantendo aspect ratio
        
        Args:
            surface: Surface original a ser escalada
            
        Returns:
            Tupla (surface_escalada, posição_xy) onde posição é para centralizar
        """
        if not surface:
            return None, (0, 0)
            
        original_w, original_h = surface.get_size()
        
        # Calcula fator de escala para caber mantendo proporção
        scale_w = self.screen_width / original_w
        scale_h = self.screen_height / original_h
        scale = min(scale_w, scale_h)
        
        # Novas dimensões
        new_w = int(original_w * scale)
        new_h = int(original_h * scale)
        
        # Escala a imagem
        scaled_surface = pygame.transform.scale(surface, (new_w, new_h))
        
        # Calcula posição para centralizar
        x = (self.screen_width - new_w) // 2
        y = (self.screen_height - new_h) // 2
        
        return scaled_surface, (x, y)
        
    def scale_to_fill(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Escala uma surface para preencher a tela toda (pode cortar bordas)
        
        Args:
            surface: Surface original a ser escalada
            
        Returns:
            Surface escalada que preenche toda a tela
        """
        if not surface:
            return None
            
        original_w, original_h = surface.get_size()
        
        # Calcula fator de escala para preencher (pode cortar)
        scale_w = self.screen_width / original_w
        scale_h = self.screen_height / original_h
        scale = max(scale_w, scale_h)
        
        # Novas dimensões
        new_w = int(original_w * scale)
        new_h = int(original_h * scale)
        
        # Escala e corta centralizando
        scaled = pygame.transform.scale(surface, (new_w, new_h))
        
        # Se for maior que a tela, corta centralizando
        if new_w > self.screen_width or new_h > self.screen_height:
            x_offset = (new_w - self.screen_width) // 2
            y_offset = (new_h - self.screen_height) // 2
            cropped = pygame.Surface((self.screen_width, self.screen_height))
            cropped.blit(scaled, (-x_offset, -y_offset))
            return cropped
            
        return scaled
        
    def render_background(self, screen: pygame.Surface, filename: str, 
                         fit_mode: str = 'fit') -> bool:
        """
        Carrega e renderiza um background na tela
        
        Args:
            screen: Surface da tela onde renderizar
            filename: Nome do arquivo de imagem
            fit_mode: 'fit' (ajusta mantendo proporção) ou 'fill' (preenche cortando)
            
        Returns:
            True se renderizou com sucesso, False caso contrário
        """
        if not filename:
            return False
            
        # Carrega a imagem
        bg_surface = self.load_background(filename)
        if not bg_surface:
            return False
            
        # Escala e renderiza
        if fit_mode == 'fill':
            scaled = self.scale_to_fill(bg_surface)
            screen.blit(scaled, (0, 0))
        else:  # fit (padrão)
            scaled, position = self.scale_to_fit(bg_surface)
            screen.blit(scaled, position)
            
        return True
        
    def clear_cache(self):
        """Limpa o cache de imagens carregadas"""
        self._cache.clear()
        print(f"[BACKGROUND_MANAGER] Cache limpo")
        
    def preload_backgrounds(self, filenames: list):
        """
        Pré-carrega uma lista de backgrounds no cache
        
        Args:
            filenames: Lista de nomes de arquivos a pré-carregar
        """
        for filename in filenames:
            if filename and filename not in self._cache:
                self.load_background(filename)
        print(f"[BACKGROUND_MANAGER] {len(filenames)} backgrounds pré-carregados")
