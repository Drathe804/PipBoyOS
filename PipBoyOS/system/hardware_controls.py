# system/hardware_controls.py
import pygame

try:
    from gpiozero import RotaryEncoder, Button
    PI_HARDWARE = True
except ImportError:
    PI_HARDWARE = False
    print("GPIO libraries not found. Hardware controls disabled.")

class PipBoyHardware:
    def __init__(self):
        if PI_HARDWARE:
            # ==========================================
            # ENCODER 1: MAIN TABS (Left / Right)
            # ==========================================
            # Example Pins: CLK=17, DT=18, SW=27
            self.enc_tabs = RotaryEncoder(17, 18, max_steps=0)
            self.enc_tabs.when_rotated_clockwise = self.inject_right
            self.enc_tabs.when_rotated_counter_clockwise = self.inject_left
            
            # Pushing the Tab dial acts as our ENTER button
            self.btn_tabs = Button(27, pull_up=True, bounce_time=0.1)
            self.btn_tabs.when_pressed = self.inject_enter

            # ==========================================
            # ENCODER 2: SUB-TABS (Up / Down)
            # ==========================================
            # Example Pins: CLK=22, DT=23 (No button needed for this one)
            self.enc_subtabs = RotaryEncoder(22, 23, max_steps=0)
            self.enc_subtabs.when_rotated_clockwise = self.inject_down
            self.enc_subtabs.when_rotated_counter_clockwise = self.inject_up

            # ==========================================
            # ENCODER 3: LIST SCROLLING (W / S)
            # ==========================================
            # Example Pins: CLK=24, DT=25 (No button needed)
            # In PipBoyOS.py, W moves the index UP (-1) and S moves it DOWN (+1)
            self.enc_scroll = RotaryEncoder(24, 25, max_steps=0)
            self.enc_scroll.when_rotated_clockwise = self.inject_s
            self.enc_scroll.when_rotated_counter_clockwise = self.inject_w

            # ==========================================
            # THE PHYSICAL POWER BUTTON
            # ==========================================
            # Example Pin: 26
            # We set a 3-second hold time for the hard quit
            self.power_btn = Button(26, pull_up=True, bounce_time=0.1, hold_time=3.0)
            
            # Quick Tap = Sleep Mode (P key)
            self.power_btn.when_pressed = self.inject_p 
            # Held for 3 seconds = Hard Quit (F12 key)
            self.power_btn.when_held = self.inject_f12

    # ==========================================
    # EVENT INJECTION HELPERS
    # ==========================================
    def inject_right(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))

    def inject_left(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))

    def inject_down(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))

    def inject_up(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
        
    def inject_s(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))

    def inject_w(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))

    def inject_enter(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        
    def inject_p(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
        
    def inject_f12(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F12))
