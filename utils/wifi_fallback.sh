#!/bin/bash

# Configuration
SSID="PlayAble_AP"
PASSWORD="playable123"
CHANNEL=1
INTERFACE="wlan0"
IP_ADDRESS="192.168.4.1"
DHCP_RANGE="192.168.4.2,192.168.4.20,255.255.255.0,24h"

# Function to check if we have internet connection
check_internet() {
    ping -c 1 8.8.8.8 >/dev/null 2>&1
    return $?
}

# Function to setup access point
setup_ap() {
    echo "Setting up access point..."
    
    # Install required packages if not present
    if ! command -v hostapd &> /dev/null || ! command -v dnsmasq &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y hostapd dnsmasq
    fi

    # Stop services
    sudo systemctl stop hostapd
    sudo systemctl stop dnsmasq

    # Configure hostapd
    cat > /tmp/hostapd.conf << EOF
interface=$INTERFACE
driver=nl80211
ssid=$SSID
hw_mode=g
channel=$CHANNEL
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$PASSWORD
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

    sudo mv /tmp/hostapd.conf /etc/hostapd/hostapd.conf

    # Configure dnsmasq
    cat > /tmp/dnsmasq.conf << EOF
interface=$INTERFACE
dhcp-range=$DHCP_RANGE
EOF

    sudo mv /tmp/dnsmasq.conf /etc/dnsmasq.conf

    # Configure static IP
    cat > /tmp/dhcpcd.conf << EOF
interface $INTERFACE
    static ip_address=$IP_ADDRESS/24
    nohook wpa_supplicant
EOF

    sudo mv /tmp/dhcpcd.conf /etc/dhcpcd.conf

    # Start services
    sudo systemctl unmask hostapd
    sudo systemctl enable hostapd
    sudo systemctl enable dnsmasq
    sudo systemctl start hostapd
    sudo systemctl start dnsmasq

    echo "Access point setup complete. SSID: $SSID, Password: $PASSWORD"
}

# Function to restore normal WiFi
restore_wifi() {
    echo "Restoring normal WiFi..."
    
    # Stop services
    sudo systemctl stop hostapd
    sudo systemctl stop dnsmasq

    # Remove AP configuration
    sudo rm -f /etc/hostapd/hostapd.conf
    sudo rm -f /etc/dnsmasq.conf
    sudo rm -f /etc/dhcpcd.conf

    # Restart networking
    sudo systemctl restart networking
    sudo systemctl restart dhcpcd

    echo "Normal WiFi restored"
}

# Main loop
while true; do
    if ! check_internet; then
        echo "No internet connection detected"
        setup_ap
    else
        echo "Internet connection available"
        restore_wifi
    fi
    sleep 30  # Check every 30 seconds
done 