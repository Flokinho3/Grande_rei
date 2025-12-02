"""
Gerenciador de status de personagens
Responsabilidade: Aplicar e persistir mudanças nos dados dos personagens (status_infor)
"""

import json
import os
from typing import Dict, Any


class StatusManager:
    """Gerencia atualizações de status dos personagens"""
    
    def __init__(self, characters: Dict[str, Dict], base_dir: str = None):
        """
        Inicializa o gerenciador de status
        
        Args:
            characters: Dicionário com dados dos personagens em memória
            base_dir: Diretório base onde estão os arquivos JSON dos personagens
        """
        self.characters = characters
        self.base_dir = base_dir or os.path.join('Game', 'data', 'script', 'Base')
        
    def apply_status_infor(self, status: dict) -> bool:
        """
        Aplica um status_infor a um personagem específico
        
        Args:
            status: Dicionário contendo 'nome' e campos a serem atualizados
            
        Returns:
            True se aplicou com sucesso, False caso contrário
            
        Raises:
            ValueError: Se o status não contém o campo 'nome'
        """
        target_name = status.get('nome')
        if not target_name:
            raise ValueError('status_infor não contém campo "nome"')
            
        # Normaliza para comparação
        target_norm = target_name.strip().lower()
        
        # Busca o personagem em memória
        matched_key = None
        for name in self.characters.keys():
            if name.strip().lower() == target_norm:
                matched_key = name
                break
                
        # Busca o arquivo JSON do personagem
        file_path = self._find_character_file(target_norm)
        
        if not file_path:
            print(f"[STATUS_MANAGER] AVISO: Arquivo JSON do personagem '{target_name}' não encontrado")
            # Ainda atualiza memória se existir
            if matched_key:
                merged = self._merge_status_into_dict(self.characters[matched_key], status)
                self.characters[matched_key] = merged
                print(f"[STATUS_MANAGER] Personagem '{matched_key}' atualizado em memória (arquivo não encontrado)")
            return False
            
        # Carrega dados do arquivo
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
        except Exception as e:
            print(f"[STATUS_MANAGER] ERRO ao carregar arquivo: {e}")
            return False
            
        # Mescla os dados
        merged_data = self._merge_status_into_dict(file_data, status)
        
        # Salva de volta no arquivo
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=4, ensure_ascii=False)
            print(f"[STATUS_MANAGER] Arquivo do personagem atualizado: {file_path}")
        except Exception as e:
            print(f"[STATUS_MANAGER] ERRO ao salvar arquivo do personagem: {e}")
            return False
            
        # Atualiza memória
        mem_key = matched_key or merged_data.get('nome')
        if mem_key:
            self.characters[mem_key] = merged_data
            print(f"[STATUS_MANAGER] Personagem '{mem_key}' atualizado em memória")
            
        return True
        
    def _find_character_file(self, target_name_normalized: str) -> str:
        """
        Busca o arquivo JSON de um personagem pelo nome normalizado
        
        Args:
            target_name_normalized: Nome do personagem em lowercase
            
        Returns:
            Caminho completo do arquivo ou None se não encontrar
        """
        for root, _, files in os.walk(self.base_dir):
            for fname in files:
                if not fname.lower().endswith('.json'):
                    continue
                    
                candidate = os.path.join(root, fname)
                try:
                    with open(candidate, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    nome_field = data.get('nome', '')
                    if isinstance(nome_field, str) and nome_field.strip().lower() == target_name_normalized:
                        return candidate
                except Exception:
                    continue
                    
        return None
        
    def _merge_status_into_dict(self, original: dict, status: dict) -> dict:
        """
        Mescla campos de status dentro de original sem perder outros campos
        
        Regras de mesclagem:
        - Campos que são listas: estendem evitando duplicatas
        - Campos com +/- : aplica operação aritmética
        - Campos simples: sobrescreve valor
        - Campo 'nome': atualiza apenas se diferente
        
        Args:
            original: Dicionário original do personagem
            status: Dicionário com campos a atualizar
            
        Returns:
            Dicionário mesclado
        """
        result = dict(original) if original else {}
        
        for k, v in status.items():
            if k == 'nome':
                # Atualiza o nome apenas se diferente
                result['nome'] = v
                continue
                
            if isinstance(v, list):
                # Mescla listas evitando duplicatas
                existing = result.get(k, [])
                if not isinstance(existing, list):
                    result[k] = v
                else:
                    for item in v:
                        if item not in existing:
                            existing.append(item)
                    result[k] = existing
                    
            elif isinstance(v, str) and len(v) > 0 and v[0] in ('+', '-'):
                # Operador aritmético: aplica ao valor numérico existente
                try:
                    delta = int(v)
                    current = result.get(k, 0)
                    if not isinstance(current, (int, float)):
                        current = 0
                    result[k] = current + delta
                    print(f"[STATUS_MANAGER] {k}: {current} -> {result[k]} (delta={v})")
                except ValueError:
                    # Se não for número válido, sobrescreve como string
                    result[k] = v
            else:
                # Sobrescreve valor simples
                result[k] = v
                
        return result
        
    def get_character_status(self, character_name: str) -> Dict[str, Any]:
        """
        Obtém o status atual de um personagem
        
        Args:
            character_name: Nome do personagem
            
        Returns:
            Dicionário com dados do personagem ou dict vazio se não encontrar
        """
        # Busca case-insensitive
        char_lower = character_name.lower()
        for name, data in self.characters.items():
            if name.lower() == char_lower:
                return data.copy()
        return {}
