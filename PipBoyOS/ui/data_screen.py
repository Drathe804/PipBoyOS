# ui/data_screen.py
import pygame
from config import GREEN, BLACK, WIDTH, HEIGHT
from system.animation import TabAnimator # Import our new tool!

# Create an animator specifically for the inventory screen
inv_animator = TabAnimator()

# --- DYNAMIC DATA DATABASE ---
DATA_DATABASE = {
    # === QUESTS FORMAT ===
    "Build Pip-Boy OS": {
        "type": "quest", 
        "steps": [("[X]", "Build UI Framework"), ("[X]", "Map scrolling logic"), ("[ ]", "Solder Encoders")]
    },
    "Integrate Hogarth AI": {
        "type": "quest", 
        "steps": [("[ ]", "Boot local server"), ("[ ]", "Link API keys")]
    },
    "Attend Planet Comicon": {
        "type": "quest", 
        "steps": [("[X]", "Secure 3-Day Pass"), ("[ ]", "Finalize Cosplay"), ("[ ]", "Deploy to KC")]
    },
    
    # === PROJECTS (Using Quest Format) ===
    "Swole Scroll App": {
        "type": "quest", 
        "steps": [("[X]", "Define core mechanics"), ("[ ]", "Design UI"), ("[ ]", "Launch Beta")]
    },
    "Raspberry Pi Hardware": {
        "type": "quest", 
        "steps": [("[X]", "Acquire Pi 4"), ("[ ]", "Print 3D Case"), ("[ ]", "Wire Battery Pack")]
    },

    # === LOGS FORMAT (Matches the 'Stats' screenshot) ===
    "Workout Log": {
        "type": "stat", 
        "stats": [("Consecutive Days", "12"), ("Max Bench", "225"), ("Distance Run", "15 mi"), ("Bananas Consumed", "42")]
    },
    "Gaming Stats": {
        "type": "stat",
        "stats": [("Shrines Cleared", "152"), ("Korok Seeds", "900"), ("Deathclaws Defeated", "4"), ("Nat 20s Rolled", "18")]
    },
    "System Diagnostics": {
        "type": "stat", 
        "stats": [("CPU Temp", "42 C"), ("Memory", "640K"), ("Network", "Connected"), ("Local Area", "Sedalia")]
    }
}

def draw_data_tab(screen, font, sub_tabs_data, sub_active_data, item_index):

    # ==========================================
    # 1. THE SUB-MENU SPRING ANIMATION
    # ==========================================
    # This ONE line now does all the physics and drawing!
    inv_animator.draw(screen, font, sub_tabs_data, sub_active_data)

    # 2. THE DYNAMIC DATA LISTS (Left Side)
    items = []
    if sub_active_data == 0:   # QUESTS
        items = ["Build Pip-Boy OS", "Integrate Hogarth AI", "Attend Planet Comicon"]
    elif sub_active_data == 1: # PROJECTS
        items = ["Swole Scroll App", "Raspberry Pi Hardware"]
    elif sub_active_data == 2: # LOGS (Stats)
        items = ["Workout Log", "Gaming Stats", "System Diagnostics"]

    selected_i = item_index % len(items) if len(items) > 0 else 0

    # Draw the list of items on the left side
    start_y = 80
    for i, item in enumerate(items):
        if i == selected_i:
            # --- NEW: Solid Block Highlight ---
            item_text = font.render(item, True, BLACK)
            highlight_rect = pygame.Rect(15, start_y + (i * 25) - 2, 200, 20)
            pygame.draw.rect(screen, GREEN, highlight_rect)
            screen.blit(item_text, (20, start_y + (i * 25) - 2))
        else:
            item_text = font.render(item, True, GREEN)
            screen.blit(item_text, (20, start_y + (i * 25))) 

    # 3. DYNAMIC RIGHT SIDE DETAILS
    if len(items) > 0:
        selected_name = items[selected_i]
        data = DATA_DATABASE.get(selected_name, {"type": "unknown"})

        # ==========================================
        # FORMAT 1: QUESTS (Icon + Divider + Checklist)
        # ==========================================
        if data["type"] == "quest":
            # Vault Boy Placeholder Box (Top Right)
            vb_box = pygame.Rect(WIDTH - 120, 70, 60, 80)
            pygame.draw.rect(screen, GREEN, vb_box, 1)
            vb_text = font.render("VB", True, GREEN)
            screen.blit(vb_text, vb_text.get_rect(center=vb_box.center))

            # Horizontal Divider Line
            line_y = 160
            pygame.draw.line(screen, GREEN, (WIDTH - 240, line_y), (WIDTH - 20, line_y), 1)

            # Draw Objectives List
            obj_y = line_y + 10
            for checkbox, step_text in data.get("steps", []):
                check_text = font.render(checkbox, True, GREEN)
                step_render = font.render(step_text, True, GREEN)
                
                screen.blit(check_text, (WIDTH - 240, obj_y))
                screen.blit(step_render, (WIDTH - 210, obj_y))
                obj_y += 20

        # ==========================================
        # FORMAT 2: STATS (Two-Column Data List)
        # ==========================================
        elif data["type"] == "stat":
            stat_y = 80
            for stat_name, stat_val in data.get("stats", []):
                # Left align the stat name
                name_text = font.render(stat_name, True, GREEN)
                screen.blit(name_text, (WIDTH - 240, stat_y))
                
                # Right align the stat value
                val_text = font.render(stat_val, True, GREEN)
                val_rect = val_text.get_rect(topright=(WIDTH - 20, stat_y))
                screen.blit(val_text, val_rect)
                
                stat_y += 20
