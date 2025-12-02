"""
Parser de comandos de sprite para cenas
Responsabilidade: Analisar texto das cenas e extrair comandos de manipulação de sprites
"""

import re
from typing import List, Tuple, Dict


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
        
        Args:
            text: Texto da cena que pode conter comandos
            
        Returns:
            Lista de tuplas (comando, parâmetros) onde comando pode ser:
            'add', 'remove', 'clear_all', 'expression'
        """
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
        
    @staticmethod
    def strip_commands(text: str) -> str:
        """
        Remove todos os comandos de sprite do texto, deixando apenas o diálogo
        
        Args:
            text: Texto que pode conter comandos
            
        Returns:
            Texto sem comandos (apenas diálogo)
        """
        # Remove tudo que está entre chaves {}
        cleaned = re.sub(r'\{[^}]+\}', '', text)
        return cleaned.strip()
        
    @staticmethod
    def has_commands(text: str) -> bool:
        """
        Verifica se o texto contém algum comando de sprite
        
        Args:
            text: Texto a verificar
            
        Returns:
            True se contém comandos, False caso contrário
        """
        return bool(re.search(r'\{[^}]+\}', text))
        
    @staticmethod
    def is_command_only(text: str) -> bool:
        """
        Verifica se a linha contém apenas comandos (sem diálogo visível)
        
        Args:
            text: Texto a verificar
            
        Returns:
            True se a linha é apenas comandos, False se tem diálogo
        """
        stripped = SpriteCommandParser.strip_commands(text)
        return stripped == ''
