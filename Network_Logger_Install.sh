#!/bin/bash

set -e

BASE_DIR="$HOME/Network_Logger"
HISTORY_DIR="$BASE_DIR/network_history"
REPO_URL="https://github.com/Mr-Vale/Network_Logger"
SERVICE_NAME="network_logger.service"

echo "  📁 Creating required directories..."
mkdir -p "$HISTORY_DIR"

echo "  🐙 Cloning repo..."
if [ ! -d "$BASE_DIR/.git" ]; then
    git clone "$REPO_URL" "$BASE_DIR"
else
    echo "Repo already cloned, skipping."
fi

echo "  🖥️ Setting hostname..."
read -p "Enter desired hostname for this Raspberry Pi: " NEW_HOSTNAME
sudo hostnamectl set-hostname "$NEW_HOSTNAME"

echo "  📝 Enter a description for this device:"
read -p "> " DESCRIPTION

# Save metadata to JSON file
cat > "$BASE_DIR/device_metadata.json" <<EOF
{
    "hostname": "$NEW_HOSTNAME",
    "description": "$DESCRIPTION"
}
EOF

echo "  🛠️ Creating systemd service..."
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
sudo bash -c "cat > $SERVICE_PATH" <<EOF
[Unit]
Description=Network Logger Service
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/python3 $BASE_DIR/01_network_logger.py
Restart=always
User=$USER
WorkingDirectory=$BASE_DIR

[Install]
WantedBy=multi-user.target
EOF

echo "  🔄 Reloading and enabling service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "  ✅ Network Logger installed and running as $SERVICE_NAME"
