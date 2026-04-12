# ui/map_screen.py
import pygame
import os
import requests
from config import BLACK, WIDTH, HEIGHT
from system.animation import TabAnimator 
from system.api_keys import GOOGLE_API_KEY
from system.theme import active_theme

inv_animator = TabAnimator()

# --- MAP CONFIGURATION ---
MAP_FILE = "assets/local_map.png"
LAT = "38.7047"
LON = "-93.2282"
ZOOM = "13" 

WORLD_SIZE = 1280

base_map_image = None   
cached_map_image = None 
zoom_level = 1.0        

world_cursor_x = WORLD_SIZE // 2
world_cursor_y = WORLD_SIZE // 2
camera_x = 0
camera_y = 0
saved_markers = []

player_world_x = WORLD_SIZE // 2
player_world_y = WORLD_SIZE // 2

# === NEW: THE TINTING MACHINE ===
# This takes the white map and flash-dyes it to match your current theme!
def apply_tint(image, color):
    tinted_image = image.copy()
    # BLEND_RGBA_MULT mathematically multiplies the RGB values.
    # White (255,255,255) * Pink = Pink!
    # Black (0,0,0) * Pink = Black!
    tinted_image.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image

def reset_map_cursor():
    global world_cursor_x, world_cursor_y, camera_x, camera_y, zoom_level
    world_cursor_x = WORLD_SIZE // 2
    world_cursor_y = WORLD_SIZE // 2
    camera_x = 0
    camera_y = 0
    zoom_level = 1.0 

def download_pipboy_map():
    if not os.path.exists(MAP_FILE):
        print("Downloading WIDE Pip-Boy Map from Google...")
        
        # === UPDATED: CHANGED 0x00ff00 (Green) to 0xffffff (White) ===
        style = (
            "&style=feature:all|element:geometry|color:0x000000"           
            "&style=feature:road|element:geometry|color:0xffffff"          
            "&style=feature:water|element:geometry|color:0x333333"         
            "&style=feature:all|element:labels.text.fill|color:0xffffff"   
            "&style=feature:all|element:labels.text.stroke|visibility:off" 
            "&style=feature:poi|visibility:off"                            
            "&style=feature:transit|visibility:off"                        
        )
        url = f"https://maps.googleapis.com/maps/api/staticmap?center={LAT},{LON}&zoom={ZOOM}&size=640x640&scale=2&maptype=roadmap{style}&key={GOOGLE_API_KEY}"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                with open(MAP_FILE, 'wb') as f:
                    f.write(response.content)
                print("Wide Map downloaded successfully!")
        except Exception as e:
            print(f"Network error downloading map: {e}")

def draw_edge_indicator(screen, obj_x, obj_y, map_rect, is_player=False):
    if obj_x < map_rect.left or obj_x > map_rect.right or obj_y < map_rect.top or obj_y > map_rect.bottom:
        cx = max(map_rect.left, min(obj_x, map_rect.right))
        cy = max(map_rect.top, min(obj_y, map_rect.bottom))
        
        if is_player:
            pygame.draw.polygon(screen, active_theme.color, [(cx, cy - 8), (cx - 6, cy + 6), (cx + 6, cy + 6)])
        else:
            pygame.draw.rect(screen, active_theme.color, (cx - 4, cy - 4, 8, 8))
        return True 
    return False 

