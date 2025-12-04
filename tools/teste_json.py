import json
import os
import sys
from typing import Dict, List

# Add the project root to sys.path so we can import Game
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from Game.system.condition_evaluator import ConditionEvaluator  # usa teu avaliador

BASE_PATH = "Game/data/script/Cap/Cap_1"

class JsonValidator:
    def __init__(self, characters: Dict[str, Dict], player_data: Dict):
        self.characters = characters
        self.player_data = player_data
        self.evaluator = ConditionEvaluator(characters, player_data)

    def validate_episode_file(self, filename: str):
        path = os.path.join(BASE_PATH, filename)

        if not os.path.exists(path):
            print(f"[ERRO] Arquivo não encontrado: {path}")
            return
        
        # 1 — Carregar JSON
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"[ERRO] JSON inválido em {filename}: {e}")
            return
        
        print(f"\n--- Validando {filename} ---")

        # 2 — Validar estrura básica
        for ep_key, scenes in data.items():
            if not isinstance(scenes, list):
                print(f"[ERRO] {ep_key} deveria ser uma lista.")
                continue
            
            for scene in scenes:
                self._validate_scene(scene)

        print(f"--- Fim da validação de {filename} ---\n")

    def _validate_scene(self, scene: Dict):
        if "id" not in scene:
            print("[ERRO] Cena sem ID!")
            return
        
        sid = scene["id"]

        # 3 — validar condições da cena (se existirem)
        if "condicao" in scene:
            for cond in scene["condicao"]:
                self._validate_condition(cond, sid)

        # 4 — validar opções
        if "opcoes" in scene:
            for opt in scene["opcoes"]:
                if "texto" not in opt:
                    print(f"[CENA {sid}] [ERRO] Opção sem texto!")
                if "proximo_id" not in opt:
                    print(f"[CENA {sid}] [ERRO] Opção sem proximo_id!")
                
                if "condicao" in opt:
                    self._validate_condition(opt["condicao"], sid, is_option=True)

    def _validate_condition(self, cond: Dict, scene_id: str, is_option=False):
        tipo = "OPÇÃO" if is_option else "CENA"
        
        # Tenta avaliar a condição com o sistema real
        try:
            result = self.evaluator._evaluate_condition(cond)
        except Exception as e:
            print(f"[{tipo} {scene_id}] [ERRO] Falha ao avaliar condição: {cond}")
            print("         ", e)
            return
        
        # Validar campos estranhos
        for key in cond:
            if key not in {"proximo_id", "dev"}:
                if "_" not in key:
                    print(f"[{tipo} {scene_id}] [ALERTA] Condição '{key}' parece incompleta (faltando yuno_?)")

        # Debugar resultado
        print(f"[{tipo} {scene_id}] Condição OK: {cond}" if result else f"[{tipo} {scene_id}] Condição válida mas NÃO corresponde ao estado atual")



# -------------------------
# COMO USAR
# -------------------------

# Exemplo de dicionário de personagens (troca pelo teu real)
characters = {
    "yuno": {
        "humor": "Triste",
        "afeto": -2
    }
}

player_data = {
    "nome": "Jogador"
}

validator = JsonValidator(characters, player_data)

# Validar EP_1 e EP_2
validator.validate_episode_file("EP_1.json")
validator.validate_episode_file("EP_2.json")
