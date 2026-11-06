#!/bin/bash
set -e

PROJECT_DIR="/opt/txtclk"
KIOSK_DIR="$PROJECT_DIR/deploy/kiosk"

AUTOSTART_DIR="$HOME/.config/labwc"
AUTOSTART_FILE="$AUTOSTART_DIR/autostart"
AUTOSTART_SOURCE="$KIOSK_DIR/autostart"

echo "Installing Chromium kiosk..."

# Install Chromium, curl and unclutter.
sudo apt update
sudo apt install -y chromium curl unclutter

# Ensure labwc configuration directory exists.
mkdir -p "$AUTOSTART_DIR"

# Copy the repository autostart file into labwc configuration.
install -m 755 "$AUTOSTART_SOURCE" "$AUTOSTART_FILE"

# Ensure kiosk startup script is executable.
chmod +x "$KIOSK_DIR/start-kiosk.sh"

echo "Kiosk installed!"
echo "Autostart installed from: $AUTOSTART_SOURCE"
echo "Autostart configured at: $AUTOSTART_FILE"