def draw_map_tab(screen, font, sub_tabs_map, sub_active_map, current_time, keys, events):
    global base_map_image, cached_map_image, world_cursor_x, world_cursor_y, camera_x, camera_y, saved_markers, zoom_level
    
    map_rect = pygame.Rect(10, 75, WIDTH - 20, HEIGHT - 110)

    if camera_x == 0 and camera_y == 0:
        camera_x = (WORLD_SIZE - map_rect.width) // 2
        camera_y = (WORLD_SIZE - map_rect.height) // 2

    # --- LAZY LOADING & ZOOM SCALING ---
    if base_map_image is None:
        if GOOGLE_API_KEY != "YOUR_API_KEY_HERE":
            download_pipboy_map()
        try:
            base_map_image = pygame.image.load(MAP_FILE).convert_alpha()
            base_map_image = pygame.transform.smoothscale(base_map_image, (WORLD_SIZE, WORLD_SIZE))
            cached_map_image = base_map_image
        except:
            base_map_image = pygame.Surface((WORLD_SIZE, WORLD_SIZE))
            base_map_image.fill((0, 20, 0))
            cached_map_image = base_map_image

    scaled_size = int(WORLD_SIZE * zoom_level)

    # 1. MOVEMENT & ZOOM LOGIC
    speed = 5
    if sub_active_map == 0: 
        if keys[pygame.K_w] and world_cursor_y > 5: world_cursor_y -= speed
        if keys[pygame.K_s] and world_cursor_y < WORLD_SIZE - 5: world_cursor_y += speed
        if keys[pygame.K_a] and world_cursor_x > 5: world_cursor_x -= speed
        if keys[pygame.K_d] and world_cursor_x < WORLD_SIZE - 5: world_cursor_x += speed

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    saved_markers.append((world_cursor_x, world_cursor_y))
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    zoom_level = min(2.5, zoom_level + 0.25) 
                    cached_map_image = pygame.transform.smoothscale(base_map_image, (scaled_size, scaled_size))
                elif event.key == pygame.K_MINUS:
                    zoom_level = max(0.5, zoom_level - 0.25) 
                    cached_map_image = pygame.transform.smoothscale(base_map_image, (scaled_size, scaled_size))

    # 2. PANNING CAMERA LOGIC
    margin = 75 
    screen_cursor_x = (world_cursor_x * zoom_level)
    screen_cursor_y = (world_cursor_y * zoom_level)

    if screen_cursor_x - camera_x < margin: camera_x = screen_cursor_x - margin
    elif screen_cursor_x - camera_x > map_rect.width - margin: camera_x = screen_cursor_x - map_rect.width + margin

    if screen_cursor_y - camera_y < margin: camera_y = screen_cursor_y - margin
    elif screen_cursor_y - camera_y > map_rect.height - margin: camera_y = screen_cursor_y - map_rect.height + margin

    camera_x = max(0, min(camera_x, scaled_size - map_rect.width))
    camera_y = max(0, min(camera_y, scaled_size - map_rect.height))

    inv_animator.draw(screen, font, sub_tabs_map, sub_active_map)

    # === UPDATED: DRAW MAP & ICONS ===
    screen.set_clip(map_rect)
    
    # Send the white map through the tinting machine right before we draw it!
    themed_map_image = apply_tint(cached_map_image, active_theme.color)
    screen.blit(themed_map_image, (map_rect.left - camera_x, map_rect.top - camera_y))

    for mx, my in saved_markers:
        draw_x = map_rect.left + (mx * zoom_level) - camera_x
        draw_y = map_rect.top + (my * zoom_level) - camera_y
        if not draw_edge_indicator(screen, draw_x, draw_y, map_rect, is_player=False):
            pygame.draw.rect(screen, active_theme.color, (draw_x - 4, draw_y - 4, 8, 8))
            pygame.draw.rect(screen, BLACK, (draw_x - 2, draw_y - 2, 4, 4))

    scaled_center = scaled_size // 2
    
    px = map_rect.left + scaled_center - camera_x
    py = map_rect.top + scaled_center - camera_y
    
    if not draw_edge_indicator(screen, px, py, map_rect, is_player=True):
        pygame.draw.polygon(screen, active_theme.color, [(px, py - 8), (px - 6, py + 6), (px + 6, py + 6)])

    cx = map_rect.left + screen_cursor_x - camera_x
    cy = map_rect.top + screen_cursor_y - camera_y
    pygame.draw.line(screen, active_theme.color, (cx - 15, cy), (cx + 15, cy), 2)
    pygame.draw.line(screen, active_theme.color, (cx, cy - 15), (cx, cy + 15), 2)

    screen.set_clip(None)

    # 5. DRAW FOOTER & DYNAMIC COORDINATES
    pygame.draw.rect(screen, active_theme.color, map_rect, 2)
    footer_rect = pygame.Rect(10, HEIGHT - 30, WIDTH - 20, 25)
    
    dynamic_lat = float(LAT) + ((WORLD_SIZE // 2) - world_cursor_y) * 0.00005
    dynamic_lon = float(LON) + (world_cursor_x - (WORLD_SIZE // 2)) * 0.00005
    
    coord_text = font.render(f"LAT: {dynamic_lat:.4f}  LON: {dynamic_lon:.4f}", True, active_theme.color)
    screen.blit(coord_text, (footer_rect.left + 10, footer_rect.top + 5))
    
    loc_text = font.render("Sedalia, MO", True, active_theme.color)
    screen.blit(loc_text, (footer_rect.right - loc_text.get_width() - 10, footer_rect.top + 5))
