"""
Gerenciador de salvamento e carregamento do progresso do jogo
Responsabilidade: Persistir e recuperar o estado do jogo (cena atual, índice de texto, dados do jogador)
"""

import json
import os


class SaveManager:
    """Gerencia operações de save/load do jogo"""
    
    def __init__(self, save_dir: str = None, player_file_path: str = None):
        """
        Inicializa o gerenciador de saves
        
        Args:
            save_dir: Diretório onde os saves serão armazenados
            player_file_path: Caminho completo para o arquivo player.json
        """
        self.save_dir = save_dir or os.path.join('Game', 'data', 'save')
        self.save_file_path = os.path.join(self.save_dir, 'save.json')
        self.player_file_path = player_file_path or os.path.join('Game', 'data', 'script', 'Base', 'player.json')
        
    def load_game_state(self, player_data: dict = None) -> dict:
        """
        Carrega o estado do jogo salvo
        
        Args:
            player_data: Dados do jogador para fallback caso não exista save
            
        Returns:
            Dicionário com 'current_scene_id' e 'current_text_index'
        """
        if os.path.exists(self.save_file_path):
            try:
                with open(self.save_file_path, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                print(f"[SAVE_MANAGER] Save carregado: cena {save_data.get('current_scene_id')}")
                return {
                    'current_scene_id': save_data.get('current_scene_id', '1'),
                    'current_text_index': save_data.get('current_text_index', 1)
                }
            except Exception as e:
                print(f"[SAVE_MANAGER] ERRO ao carregar save: {e}")
                
        # Fallback: usa dados do player.json se disponível
        if player_data and 'save' in player_data:
            return {
                'current_scene_id': player_data['save'].get('Cena', '1'),
                'current_text_index': 1
            }
            
        # Default inicial
        return {
            'current_scene_id': '1',
            'current_text_index': 1
        }
        
    def save_game_state(self, scene_id: str, text_index: int) -> bool:
        """
        Salva o estado atual do jogo
        
        Args:
            scene_id: ID da cena atual
            text_index: Índice de texto atual
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        save_data = {
            'current_scene_id': scene_id,
            'current_text_index': text_index
        }
        
        try:
            os.makedirs(self.save_dir, exist_ok=True)
            with open(self.save_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)
            print(f"[SAVE_MANAGER] Jogo salvo: cena {scene_id}, linha {text_index}")
            return True
        except Exception as e:
            print(f"[SAVE_MANAGER] ERRO ao salvar jogo: {e}")
            return False
            
    def save_player_data(self, player_data: dict) -> bool:
        """
        Salva os dados do jogador (inventário, status, etc)
        
        Args:
            player_data: Dicionário com todos os dados do jogador
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            with open(self.player_file_path, 'w', encoding='utf-8') as f:
                json.dump(player_data, f, indent=4, ensure_ascii=False)
            print(f"[SAVE_MANAGER] Dados do jogador salvos")
            return True
        except Exception as e:
            print(f"[SAVE_MANAGER] ERRO ao salvar dados do jogador: {e}")
            return False
            
    def save_complete(self, scene_id: str, text_index: int, player_data: dict) -> bool:
        """
        Salva tanto o estado do jogo quanto os dados do jogador
        
        Args:
            scene_id: ID da cena atual
            text_index: Índice de texto atual
            player_data: Dados completos do jogador
            
        Returns:
            True se ambos salvaram com sucesso
        """
        state_saved = self.save_game_state(scene_id, text_index)
        player_saved = self.save_player_data(player_data)
        return state_saved and player_saved
        
    def delete_save(self) -> bool:
        """
        Remove o arquivo de save (útil para começar novo jogo)
        
        Returns:
            True se removeu com sucesso ou não existia
        """
        try:
            if os.path.exists(self.save_file_path):
                os.remove(self.save_file_path)
                print(f"[SAVE_MANAGER] Save deletado")
            return True
        except Exception as e:
            print(f"[SAVE_MANAGER] ERRO ao deletar save: {e}")
            return False
