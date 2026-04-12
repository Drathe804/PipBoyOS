# games/red_menace.py
import pygame
import math
import random
from config import BLACK, WIDTH, HEIGHT
from system.theme import active_theme

class RedMenace:
    def __init__(self):
        self.large_font = pygame.font.Font("fallout.ttf", 48)
        self.small_font = pygame.font.Font("fallout.ttf", 24)
        
        self.state = "PLAYING" 
        self.score = 0
        
        self.player_rect = pygame.Rect(40, HEIGHT - 34, 14, 14) 
        self.speed = 3.5        
        
        # --- FIXED: THE FLOATY JUMP ---
        # Lower jump power, but much lower gravity = same height, longer hang time!
        self.vel_y = 0          
        self.jump_power = -4.5  
        self.gravity = 0.35      
        
        self.on_ground = False  
        self.on_ladder = False  

        self.platforms = [
            {"x1": 20, "y1": HEIGHT - 20,  "x2": WIDTH - 20, "y2": HEIGHT - 20},  
            {"x1": 20, "y1": HEIGHT - 80,  "x2": WIDTH - 40, "y2": HEIGHT - 50},  
            {"x1": 40, "y1": HEIGHT - 110, "x2": WIDTH - 20, "y2": HEIGHT - 140}, 
            {"x1": 20, "y1": HEIGHT - 190, "x2": WIDTH - 40, "y2": HEIGHT - 160}, 
            {"x1": 40, "y1": HEIGHT - 230, "x2": 250,        "y2": HEIGHT - 230}  
        ]
        
        ladder_data = [
            {"x": WIDTH - 100, "top_i": 1, "bot_i": 0},
            {"x": 100,         "top_i": 2, "bot_i": 1},
            {"x": WIDTH - 100, "top_i": 3, "bot_i": 2},
            {"x": 150,         "top_i": 4, "bot_i": 3}
        ]
        
        self.ladders = []
        for ld in ladder_data:
            top_y = self.get_plat_y(self.platforms[ld["top_i"]], ld["x"])
            bot_y = self.get_plat_y(self.platforms[ld["bot_i"]], ld["x"])
            self.ladders.append(pygame.Rect(ld["x"], top_y, 20, (bot_y - top_y) + 8))

        self.boss_rect = pygame.Rect(50, HEIGHT - 254, 24, 24)
        self.goal_rect = pygame.Rect(200, HEIGHT - 246, 12, 16) 
        
        # --- NEW: ORGANIC BOMB TIMERS ---
        self.bombs = []
        self.bomb_spawn_timer = 0
        self.next_bomb_time = random.randint(60, 140) # First bomb drops between 1 and 2.5 seconds

    def get_plat_y(self, plat, x):
        ratio = (x - plat["x1"]) / (plat["x2"] - plat["x1"])
        return plat["y1"] + ratio * (plat["y2"] - plat["y1"])

    def reset_game(self):
        self.player_rect.topleft = (40, HEIGHT - 34)
        self.vel_y = 0
        self.bombs.clear()
        self.bomb_spawn_timer = 0
        self.next_bomb_time = random.randint(60, 140) # Reset the RNG timer
        self.state = "PLAYING"

    def update(self, events):
        if self.state in ["GAME_OVER", "LEVEL_CLEAR"]:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.reset_game()
            return

        keys = pygame.key.get_pressed()
        cx = self.player_rect.centerx

        # --- 1. HORIZONTAL MOVEMENT ---
        if keys[pygame.K_LEFT]:  self.player_rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.player_rect.x += self.speed
        self.player_rect.x = max(20, min(self.player_rect.x, WIDTH - 20 - self.player_rect.width))
        cx = self.player_rect.centerx

        # --- 2. LADDER DETECTION ---
        touching_ladder = any(self.player_rect.colliderect(l) for l in self.ladders)
        if touching_ladder and (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            self.on_ladder = True
        elif not touching_ladder:
            self.on_ladder = False 

        # --- 3. CLIMBING VS GRAVITY ---
        if self.on_ladder:
            self.vel_y = 0 
            if keys[pygame.K_UP]:   self.player_rect.y -= int(self.speed * 0.6) 
            if keys[pygame.K_DOWN]: self.player_rect.y += int(self.speed * 0.6) 
        else:
            self.vel_y += self.gravity          
            self.player_rect.y += self.vel_y    
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.on_ground:
                    self.vel_y = self.jump_power
                    self.on_ground = False

        # --- 4. SLANTED FLOOR COLLISION ---
        self.on_ground = False 
        if not self.on_ladder:
            for plat in self.platforms:
                if plat["x1"] <= cx <= plat["x2"]:
                    plat_y = self.get_plat_y(plat, cx)
                    if self.vel_y >= 0 and (plat_y - 12) <= self.player_rect.bottom <= (plat_y + 12):
                        self.player_rect.bottom = plat_y
                        self.vel_y = 0       
                        self.on_ground = True 
                        break

        # --- 5. ORGANIC BOMB PHYSICS ---
        self.bomb_spawn_timer += 1
        if self.bomb_spawn_timer > self.next_bomb_time: 
            self.bomb_spawn_timer = 0
            
            # Pick a new random time for the next bomb
            self.next_bomb_time = random.randint(70, 150) 
            
            self.bombs.append({
                "x": self.boss_rect.right + 10,
                "y": self.boss_rect.bottom - 10,
                "vel_y": 0,
                "dir": 1, 
                "speed": random.uniform(1.2, 2.0), # RANDOM SPEED! Some are fast, some are slow!
                "rect": pygame.Rect(0, 0, 10, 10) 
            })

        for bomb in self.bombs:
            bomb["vel_y"] += self.gravity
            bomb["y"] += bomb["vel_y"]
            bomb["rect"].center = (int(bomb["x"]), int(bomb["y"]))
            
            bomb_on_ground = False
            for plat in self.platforms:
                if plat["x1"] <= bomb["rect"].centerx <= plat["x2"]:
                    plat_y = self.get_plat_y(plat, bomb["rect"].centerx)
                    if bomb["vel_y"] > 0 and (plat_y - 12) <= bomb["rect"].bottom <= (plat_y + 12):
                        bomb["rect"].bottom = plat_y
                        bomb["y"] = bomb["rect"].centery
                        bomb["vel_y"] = 0
                        bomb_on_ground = True
                        
                        if plat["y1"] < plat["y2"]:   bomb["dir"] = 1  
                        elif plat["y1"] > plat["y2"]: bomb["dir"] = -1 
                        break
            
            if bomb_on_ground:
                bomb["x"] += bomb["speed"] * bomb["dir"]

            if self.player_rect.colliderect(bomb["rect"]):
                self.state = "GAME_OVER"

        self.bombs = [b for b in self.bombs if b["rect"].top < HEIGHT and 0 < b["rect"].centerx < WIDTH]

        if self.player_rect.colliderect(self.goal_rect):
            self.score += 1000
            self.state = "LEVEL_CLEAR"
            
        if self.player_rect.colliderect(self.boss_rect):
            self.state = "GAME_OVER"

    def draw_girder(self, screen, x1, y1, x2, y2):
        thickness = 8
        pygame.draw.line(screen, active_theme.color, (x1, y1), (x2, y2), 2)
        pygame.draw.line(screen, active_theme.color, (x1, y1 + thickness), (x2, y2 + thickness), 2)
        
        dist = math.hypot(x2 - x1, y2 - y1)
        steps = int(dist // 12) 
        if steps > 0:
            dx = (x2 - x1) / steps
            dy = (y2 - y1) / steps
            for i in range(steps):
                curr_x = x1 + i * dx
                curr_y = y1 + i * dy
                next_x = x1 + (i + 1) * dx
                next_y = y1 + (i + 1) * dy
                
                pygame.draw.line(screen, active_theme.color, (curr_x, curr_y), (next_x, next_y + thickness), 1)
                pygame.draw.line(screen, active_theme.color, (curr_x, curr_y + thickness), (next_x, next_y), 1)

    def draw_ladder(self, screen, rect):
        pygame.draw.line(screen, active_theme.color, (rect.left, rect.top), (rect.left, rect.bottom), 2)
        pygame.draw.line(screen, active_theme.color, (rect.right, rect.top), (rect.right, rect.bottom), 2)
        for y in range(int(rect.top) + 5, int(rect.bottom), 12):
            pygame.draw.line(screen, active_theme.color, (rect.left, y), (rect.right, y), 2)

    def draw(self, screen):
        screen.fill(BLACK)
        pygame.draw.rect(screen, active_theme.color, (20, 20, WIDTH - 40, HEIGHT - 40), 2)

        for ladder in self.ladders:
            self.draw_ladder(screen, ladder)

        for plat in self.platforms:
            self.draw_girder(screen, plat["x1"], plat["y1"], plat["x2"], plat["y2"])

        pygame.draw.rect(screen, active_theme.color, self.goal_rect)
        pygame.draw.circle(screen, active_theme.color, (self.goal_rect.centerx, self.goal_rect.top - 4), 6)

        pygame.draw.rect(screen, active_theme.color, self.boss_rect)
        pygame.draw.rect(screen, BLACK, (self.boss_rect.x + 4, self.boss_rect.y + 6, 4, 4))
        pygame.draw.rect(screen, BLACK, (self.boss_rect.x + 14, self.boss_rect.y + 6, 4, 4))

        pygame.draw.rect(screen, active_theme.color, self.player_rect)

        for bomb in self.bombs:
            pygame.draw.circle(screen, active_theme.color, bomb["rect"].center, bomb["rect"].width // 2)

        score_surf = self.small_font.render(f"SCORE {self.score}", True, active_theme.color)
        screen.blit(score_surf, (WIDTH - 150, 30))

        prompt_surf = self.small_font.render("TAB TO EJECT", True, active_theme.color)
        screen.blit(prompt_surf, (30, 30))

        if self.state == "GAME_OVER":
            go_surf = self.large_font.render("YOU DIED", True, active_theme.color, BLACK)
            screen.blit(go_surf, (WIDTH // 2 - go_surf.get_width() // 2, HEIGHT // 3))

        elif self.state == "LEVEL_CLEAR":
            lc_surf = self.large_font.render("MENACE DEFEATED!", True, active_theme.color, BLACK)
            screen.blit(lc_surf, (WIDTH // 2 - lc_surf.get_width() // 2, HEIGHT // 3))
