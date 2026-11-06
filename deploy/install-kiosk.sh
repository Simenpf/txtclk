#!/bin/bash
set -e

PROJECT_DIR="/opt/txtclk"
KIOSK_DIR="$PROJECT_DIR/deploy/kiosk"
AUTOSTART_DIR="$HOME/.config/labwc"
AUTOSTART_FILE="$AUTOSTART_DIR/autostart"

echo "Installing Chromium kiosk..."

# Install Chromium and curl
sudo apt update
sudo apt install -y chromium curl unclutter

# Ensure labwc configuration directory exists
mkdir -p "$AUTOSTART_DIR"

# Add our autostart configuration
touch "$AUTOSTART_FILE"

# Avoid adding duplicate entries
if ! grep -q "txtclk kiosk" "$AUTOSTART_FILE"; then
    cat >> "$AUTOSTART_FILE" <<EOF

# txtclk kiosk
$KIOSK_DIR/start-kiosk.sh &
EOF
fi

chmod +x "$KIOSK_DIR/start-kiosk.sh"

echo "Kiosk installed!"
echo "Autostart configured at: $AUTOSTART_FILE"