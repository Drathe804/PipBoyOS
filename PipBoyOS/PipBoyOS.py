# PipBoyOS.py
import pygame
import sys
import random
from config import *
from crt import CRTFilter
from system.boot import BootManager
from system.navigation import draw_navigation
from ui.stat_screen import draw_stat_tab
from system.animation import SpriteAnimation
from ui.inventory_screen import draw_inventory_tab
from ui.data_screen import draw_data_tab
from ui.map_screen import draw_map_tab
from ui.radio_screen import draw_radio_tab
from ui.map_screen import draw_map_tab, reset_map_cursor
from system.hardware_controls import PipBoyHardware

# --- 1. SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pip-Boy OS")

font = pygame.font.Font("fallout.ttf", 14) 
large_font = pygame.font.Font("fallout.ttf", 48) 

crt_filter = CRTFilter()
boot_manager = BootManager()

# Start listening to the GPIO pins in the background!
hardware_listener = PipBoyHardware()

walk_anim = SpriteAnimation("assets/idle-walking", frame_rate=100, scale=0.5) # Adjust frame_rate to make him walk faster/slower

current_state = "BOOTING" 
running = True

glitch_timer = 0
roll_speed = 0
power_anim_timer = 0

active_tab = 0
sub_active_stat = 0
sub_active_inv = 0
sub_active_data = 0
sub_active_map = 0
sub_active_radio = 0
item_index = 0
quitting_completely = False

active_game = None

