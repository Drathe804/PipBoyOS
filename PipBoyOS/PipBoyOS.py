# PipBoyOS.py
import pygame
import sys
import os
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
from system.theme import active_theme
from ui.settings_screen import draw_settings_tab

# --- SMART HARDWARE SETUP ---
try:
    import RPi.GPIO as GPIO
    import serial
    print("Raspberry Pi Hardware Detected. GPIO & Serial Active.")
    
    # Open the real physical data wires (Pins 8 & 10)
    radio_serial = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
    
except ImportError:
    print("Laptop Detected. Loading Dummy Hardware.")
    
    class DummyGPIO:
        BOARD = "BOARD"
        OUT = "OUT"
        HIGH = "HIGH"
        LOW = "LOW"
        def setmode(self, mode): pass
        def setup(self, pin, mode): pass
        def output(self, pin, state): pass
        def cleanup(self): pass
    GPIO = DummyGPIO()

    class DummySerial:
        def write(self, data): 
            print(f"[LAPTOP MOCK SERIAL] Sent: {data.decode('utf-8').strip()}")
        def close(self): pass
    radio_serial = DummySerial()


# --- RADIO HARDWARE SETUP ---
PTT_PIN = 11  # Physical Pin 11 (Orange wire - Push to Talk)
PD_PIN = 13   # Physical Pin 13 (Purple wire - Power Down / Sleep)

GPIO.setmode(GPIO.BOARD) # Use physical pin numbers

# Setup Push-To-Talk
GPIO.setup(PTT_PIN, GPIO.OUT)
GPIO.output(PTT_PIN, GPIO.HIGH) # HIGH means "Listen Mode"

# Setup Sleep Mode
GPIO.setup(PD_PIN, GPIO.OUT)
GPIO.output(PD_PIN, GPIO.LOW) # LOW means "Deep Sleep" on boot!


# --- 1. SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Pip-Boy OS")

font = pygame.font.Font("fallout.ttf", 14) 
large_font = pygame.font.Font("fallout.ttf", 48) 

crt_filter = CRTFilter()
boot_manager = BootManager()

walk_anim = SpriteAnimation("assets/idle-walking", frame_rate=100, scale=0.5) 

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

# --- NEW RADIO & SETTINGS VARIABLES ---
vfo_mode = False
manual_freq = 462.0000
saved_channels = []
radio_power_on = False 
is_transmitting = False
power_press_time = 0
radio_press_time = 0 
rgb_mode = False # NEW: Slider lock tracker

# --- RADIO TUNING FUNCTION ---
def tune_radio(freq_string):
    # The SA818 chip ignores commands if it is asleep!
    if not radio_power_on:
        print("Cannot tune: Radio is powered OFF.")
        return
        
    # Format: AT+DMOSETGROUP=Bandwidth, TX_Freq, RX_Freq, TX_CTCSS, RX_CTCSS, Squelch
    command = f"AT+DMOSETGROUP=0,{freq_string},{freq_string},0000,0000,4\r\n"
    
    try:
        radio_serial.write(command.encode('utf-8'))
        print(f"Successfully tuned radio to {freq_string} MHz!")
    except Exception as e:
        print(f"Serial write error: {e}")


