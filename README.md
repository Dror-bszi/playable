# Project Structure for PlayAble - Movement-Assisted Controller

# Root Directory: playable/

# ─── Core Logic ─────────────────────────────────────────────
core/
├── __init__.py
├── gestures.py              # MediaPipe gesture detection logic
├── mappings.py              # Gesture-to-button mapping
├── controller.py            # Local trigger interface for motion-mapped buttons
├── threshold_manager.py     # Adaptive sensitivity & thresholds

# ─── UI Components ─────────────────────────────────────────
ui/
├── __init__.py
├── visualizer.py            # Tkinter GUI for button states
├── wifi_setup.py            # GUI button to change Wi-Fi

# ─── Utility Modules ───────────────────────────────────────
utils/
├── __init__.py
├── video_capture.py         # Threaded camera stream
├── logger.py                # Movement and event logger

# ─── Configuration Files ───────────────────────────────────
config/
├── settings.yaml            # Global system settings
├── thresholds.yaml          # Gesture thresholds and auto-adjust data

# ─── Runtime and Logs ──────────────────────────────────────
logs/                        # Gesture log CSVs
captures/                    # Optional image capture folder
models/                      # For storing AI/ML models (future use)
output/                      # Any processed output like STL files (if extended)

# ─── Web Interface (Local Network GUI) ─────────────────────
web/
├── __init__.py
├── server.py                # Flask server to manage settings/logs
├── templates/               # HTML templates for web UI
├── static/                  # JS/CSS for frontend behavior and styling

# ─── Remote Play Integration ───────────────────────────────
remote/
├── __init__.py
├── psrc_runner.py           # Launch and manage PSRC session
├── input_bridge.py          # Inject 1–3 motion-triggered button presses to PS5 (rest via physical controller)
├── controller_bridge.py     # Read inputs from DualSense and forward allowed inputs to PSRC
├── auth.json                # Stored PSRC device pairing credentials

# ─── Scripts & Main Entry ─────────────────────────────────
main.py                      # App entry point
requirements.txt             # Python dependencies
install.sh                   # Full setup script for Raspberry Pi OS Lite
README.md                  # Project overview and setup guide


# ─── README.md Content ─────────────────────────────────────────

# PlayAble: Movement-Assisted PS5 Controller for Rehabilitation

PlayAble is a hybrid gesture-to-game control system designed for rehabilitation. It enables 1–3 specific PlayStation buttons (e.g., `X`, `O`, `R1`) to be triggered by patient movements — like a leg raise or a mouth open — while allowing the rest of the gameplay to be controlled by a standard PS5 controller. This approach helps make physical therapy engaging through interactive gaming.

The system runs on a Raspberry Pi and uses a camera for motion detection, MediaPipe for pose estimation, and PSRC (a Remote Play client) to inject virtual controller inputs to the PS5 over Wi-Fi.

---

## 🚀 Features
- 🎮 Hybrid input: Physical controller + gesture-activated buttons
- 🔄 Real-time gesture detection with MediaPipe
- 🧠 Adaptive threshold tuning based on effort
- 🌐 Web-based interface for configuration
- 📶 Captive portal Wi-Fi setup
- 🧩 Modular and customizable for clinics or home use

---

## 🧭 How the System Flows
1. **Camera Input**: Captures live video feed.
2. **Gesture Detection (`core/gestures.py`)**: Extracts body landmarks using MediaPipe.
3. **Mapping & Thresholding**:
   - Compares landmark positions to gesture thresholds (`core/threshold_manager.py`)
   - Converts gestures into logical button triggers (`core/mappings.py`)
4. **Button Injection**:
   - Motion-triggered buttons are sent to the PS5 via PSRC (`remote/input_bridge.py`)
   - DualSense inputs are filtered through the Pi and forwarded (`remote/controller_bridge.py`)
5. **Feedback**:
   - GUI displays visual status (`ui/visualizer.py`)
   - Logs attempts and outcomes for therapist review (`utils/logger.py`)

---

## 📁 Folder Overview (Detailed)

### `core/`
- Motion analysis, gesture recognition, and mappings
- Handles threshold logic and input decisions

