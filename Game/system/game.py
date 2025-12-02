
import pygame
import sys
import json
import os
import re

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
        self.current_sprite = None
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
                self.current_sprite = None  # Reset sprite on scene change

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
                            self.current_text_index += 1
                            # Parse the new line for sprite command
                            line = scene['texto'][self.current_text_index - 1]
                            print(f"[DEBUG] Linha atual: {line}")
                            match = re.search(r'\{img_esquerda:([^}]+)\}', line)
                            if match:
                                # Update sprite to the new character
                                self.current_sprite = match.group(1)
                                print(f"[DEBUG] Sprite detectado: {self.current_sprite}")
                            # Check for sprite clear command
                            if '{img_esquerda:}' in line or '{img_clear}' in line:
                                self.current_sprite = None
                                print(f"[DEBUG] Sprite removido")
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
            buttons = self.renderer.display_scene(scene, self.player_name, self.current_text_index, self.characters, self.renderer.text_processor, buttons, self.current_sprite, self.item_notification)

            # Cap frame rate

            self.clock.tick(60)