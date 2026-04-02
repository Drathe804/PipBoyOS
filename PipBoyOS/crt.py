# crt.py
import pygame
from config import WIDTH, HEIGHT

class CRTFilter:
    def __init__(self):
        # 1. Static Scanlines
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 3):
            pygame.draw.line(self.overlay, (0, 0, 0, 80), (0, y), (WIDTH, y), 1)

        # 2. Rolling Refresh Line
        self.rolling_line = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        self.rolling_line.fill((0, 15, 0, 70))
        self.scanline_y = 0
        self.scanline_speed = 1

    def draw(self, screen):
        # Draw the static scanlines over everything
        screen.blit(self.overlay, (0, 0))
        
        # Update and draw the rolling V-Sync line
        self.scanline_y += self.scanline_speed
        if self.scanline_y > HEIGHT:
            self.scanline_y = -40 
            
        screen.blit(self.rolling_line, (0, self.scanline_y))
