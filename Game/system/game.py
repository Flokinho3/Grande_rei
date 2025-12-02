"""
Loop principal do jogo
Responsabilidade: Gerenciar o loop de jogo, eventos de input e progressão de cenas
"""

import pygame
import sys
import re

from .sprite_command_parser import SpriteCommandParser
from .save_manager import SaveManager
from .status_manager import StatusManager
from .item_notification_manager import ItemNotificationManager


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
        
        # Managers especializados
        self.sprite_manager = renderer.sprite_manager
        self.save_manager = SaveManager()
        self.status_manager = StatusManager(self.characters)
        self.notification_manager = ItemNotificationManager(duration=180, fps=60)
        
        # Carrega estado inicial
        self._load_initial_state()

    def _load_initial_state(self):
        """Carrega o estado inicial do jogo usando SaveManager"""
        state = self.save_manager.load_game_state(self.player_data)
        self.current_scene_id = state['current_scene_id']
        self.current_text_index = state['current_text_index']

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
                # Handle save_point usando SaveManager
                if 'save_point' in scene and scene['save_point']:
                    self.save_manager.save_complete(
                        self.current_scene_id,
                        self.current_text_index,
                        self.player_data
                    )
                    
                # Handle add_item usando ItemNotificationManager
                if 'add_item' in scene:
                    item = scene['add_item']
                    self.player_data['inventario'].append(item)
                    self.notification_manager.show_notification(item)
                    
                # Aplicar status_infor usando StatusManager
                if 'status_infor' in scene and isinstance(scene['status_infor'], dict):
                    try:
                        self.status_manager.apply_status_infor(scene['status_infor'])
                    except Exception as e:
                        print(f"[GAME] ERRO ao aplicar status_infor: {e}")
                
                # Auto-pular linhas iniciais que sejam apenas comandos ou vazias
                self._auto_skip_command_lines(scene)

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
                            # Avança para próxima linha
                            self.current_text_index += 1
                            
                            # Pula linhas vazias ou só com comandos automaticamente
                            while self.current_text_index <= len(scene['texto']):
                                line = scene['texto'][self.current_text_index - 1]
                                print(f"[DEBUG] Linha atual: {line}")
                                
                                # Processa comandos de sprite
                                commands = SpriteCommandParser.parse_sprite_command(line)
                                for command, params in commands:
                                    self._process_sprite_command(command, params)
                                
                                # Remove comandos entre chaves e verifica se sobra texto visível
                                stripped = re.sub(r'\{[^}]+\}', '', line).strip()
                                
                                if stripped == '' and self.current_text_index < len(scene['texto']):
                                    # Linha vazia ou só comandos - avança automaticamente
                                    print(f"[DEBUG] Auto-pulando linha vazia/comando")
                                    self.current_text_index += 1
                                else:
                                    # Encontrou linha com texto - para
                                    break
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

            # Atualizar notificação usando ItemNotificationManager
            self.notification_manager.update()

            # Draw once per frame using current/updated buttons; display_scene will create buttons
            current_notification = self.notification_manager.get_current_notification()
            buttons = self.renderer.display_scene(
                scene, 
                self.player_name, 
                self.current_text_index, 
                self.characters, 
                self.renderer.text_processor, 
                buttons, 
                self.sprite_manager, 
                current_notification
            )

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
                    # Verifica se já existe sprite nessa posição - se sim, não faz fade
                    should_fade = not self.sprite_manager.has_sprite(position)
                    self.sprite_manager.add_sprite(
                        actual_char_name,
                        char_data['img'],
                        position,
                        expression,
                        z_index=0,
                        fade_in=should_fade
                    )
                    print(f"[GAME] Sprite adicionado: {actual_char_name} em {position} (fade={should_fade})")
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

    def _auto_skip_command_lines(self, scene: dict):
        """Pula automaticamente linhas que sejam apenas comandos ou vazias"""
        if 'texto' not in scene:
            return
        # `self.current_text_index` é 1-based (1 = primeiro elemento em texto[0])
        while 1 <= self.current_text_index <= len(scene['texto']):
            line = scene['texto'][self.current_text_index - 1]
            # Remove comandos entre chaves e verifica se sobra texto
            stripped = re.sub(r'\{[^}]+\}', '', line).strip()
            
            if stripped == '':
                # Linha vazia ou só comandos - processa e pula
                print(f"[DEBUG] Auto-pulando linha vazia/comando: {line}")
                commands = SpriteCommandParser.parse_sprite_command(line)
                for command, params in commands:
                    self._process_sprite_command(command, params)
                # Avança para a próxima linha (1-based)
                self.current_text_index += 1
                # continue loop to check following lines
            else:
                # Encontrou linha com texto - para
                break