"""
Avaliador de condições para exibição dinâmica de diálogos e opções
Responsabilidade: Avaliar condições baseadas em status de personagens e variáveis do jogo
"""

import re
from typing import Dict, Any, List, Optional


class ConditionEvaluator:
    """Avalia condições para determinar qual cena/opção exibir"""
    
    def __init__(self, characters: Dict[str, Dict], player_data: Dict):
        """
        Inicializa o avaliador de condições
        
        Args:
            characters: Dicionário com dados dos personagens
            player_data: Dados do jogador
        """
        self.characters = characters
        self.player_data = player_data
        
    def evaluate_scene_conditions(self, scene: Dict[str, Any]) -> Optional[str]:
        """
        Avalia as condições de uma cena e retorna o proximo_id apropriado
        
        Args:
            scene: Dicionário da cena com campo 'condicao'
            
        Returns:
            ID da próxima cena baseado nas condições ou None se nenhuma condição for atendida
        """
        if 'condicao' not in scene:
            return None
            
        conditions = scene['condicao']
        if not isinstance(conditions, list):
            return None
            
        # Avalia cada condição em ordem
        for condition in conditions:
            if self._evaluate_condition(condition):
                next_id = condition.get('proximo_id')
                print(f"[CONDITION] Condição atendida: {condition.get('dev', 'N/A')} -> {next_id}")
                return next_id
                
        print(f"[CONDITION] Nenhuma condição atendida")
        return None
        
    def filter_options_by_conditions(self, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra opções baseado em condições
        
        Args:
            options: Lista de opções, cada uma podendo ter campo 'condicao'
            
        Returns:
            Lista de opções que atendem às condições
        """
        filtered = []
        
        for option in options:
            # Se não tem condição, sempre inclui
            if 'condicao' not in option:
                filtered.append(option)
                continue
                
            # Avalia a condição
            condition = option['condicao']
            if isinstance(condition, dict):
                if self._evaluate_condition(condition):
                    print(f"[CONDITION] Opção '{option.get('texto', 'N/A')}' disponível")
                    filtered.append(option)
                else:
                    print(f"[CONDITION] Opção '{option.get('texto', 'N/A')}' bloqueada")
            else:
                # Se condição inválida, inclui por segurança
                filtered.append(option)
                
        return filtered
        
    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Avalia uma condição individual
        
        Args:
            condition: Dicionário com campos de condição (afeto, humor, etc)
            
        Returns:
            True se todas as condições são atendidas, False caso contrário
        """
        # Remove campos que não são condições
        non_condition_fields = {'dev', 'proximo_id', 'texto', 'cena'}
        
        all_met = True
        
        for key, value in condition.items():
            if key in non_condition_fields:
                continue
                
            # Processa a condição baseado no formato
            if not self._check_condition(key, value):
                all_met = False
                break
                
        return all_met
        
    def _check_condition(self, field: str, expected_value: Any) -> bool:
        """
        Verifica uma condição específica
        
        Args:
            field: Nome do campo a verificar (ex: 'afeto', 'yuno_humor', 'mestre_yuno_forca', 'flag', 'memoria')
            expected_value: Valor esperado (pode ser número, string, range, ou flag com !)
            
        Returns:
            True se a condição é atendida
        """
        # Verifica se é uma condição de flag
        if field.lower() == 'flag':
            return self._check_flag_condition(expected_value)
        
        # Verifica se é uma condição de memoria
        if field.lower() == 'memoria':
            return self._check_memoria_condition(expected_value)
        
        # Separa o nome do personagem se necessário (ex: yuno_humor -> yuno, humor)
        parts = field.split('_', 1)
        
        if len(parts) == 2:
            # Condição de personagem específico (ex: yuno_afeto, mestre_yuno_humor)
            char_key = parts[0].lower()
            attribute = parts[1]
            
            # Busca o personagem usando lowercase
            char_data = self._find_character(char_key)
            if not char_data:
                print(f"[CONDITION] Personagem '{char_key}' não encontrado")
                return False
                
            current_value = char_data.get(attribute)
        else:
            # Condição global ou do player
            attribute = field
            current_value = self.player_data.get(attribute)
            
        # Avalia baseado no tipo de valor esperado
        return self._compare_values(current_value, expected_value, attribute)
    
    def _check_flag_condition(self, flag_value: str) -> bool:
        """
        Verifica uma condição de flag
        
        Args:
            flag_value: Nome da flag, pode começar com ! para negação
            
        Returns:
            True se a condição de flag é atendida
        """
        player_flags = self.player_data.get('flags', [])
        
        # Verifica se é negação (!flag)
        if flag_value.startswith('!'):
            flag_name = flag_value[1:]
            result = flag_name not in player_flags
            print(f"[CONDITION] Flag '{flag_name}' NOT set = {result}")
            return result
        else:
            result = flag_value in player_flags
            print(f"[CONDITION] Flag '{flag_value}' set = {result}")
            return result
    
    def _check_memoria_condition(self, memoria_value: str) -> bool:
        """
        Verifica uma condição de memoria
        
        Args:
            memoria_value: Nome da memoria, pode começar com ! para negação
            
        Returns:
            True se a condição de memoria é atendida
        """
        player_memorias = self.player_data.get('memorias', [])
        
        # Verifica se é negação (!memoria)
        if memoria_value.startswith('!'):
            memoria_name = memoria_value[1:]
            result = memoria_name not in player_memorias
            print(f"[CONDITION] Memoria '{memoria_name}' NOT set = {result}")
            return result
        else:
            result = memoria_value in player_memorias
            print(f"[CONDITION] Memoria '{memoria_value}' set = {result}")
            return result
        
    def _compare_values(self, current: Any, expected: Any, field_name: str) -> bool:
        """
        Compara valores atual vs esperado
        
        Args:
            current: Valor atual
            expected: Valor esperado (pode incluir operadores: <=, >=, <, >, range)
            field_name: Nome do campo para debug
            
        Returns:
            True se os valores correspondem
        """
        # Se o valor atual não existe, falha
        if current is None:
            print(f"[CONDITION] Campo '{field_name}' não existe")
            return False
            
        # String comparison
        if isinstance(expected, str):
            # Check for comparison operators
            if expected.startswith('<='):
                try:
                    return float(current) <= float(expected[2:])
                except (ValueError, TypeError):
                    return False
                    
            elif expected.startswith('>='):
                try:
                    return float(current) >= float(expected[2:])
                except (ValueError, TypeError):
                    return False
                    
            elif expected.startswith('<'):
                try:
                    return float(current) < float(expected[1:])
                except (ValueError, TypeError):
                    return False
                    
            elif expected.startswith('>'):
                try:
                    return float(current) > float(expected[1:])
                except (ValueError, TypeError):
                    return False
                    
            # Check for range (ex: "1-5", "6-10")
            elif '-' in expected and expected[0].isdigit():
                try:
                    min_val, max_val = expected.split('-')
                    min_val = float(min_val)
                    max_val = float(max_val)
                    current_num = float(current)
                    result = min_val <= current_num <= max_val
                    print(f"[CONDITION] {field_name}: {current} in range [{min_val}-{max_val}] = {result}")
                    return result
                except (ValueError, TypeError):
                    pass
                    
            # Direct string comparison (case insensitive)
            result = str(current).strip().lower() == expected.strip().lower()
            print(f"[CONDITION] {field_name}: '{current}' == '{expected}' = {result}")
            return result
            
        # Numeric comparison
        elif isinstance(expected, (int, float)):
            try:
                return float(current) == float(expected)
            except (ValueError, TypeError):
                return False
                
        # Direct comparison as fallback
        return current == expected
        
    def _find_character(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Busca um personagem por nome (case-insensitive)
        
        Args:
            name: Nome do personagem
            
        Returns:
            Dados do personagem ou None
        """
        name_lower = name.lower()
        for char_name, char_data in self.characters.items():
            if char_name.lower() == name_lower:
                return char_data
        return None
