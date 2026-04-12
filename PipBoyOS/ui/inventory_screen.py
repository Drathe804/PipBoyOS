# ui/inventory_screen.py
import pygame
import json
import os
from config import BLACK, WIDTH, HEIGHT
from system.animation import TabAnimator
from system.theme import active_theme

inv_animator = TabAnimator()

# --- 1. LOAD THE JSON INVENTORY (NO CHANGE) ---
inventory_data = {"weapons": [], "apparel": [], "aid": [], "misc": []}
try:
    with open("inventory.json", "r") as f:
        inventory_data = json.load(f)
except Exception as e:
    print(f"Could not load inventory: {e}")

def get_selected_inventory_item(sub_active_inv, item_index):
    """Returns the JSON dictionary of the currently highlighted item."""
    category_keys = ["weapons", "apparel", "aid", "misc"]
    current_category = category_keys[sub_active_inv]
    items = inventory_data.get(current_category, [])
    
    if not items: return None
    safe_index = max(0, min(item_index, len(items) - 1))
    return items[safe_index]

# --- 2. THE IMAGE TINTING HELPER ---
# Forces any icon to match your radioactive active_theme.color UI color!
def tint_image(image, color):
    tinted = image.copy()
    # BLEND_RGB_MULT multiplies the colors. White/greyscale pixels become active_theme.color!
    tinted.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return tinted


# --- 3. CACHE THE GENERIC ICONS (SCALED SMALLER) ---
def load_icon(filename):
    path = os.path.join("assets", "icons", filename)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        # Scale down slightly to fit the narrower info box
        return pygame.transform.smoothscale(img, (90, 90)) 
    return None

icon_cache = {}
custom_image_cache = {}


# --- 4. NEW HELPER: THE "HIGHLIGHTED" DATA ROW ---
# Instead of an underline, this draws a transparent glowing box behind the text row.
def draw_highlighted_stat_row(screen, font, label, value, x, y, width, trans_surf):
    """
    label: Left-aligned text (e.g., "Damage")
    value: Right-aligned text (e.g., "50 ++")
    width: Total width of the info column
    trans_surf: A reusable transparent active_theme.color surface for the highlight effect
    """
    
    # 1. POSITION THE ROW HIGHLIGHT (BEHIND THE TEXT)
    # The translucent surface is created once in draw_inventory_tab for efficiency
    text_height = font.get_height()
    
    # Centre the text row inside the translucent band
    # We slightly increase the area to give it breathing room
    acc_rect = pygame.Rect(x, y - 2, width, text_height + 4)
    
    # Blit the transparent highlight FIRST (the background glow)
    screen.blit(trans_surf, acc_rect.topleft, pygame.Rect(0, 0, width, acc_rect.height))

    # 2. DRAW THE TINTED active_theme.color TEXT (ON TOP OF HIGHLIGHT)
    
    # Left-align the label
    label_surf = font.render(label, True, active_theme.color)
    screen.blit(label_surf, (x + 4, y)) # slight padding from left edge

    # Right-align the value
    val_surf = font.render(str(value), True, active_theme.color)
    val_width = val_surf.get_width()
    screen.blit(val_surf, (x + width - val_width - 4, y)) # slight padding from right edge


# --- HELPER: DRAW BOTTOM FOOTER ICON STATS (NO CHANGE) ---
def draw_footer_stat(screen, font, label, value, x, y):
    full_text = f"{label} {value}"
    stat_surf = font.render(full_text, True, active_theme.color)
    screen.blit(stat_surf, (x, y))


