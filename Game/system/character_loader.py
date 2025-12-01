import json
import os

class CharacterLoader:
    def load_characters(self):
        characters = {}
        player_name = None
        base_dir = 'Game/data/script/Base'
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.json'):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        name = data['nome']
                        color = tuple(map(int, data['cor'].split(',')))
                        characters[name] = color
                        if 'save' in data:
                            player_name = name
        if player_name is None:
            player_name = 'Jogador'  # Default
        return characters, player_name