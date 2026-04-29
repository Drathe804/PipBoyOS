# ui/radio_screen.py
import pygame
import math
from config import BLACK, WIDTH, HEIGHT
from system.animation import TabAnimator
from system.theme import active_theme

inv_animator = TabAnimator()

# --- DYNAMIC RADIO DATABASE ---
RADIO_DATABASE = {
    "Galaxy News Radio": {"freq": "FREQ: 104.4 FM", "amp": 30, "speed": 0.005, "style": "complex"},
    "Diamond City Radio": {"freq": "FREQ: 89.9 FM", "amp": 20, "speed": 0.010, "style": "simple"},
    "Here Come The Mummies": {"freq": "STREAM: ENCRYPTED", "amp": 40, "speed": 0.020, "style": "chaotic"},
    "Sedalia Local 92.3": {"freq": "FREQ: 92.3 FM", "amp": 15, "speed": 0.003, "style": "simple"},
    
    "Wasteland Survival Guide": {"freq": "DL: 99% COMPLETE", "amp": 10, "speed": 0.002, "style": "simple"},
    "Swole Scroll Devlog": {"freq": "PORT: 8080 (LOCAL)", "amp": 25, "speed": 0.008, "style": "complex"},
    
    "FRS Channel 1": {"freq": "UHF: 462.5625 MHz", "amp": 5, "speed": 0.05, "style": "simple"},
    "FRS Channel 2": {"freq": "UHF: 462.5875 MHz", "amp": 5, "speed": 0.05, "style": "simple"},
    
    "MANUAL TUNE (VFO)": {"freq": "CUSTOM", "amp": 8, "speed": 0.03, "style": "simple"}
}

def draw_radio_tab(screen, font, sub_tabs_radio, sub_active_radio, current_time, item_index, vfo_mode, manual_freq, saved_channels, radio_power_on, is_transmitting):

    inv_animator.draw(screen, font, sub_tabs_radio, sub_active_radio)

    # 1. THE STATION LISTS
    items = []
    if sub_active_radio == 0:   
        items = ["Galaxy News Radio", "Diamond City Radio", "Here Come The Mummies", "Sedalia Local 92.3"]
    elif sub_active_radio == 1: 
        items = ["Wasteland Survival Guide", "Swole Scroll Devlog"]
    elif sub_active_radio == 2: 
        items = ["FRS Channel 1", "FRS Channel 2"]
        # Add any dynamically saved channels here!
        for ch in saved_channels:
            items.append(ch)
        # Always keep Manual Tune at the very bottom
        items.append("MANUAL TUNE (VFO)")

    selected_i = item_index % len(items) if len(items) > 0 else 0
    selected_name = items[selected_i] if len(items) > 0 else ""

    start_y = 80
    for i, item in enumerate(items):
        if i == selected_i:
            # If VFO mode is locked, flash the highlight box to let you know the dial is hijacked!
            if vfo_mode and selected_name == "MANUAL TUNE (VFO)" and current_time % 1000 < 500:
                pygame.draw.rect(screen, active_theme.color, pygame.Rect(15, start_y + (i * 30) - 2, 220, 22), 2)
                item_text = font.render(item, True, active_theme.color)
            else:
                pygame.draw.rect(screen, active_theme.color, pygame.Rect(15, start_y + (i * 30) - 2, 220, 22))
                item_text = font.render(item, True, BLACK)
                
            screen.blit(item_text, (20, start_y + (i * 30) - 2))
        else:
            item_text = font.render(item, True, active_theme.color)
            screen.blit(item_text, (20, start_y + (i * 30))) 

    # ==========================================
    # PUSH-TO-TALK LOGIC
    # ==========================================
    if sub_active_radio == 2:
        if is_transmitting:
            status_surf = font.render(" STATUS: [ TX ] TRANSMITTING ", True, BLACK, active_theme.color)
        else:
            status_surf = font.render(" STATUS: [ RX ] RECEIVING ", True, active_theme.color)
        screen.blit(status_surf, (WIDTH - 210, 75))

    # ==========================================
    # DYNAMIC AUDIO WAVEFORM & FOOTER
    # ==========================================
    wave_box = pygame.Rect(WIDTH - 220, 100, 190, 80)
    pygame.draw.rect(screen, active_theme.color, wave_box, 2)

    station_data = RADIO_DATABASE.get(selected_name, {"freq": "OFFLINE", "amp": 5, "speed": 0.001, "style": "simple"})

    mid_y = wave_box.centery
    points = []
    
    speed = current_time * station_data["speed"]
    amplitude = station_data["amp"] 
    
    if is_transmitting:
        amplitude = 35
        station_data["style"] = "chaotic"
    elif current_time % 3000 < 500:
        amplitude = 2 

    for x in range(wave_box.left + 5, wave_box.right - 5, 2):
        if station_data["style"] == "complex":
            y = mid_y + math.sin(x * 0.1 + speed) * amplitude * math.cos(x * 0.05 - speed)
        elif station_data["style"] == "chaotic":
            y = mid_y + math.sin(x * 0.3 + speed) * amplitude * math.cos(x * 0.2 + speed)
        else: 
            y = mid_y + math.sin(x * 0.05 + speed) * amplitude
            
        points.append((x, y))

    if len(points) > 1:
        pygame.draw.lines(screen, active_theme.color, False, points, 2)

    # --- THE LIVE FREQUENCY OVERRIDE ---
    if selected_name == "MANUAL TUNE (VFO)":
        if vfo_mode:
            display_freq = f"UHF: > {manual_freq:.4f} <" 
        else:
            display_freq = f"UHF: {manual_freq:.4f} MHz"
    else:
        display_freq = station_data["freq"]

    freq_text = font.render(display_freq, True, active_theme.color)
    screen.blit(freq_text, (wave_box.left + 5, wave_box.bottom + 10))
