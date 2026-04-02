# ui/radio_screen.py
import pygame
import math
from config import GREEN, BLACK, WIDTH, HEIGHT
from system.animation import TabAnimator # Import our new tool!

# Create an animator specifically for the inventory screen
inv_animator = TabAnimator()

# --- DYNAMIC RADIO DATABASE ---
RADIO_DATABASE = {
    # STATIONS
    "Galaxy News Radio": {"freq": "FREQ: 104.4 FM", "amp": 30, "speed": 0.005, "style": "complex"},
    "Diamond City Radio": {"freq": "FREQ: 89.9 FM", "amp": 20, "speed": 0.010, "style": "simple"},
    "Here Come The Mummies": {"freq": "STREAM: ENCRYPTED", "amp": 40, "speed": 0.020, "style": "chaotic"},
    "Sedalia Local 92.3": {"freq": "FREQ: 92.3 FM", "amp": 15, "speed": 0.003, "style": "simple"},
    
    # PODCASTS
    "Wasteland Survival Guide": {"freq": "DL: 99% COMPLETE", "amp": 10, "speed": 0.002, "style": "simple"},
    "Swole Scroll Devlog": {"freq": "PORT: 8080 (LOCAL)", "amp": 25, "speed": 0.008, "style": "complex"}
}

def draw_radio_tab(screen, font, sub_tabs_radio, sub_active_radio, current_time, item_index):

    # ==========================================
    # 1. THE SUB-MENU SPRING ANIMATION
    # ==========================================
    # This ONE line now does all the physics and drawing!
    inv_animator.draw(screen, font, sub_tabs_radio, sub_active_radio)

    # 2. THE STATION LISTS
    items = []
    if sub_active_radio == 0:   # STATIONS
        items = ["Galaxy News Radio", "Diamond City Radio", "Here Come The Mummies", "Sedalia Local 92.3"]
    elif sub_active_radio == 1: # PODCASTS
        items = ["Wasteland Survival Guide", "Swole Scroll Devlog"]

    selected_i = item_index % len(items) if len(items) > 0 else 0

    # Draw the list of stations
    start_y = 80
    for i, item in enumerate(items):
        if i == selected_i:
            item_text = font.render(item, True, BLACK)
            highlight_rect = pygame.Rect(15, start_y + (i * 30) - 2, 220, 22)
            pygame.draw.rect(screen, GREEN, highlight_rect)
            screen.blit(item_text, (20, start_y + (i * 30) - 2))
        else:
            item_text = font.render(item, True, GREEN)
            screen.blit(item_text, (20, start_y + (i * 30))) 

    # ==========================================
    # 3. DYNAMIC AUDIO WAVEFORM
    # ==========================================
    wave_box = pygame.Rect(WIDTH - 180, 100, 150, 80)
    pygame.draw.rect(screen, GREEN, wave_box, 2)

    # Grab the selected station's data
    selected_name = items[selected_i] if len(items) > 0 else ""
    station_data = RADIO_DATABASE.get(selected_name, {"freq": "OFFLINE", "amp": 5, "speed": 0.001, "style": "simple"})

    mid_y = wave_box.centery
    points = []
    
    # Apply the station's custom speed and amplitude
    speed = current_time * station_data["speed"]
    amplitude = station_data["amp"] 
    
    # Brief pause to simulate radio static/chatter breaks
    if current_time % 3000 < 500:
        amplitude = 2 

    # Calculate the waveform based on the station's style
    for x in range(wave_box.left + 5, wave_box.right - 5, 2):
        if station_data["style"] == "complex":
            # A bouncy, undulating wave (sine * cosine)
            y = mid_y + math.sin(x * 0.1 + speed) * amplitude * math.cos(x * 0.05 - speed)
        
        elif station_data["style"] == "chaotic":
            # A highly jagged, fast wave (high frequency sine + tight cosine)
            y = mid_y + math.sin(x * 0.3 + speed) * amplitude * math.cos(x * 0.2 + speed)
            
        else: # "simple"
            # A standard, smooth rolling sine wave
            y = mid_y + math.sin(x * 0.05 + speed) * amplitude
            
        points.append((x, y))

    if len(points) > 1:
        pygame.draw.lines(screen, GREEN, False, points, 2)

    # Print the custom frequency footer
    freq_text = font.render(station_data["freq"], True, GREEN)
    screen.blit(freq_text, (wave_box.left + 5, wave_box.bottom + 10))
