# ui/stat_screen.py
import pygame
from config import BLACK, WIDTH, HEIGHT
from system.animation import TabAnimator # Import our new tool!
from system.theme import active_theme

# Create an animator specifically for the inventory screen
inv_animator = TabAnimator()

def draw_stat_tab(screen, font, sub_tabs_stat, sub_active_stat, walk_anim, current_time):

    # ==========================================
    # 1. THE SUB-MENU SPRING ANIMATION
    # ==========================================
    # This ONE line now does all the physics and drawing!
    inv_animator.draw(screen, font, sub_tabs_stat, sub_active_stat)

    # 2. UPDATE THE ANIMATION FRAME
    walk_anim.update(current_time)
    frame = walk_anim.get_frame()

    # ==========================================
    # 3. DYNAMIC CONTENT BASED ON SUB-TAB
    # ==========================================
    
    # --- STATUS TAB (Center Vault Boy & Limbs) ---
    if sub_active_stat == 0:
        if frame:
            frame_rect = frame.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 15))
            screen.blit(frame, frame_rect)
            

    # --- SPECIAL TAB (Left List, Right Vault Boy) ---
    elif sub_active_stat == 1:
        if frame:
            # Notice we changed the X coordinate to push him to the right!
            frame_rect = frame.get_rect(center=(WIDTH - 100, HEIGHT // 2 + 15))
            screen.blit(frame, frame_rect)

        # The S.P.E.C.I.A.L. Data
        special_stats = [
            ("Strength", 6),
            ("Perception", 5),
            ("Endurance", 7),
            ("Charisma", 8),
            ("Intelligence", 9),
            ("Agility", 6),
            ("Luck", 7)
        ]
        
        start_y = 80
        for i, (stat, val) in enumerate(special_stats):
            # Left align the word
            stat_text = font.render(stat, True, active_theme.color)
            screen.blit(stat_text, (30, start_y + (i * 22)))
            
            # Right align the number to a specific column
            val_text = font.render(str(val), True, active_theme.color)
            screen.blit(val_text, (180, start_y + (i * 22)))

    # --- PERKS TAB (Left List, Right Vault Boy) ---
    elif sub_active_stat == 2:
        if frame:
            frame_rect = frame.get_rect(center=(WIDTH - 100, HEIGHT // 2 + 15))
            screen.blit(frame, frame_rect)

        # Custom Perks List
        perks = [
            "Toughness", 
            "Hacker", 
            "Swole Scroll Initiate", # Future hook for your fitness app!
            "Robotics Expert"
        ]
        
        start_y = 80
        for i, perk in enumerate(perks):
            perk_text = font.render(f"> {perk}", True, active_theme.color)
            screen.blit(perk_text, (30, start_y + (i * 25)))
