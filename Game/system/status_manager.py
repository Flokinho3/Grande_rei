"""
Gerenciador de status de personagens
Responsabilidade: Aplicar e persistir mudanças nos dados dos personagens (status_infor)
"""

import json
import os
from typing import Dict, Any, Optional


class StatusManager:
    """Gerencia atualizações de status dos personagens"""
    
    def __init__(self, characters: Dict[str, Dict], base_dir: Optional[str] = None):
        """
        Inicializa o gerenciador de status
        
        Args:
            characters: Dicionário com dados dos personagens em memória
            base_dir: Diretório base onde estão os arquivos JSON dos personagens
        """
        self.characters = characters
        self.base_dir = base_dir or os.path.join('Game', 'data', 'script', 'Base')
        self.applied_status_ids = []  # Lista para manter histórico de IDs aplicados
        
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
        # Verifica se tem ID e se já foi aplicado (verifica no arquivo do personagem)
        status_id = status.get('ID')
        if status_id:
            # Busca o arquivo do personagem para verificar IDs já aplicados
            target_name = status.get('nome')
            if target_name:
                target_norm = target_name.strip().lower()
                file_path = self._find_character_file(target_norm)
                
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_data = json.load(f)
                        
                        # Verifica se o ID já foi aplicado (campo ID deve ser lista no arquivo)
                        applied_ids = file_data.get('ID', [])
                        if isinstance(applied_ids, list) and status_id in applied_ids:
                            print(f"[STATUS_MANAGER] Status ID '{status_id}' já foi aplicado ao personagem '{target_name}'. Ignorando.")
                            return False
                    except Exception as e:
                        print(f"[STATUS_MANAGER] ERRO ao verificar IDs aplicados: {e}")
                        # Continua normalmente se não conseguir verificar
        
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
        
        # Aplica limites de configuração se existir
        config = self._load_character_config(target_name)
        if config:
            for attr, limits in config.items():
                if attr in merged_data:
                    min_val = limits.get('min', -float('inf'))
                    max_val = limits.get('max', float('inf'))
                    current_val = merged_data[attr]
                    if isinstance(current_val, (int, float)):
                        clamped_val = max(min_val, min(current_val, max_val))
                        if clamped_val != current_val:
                            print(f"[STATUS_MANAGER] {attr}: {current_val} clamped to {clamped_val} (min={min_val}, max={max_val})")
                        merged_data[attr] = clamped_val
        
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
        
        # Adiciona ID ao histórico do personagem após aplicação bem-sucedida
        if status_id:
            # Busca o arquivo do personagem para adicionar o ID
            target_name = status.get('nome')
            if target_name:
                target_norm = target_name.strip().lower()
                file_path = self._find_character_file(target_norm)
                
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_data = json.load(f)
                        
                        # Adiciona ID à lista de IDs aplicados
                        applied_ids = file_data.get('ID', [])
                        if not isinstance(applied_ids, list):
                            applied_ids = []
                        
                        if status_id not in applied_ids:
                            applied_ids.append(status_id)
                            file_data['ID'] = applied_ids
                            
                            # Salva de volta no arquivo
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(file_data, f, indent=4, ensure_ascii=False)
                            
                            print(f"[STATUS_MANAGER] ID '{status_id}' registrado no personagem '{target_name}'")
                    except Exception as e:
                        print(f"[STATUS_MANAGER] ERRO ao registrar ID no personagem: {e}")
            
        return True
        
    def _load_character_config(self, character_name: str) -> Optional[Dict[str, Dict[str, int]]]:
        """
        Carrega a configuração de limites para um personagem
        
        Args:
            character_name: Nome do personagem
            
        Returns:
            Dicionário com limites de atributos ou None se não encontrar
        """
        config_path = os.path.join(self.base_dir, 'NPC', 'config', f'{character_name.lower()}_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[STATUS_MANAGER] ERRO ao carregar config do personagem '{character_name}': {e}")
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
                
            if k == 'ID':
                # Campo ID é gerenciado separadamente - não sobrescrever
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