# --- 2. MAIN LOOP ---
while running:
    current_time = pygame.time.get_ticks()
    
    # Grab all events and key states ONCE per frame
    events = pygame.event.get()
    keys = pygame.key.get_pressed()


    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # --- NEW: THE HARD QUIT BUTTON (F12) ---
            if event.key == pygame.K_F12:
                current_state = "POWERING_OFF"
                power_anim_timer = 40 
                quitting_completely = True # Tell it to close when the animation finishes!

            # --- THE SLEEP BUTTON (P) ---
            elif event.key == pygame.K_p:
                if current_state in ["MAIN_MENU", "BOOTING"]:
                    current_state = "POWERING_OFF"
                    power_anim_timer = 40 
                    quitting_completely = False # Just go to sleep normally
                elif current_state == "POWERED_OFF":
                    boot_manager.__init__() 
                    current_state = "BOOTING" 

            
            # --- EXISTING MAIN MENU CONTROLS ---
            elif current_state == "MAIN_MENU": 
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    item_index = 0
                    reset_map_cursor()
                
                # --- W & S: List Scrolling ---
                if event.key == pygame.K_s:
                    item_index += 1
                elif event.key == pygame.K_w:
                    item_index -= 1

                # --- LEFT & RIGHT: Main Tabs ---
                if event.key == pygame.K_RIGHT:
                    active_tab = (active_tab + 1) % len(tabs)
                    glitch_timer = 6 
                    # Pick a random roll speed! 0 means no roll.
                    roll_speed = random.choice([0, 0, 40, -40, 60, -60]) 
                    if active_tab == 3: 
                        reset_map_cursor()
                        
                elif event.key == pygame.K_LEFT:
                    active_tab = (active_tab - 1) % len(tabs)
                    glitch_timer = 6 
                    roll_speed = random.choice([0, 0, 40, -40, 60, -60]) 
                    if active_tab == 3: 
                        reset_map_cursor()
                
                elif active_tab == 0: # We are on STAT
                    if event.key == pygame.K_DOWN:
                        sub_active_stat = (sub_active_stat + 1) % len(sub_tabs_stat)
                    elif event.key == pygame.K_UP:
                        sub_active_stat = (sub_active_stat - 1) % len(sub_tabs_stat)
                        
                elif active_tab == 1: # We are on INV
                    if event.key == pygame.K_DOWN:
                        sub_active_inv = (sub_active_inv + 1) % len(sub_tabs_inv)
                        item_index = 0 # Reset scrolling when switching sub-tabs
                    elif event.key == pygame.K_UP:
                        sub_active_inv = (sub_active_inv - 1) % len(sub_tabs_inv)
                        item_index = 0
                        
                    # --- THE HOLOTAPE LAUNCHER ---
                    elif event.key == pygame.K_RETURN: # The ENTER key
                        from ui.inventory_screen import get_selected_inventory_item
                        
                        selected_item = get_selected_inventory_item(sub_active_inv, item_index)
                        
                        if selected_item and "game" in selected_item:
                            game_id = selected_item["game"]
                            
                            if game_id == "AtomicCommand":
                                from games.atomic_command import AtomicCommand
                                active_game = AtomicCommand()
                                current_state = "PLAYING_HOLOTAPE"

                            elif game_id == "RedMenace":
                                from games.red_menace import RedMenace
                                active_game = RedMenace()
                                current_state = "PLAYING_HOLOTAPE"
                                
                            # We will add RedMenace, Pipfall, etc., here later!

                        
                elif active_tab == 2: # We are on DATA
                    if event.key == pygame.K_DOWN:
                        sub_active_data = (sub_active_data + 1) % len(sub_tabs_data)
                    elif event.key == pygame.K_UP:
                        sub_active_data = (sub_active_data - 1) % len(sub_tabs_data)

                elif active_tab == 3: # We are on MAP
                    if event.key == pygame.K_DOWN:
                        sub_active_map = (sub_active_map + 1) % len(sub_tabs_map)
                    elif event.key == pygame.K_UP:
                        sub_active_map = (sub_active_map - 1) % len(sub_tabs_map)

                elif active_tab == 4: # We are on RADIO
                    if event.key == pygame.K_DOWN:
                        sub_active_radio = (sub_active_radio + 1) % len(sub_tabs_radio)
                    elif event.key == pygame.K_UP:
                        sub_active_radio = (sub_active_radio - 1) % len(sub_tabs_radio)

            # --- NEW: GUARANTEED HOLOTAPE EXIT ---
            elif current_state == "PLAYING_HOLOTAPE":
                if event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                    active_game = None
                    current_state = "MAIN_MENU"

    screen.fill(BLACK) 

    # --- 3. STATE MACHINE ---
    if current_state == "BOOTING":
        # Let the BootManager handle everything, just ask it for its status
        status = boot_manager.update_and_draw(screen, font, large_font, current_time)
        if status == "DONE":
            current_state = "MAIN_MENU"

    elif current_state == "MAIN_MENU":
        draw_navigation(screen, font, tabs, active_tab)
        
        # Tab-Specific Content
        if active_tab == 0: 
            draw_stat_tab(screen, font, sub_tabs_stat, sub_active_stat, walk_anim, current_time)
        elif active_tab == 1:
            draw_inventory_tab(screen, font, sub_tabs_inv, sub_active_inv, item_index)
        elif active_tab == 2:
            draw_data_tab(screen, font, sub_tabs_data, sub_active_data, item_index)
        elif active_tab == 3:
            # Pass keys and events at the end!
            draw_map_tab(screen, font, sub_tabs_map, sub_active_map, current_time, keys, events)

        elif active_tab == 4:
            draw_radio_tab(screen, font, sub_tabs_radio, sub_active_radio, current_time, item_index)

    elif current_state == "PLAYING_HOLOTAPE":
        screen.fill(BLACK)
        
        if active_game: # Safety check!
            # Pass the events list into the cartridge!
            active_game.update(events) 
            active_game.draw(screen)


    # === NEW: THE CRT POWER DOWN ANIMATION ===
    elif current_state == "POWERING_OFF":
        screen.fill(BLACK)
        
        # Calculate progress from 1.0 (start) down to 0.0 (end)
        progress = power_anim_timer / 40.0 
        
        if progress > 0.5:
            # Stage 1: The screen violently collapses vertically into a bright horizontal line
            # It maps the top 50% of the timer to shrinking the height
            h_progress = (progress - 0.5) * 2 
            h = int(HEIGHT * h_progress)
            w = WIDTH
        else:
            # Stage 2: The horizontal line rapidly shrinks into a dot
            # It maps the bottom 50% of the timer to shrinking the width
            w_progress = progress * 2
            h = 4 # Keep it 4 pixels thick
            w = int(WIDTH * w_progress)

        # Ensure the dot never completely disappears until the timer hits 0
        if h < 4: h = 4
        if w < 4: w = 4

        # Draw the glowing collapsed beam exactly in the center of the screen
        beam_rect = pygame.Rect(0, 0, w, h)
        beam_rect.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(screen, GREEN, beam_rect)

        power_anim_timer -= 1
        if power_anim_timer <= 0:
            current_state = "POWERED_OFF"
        
        # When the animation hits zero, decide what to do!
        if power_anim_timer <= 0:
            if quitting_completely:
                running = False # Kills the main loop, closing the OS entirely!
            else:
                current_state = "POWERED_OFF" # Just goes to sleep mode

    # === NEW: SLEEP MODE ===
    elif current_state == "POWERED_OFF":
        # The OS is asleep. Draw nothing but pure black.
        screen.fill(BLACK)

    # --- 4. POST-PROCESSING ---
    
    # === THE FALLOUT 3 CRT GLITCH ===
    if glitch_timer > 0:
        
        # --- 1. THE V-SYNC ROLL ---
        if roll_speed != 0:
            # Calculate how far the screen has shifted up or down
            roll_y = (glitch_timer * roll_speed) % HEIGHT
            
            # Copy the pristine screen before we mess it up
            screen_copy = screen.copy()
            screen.fill(BLACK)
            
            # Draw it shifted
            screen.blit(screen_copy, (0, roll_y))
            
            # Draw the piece that got cut off wrapping around to the other side!
            if roll_y > 0:
                screen.blit(screen_copy, (0, roll_y - HEIGHT))
            else:
                screen.blit(screen_copy, (0, roll_y + HEIGHT))

        # --- 2. THE HORIZONTAL TEAR ---
        tear_y = random.randint(0, HEIGHT - 40)
        tear_h = random.randint(20, 40)       # Your upgraded violent height!
        tear_offset = random.randint(-55, 55) # Your upgraded violent offset!
        
        slice_rect = pygame.Rect(0, tear_y, WIDTH, tear_h)
        screen_slice = screen.subsurface(slice_rect).copy()
        
        pygame.draw.rect(screen, BLACK, slice_rect)
        screen.blit(screen_slice, (tear_offset, tear_y))

        # --- 3. STATIC TRACKING LINES ---
        for _ in range(4):
            line_y = random.randint(0, HEIGHT)
            pygame.draw.line(screen, GREEN, (0, line_y), (WIDTH, line_y), 1)

        glitch_timer -= 1 


    crt_filter.draw(screen)

    pygame.display.flip()
    pygame.time.Clock().tick(60) 

pygame.quit()
sys.exit()
