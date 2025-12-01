import pygame
import sys

class Game:
    def __init__(self, scenes, scenes_order, characters, player_name, renderer, clock):
        self.scenes = scenes
        self.scenes_order = scenes_order
        self.characters = characters
        self.player_name = player_name
        self.renderer = renderer
        self.clock = clock
        self.current_scene_id = "1"
        self.current_text_index = 1

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

            # Process events using current button objects (from previous frame)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION and buttons:
                    mouse_pos = pygame.mouse.get_pos()
                    for button, _ in buttons:
                        button.update_hover(mouse_pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.current_text_index < len(scene['texto']):
                            self.current_text_index += 1
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

            # Draw once per frame using current/updated buttons; display_scene will create buttons
            buttons = self.renderer.display_scene(scene, self.player_name, self.current_text_index, self.characters, self.renderer.text_processor, buttons)

            # Cap frame rate

            self.clock.tick(60)