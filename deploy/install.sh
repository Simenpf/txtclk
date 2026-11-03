
#!/bin/bash
set -e

PROJECT_DIR="/opt/txtclk"
SERVICE_NAME="txtclk"
SERVICE_TEMPLATE="$PROJECT_DIR/deploy/systemd/$SERVICE_NAME.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# Check that we're running from the expected installation
if [ ! -f "$PROJECT_DIR/pyproject.toml" ]; then
    echo "Error: Project not found at $PROJECT_DIR"
    exit 1
fi

# Current user
PI_USER="$(whoami)"

# Locate uv
UV_PATH="$(command -v uv)"

if [ -z "$UV_PATH" ]; then
    echo "Error: uv not found. Install uv first."
    exit 1
fi

echo "Installing systemd service..."
echo "User: $PI_USER"
echo "Project: $PROJECT_DIR"
echo "uv: $UV_PATH"

# Generate service file from template
sed \
    -e "s|__USER__|$PI_USER|g" \
    -e "s|__UV_PATH__|$UV_PATH|g" \
    "$SERVICE_TEMPLATE" \
    | sudo tee "$SERVICE_FILE" > /dev/null

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

echo "Service installed and started!"
