import json
import os

class CharacterLoader:
    def load_characters(self):
        characters = {}
        player_name = None
        player_data = None
        base_dir = 'Game/data/script/Base'
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                # Pula diretórios de configuração
                dirs[:] = [d for d in dirs if d != 'config']
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        name = data['nome']
                        color = tuple(map(int, data['cor'].split(',')))
                        img = data.get('img')
                        print(f"[DEBUG LOADER] Carregando {file}: nome={name}, img={img}")
                        # Carrega todos os dados do personagem, não apenas color e img
                        characters[name] = data.copy()
                        characters[name]['color'] = color  # Substitui a string 'cor' pela tupla
                        if 'save' in data:
                            player_name = name
                            player_data = data
        if player_name is None:
            player_name = 'Jogador'  # Default
            player_data = {'nome': player_name, 'cor': '255,255,255', 'vida': 100, 'forca': 10, 'inteligencia': 10, 'agilidade': 10, 'inventario': [], 'estatus': []}
        return characters, player_name, player_data