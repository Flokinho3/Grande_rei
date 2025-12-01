import json
import os

class DataLoader:
    def load_scenes(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        scenes = {}
        order = []
        for scene in data['EP_1']:
            scenes[scene['id']] = scene
            order.append(scene['id'])
        return scenes, order