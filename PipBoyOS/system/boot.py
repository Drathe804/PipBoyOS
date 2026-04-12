# system/boot.py
import pygame
from config import boot_lines, WIDTH, HEIGHT
from system.theme import active_theme
from system.animation import SpriteAnimation

class BootManager:
    def __init__(self):
        self.current_line = 0
        self.current_char = 0
        self.typing_speed = 30  
        self.last_update_time = pygame.time.get_ticks()
        self.scroll_y = 0        
        self.logo_alpha = 0      
        self.logo_timer = 0  
        self.state = "BOOT_TEXT"
        
        # Load the thumbs up animation
        self.thumbs_anim = SpriteAnimation("assets/boot-success", frame_rate=100, scale=0.4)

    def update_and_draw(self, screen, font, large_font, current_time):
        
        # ... [KEEP YOUR EXISTING BOOT_TEXT AND SCROLL_UP LOGIC HERE] ...
        if self.state == "BOOT_TEXT":
            if current_time - self.last_update_time > self.typing_speed:
                if self.current_line < len(boot_lines):
                    if self.current_char < len(boot_lines[self.current_line]):
                        self.current_char += 1
                        self.last_update_time = current_time
                    else:
                        self.current_line += 1
                        self.current_char = 0
                        self.last_update_time = current_time + 500 
                else:
                    pygame.time.delay(1000) 
                    self.state = "SCROLL_UP"

        elif self.state == "SCROLL_UP":
            self.scroll_y -= 4 
            if self.scroll_y < -250: 
                self.state = "FADE_LOGO"

        if self.state in ["BOOT_TEXT", "SCROLL_UP"]:
            for i in range(self.current_line):
                text_surface = font.render(boot_lines[i], True, active_theme.color)
                screen.blit(text_surface, (10, 10 + (i * 25) + self.scroll_y))

            if self.current_line < len(boot_lines):
                text_to_render = boot_lines[self.current_line][:self.current_char]
                if current_time % 600 < 300: 
                    text_to_render += "_"
                text_surface = font.render(text_to_render, True, active_theme.color)
                screen.blit(text_surface, (10, 10 + (self.current_line * 25) + self.scroll_y))

        # --- UPDATED FADE_LOGO SECTIONS ---
        elif self.state == "FADE_LOGO" or self.state == "FADE_OUT_LOGO":
            
            # 1. Update and get the current frame of the animation
            self.thumbs_anim.update(current_time)
            frame = self.thumbs_anim.get_frame()
            
            if frame:
                # We copy the frame so we don't permanently alter the original image's alpha
                current_img = frame.copy()
                current_img.set_alpha(self.logo_alpha)
                img_rect = current_img.get_rect(center=(WIDTH/2, HEIGHT/2 - 20))
                screen.blit(current_img, img_rect)

            # 2. Draw the "Success!" text underneath it
            success_text = font.render("Success!", True, active_theme.color)
            success_text.set_alpha(self.logo_alpha)
            text_rect = success_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 60))
            screen.blit(success_text, text_rect)

            # 3. Handle the fading logic
            if self.state == "FADE_LOGO":
                if self.logo_alpha < 255:
                    self.logo_alpha += 5
                else:
                    if self.logo_timer == 0:
                        self.logo_timer = current_time
                    elif current_time - self.logo_timer > 2000:
                        self.state = "FADE_OUT_LOGO" 
                        
            elif self.state == "FADE_OUT_LOGO":
                if self.logo_alpha > 0:
                    self.logo_alpha -= 5
                else:
                    self.state = "DONE" 
        
        return self.state
