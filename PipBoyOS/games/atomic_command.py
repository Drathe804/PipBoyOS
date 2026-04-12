# games/atomic_command.py
import pygame
import math
import random
import os
from config import BLACK, WIDTH, HEIGHT
from system.theme import active_theme

# Helper to tint your custom missile PNG to Pip-Boy active_theme.color!
def tint_image(image, color):
    tinted = image.copy()
    tinted.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return tinted

class AtomicCommand:
    def __init__(self):
        self.large_font = pygame.font.Font("fallout.ttf", 48)
        self.small_font = pygame.font.Font("fallout.ttf", 24)
        
        self.cross_x = WIDTH // 2
        self.cross_y = HEIGHT // 2
        self.cross_speed = 6
        
        self.lasers = [] 
        self.explosions = [] 
        self.enemy_missiles = []
        self.score = 0
        
        # --- NEW: GAME STATE & WAVE PROGRESSION ---
        self.state = "PLAYING" # Can be: PLAYING, GAME_OVER, LEVEL_CLEAR
        self.level = 1
        self.missiles_per_wave = 10
        self.missiles_spawned = 0
        self.transition_timer = 0 # Used for dramatic pauses between levels
        
        # --- LOAD CUSTOM MISSILE PNG (IF IT EXISTS) ---
        self.missile_img = None
        img_path = os.path.join("assets", "enemy_missile.png")
        if os.path.exists(img_path):
            raw_img = pygame.image.load(img_path).convert_alpha()
            # FIXED: Scaled to a perfect square (24x24) so it doesn't crush the pixels!
            scaled = pygame.transform.smoothscale(raw_img, (24, 24)) 
            self.missile_img = tint_image(scaled, active_theme.color)

        
        self.cities = [
            {"x": 60, "alive": True},
            {"x": 140, "alive": True},
            {"x": WIDTH - 180, "alive": True},
            {"x": WIDTH - 100, "alive": True}
        ]

    def reset_game(self):
        """Completely resets the board after a Game Over."""
        self.level = 1
        self.score = 0
        self.missiles_per_wave = 10
        self.missiles_spawned = 0
        self.lasers.clear()
        self.explosions.clear()
        self.enemy_missiles.clear()
        for city in self.cities:
            city["alive"] = True
        self.state = "PLAYING"

    def start_next_wave(self):
        """Ramps up the difficulty for the next level."""
        self.level += 1
        self.missiles_per_wave += 5 # 5 more missiles each wave!
        self.missiles_spawned = 0
        self.lasers.clear()
        self.explosions.clear()
        self.enemy_missiles.clear()
        self.state = "PLAYING"

    def update(self, events):
        # --- HANDLE GAME OVER STATE ---
        if self.state == "GAME_OVER":
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.reset_game()
            return # Don't run the rest of the game math!

        # --- HANDLE LEVEL COMPLETE STATE ---
        if self.state == "LEVEL_CLEAR":
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.start_next_wave()
            return # Don't run the rest of the game math!

        # ==========================================
        # NORMAL PLAYING MATH BELOW
        # ==========================================
        
        # --- 1. MOVEMENT ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: self.cross_y -= self.cross_speed
        if keys[pygame.K_DOWN]: self.cross_y += self.cross_speed
        if keys[pygame.K_LEFT]: self.cross_x -= self.cross_speed
        if keys[pygame.K_RIGHT]: self.cross_x += self.cross_speed
            
        self.cross_x = max(30, min(self.cross_x, WIDTH - 30))
        self.cross_y = max(30, min(self.cross_y, HEIGHT - 60))

        # --- 2. FIRING ---
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    new_laser = {
                        "start_x": WIDTH // 2,
                        "start_y": HEIGHT - 40, # Fire from the top of the dome
                        "target_x": self.cross_x,
                        "target_y": self.cross_y,
                        "progress": 0.0 
                    }
                    self.lasers.append(new_laser)

        # --- 3. WAVE SPAWNING LOGIC ---
        if self.missiles_spawned < self.missiles_per_wave:
            # RAMP UP SPAWN RATE BASED ON LEVEL
            spawn_chance = 0.01 + (self.level * 0.002) 
            
            if random.random() < spawn_chance: 
                alive_targets = [c for c in self.cities if c["alive"]]
                if alive_targets and random.random() < 0.8:
                    target = random.choice(alive_targets)
                    t_x = target["x"] + 20 
                else:
                    t_x = WIDTH // 2 
                    
                self.enemy_missiles.append({
                    "x": random.randint(30, WIDTH - 30),
                    "y": -20, # Spawn slightly off-screen
                    "target_x": t_x,
                    "target_y": HEIGHT - 20, 
                    "speed": random.uniform(0.001, 0.003) + (self.level * 0.0005), # RAMP UP SPEED
                    "progress": 0.0
                })
                self.missiles_spawned += 1
                
        # Did we finish the wave?
        elif len(self.enemy_missiles) == 0:
            self.state = "LEVEL_CLEAR"
            self.transition_timer = 180 # Pause for 3 seconds (60 frames * 3)
            self.score += (self.level * 100) # Bonus points for clearing the wave!

        # --- 4. UPDATE LASERS & EXPLOSIONS ---
        for laser in self.lasers:
            laser["progress"] += 0.05 
            if laser["progress"] >= 1.0:
                self.explosions.append({
                    "x": laser["target_x"], "y": laser["target_y"],
                    "radius": 1, "max_radius": 40
                })
        self.lasers = [l for l in self.lasers if l["progress"] < 1.0]

        for exp in self.explosions:
            exp["radius"] += 1.5 
        self.explosions = [e for e in self.explosions if e["radius"] < e["max_radius"]]

        # --- 5. UPDATE ENEMY MISSILES & CHECK COLLISIONS ---
        for em in self.enemy_missiles:
            em["progress"] += em["speed"]
            current_x = em["x"] + (em["target_x"] - em["x"]) * em["progress"]
            current_y = em["y"] + (em["target_y"] - em["y"]) * em["progress"]
            
            if em["progress"] >= 1.0:
                em["destroyed"] = True
                for city in self.cities:
                    if city["alive"] and abs(city["x"] + 20 - current_x) < 30:
                        city["alive"] = False
                        
                # Did we just lose the last city? GAME OVER CHECK
                if not any(c["alive"] for c in self.cities):
                    self.state = "GAME_OVER"
            
            for exp in self.explosions:
                dist = math.hypot(current_x - exp["x"], current_y - exp["y"])
                if dist < exp["radius"]:
                    em["destroyed"] = True
                    self.score += 10 * self.level 
                    
        self.enemy_missiles = [em for em in self.enemy_missiles if not em.get("destroyed", False)]

    # --- DRAW HELPERS ---
    def draw_city(self, screen, x, y, alive):
        if alive:
            pygame.draw.rect(screen, active_theme.color, (x, y - 15, 12, 15))      
            pygame.draw.rect(screen, active_theme.color, (x + 14, y - 25, 14, 25)) 
            pygame.draw.rect(screen, active_theme.color, (x + 30, y - 10, 10, 10)) 
        else:
            pygame.draw.rect(screen, active_theme.color, (x, y - 4, 40, 4))
            pygame.draw.rect(screen, active_theme.color, (x + 10, y - 8, 20, 4))

    def draw_turret(self, screen):
        """Draws a base, a dome, and a dynamic rotating barrel."""
        tx, ty = WIDTH // 2, HEIGHT - 40 # Center of the dome
        
        # Calculate the angle from the turret to the crosshair
        angle = math.atan2(self.cross_y - ty, self.cross_x - tx)
        
        # 1. Base
        pygame.draw.rect(screen, active_theme.color, (tx - 30, HEIGHT - 20, 60, 20))
        pygame.draw.rect(screen, active_theme.color, (tx - 20, HEIGHT - 25, 40, 5))
        
        # 2. Rotating Barrel
        barrel_length = 25
        end_x = tx + math.cos(angle) * barrel_length
        end_y = ty + math.sin(angle) * barrel_length
        pygame.draw.line(screen, active_theme.color, (tx, ty), (end_x, end_y), 6) # Thick barrel
        
        # 3. Dome (drawn on top of the barrel to hide the joint)
        pygame.draw.circle(screen, active_theme.color, (tx, ty), 15)
        # Cut off the bottom half of the circle so it sits flat
        pygame.draw.rect(screen, BLACK, (tx - 15, ty, 30, 15)) 
        pygame.draw.line(screen, active_theme.color, (tx - 15, ty), (tx + 15, ty), 2)

    def draw(self, screen):
        screen.fill(BLACK)
        pygame.draw.rect(screen, active_theme.color, (20, 20, WIDTH - 40, HEIGHT - 40), 2)
        
        self.draw_turret(screen)
        
        for city in self.cities:
            self.draw_city(screen, city["x"], HEIGHT - 20, city["alive"])
            
        # --- DRAW ENEMY MISSILES ---
        for em in self.enemy_missiles:
            current_x = em["x"] + (em["target_x"] - em["x"]) * em["progress"]
            current_y = em["y"] + (em["target_y"] - em["y"]) * em["progress"]
            
            if self.missile_img:
                # Calculate the raw angle
                raw_angle = math.degrees(math.atan2(em["y"] - em["target_y"], em["target_x"] - em["x"])) - 90
                
                # FIXED: Subtract 45 degrees to compensate for your diagonal PNG!
                # (If it aims the wrong way, try + 45 instead)
                final_angle = raw_angle - 45
                
                rotated_img = pygame.transform.rotate(self.missile_img, final_angle)
                img_rect = rotated_img.get_rect(center=(current_x, current_y))
                screen.blit(rotated_img, img_rect.topleft)
            else:
                # FALLBACK: Draw a cool downward pointing dart
                pygame.draw.line(screen, active_theme.color, (em["x"], em["y"]), (current_x, current_y), 1)
                pygame.draw.polygon(screen, active_theme.color, [
                    (current_x, current_y + 4), 
                    (current_x - 3, current_y - 3), 
                    (current_x + 3, current_y - 3)
                ])
        
        for laser in self.lasers:
            current_x = laser["start_x"] + (laser["target_x"] - laser["start_x"]) * laser["progress"]
            current_y = laser["start_y"] + (laser["target_y"] - laser["start_y"]) * laser["progress"]
            pygame.draw.line(screen, active_theme.color, (laser["start_x"], laser["start_y"]), (current_x, current_y), 3)

        for exp in self.explosions:
            pygame.draw.circle(screen, active_theme.color, (int(exp["x"]), int(exp["y"])), int(exp["radius"]))

        # Crosshair
        pygame.draw.rect(screen, active_theme.color, (self.cross_x - 1, self.cross_y - 1, 2, 2))
        pygame.draw.circle(screen, active_theme.color, (self.cross_x, self.cross_y), 8, 1)
        pygame.draw.line(screen, active_theme.color, (self.cross_x, self.cross_y - 8), (self.cross_x, self.cross_y - 16), 1) 
        pygame.draw.line(screen, active_theme.color, (self.cross_x, self.cross_y + 8), (self.cross_x, self.cross_y + 16), 1) 
        pygame.draw.line(screen, active_theme.color, (self.cross_x - 8, self.cross_y), (self.cross_x - 16, self.cross_y), 1) 
        pygame.draw.line(screen, active_theme.color, (self.cross_x + 8, self.cross_y), (self.cross_x + 16, self.cross_y), 1) 

        # UI Text
        score_surf = self.small_font.render(f"SCORE {self.score}", True, active_theme.color)
        screen.blit(score_surf, (WIDTH - 150, 30))
        
        level_surf = self.small_font.render(f"WAVE {self.level}", True, active_theme.color)
        screen.blit(level_surf, (WIDTH // 2 - level_surf.get_width() // 2, 30))
        
        prompt_surf = self.small_font.render("TAB TO EJECT", True, active_theme.color)
        screen.blit(prompt_surf, (30, 30))

        # --- DRAW STATE OVERLAYS ---
        if self.state == "GAME_OVER":
            go_surf = self.large_font.render("GAME OVER", True, active_theme.color, BLACK)
            screen.blit(go_surf, (WIDTH // 2 - go_surf.get_width() // 2, HEIGHT // 3))
            sub_surf = self.small_font.render("PRESS SPACE TO RESTART", True, active_theme.color, BLACK)
            screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, HEIGHT // 3 + 60))

        elif self.state == "LEVEL_CLEAR":
            lc_surf = self.large_font.render(f"WAVE {self.level} CLEARED", True, active_theme.color, BLACK)
            screen.blit(lc_surf, (WIDTH // 2 - lc_surf.get_width() // 2, HEIGHT // 3))
            bonus_surf = self.small_font.render(f"INCOMING WAVE {self.level + 1}...", True, active_theme.color, BLACK)
            screen.blit(bonus_surf, (WIDTH // 2 - bonus_surf.get_width() // 2, HEIGHT // 3 + 60))
