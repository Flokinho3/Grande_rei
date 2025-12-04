import json
import os
import re

class DataLoader:
    def __init__(self):
        self.current_episode = 1
        self.current_chapter = 1
        self.room_stack = []  # Stack para rastrear salas visitadas
        
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
    
    def load_room(self, room_name):
        """Carrega cenas de um cômodo/sala específico"""
        base_path = f'Game/data/script/Cap/Cap_{self.current_chapter}/Comodos'
        room_path = os.path.join(base_path, f'{room_name}.json')
        
        if not os.path.exists(room_path):
            print(f"[DATA_LOADER] ERRO: Cômodo '{room_name}' não encontrado em {room_path}")
            return None, None
            
        try:
            with open(room_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Identifica a chave do cômodo
            if room_name not in data:
                print(f"[DATA_LOADER] ERRO: Chave '{room_name}' não encontrada no arquivo")
                return None, None
                
            scenes = {}
            order = []
            for scene in data[room_name]:
                scenes[scene['id']] = scene
                order.append(scene['id'])
            
            print(f"[DATA_LOADER] Cômodo '{room_name}' carregado com {len(scenes)} cenas")
            return scenes, order
            
        except Exception as e:
            print(f"[DATA_LOADER] ERRO ao carregar cômodo: {e}")
            return None, None
    
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