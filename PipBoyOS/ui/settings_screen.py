# ui/settings_screen.py
import pygame
from config import BLACK, WIDTH, HEIGHT
from system.animation import TabAnimator 

settings_animator = TabAnimator()

def draw_settings_tab(screen, font, sub_tabs, sub_active, item_index, active_theme, rgb_mode, current_time):
    THEME_COLOR = active_theme.color
    
    # Draw the DATA sub-tab headers at the top
    settings_animator.draw(screen, font, sub_tabs, sub_active)
    
    # 6 Total Items in the list!
    items = ["THEME: DEFAULT", "THEME: BARBIE", "THEME: CUSTOM", "DISPLAY: RED", "DISPLAY: GREEN", "DISPLAY: BLUE"]
    selected_i = item_index % len(items) if len(items) > 0 else 0

    start_y = 80
    for i, item in enumerate(items):
        y_pos = start_y + (i * 35)
        
        # --- 1. THE HIGHLIGHT BOX ---
        if i == selected_i:
            # If the RGB dial is locked, flash the highlight!
            if rgb_mode and i >= 3 and current_time % 1000 < 500:
                pygame.draw.rect(screen, THEME_COLOR, (15, y_pos - 2, 160, 22), 2)
                text = font.render(item, True, THEME_COLOR)
            else:
                pygame.draw.rect(screen, THEME_COLOR, (15, y_pos - 2, 160, 22))
                text = font.render(item, True, BLACK)
        else:
            text = font.render(item, True, THEME_COLOR)
        
        screen.blit(text, (20, y_pos))

        # --- 2. THE DYNAMIC READOUTS ---
        if i < 3: 
            # Show which theme is currently active
            theme_mapping = ["DEFAULT", "BARBIE", "CUSTOM"]
            if active_theme.mode == theme_mapping[i]:
                active_txt = font.render("[ACTIVE]", True, BLACK if i == selected_i else THEME_COLOR)
                screen.blit(active_txt, (185, y_pos))
                
        else: 
            # Draw the visual sliders for the colors!
            color_idx = i - 3 # Math to map list index 3,4,5 to RGB index 0,1,2
            val = active_theme.custom_rgb[color_idx]
            
            # Draw the empty slider box
            pygame.draw.rect(screen, THEME_COLOR, (185, y_pos + 2, 220, 12), 1)
            
            # Fill the slider box based on the 0-255 value
            if val > 0:
                fill_width = int((val / 255.0) * 220)
                pygame.draw.rect(screen, THEME_COLOR, (185, y_pos + 2, fill_width, 12))
            
            # Print the exact number
            val_txt = font.render(str(val), True, THEME_COLOR)
            screen.blit(val_txt, (420, y_pos - 2))