def draw_inventory_tab(screen, font, sub_tabs_inv, sub_active_inv, item_index):
    global icon_cache 
    
    # LAZY LOADING (NO CHANGE)
    if not icon_cache:
        icon_cache["weapon"] = load_icon("icon_weapon.png")
        icon_cache["apparel"] = load_icon("icon_apparel.png")
        icon_cache["aid"] = load_icon("icon_aid.png")
        icon_cache["misc"] = load_icon("icon_misc.png")

    # --- ANIMATE THE TABS (NO CHANGE) ---
    inv_animator.draw(screen, font, sub_tabs_inv, sub_active_inv)

    # --- CATEGORY LOGIC (NO CHANGE) ---
    category_keys = ["weapons", "apparel", "aid", "misc"]
    current_category = category_keys[sub_active_inv]
    items = inventory_data.get(current_category, [])

    if not items:
        empty_text = font.render("NO ITEMS FOUND", True, active_theme.color)
        screen.blit(empty_text, (20, 80))
        return

    safe_index = max(0, min(item_index, len(items) - 1))

    # --- DRAW THE ITEM LIST (NO CHANGE, still all active_theme.color) ---
    list_start_y = 80
    for i, item in enumerate(items):
        item_name = item.get("name", "Unknown Item")
        if i == safe_index:
            text_surface = font.render(item_name, True, BLACK)
            rect = text_surface.get_rect(topleft=(20, list_start_y))
            rect.inflate_ip(10, 4)
            pygame.draw.rect(screen, active_theme.color, rect)
            screen.blit(text_surface, (25, list_start_y + 2))
        else:
            text_surface = font.render(item_name, True, active_theme.color)
            screen.blit(text_surface, (25, list_start_y + 2))
        list_start_y += 25

    # ==========================================
    # --- UPGRADED: NARROWER INFO BLOCK ---
    # ==========================================
    info_column_x = WIDTH - 140
    column_width = 120
    info_rect = pygame.Rect(info_column_x, 80, column_width, 130)

    selected_item = items[safe_index]
    
    # 1. DRAW THE PREVIEW IMAGE (TINTED)
    image_to_draw = None
    item_type = selected_item.get("type", "misc")
    custom_image_path = selected_item.get("image")

    if custom_image_path and os.path.exists(os.path.join("assets", custom_image_path)):
        if custom_image_path not in custom_image_cache:
            img = pygame.image.load(os.path.join("assets", custom_image_path)).convert_alpha()
            # Scale custom images smaller to fit
            custom_image_cache[custom_image_path] = pygame.transform.smoothscale(img, (110, 110))
        image_to_draw = custom_image_cache[custom_image_path]
    else:
        # Fallback to scaled generic icon
        image_to_draw = icon_cache.get(item_type)

    if image_to_draw:
        # User requested image itself same color as UI? TINT IT BEFORE BLITTING!
        # Forces white icons or full-color images to match the phosphor active_theme.color.
        tinted_image = tint_image(image_to_draw, active_theme.color)
        img_rect = tinted_image.get_rect(center=info_rect.center)
        screen.blit(tinted_image, img_rect.topleft)

    # ==========================================
    # 2. CREATE THE ROW HIGHLIGHT SURFACE
    # ==========================================
    # We create this once in the loop for high performance on the Raspberry Pi
    trans_alpha = 40 # Subtle glow (out of 255)
    row_height = font.get_height() + 2 # Add padding
    trans_surf = pygame.Surface((column_width, row_height), pygame.SRCALPHA)
    # Fill with the radioactive active_theme.color at low opacity
    trans_surf.fill((active_theme.color[0], active_theme.color[1], active_theme.color[2], trans_alpha))

    # ==========================================
    # 3. DRAW DYNAMIC STATS WITH ROW HIGHLIGHTS
    # ==========================================
    # We remove line drawing and apply background rectangles
    stat_start_y = info_rect.bottom + 10
    line_spacing = row_height + 2 # Spacing between rows

    stats_to_process = [
        {"key": "damage", "label": "Damage"},
        {"key": "ab_round", "label": "AB Round"},
        {"key": "fire_rate", "label": "Fire Rate"},
        {"key": "range", "label": "Range"},
        {"key": "accuracy", "label": "Accuracy"},
        {"key": "weight", "label": "Weight"},
        {"key": "value", "label": "Value"}
    ]

    for stat in stats_to_process:
        key = stat["key"]
        label = stat["label"]
        if key in selected_item:
            # CALL THE NEW ROW HIGHLIGHT HELPER
            draw_highlighted_stat_row(screen, font, label, selected_item[key], info_column_x, stat_start_y, column_width, trans_surf)
            stat_start_y += line_spacing 

    # ==========================================
    # 4. DRAW THE IMMERSIVE BOTTOM-BAR STATS
    # ==========================================
    # Standard footer behavior—usually not highlighted.
    footer_y = info_rect.bottom + (line_spacing * (len(stats_to_process) + 1))
    
    draw_footer_stat(screen, font, "91/285 WG", "", info_column_x, footer_y)
    draw_footer_stat(screen, font, "575 CP", "", info_column_x + 60, footer_y)
    draw_footer_stat(screen, font, "LEVEL 25", "", info_column_x, footer_y + 20)

    # ==========================================
    # 5. THE HOLOTAPE PROMPT
    # ==========================================
    if "game" in selected_item:
        prompt_surf = font.render("LOAD HOLOTAPE", True, BLACK, active_theme.color) # Black text on active_theme.color box
        # Draw it neatly aligned on the right side above the stats
        screen.blit(prompt_surf, (info_column_x, stat_start_y)) 
