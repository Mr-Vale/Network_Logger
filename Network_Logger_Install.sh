#!/bin/bash

# Exit immediately on error
set -e

BASE_DIR="$HOME/Network_Logger"
HISTORY_DIR="$BASE_DIR/network_history"
REPO_URL="https://github.com/Mr-Vale/Network_Logger"
SERVICE_NAME="network_logger.service"

echo ""
echo "📁 Creating required directories..."
mkdir -p "$HISTORY_DIR"

echo ""
echo "🐙 Cloning repo..."
if [ ! -d "$BASE_DIR/.git" ]; then
    git clone "$REPO_URL" "$BASE_DIR"
else
    echo "Repo already cloned, skipping."
fi

# Function to validate hostname
is_valid_hostname() {
    local hn="$1"
    if [[ ${#hn} -gt 63 ]]; then
        return 1
    elif [[ "$hn" =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$ ]]; then
        return 0
    else
        return 1
    fi
}

# Prompt for hostname until valid
while true; do
    read -p "Enter desired hostname for this Raspberry Pi: " NEW_HOSTNAME
    if is_valid_hostname "$NEW_HOSTNAME"; then
        echo ""
        echo "✅ Hostname valid: $NEW_HOSTNAME"
        break
    else
		echo ""
        echo "❌ Invalid hostname. Use only letters, numbers, and dashes. No spaces. Max 63 characters. Cannot start or end with a dash."
    fi
done

echo ""
echo "🖥️ Setting hostname..."
sudo hostnamectl set-hostname "$NEW_HOSTNAME"

# Update /etc/hosts so sudo can resolve the new hostname
sudo sed -i "s/127.0.1.1.*/127.0.1.1    $NEW_HOSTNAME/" /etc/hosts


# Prompt for description
echo ""
echo "📝 Enter a description for this device:"
read -p "> " DESCRIPTION

# Save metadata to JSON file
cat > "$BASE_DIR/device_metadata.json" <<EOF
{
    "hostname": "$NEW_HOSTNAME",
    "description": "$DESCRIPTION"
}
EOF

echo ""
echo "🛠️ Creating systemd service..."
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

echo ""
echo "🔄 Reloading and enabling service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo ""
echo "✅ Network Logger installed and running as $SERVICE_NAME"
