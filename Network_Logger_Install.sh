#!/bin/bash

# Exit on error
set -e

BASE_DIR="$HOME/Network_Logger"
HISTORY_DIR="$BASE_DIR/network_history"
REPO_URL="https://github.com/Mr-Vale/Network_Logger"
SERVICE_NAME="network_logger.service"
VENV_DIR="$BASE_DIR/venv"

echo ""
echo "🐙 Cloning repo..."
if [ ! -d "$BASE_DIR/.git" ]; then
    git clone "$REPO_URL" "$BASE_DIR"
else
    echo "Repo already cloned, skipping."
fi

echo ""
echo "📁 Creating required directories..."
mkdir -p "$HISTORY_DIR"

# ✅ Install required system packages
echo ""
echo "📦 Installing system Python and venv dependencies..."
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-netifaces

# ✅ Create virtual environment
echo ""
echo "🐍 Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

# ✅ Activate and install Python dependencies
echo ""
echo "📦 Installing Python packages into virtual environment..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install \
    netifaces \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib
deactivate

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

echo "=================================================================== "
echo ""
while true; do
    read -p "Please Enter desired hostname for this Raspberry Pi: " NEW_HOSTNAME
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

echo "You may see an error 'unable to resolve host' this is normal"
echo ""
echo "..."
sleep 5

echo ""
echo "🧹 Ensuring /etc/hosts maps hostname correctly..."
if grep -q "^127\.0\.1\.1" /etc/hosts; then
    sudo sed -i "s/^127\.0\.1\.1.*/127.0.1.1    $NEW_HOSTNAME/" /etc/hosts
else
    echo "127.0.1.1    $NEW_HOSTNAME" | sudo tee -a /etc/hosts > /dev/null
fi

echo "=================================================================== "
echo ""
echo "📝 Enter a description for this device:"
read -p "> " DESCRIPTION

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
ExecStart=$VENV_DIR/bin/python $BASE_DIR/01_network_logger.py
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
echo "" 
echo "=================================================================== "
echo ""
echo "Remeber to copy accross the upload credentials to $BASE_DIR"
echo ""
read -n 1 -s -r -p "Press any key to continue..."
echo
 
