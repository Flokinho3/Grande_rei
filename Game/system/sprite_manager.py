"""
Gerenciador avançado de sprites de personagens
Suporta múltiplos sprites, posicionamento, expressões, transições e efeitos
"""

import pygame
import os
from typing import Dict, Optional, Tuple, List


class Sprite:
    """Representa um sprite individual com suas propriedades"""
    
    def __init__(self, name: str, image_path: str, position: str = 'left', 
                 expression: str = '', z_index: int = 0):
        self.name = name
        self.image_path = image_path
        self.position = position  # 'left', 'center', 'right', 'custom'
        self.expression = expression  # '', 'happy', 'sad', 'angry', etc.
        self.z_index = z_index  # Para controlar ordem de renderização
        self.surface = None
        self.rect = None
        self.alpha = 255  # Para efeitos de fade
        self.offset_x = 0  # Para animações de slide
        self.offset_y = 0
        self.target_alpha = 255
        self.fade_speed = 15
        
    def load_image(self, base_path: str, screen_width: int, screen_height: int) -> bool:
        """Carrega e escala a imagem do sprite"""
        # Tenta carregar com expressão primeiro (ex: yuno_happy.png)
        if self.expression:
            expr_filename = self.image_path.replace('.png', f'_{self.expression}.png')
            expr_path = os.path.join(base_path, expr_filename)
            if os.path.exists(expr_path):
                full_path = expr_path
            else:
                full_path = os.path.join(base_path, self.image_path)
        else:
            full_path = os.path.join(base_path, self.image_path)
            
        if not os.path.exists(full_path):
            print(f"[SPRITE_MANAGER] AVISO: Imagem não encontrada: {full_path}")
            return False
            
        try:
            self.surface = pygame.image.load(full_path).convert_alpha()
            sw, sh = self.surface.get_size()
            
            # Escala baseada na posição
            if self.position == 'center':
                max_width = int(screen_width * 0.35)
                max_height = int(screen_height * 0.70)
            else:  # left ou right
                max_width = int(screen_width * 0.30)
                max_height = int(screen_height * 0.60)
                
            scale = min(max_width / sw, max_height / sh, 1.0) if sw > 0 and sh > 0 else 1.0
            new_size = (int(sw * scale), int(sh * scale))
            self.surface = pygame.transform.scale(self.surface, new_size)
            self.rect = self.surface.get_rect()
            
            # Define posição base
            self._set_position(screen_width, screen_height)
            return True
            
        except Exception as e:
            print(f"[SPRITE_MANAGER] ERRO ao carregar imagem: {e}")
            return False
    
    def _set_position(self, screen_width: int, screen_height: int):
        """Define a posição do sprite na tela"""
        if not self.rect:
            return
            
        # Altura base (alinhado ao fundo, acima da caixa de texto)
        text_box_area = int(screen_height * 0.25)
        self.rect.bottom = screen_height - text_box_area
        
        if self.position == 'left':
            self.rect.left = int(screen_width * 0.05)
        elif self.position == 'center':
            self.rect.centerx = screen_width // 2
        elif self.position == 'right':
            self.rect.right = int(screen_width * 0.95)
            
    def update(self):
        """Atualiza animações (fade, movimento, etc)"""
        # Fade in/out
        if self.alpha != self.target_alpha:
            if self.alpha < self.target_alpha:
                self.alpha = min(self.alpha + self.fade_speed, self.target_alpha)
            else:
                self.alpha = max(self.alpha - self.fade_speed, self.target_alpha)
                
    def set_fade_out(self):
        """Inicia efeito de fade out"""
        self.target_alpha = 0
        
    def set_fade_in(self):
        """Inicia efeito de fade in"""
        self.target_alpha = 255
        
    def is_faded_out(self) -> bool:
        """Verifica se o sprite está completamente invisível"""
        return self.alpha == 0
        
    def render(self, surface: pygame.Surface):
        """Renderiza o sprite na tela"""
        if not self.surface or not self.rect:
            return
            
        # Aplica transparência se necessário
        if self.alpha < 255:
            temp_surface = self.surface.copy()
            temp_surface.set_alpha(self.alpha)
            surface.blit(temp_surface, (self.rect.x + self.offset_x, self.rect.y + self.offset_y))
        else:
            surface.blit(self.surface, (self.rect.x + self.offset_x, self.rect.y + self.offset_y))