### `remote/`
- Starts and manages PSRC sessions to the PS5
- Injects gesture-based button events
- Filters DualSense input, blocking buttons controlled by gestures

### `ui/`
- Tkinter-based visual feedback
- Local GUI for real-time state and manual Wi-Fi change

### `web/`
- Flask-based web server
- Provides therapists a configuration portal (thresholds, mappings, logs)

### `utils/`
- Video stream capture via threads
- Logging gesture success/failures

### `config/`
- YAML-based settings for gesture thresholds, system behavior, and mappings

### `services/`
- `systemd` services to auto-start PlayAble and Wi-Fi portal on boot

### `docs/`
- In-depth technical breakdowns, deployment guide, and customization tips

### Root files
- `main.py`: Launch point
- `install.sh`: One-shot setup script
- `requirements.txt`: Python dependencies
- `README.md`: You’re reading it!

---

## 📦 System Requirements
- Raspberry Pi (Pi 4 or Zero 2 W recommended)
- Raspberry Pi OS Lite (64-bit)
- USB or Pi Camera module
- PS5 with Remote Play enabled
- DualSense controller connected to the Pi via Bluetooth

---

## 🧪 To Get Started
```bash
git clone https://github.com/yourusername/playable.git
cd playable
chmod +x install.sh
./install.sh
```

---

## 📚 Next Steps
- Learn the architecture: `docs/architecture.md`
- See how controller + motion are integrated: `docs/pairing_and_input.md`
- Configure for your use case: `docs/customization.md`
- Deploy to real environments: `docs/deployment.md`

PlayAble is built for flexibility, precision, and meaningful rehabilitation through play.

# PlayAble: Movement-Assisted PS5 Controller for Rehabilitation

PlayAble is a gesture-enhanced controller system designed to assist physical rehabilitation by allowing 1–3 specific PlayStation buttons (e.g., `X`, `O`, `R1`) to be triggered through therapist-guided exercises. The rest of the game is controlled normally using a physical DualSense controller.

The system runs on a Raspberry Pi using a camera and integrates with the PS5 through Remote Play (via PSRC). Gestures are detected using MediaPipe, and the Pi acts as a filter that forwards only allowed controller inputs.

---

## Features
- 🎮 Hybrid control: Regular controller + motion-triggered buttons
- 🧠 Adaptive gesture sensitivity and learning
- 🖥️ Local GUI for live feedback
- 🌐 Web interface for remote configuration
- 📶 Portable with Wi-Fi setup mode
- 🔗 PSRC integration for direct PS5 input

---

## How It Works
1. The user plays with a normal PS5 controller.
2. Specific gestures (e.g. leg lift, mouth open) are detected.
3. Those gestures trigger button presses via Remote Play.
4. The Pi blocks those same buttons from being used on the DualSense.

---

## Quick Start
```bash
git clone https://github.com/yourusername/playable.git
cd playable
chmod +x install.sh
./install.sh
```

---

## Folder Overview
- `core/` – Gesture detection, input mapping, threshold logic
- `remote/` – PSRC and controller bridging
- `ui/` – Tkinter interface
- `web/` – Web interface for therapists
- `config/` – YAML settings and thresholds
- `services/` – Auto-start systemd services
- `docs/` – Technical and usage documentation

---

## Requirements
- Raspberry Pi OS Lite
- Pi Camera or USB webcam
- PS5 + Remote Play enabled
- DualSense controller (connected via Bluetooth to Pi)

---

For more details, see `docs/architecture.md` and `docs/deployment.md`.

# ─── System Services ───────────────────────────────────────
services/
├── playable.service         # systemd unit to auto-launch PlayAble
├── wifi-connect.service     # Optional: launch captive portal if no Wi-Fi

# ─── Documentation ─────────────────────────────────────────
docs/
├── architecture.md          # System flow, component interaction
├── pairing_and_input.md     # How controller and gestures integrate
├── deployment.md            # Installation and field setup instructions
├── customization.md         # Therapist config, gesture mapping guide
└── README.md                # Project overview, goals, and directory reference