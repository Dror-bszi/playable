# PlayAble: Movement-Assisted PS5 Controller for Rehabilitation

PlayAble is a hybrid **gesture-to-game control system** designed for physical rehabilitation. It enables specific PlayStation buttons (like `X`, `O`, `R1`) to be triggered by body movements (e.g., a leg lift) while still allowing normal use of a PS5 DualSense controller.

The system runs on a **Raspberry Pi** using a **camera**, integrates with the **PS5** via **Remote Play** (Chiaki/PSRC), and uses **MediaPipe** for real-time gesture detection.

---

## 🎉 Features
- 🏎️ Hybrid control: Physical controller + gesture-triggered buttons
- 🧪 Real-time gesture recognition with MediaPipe
- 💡 Simple web dashboard to monitor system status
- 🚪 Virtual controller input injection via Remote Play (Chiaki or PSRC)
- 📊 Event and error logging

---

## 📊 Project Structure

```plaintext
playable/
├── build/                        # (optional) for build artifacts
├── config/
│   ├── settings.yaml           # Global settings (future use)
│   └── thresholds.yaml         # Gesture thresholds (future use)
├── core/
│   ├── controller.py           # (empty placeholder)
│   ├── gestures.py             # GestureDetector: Calibration and elbow detection
│   ├── mappings.py             # Gesture name ➔ Controller button mapping
│   └── threshold_manager.py    # (empty placeholder)
├── docs/                        # Documentation
├── logs/
│   └── playable_web.log         # Web server and system logs
├── remote/
│   ├── auth.json               # PSRC pairing credentials (for remote play)
│   ├── controller_bridge.py    # (placeholder)
│   ├── input_bridge.py         # (placeholder)
│   ├── ps5_remote_sender.py    # Send button presses to Chiaki/PS5
├── services/
│   ├── playable.service         # Systemd service to auto-start PlayAble
│   └── wifi-connect.service     # (optional) Wi-Fi captive portal (future)
├── ui/
│   ├── controller_bluetooth.py  # Scan and pair Bluetooth controllers
│   ├── controller_live_status.py # Monitor live DualSense controller input
│   └── wifi_setup.py            # (placeholder)
├── utils/
│   ├── logger.py                # (placeholder)
│   ├── pair_controller.expect   # Expect script to auto-pair controllers
│   └── video_capture.py         # (placeholder)
├── web/
│   ├── server.py                # Flask web server for dashboard
│   └── templates/
│       ├── index.html             # Dashboard (camera preview, shutdown, links)
│       ├── controller.html         # Bluetooth controller management
│       └── controller_status.html  # Live controller input view
├── main.py                     # Main application entry point
├── install.sh                  # (placeholder, previous setup script)
├── setup.sh                    # Full environment setup script
├── update.sh                   # Git pull updater script
├── requirements.txt            # Python package dependencies
└── controller_raw_listener.py  # Tool to debug raw controller events
```

---

## 🌐 Web Interface
- **Dashboard**: Live camera stream, shutdown button, navigation links
- **Controller Setup**: Scan, pair, and connect to Bluetooth DualSense
- **Live Controller Status**: View real-time button presses, trigger values, joystick movements

---

## 🛠️ How to Set Up

```bash
# On Raspberry Pi OS Lite (64-bit)
sudo apt update
sudo apt install -y git

# Clone the repo
git clone https://github.com/yourusername/playable.git
cd playable

# Set up the system
chmod +x insatll.sh
./install.sh

# Start PlayAble (run with sudo!)
sudo -E python3 main.py
```

---

## 📅 Future Expansion
- More gestures (e.g., head nod, knee raise)
- Adaptive threshold learning
- Gesture-to-multiple-buttons mapping
- Machine Learning personalized gesture profiles
- Full Wi-Fi captive portal for easier deployment

---

## 🔧 System Requirements
- Raspberry Pi 4 / Zero 2 W recommended
- Raspberry Pi OS Lite (64-bit)
- USB or Pi Camera module
- PS5 with Remote Play enabled
- DualSense controller (connected via Bluetooth)

---

# Let's PlayAble! 🚀
Helping patients reconnect through gaming and movement.