# --- 2. MAIN LOOP ---
while running:
    current_time = pygame.time.get_ticks()
    
    events = pygame.event.get()
    keys = pygame.key.get_pressed()

    # --- NEW: HARDWARE SHUTDOWN CHECK ---
    if keys[pygame.K_p] and power_press_time > 0:
        if current_time - power_press_time > 3000:  # 3000 milliseconds = 3 seconds
            print("Initiating Hardware Shutdown...")
            os.system("sudo shutdown -h now")
            power_press_time = current_time # Reset to prevent spamming the command
    # ------------------------------------

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12:
                current_state = "POWERING_OFF"
                power_anim_timer = 40 
                quitting_completely = True 

            elif event.key == pygame.K_p:
                power_press_time = pygame.time.get_ticks()

            elif event.key == pygame.K_t:
                radio_press_time = pygame.time.get_ticks()
                if radio_power_on:
                    is_transmitting = True
                    GPIO.output(PTT_PIN, GPIO.LOW)
            
            elif current_state == "MAIN_MENU": 
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    item_index = 0
                    reset_map_cursor()
                
                # --- W & S: List Scrolling, VFO, OR RGB Sliders! ---
                if event.key == pygame.K_s:
                    if active_tab == 4 and vfo_mode:
                        manual_freq -= 0.0125
                    elif active_tab == 2 and sub_active_data == 3 and rgb_mode:
                        # Dial the color down! (Math trick to get 0, 1, or 2)
                        c_idx = (item_index % 6) - 3 
                        active_theme.custom_rgb[c_idx] = max(0, active_theme.custom_rgb[c_idx] - 5)
                        active_theme.update_custom_color(*active_theme.custom_rgb)
                    else:
                        item_index += 1

                elif event.key == pygame.K_w:
                    if active_tab == 4 and vfo_mode:
                        manual_freq += 0.0125
                    elif active_tab == 2 and sub_active_data == 3 and rgb_mode:
                        # Dial the color up!
                        c_idx = (item_index % 6) - 3 
                        active_theme.custom_rgb[c_idx] = min(255, active_theme.custom_rgb[c_idx] + 5)
                        active_theme.update_custom_color(*active_theme.custom_rgb)
                    else:
                        item_index -= 1

                # --- LEFT & RIGHT: Main Tabs ---
                if event.key == pygame.K_RIGHT:
                    active_tab = (active_tab + 1) % len(tabs)
                    glitch_timer = 6 
                    roll_speed = random.choice([0, 0, 40, -40, 60, -60]) 
                    if active_tab == 3: reset_map_cursor()
                        
                elif event.key == pygame.K_LEFT:
                    active_tab = (active_tab - 1) % len(tabs)
                    glitch_timer = 6 
                    roll_speed = random.choice([0, 0, 40, -40, 60, -60]) 
                    if active_tab == 3: reset_map_cursor()
                
                elif active_tab == 0: 
                    if event.key == pygame.K_DOWN: sub_active_stat = (sub_active_stat + 1) % len(sub_tabs_stat)
                    elif event.key == pygame.K_UP: sub_active_stat = (sub_active_stat - 1) % len(sub_tabs_stat)
                        
                elif active_tab == 1: 
                    if event.key == pygame.K_DOWN: sub_active_inv = (sub_active_inv + 1) % len(sub_tabs_inv)
                    elif event.key == pygame.K_UP: sub_active_inv = (sub_active_inv - 1) % len(sub_tabs_inv)
                        
                elif active_tab == 2: 
                    if event.key == pygame.K_DOWN: sub_active_data = (sub_active_data + 1) % len(sub_tabs_data)
                    elif event.key == pygame.K_UP: sub_active_data = (sub_active_data - 1) % len(sub_tabs_data)

                elif active_tab == 3: 
                    if event.key == pygame.K_DOWN: sub_active_map = (sub_active_map + 1) % len(sub_tabs_map)
                    elif event.key == pygame.K_UP: sub_active_map = (sub_active_map - 1) % len(sub_tabs_map)

                elif active_tab == 4: 
                    if event.key == pygame.K_DOWN: sub_active_radio = (sub_active_radio + 1) % len(sub_tabs_radio)
                    elif event.key == pygame.K_UP: sub_active_radio = (sub_active_radio - 1) % len(sub_tabs_radio)

                # --- THE ENTER KEY ---
                if event.key == pygame.K_RETURN: 
                    if active_tab == 1: 
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
                                
                    elif active_tab == 4 and sub_active_radio == 2: 
                        # Figure out exactly what item we are hovering over
                        radio_items = ["FRS Channel 1", "FRS Channel 2"] + saved_channels + ["MANUAL TUNE (VFO)"]
                        hovered_item = radio_items[item_index % len(radio_items)]

                        if hovered_item == "MANUAL TUNE (VFO)":
                            vfo_mode = not vfo_mode 
                            # If we just TURNED OFF VFO mode, lock in the manual frequency!
                            if not vfo_mode:
                                tune_radio(f"{manual_freq:.4f}")
                                
                        elif hovered_item == "FRS Channel 1":
                            tune_radio("462.5625")
                            
                        elif hovered_item == "FRS Channel 2":
                            tune_radio("462.5875")


                    # NEW: Theme & RGB Selector for the DATA Tab!
                    elif active_tab == 2 and sub_active_data == 3: 
                        idx = item_index % 6
                        if idx <= 2: 
                            # They clicked a Theme!
                            themes = ["DEFAULT", "BARBIE", "CUSTOM"]
                            active_theme.apply_theme(themes[idx])
                            try:
                                walk_anim = SpriteAnimation(active_theme.walk_sprite, frame_rate=100, scale=0.5)
                            except Exception as e:
                                pass # Silently ignore if you haven't added the Barbie assets to the folder yet
                        else: 
                            # They clicked an RGB Slider!
                            rgb_mode = not rgb_mode

            elif current_state == "PLAYING_HOLOTAPE":
                if event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                    active_game = None
                    current_state = "MAIN_MENU"

            elif event.key == pygame.K_LEFTBRACKET: 
                manual_freq -= 0.0125
            elif event.key == pygame.K_RIGHTBRACKET: 
                manual_freq += 0.0125


        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_p:
                press_duration = pygame.time.get_ticks() - power_press_time
                if press_duration > 1500:
                    current_state = "POWERING_OFF"
                    power_anim_timer = 40 
                    quitting_completely = True 
                else:
                    if current_state in ["MAIN_MENU", "BOOTING", "PLAYING_HOLOTAPE"]:
                        current_state = "POWERING_OFF"
                        power_anim_timer = 40 
                        quitting_completely = False 
                    elif current_state == "POWERED_OFF":
                        boot_manager.__init__() 
                        current_state = "BOOTING"

            elif event.key in (pygame.K_t, pygame.K_SPACE):
                is_transmitting = False 
                GPIO.output(PTT_PIN, GPIO.HIGH) # Stop transmitting
                
                # Calculate how long the button was held
                radio_duration = pygame.time.get_ticks() - radio_press_time
                
                # If it was a quick tap (< 500ms), toggle the power!
                if radio_duration < 500: 
                    radio_power_on = not radio_power_on
                    
                    # --- HARDWARE DEEP SLEEP LOGIC ---
                    if radio_power_on:
                        GPIO.output(PD_PIN, GPIO.HIGH) # Wake up the SA818!
                        print("Radio Status: AWAKE")
                    else:
                        GPIO.output(PD_PIN, GPIO.LOW)  # Put SA818 to sleep!
                        print("Radio Status: ASLEEP")



    screen.fill(BLACK) 

    # --- 3. STATE MACHINE ---
    if current_state == "BOOTING":
        status = boot_manager.update_and_draw(screen, font, large_font, current_time)
        if status == "DONE":
            current_state = "MAIN_MENU"

    elif current_state == "MAIN_MENU":
        draw_navigation(screen, font, tabs, active_tab)
        
        if active_tab == 0: 
            draw_stat_tab(screen, font, sub_tabs_stat, sub_active_stat, walk_anim, current_time)
        elif active_tab == 1:
            draw_inventory_tab(screen, font, sub_tabs_inv, sub_active_inv, item_index)
        elif active_tab == 2:
            # Check if we are on the brand new SETTINGS sub-tab!
            if sub_active_data == 3:
                draw_settings_tab(screen, font, sub_tabs_data, sub_active_data, item_index, active_theme, rgb_mode, current_time)
            else:
                draw_data_tab(screen, font, sub_tabs_data, sub_active_data, item_index)
        elif active_tab == 3:
            draw_map_tab(screen, font, sub_tabs_map, sub_active_map, current_time, keys, events)
        elif active_tab == 4:
            draw_radio_tab(screen, font, sub_tabs_radio, sub_active_radio, current_time, item_index, vfo_mode, manual_freq, saved_channels, radio_power_on, is_transmitting)

    elif current_state == "PLAYING_HOLOTAPE":
        screen.fill(BLACK)
        if active_game: 
            active_game.update(events) 
            active_game.draw(screen)

    elif current_state == "POWERING_OFF":
        screen.fill(BLACK)
        progress = power_anim_timer / 40.0 
        
        if progress > 0.5:
            h_progress = (progress - 0.5) * 2 
            h = int(HEIGHT * h_progress)
            w = WIDTH
        else:
            w_progress = progress * 2
            h = 4 
            w = int(WIDTH * w_progress)

        if h < 4: h = 4
        if w < 4: w = 4

        beam_rect = pygame.Rect(0, 0, w, h)
        beam_rect.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(screen, active_theme.color, beam_rect)

        power_anim_timer -= 1
        if power_anim_timer <= 0:
            if quitting_completely:
                running = False 
            else:
                current_state = "POWERED_OFF" 

    elif current_state == "POWERED_OFF":
        screen.fill(BLACK)

    # --- 4. POST-PROCESSING ---

    # --- GLOBAL TRANSMITTING ICON ---
    # If transmitting, but we are NOT on the radio tab (active_tab != 4)
    if is_transmitting and active_tab != 4:
        tx_rect = pygame.Rect(WIDTH - 120, HEIGHT - 40, 100, 25)
        pygame.draw.rect(screen, active_theme.color, tx_rect)
        tx_text = font.render("[ TX ]", True, BLACK)
        screen.blit(tx_text, (tx_rect.x + 30, tx_rect.y + 4))

    if glitch_timer > 0:
        if roll_speed != 0:
            roll_y = (glitch_timer * roll_speed) % HEIGHT
            screen_copy = screen.copy()
            screen.fill(BLACK)
            screen.blit(screen_copy, (0, roll_y))
            if roll_y > 0:
                screen.blit(screen_copy, (0, roll_y - HEIGHT))
            else:
                screen.blit(screen_copy, (0, roll_y + HEIGHT))

        tear_y = random.randint(0, HEIGHT - 40)
        tear_h = random.randint(20, 40)       
        tear_offset = random.randint(-55, 55) 
        
        slice_rect = pygame.Rect(0, tear_y, WIDTH, tear_h)
        screen_slice = screen.subsurface(slice_rect).copy()
        
        pygame.draw.rect(screen, BLACK, slice_rect)
        screen.blit(screen_slice, (tear_offset, tear_y))

        for _ in range(4):
            line_y = random.randint(0, HEIGHT)
            pygame.draw.line(screen, active_theme.color, (0, line_y), (WIDTH, line_y), 1)

        glitch_timer -= 1 

    crt_filter.draw(screen)

    pygame.display.flip()
    pygame.time.Clock().tick(60) 

GPIO.cleanup()
pygame.quit()
sys.exit()
