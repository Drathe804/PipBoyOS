# system/navigation.py
import pygame
import datetime
from config import WIDTH, HEIGHT
from system.theme import active_theme

def draw_navigation(screen, font, tabs, active_tab):
    tab_width = WIDTH // len(tabs)
    tab_height = 30
    active_text_rect = None

    for i, tab in enumerate(tabs):
        tab_rect = pygame.Rect(i * tab_width, 0, tab_width, tab_height)
        text_surface = font.render(tab, True, active_theme.color)
        text_rect = text_surface.get_rect(center=tab_rect.center)
        screen.blit(text_surface, text_rect)
        
        if i == active_tab:
            active_text_rect = text_rect

    line_y = tab_height + 1
    padding = 10
    tick_width = 8 
    
    b_left = active_text_rect.left - padding 
    b_right = active_text_rect.right + padding
    b_top = active_text_rect.top + 5

    if b_left > 10:
        pygame.draw.line(screen, active_theme.color, (10, line_y), (b_left, line_y), 2)
        
    pygame.draw.lines(screen, active_theme.color, False, [(b_left, line_y), (b_left, b_top), (b_left + tick_width, b_top)], 2)
    pygame.draw.lines(screen, active_theme.color, False, [(b_right - tick_width, b_top), (b_right, b_top), (b_right, line_y)], 2)

    if b_right < WIDTH - 10:
        pygame.draw.line(screen, active_theme.color, (b_right, line_y), (WIDTH - 10, line_y), 2)

    pygame.draw.line(screen, active_theme.color, (10, HEIGHT - 35), (WIDTH - 10, HEIGHT - 35), 2) 
    
    if active_tab not in [3, 4]:
        # --- FOOTER STATS ---
        hp_text = font.render("HP 100/100", True, active_theme.color)
        screen.blit(hp_text, (20, HEIGHT - 28))
    
        ap_text = font.render("AP 50/50", True, active_theme.color)
        screen.blit(ap_text, (WIDTH - 110, HEIGHT - 28))

        # ==========================================
        # DYNAMIC LEVEL & XP BAR
        # ==========================================
        today = datetime.date.today()
        bday_month, bday_day = 8, 4
        bday_year = 2000
    
        # Calculate Age (Level)
        age = today.year - bday_year - ((today.month, today.day) < (bday_month, bday_day))
    
        # Calculate Progress (XP)
        last_bday = datetime.date(today.year if (today.month, today.day) >= (bday_month, bday_day) else today.year - 1, bday_month, bday_day)
        next_bday = datetime.date(last_bday.year + 1, bday_month, bday_day)
    
        days_passed = (today - last_bday).days
        total_days = (next_bday - last_bday).days
        progress = days_passed / total_days
    
        # Draw Level Text
        level_text = font.render(f"LEVEL {age}", True, active_theme.color)
        lvl_x = (WIDTH // 2) - 70 # Center it on the screen
        screen.blit(level_text, (lvl_x, HEIGHT - 28))
    
        # Draw the Bar Outline
        bar_x = lvl_x + level_text.get_width() + 10
        bar_y = HEIGHT - 24
        bar_width = 80
        bar_height = 8
        pygame.draw.rect(screen, active_theme.color, (bar_x, bar_y, bar_width, bar_height), 1)
    
        # Draw the Bar Fill
        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, active_theme.color, (bar_x, bar_y, fill_width, bar_height))
