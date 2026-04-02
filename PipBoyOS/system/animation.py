# system/animation.py
import pygame
import os
from config import GREEN, BLACK


class SpriteAnimation:
    # Added a 'scale' parameter here (1.0 means 100%, 0.5 means 50%)
    def __init__(self, folder_path, frame_rate=100, scale=1.0):
        self.frames = []
        self.frame_rate = frame_rate
        self.last_update = 0
        self.current_frame = 0

        try:
            valid_files = [f for f in os.listdir(folder_path) if f.endswith('.gif')]
            valid_files.sort() 
            
            for file_name in valid_files:
                path = os.path.join(folder_path, file_name)
                img = pygame.image.load(path).convert_alpha()
                
                # --- NEW SCALING LOGIC ---
                if scale != 1.0:
                    new_width = int(img.get_width() * scale)
                    new_height = int(img.get_height() * scale)
                    # Smoothscale looks a bit better when shrinking pixel art!
                    img = pygame.transform.smoothscale(img, (new_width, new_height))
                    
                self.frames.append(img)
        except Exception as e:
            print(f"Error loading animation from {folder_path}: {e}")

    def update(self, current_time):
        if self.frames and current_time - self.last_update > self.frame_rate:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def get_frame(self):
        if self.frames:
            return self.frames[self.current_frame]
        return None

class TabAnimator:
    def __init__(self, start_x=20):
        # Every menu gets its own independent spring variables
        self.anim_x = start_x
        self.anim_w = 50
        self.anim_v_x = 0
        self.anim_v_w = 0

    def draw(self, screen, font, tabs_list, active_index, start_x=20, start_y=45):
        target_x = start_x
        target_w = 0
        current_x = start_x
        
        # 1. Calculate targets
        for i, sub in enumerate(tabs_list):
            text_w = font.size(sub)[0]
            box_w = text_w + 12 
            
            if i == active_index:
                target_x = current_x
                target_w = box_w
                
            current_x += box_w + 10 

        # 2. Apply Spring Physics
        tension = 0.45    
        dampening = 0.40  
        
        self.anim_v_x = (self.anim_v_x + ((target_x - self.anim_x) * tension)) * dampening
        self.anim_x += self.anim_v_x
        
        self.anim_v_w = (self.anim_v_w + ((target_w - self.anim_w) * tension)) * dampening
        self.anim_w += self.anim_v_w

        # 3. Draw Box
        highlight_rect = pygame.Rect(self.anim_x, start_y, self.anim_w, 20)
        pygame.draw.rect(screen, GREEN, highlight_rect)
        
        # 4. Draw Text
        current_x = start_x
        for i, sub in enumerate(tabs_list):
            color = BLACK if i == active_index else GREEN
            sub_text = font.render(sub, True, color)
            
            screen.blit(sub_text, (current_x + 6, start_y + 2))
            
            text_w = font.size(sub)[0]
            box_w = text_w + 12
            current_x += box_w + 10