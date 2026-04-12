# Pip-Boy OS

A Fallout-inspired wearable operating system built with Python and Raspberry Pi, combining immersive UI design with real-world functionality like mapping, radio communication, and modular mini-games.

---

## 🎬 Demo

> ⚡ 23-second demo showcasing UI navigation, dynamic themes, radio TX/RX, mapping, and integrated mini-games

<p align="center">
  <video width="700" controls muted>
    <source src="./assets/demo/pipboy_demo.mp4" type="video/mp4">
  </video>
</p>

---

## 🚀 Overview

Pip-Boy OS is a custom-built interactive system inspired by the Pip-Boy from Fallout.

The goal was not just to recreate the look of the UI, but to build something that behaves like a real device:
- modular systems
- dynamic UI
- interactive elements
- expandable hardware integration

Originally created for cosplay and conventions, it has evolved into a full software + hardware concept.

---

## 🧩 Features

### 🎨 Dynamic Theme System
- Full-screen real-time RGB theming (inspired by Fallout 4)
- Preset themes (default green, Barbie theme)
- Entire UI updates consistently across all systems (including games)

### 📡 Radio System
- Station selection interface
- TX / RX state switching
- Waveform visualization
- Frequency display
- Designed for future real-world communication integration

### 🗺️ Mapping System
- Coordinate-based map rendering
- Zoom and cursor movement
- Persistent markers
- Edge-aware marker display

### 🎮 Mini-Games (Holotapes)
- Atomic Command (playable)
- Red Menace (in progress)
- Holotape-based game system for future NFC integration

### 🎒 Inventory System
- Categorized item lists
- Holotape selection interface
- Context panels and actions

### 🧠 STAT System
- SPECIAL stats display
- Perk framework
- Fallout-style layout and presentation

### ⚙️ Boot System
- RobCo-style startup sequence
- CRT-style UI behavior
- Immersive system loading

---

## 🖼️ Gallery

### 🖥️ Core Interface
<p align="center">
  <img src="./assets/images/pipboy_inventory_holotapes.png" width="700"/>
  <img src="./assets/images/pipboy_special_stats.png" width="700"/>
</p>

---

### 🎨 Dynamic Themes
<p align="center">
  <img src="./assets/images/pipboy_theme_default.png" width="700"/>
  <img src="./assets/images/pipboy_theme_barbie_active.png" width="700"/>
  <img src="./assets/images/pipboy_theme_custom.png" width="700"/>
</p>

---

### 📡 Radio System
<p align="center">
  <img src="./assets/images/pipboy_radio_tx.png" width="700"/>
  <img src="./assets/images/pipboy_radio_rx.png" width="700"/>
</p>

---

### 🎮 Mini-Games
<p align="center">
  <img src="./assets/images/pipboy_atomic_command_action.png" width="700"/>
  <img src="./assets/images/pipboy_atomic_command_wave.png" width="700"/>
</p>

---

### 🗺️ Mapping System
<p align="center">
  <img src="./assets/images/pipboy_map_zoomed_out.png" width="700"/>
  <img src="./assets/images/pipboy_map_zoomed_in.png" width="700"/>
  <img src="./assets/images/pipboy_map_cursor.png" width="700"/>
</p>

---

## 🛠️ Tech Stack

- Python
- Pygame
- Raspberry Pi (target hardware)
- JSON for data/configuration
- Planned: Arduino / microcontrollers, NFC

---

## 🧠 Design Philosophy

- **Immersion first** — UI behaves like a real Pip-Boy
- **System over screens** — everything is connected, not isolated
- **Expandable architecture** — built to grow with hardware and features
- **Fun + functional** — gamifying real-world interactions

---

## ⚔️ Challenges Solved

- Maintaining consistent UI across dynamic theme changes  
- Handling coordinate-based map rendering with persistent markers  
- Designing a believable OS-style interface instead of static screens  
- Simulating radio transmission states visually  
- Integrating games into a cohesive system instead of standalone apps  

---

## 🔮 Future Plans

- NFC holotapes (physical game/media loading)
- Wearable Pip-Boy casing
- Rotary encoder / hardware controls
- Real radio communication modules
- Health/stat integration via smartwatch APIs
- Expanded quest/log systems

---

## ▶️ Running the Project

```bash
python PipBoyOS.py
