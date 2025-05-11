# PlayAble for Raspberry Pi Zero 2W

This is the PlayAble system optimized for Raspberry Pi Zero 2W with AI camera support.

## Prerequisites

- Raspberry Pi Zero 2W
- Raspberry Pi AI Camera (IMX500)
- Raspberry Pi OS (64-bit)
- Internet connection
- Power supply (5V, 2.5A recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/PlayAble.git
   cd PlayAble
   ```

2. **Run the setup script**
   ```bash
   sudo chmod +x setup.sh
   sudo ./setup.sh
   ```

3. **Reboot the system**
   ```bash
   sudo reboot
   ```

4. **Test the camera**
   ```bash
   python3 test_camera.py
   ```

## Hardware Setup

1. Connect the AI camera to the Raspberry Pi Zero 2W:
   - Use the smaller ribbon cable that came with the camera
   - Connect to the camera connector on the Pi
   - Make sure the cable is properly seated and the tab is down

2. Position the camera:
   - Mount the camera so it can see the user's upper body
   - Ensure good lighting in the room
   - Keep the camera stable

## Running PlayAble

After installation and setup:

1. Start the system:
   ```bash
   sudo python3 main.py
   ```

2. Access the web interface:
   - Open a web browser
   - Navigate to `http://[raspberry-pi-ip]:5000`

## Troubleshooting

If you encounter issues:

1. **Camera not detected**
   - Check camera connection
   - Verify camera permissions
   - Run `vcgencmd get_camera` to check camera status

2. **Permission issues**
   - Ensure you're in the video and input groups
   - Run `groups` to verify

3. **Performance issues**
   - Close unnecessary applications
   - Ensure adequate power supply
   - Check system temperature with `vcgencmd measure_temp`

## Support

For issues and support, please open an issue on the GitHub repository. 