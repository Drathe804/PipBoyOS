# system/theme.py
import json
import os

class PipTheme:
    def __init__(self):
        self.settings_file = "theme_settings.json" # The "sticky note" file
        
        # Fallback defaults
        self.mode = "DEFAULT"
        self.custom_rgb = [0, 255, 0] 
        self.color = (20, 255, 20)
        self.walk_sprite = "assets/idle-walking"
        
        # Read the sticky note on boot!
        self.load_settings()


    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    self.mode = data.get("mode", "DEFAULT")
                    self.custom_rgb = data.get("custom_rgb", [0, 255, 0])
            except Exception as e:
                print(f"Error loading theme: {e}")
        
        # Apply whatever we just loaded
        self.apply_theme(self.mode, save=False)

    def save_settings(self):
        # Write the current settings to the sticky note
        try:
            with open(self.settings_file, "w") as f:
                json.dump({"mode": self.mode, "custom_rgb": self.custom_rgb}, f)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def apply_theme(self, mode_name, save=True):
        self.mode = mode_name
        
        if self.mode == "DEFAULT":
            self.color = (20, 255, 20) 
            self.walk_sprite = "assets/idle-walking"
            
        elif self.mode == "BARBIE":
            self.color = (255, 51, 153) 
            self.walk_sprite = "assets/barbie-walking" 
            
        elif self.mode == "CUSTOM":
            self.color = tuple(self.custom_rgb)
            # You can map CUSTOM to a specific sprite later if you want!
            self.walk_sprite = "assets/idle-walking"

        # Save the choice so it remembers for next time
        if save:
            self.save_settings()

    def update_custom_color(self, r, g, b):
        self.custom_rgb = [r, g, b]
        if self.mode == "CUSTOM":
            self.color = tuple(self.custom_rgb)
        
        # Save the exact RGB sliders
        self.save_settings()

# Create a single global instance that everything can share
active_theme = PipTheme()
