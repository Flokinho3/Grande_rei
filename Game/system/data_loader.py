import json
import os
import re

class DataLoader:
    def __init__(self):
        self.current_episode = 1
        self.current_chapter = 1
        
    def load_scenes(self, path):
        """Carrega cenas de um episódio específico"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extrai número do episódio do caminho
        ep_match = re.search(r'EP_(\d+)', path)
        if ep_match:
            self.current_episode = int(ep_match.group(1))
        
        # Extrai número do capítulo do caminho
        cap_match = re.search(r'Cap_(\d+)', path)
        if cap_match:
            self.current_chapter = int(cap_match.group(1))
            
        # Identifica a chave do episódio
        ep_key = f'EP_{self.current_episode}'
        if ep_key not in data:
            raise ValueError(f"Episódio '{ep_key}' não encontrado em {path}")
            
        scenes = {}
        order = []
        for scene in data[ep_key]:
            scenes[scene['id']] = scene
            order.append(scene['id'])
        return scenes, order
    
    def get_next_episode_path(self):
        """Retorna o caminho do próximo episódio"""
        next_ep = self.current_episode + 1
        base_path = f'Game/data/script/Cap/Cap_{self.current_chapter}'
        next_path = os.path.join(base_path, f'EP_{next_ep}.json')
        
        if os.path.exists(next_path):
            return next_path
        return None
    
    def load_next_episode(self):
        """Carrega o próximo episódio se existir"""
        next_path = self.get_next_episode_path()
        if next_path:
            print(f"[DATA_LOADER] Carregando próximo episódio: {next_path}")
            return self.load_scenes(next_path)
        return None, None