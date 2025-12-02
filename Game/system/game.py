
import pygame
import sys
import json
import os
import re
from .sprite_manager import SpriteCommandParser

class Game:
    def __init__(self, scenes, scenes_order, characters, player_name, player_data, renderer, clock):
        self.scenes = scenes
        self.scenes_order = scenes_order
        self.characters = characters
        print(f"[DEBUG INIT] Personagens carregados: {list(characters.keys())}")
        for name, data in characters.items():
            print(f"[DEBUG INIT] {name}: img={data.get('img', 'N/A')}")
        self.player_name = player_name
        self.player_data = player_data
        self.renderer = renderer
        self.clock = clock
        self.current_scene_id = "1"
        self.current_text_index = 1
        self.inventory = self.player_data.get('inventario', [])
        # Novo sistema de sprites
        self.sprite_manager = renderer.sprite_manager
        # Sistema de notificação de itens
        self.item_notification = None
        self.item_notification_timer = 0
        self.item_notification_duration = 180  # 3 segundos a 60 FPS
        self.load_game()

    def save_player_data(self):
        player_path = os.path.join('Game', 'data', 'script', 'Base', 'player.json')
        with open(player_path, 'w', encoding='utf-8') as f:
            json.dump(self.player_data, f, indent=4, ensure_ascii=False)

    def load_game(self):
        save_path = os.path.join('Game', 'data', 'save', 'save.json')
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            self.current_scene_id = save_data.get('current_scene_id', '1')
            self.current_text_index = save_data.get('current_text_index', 1)
        else:
            # Use initial save from player_data if available
            if 'save' in self.player_data:
                self.current_scene_id = self.player_data['save'].get('Cena', '1')
                self.current_text_index = 1

    def save_game(self):
        # Save scene progress
        save_data = {
            'current_scene_id': self.current_scene_id,
            'current_text_index': self.current_text_index
        }
        save_path = os.path.join('Game', 'data', 'save', 'save.json')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=4)
        # Save player data
        self.save_player_data()

    def run(self):
        running = True
        buttons = None
        last_scene_id = None
        while running:
            scene = self.scenes.get(self.current_scene_id)
            if not scene:
                print("Scene not found:", self.current_scene_id)
                running = False
                continue
            # Reset buttons when scene changes
            if last_scene_id != self.current_scene_id:
                buttons = None
                last_scene_id = self.current_scene_id
                # Handle save_point and add_item when entering scene
                if 'save_point' in scene and scene['save_point']:
                    self.save_game()
                if 'add_item' in scene:
                    item = scene['add_item']
                    self.player_data['inventario'].append(item)
                    # Ativar notificação de item
                    self.item_notification = item
                    self.item_notification_timer = self.item_notification_duration
                # Aplicar status_infor se presente na cena
                if 'status_infor' in scene and isinstance(scene['status_infor'], dict):
                    try:
                        self._apply_status_infor(scene['status_infor'])
                    except Exception as e:
                        print(f"[GAME] ERRO ao aplicar status_infor: {e}")

            # Process events using current button objects (from previous frame)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION and buttons:
                    mouse_pos = pygame.mouse.get_pos()
                    for button, _ in buttons:
                        button.update_hover(mouse_pos)
                elif event.type == pygame.KEYDOWN:
                    # "esc" para encerrar o jogo
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.current_text_index < len(scene['texto']):
                            # Olha a próxima linha (sem incrementar ainda)
                            next_line = scene['texto'][self.current_text_index]
                            print(f"[DEBUG] Próxima linha (peek): {next_line}")
                            # Verifica se, ao remover tokens entre chaves, sobra texto visível
                            # Se sobrar apenas espaço em branco, trataremos como linha de comando apenas
                            stripped = re.sub(r'\{[^}]+\}', '', next_line).strip()
                            only_commands = (stripped == '')

                            if only_commands:
                                # Processar comandos da linha (não mostra texto: apenas executa comandos)
                                commands = SpriteCommandParser.parse_sprite_command(next_line)
                                for command, params in commands:
                                    self._process_sprite_command(command, params)
                                # Consome a linha de comando e aguarda próxima tecla para avançar ao diálogo
                                self.current_text_index += 1
                            else:
                                # Linha com texto (pode conter comandos inline). Avança normalmente e processa comandos
                                self.current_text_index += 1
                                line = scene['texto'][self.current_text_index - 1]
                                print(f"[DEBUG] Linha atual: {line}")
                                commands = SpriteCommandParser.parse_sprite_command(line)
                                for command, params in commands:
                                    self._process_sprite_command(command, params)
                        else:
                            # If scene has explicit next, use it
                            if not buttons and 'x_x' in scene:
                                self.current_scene_id = scene['x_x']
                                self.current_text_index = 1
                            else:
                                # If no options, auto-advance to the next scene in file order
                                if not buttons:
                                    try:
                                        idx = self.scenes_order.index(self.current_scene_id)
                                        if idx + 1 < len(self.scenes_order):
                                            self.current_scene_id = self.scenes_order[idx + 1]
                                            self.current_text_index = 1
                                    except ValueError:
                                        pass
                elif event.type == pygame.MOUSEBUTTONDOWN and buttons:
                    mouse_pos = pygame.mouse.get_pos()
                    for button, next_scene in buttons:
                        if button.is_clicked(mouse_pos, event):
                            self.current_scene_id = next_scene
                            self.current_text_index = 1
                            # when scene changes, we'll reset buttons next loop
                            break

            # Atualizar timer de notificação
            if self.item_notification_timer > 0:
                self.item_notification_timer -= 1
                if self.item_notification_timer <= 0:
                    self.item_notification = None

            # Draw once per frame using current/updated buttons; display_scene will create buttons
            buttons = self.renderer.display_scene(scene, self.player_name, self.current_text_index, self.characters, self.renderer.text_processor, buttons, self.sprite_manager, self.item_notification)

            # Cap frame rate
            self.clock.tick(60)

    def _process_sprite_command(self, command: str, params: dict):
        """Processa comandos de sprite"""
        if command == 'add':
            char_name = params['character']
            position = params['position']
            expression = params.get('expression', '')
            
            # Normalizar nome do personagem (case-insensitive)
            actual_char_name = None
            char_lower = char_name.lower()
            for name in self.characters.keys():
                if name.lower() == char_lower:
                    actual_char_name = name
                    break
                    
            if actual_char_name and actual_char_name in self.characters:
                char_data = self.characters[actual_char_name]
                if 'img' in char_data and char_data['img']:
                    self.sprite_manager.add_sprite(
                        actual_char_name,
                        char_data['img'],
                        position,
                        expression,
                        z_index=0,
                        fade_in=True
                    )
                    print(f"[GAME] Sprite adicionado: {actual_char_name} em {position}")
                else:
                    print(f"[GAME] AVISO: Personagem {actual_char_name} não tem imagem")
            else:
                print(f"[GAME] AVISO: Personagem '{char_name}' não encontrado")
                
        elif command == 'remove':
            position = params['position']
            self.sprite_manager.remove_sprite(position, fade_out=True)
            print(f"[GAME] Sprite removido de: {position}")
            
        elif command == 'clear_all':
            self.sprite_manager.remove_all_sprites(fade_out=True)
            print(f"[GAME] Todos sprites removidos")
            
        elif command == 'expression':
            position = params['position']
            expression = params['expression']
            if self.sprite_manager.change_expression(position, expression):
                print(f"[GAME] Expressão alterada em {position}: {expression}")
            else:
                print(f"[GAME] AVISO: Não foi possível alterar expressão em {position}")

    def _apply_status_infor(self, status: dict):
        """Procura o personagem pelo nome e mescla os campos do status no arquivo JSON correspondente

        Regras de mesclagem:
        - Campos que são listas serão estendidos (evitando duplicatas)
        - Campos simples (string/number) serão sobrescritos pelo novo valor
        - O campo 'nome' é usado apenas para localizar o personagem
        """
        target_name = status.get('nome')
        if not target_name:
            raise ValueError('status_infor não contém campo "nome"')

        # Normaliza para comparação
        target_norm = target_name.strip().lower()

        # Primeiro, tenta encontrar no dicionário em memória
        matched_key = None
        for name in self.characters.keys():
            if name.strip().lower() == target_norm:
                matched_key = name
                break

        file_path = None
        # Se não encontrar em memória (ou mesmo se encontrar, buscamos o arquivo para persistir)
        base_dir = os.path.join('Game', 'data', 'script', 'Base')
        for root, _, files in os.walk(base_dir):
            for fname in files:
                if not fname.lower().endswith('.json'):
                    continue
                candidate = os.path.join(root, fname)
                try:
                    with open(candidate, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    nome_field = data.get('nome', '')
                    if isinstance(nome_field, str) and nome_field.strip().lower() == target_norm:
                        file_path = candidate
                        file_data = data
                        break
                except Exception:
                    continue
            if file_path:
                break

        if not file_path:
            print(f"[GAME] AVISO: Arquivo JSON do personagem '{target_name}' não encontrado em {base_dir}")
            # Ainda assim atualiza memória se existir chave correspondente
            if matched_key:
                merged = self._merge_status_into_dict(self.characters[matched_key], status)
                self.characters[matched_key] = merged
                print(f"[GAME] Personagem '{matched_key}' atualizado em memória (arquivo não encontrado)")
            return

        # Mescla os dados no objeto carregado
        merged_data = self._merge_status_into_dict(file_data, status)

        # Salva de volta no arquivo
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=4, ensure_ascii=False)
            print(f"[GAME] Arquivo do personagem atualizado: {file_path}")
        except Exception as e:
            print(f"[GAME] ERRO ao salvar arquivo do personagem: {e}")

        # Atualiza o dicionário em memória também
        # Se não havia chave em memória, usa o nome do arquivo (campo 'nome' do merged)
        mem_key = matched_key or merged_data.get('nome')
        if mem_key:
            self.characters[mem_key] = merged_data

    def _merge_status_into_dict(self, original: dict, status: dict) -> dict:
        """Mescla campos de `status` dentro de `original` sem perder outros campos"""
        result = dict(original) if original else {}
        for k, v in status.items():
            if k == 'nome':
                # atualiza o nome apenas se diferente
                result['nome'] = v
                continue
            if isinstance(v, list):
                existing = result.get(k, [])
                if not isinstance(existing, list):
                    result[k] = v
                else:
                    # Extende evitando duplicatas mantendo ordem
                    for item in v:
                        if item not in existing:
                            existing.append(item)
                    result[k] = existing
            else:
                # sobrescreve valor simples
                result[k] = v
        return result