class SpriteManager:
    """Gerencia todos os sprites na tela"""
    
    def __init__(self, screen_width: int, screen_height: int, base_image_path: str):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.base_image_path = base_image_path
        self.sprites: Dict[str, Sprite] = {}  # position -> Sprite
        self.fade_out_queue: List[str] = []  # sprites sendo removidos
        
    def add_sprite(self, character_name: str, image_filename: str, 
                   position: str = 'left', expression: str = '', 
                   z_index: int = 0, fade_in: bool = True) -> bool:
        """Adiciona ou substitui um sprite em uma posição"""
        sprite = Sprite(character_name, image_filename, position, expression, z_index)
        
        if sprite.load_image(self.base_image_path, self.screen_width, self.screen_height):
            # Se já existe sprite nessa posição, remove o antigo
            if position in self.sprites:
                self.remove_sprite(position, fade_out=True)
                
            if fade_in:
                sprite.alpha = 0
                sprite.set_fade_in()
                
            self.sprites[position] = sprite
            print(f"[SPRITE_MANAGER] Sprite adicionado: {character_name} em {position}")
            return True
        return False
        
    def remove_sprite(self, position: str, fade_out: bool = True):
        """Remove um sprite de uma posição"""
        if position in self.sprites:
            if fade_out:
                self.sprites[position].set_fade_out()
                self.fade_out_queue.append(position)
            else:
                del self.sprites[position]
            print(f"[SPRITE_MANAGER] Sprite removido de: {position}")
            
    def remove_all_sprites(self, fade_out: bool = True):
        """Remove todos os sprites"""
        positions = list(self.sprites.keys())
        for pos in positions:
            self.remove_sprite(pos, fade_out)
            
    def change_expression(self, position: str, new_expression: str) -> bool:
        """Muda a expressão de um sprite existente"""
        if position not in self.sprites:
            return False
            
        sprite = self.sprites[position]
        sprite.expression = new_expression
        # Recarrega a imagem com a nova expressão
        return sprite.load_image(self.base_image_path, self.screen_width, self.screen_height)
        
    def has_sprite(self, position: str) -> bool:
        """Verifica se existe sprite em uma posição"""
        return position in self.sprites
        
    def update(self):
        """Atualiza todos os sprites (animações, efeitos)"""
        # Atualiza sprites ativos
        for sprite in self.sprites.values():
            sprite.update()
            
        # Remove sprites que completaram o fade out
        for pos in self.fade_out_queue[:]:
            if pos in self.sprites and self.sprites[pos].is_faded_out():
                del self.sprites[pos]
                self.fade_out_queue.remove(pos)
                
    def render(self, surface: pygame.Surface):
        """Renderiza todos os sprites ordenados por z-index"""
        # Ordena sprites por z-index (menor primeiro = mais atrás)
        sorted_sprites = sorted(self.sprites.values(), key=lambda s: s.z_index)
        
        for sprite in sorted_sprites:
            sprite.render(surface)
            
    def clear(self):
        """Limpa todos os sprites imediatamente"""
        self.sprites.clear()
        self.fade_out_queue.clear()


class SpriteCommandParser:
    """Parse comandos de sprite do texto das cenas"""
    
    @staticmethod
    def parse_sprite_command(text: str) -> List[Tuple[str, Dict]]:
        """
        Parse comandos de sprite do texto
        Retorna lista de (comando, parâmetros)
        
        Comandos suportados:
        - {sprite:nome:left} - adiciona sprite à esquerda
        - {sprite:nome:center} - adiciona sprite ao centro
        - {sprite:nome:right} - adiciona sprite à direita
        - {sprite:nome:left:happy} - adiciona sprite com expressão
        - {sprite_clear:left} - remove sprite da esquerda
        - {sprite_clear:all} - remove todos sprites
        - {expr:left:sad} - muda expressão do sprite à esquerda
        
        Comandos legados (compatibilidade):
        - {img_esquerda:nome} - adiciona à esquerda
        - {img_esquerda:} ou {img_clear} - remove todos
        """
        import re
        commands = []
        
        # Novo formato: {sprite:nome:posição:expressão}
        sprite_pattern = r'\{sprite:([^:}]+):([^:}]+)(?::([^:}]+))?\}'
        for match in re.finditer(sprite_pattern, text):
            char_name = match.group(1).strip()
            position = match.group(2).strip()
            expression = match.group(3).strip() if match.group(3) else ''
            commands.append(('add', {
                'character': char_name,
                'position': position,
                'expression': expression
            }))
            
        # Comando de remoção: {sprite_clear:posição}
        clear_pattern = r'\{sprite_clear:([^}]+)\}'
        for match in re.finditer(clear_pattern, text):
            target = match.group(1).strip()
            if target == 'all':
                commands.append(('clear_all', {}))
            else:
                commands.append(('remove', {'position': target}))
                
        # Comando de expressão: {expr:posição:expressão}
        expr_pattern = r'\{expr:([^:}]+):([^}]+)\}'
        for match in re.finditer(expr_pattern, text):
            position = match.group(1).strip()
            expression = match.group(2).strip()
            commands.append(('expression', {
                'position': position,
                'expression': expression
            }))
            
        # Compatibilidade: {img_esquerda:nome}
        legacy_pattern = r'\{img_esquerda:([^}]*)\}'
        for match in re.finditer(legacy_pattern, text):
            char_name = match.group(1).strip()
            if char_name:
                commands.append(('add', {
                    'character': char_name,
                    'position': 'left',
                    'expression': ''
                }))
            else:
                commands.append(('clear_all', {}))
                
        # Compatibilidade: {img_clear}
        if '{img_clear}' in text:
            commands.append(('clear_all', {}))
            
        return commands
