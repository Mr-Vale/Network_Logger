#!/usr/bin/env python3

import os
import json
import time
import socket
import uuid
from datetime import datetime
from Upload_File import upload_file_to_drive  # Import your uploader scaffold

# CONFIGURATION
BASE_DIR = os.path.expanduser("~/Network_Logger")
HISTORY_DIR = os.path.join(BASE_DIR, "network_history")
UPLOAD_TO_DRIVE = False  # Set to True once Drive upload is ready
GOOGLE_CREDENTIALS = None  # Placeholder
DELAY_AT_STARTUP_SEC = 120  # Wait time at boot (adjust if needed)

# Ensure folders exist
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_ip():
    """Returns the current non-loopback IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Use Google DNS just to resolve outbound interface
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unavailable"

def get_mac():
    """Returns the device MAC address"""
    try:
        mac = uuid.getnode()
        return ':'.join(f'{(mac >> ele) & 0xff:02x}' for ele in range(40, -8, -8))
    except:
        return "Unavailable"

def load_metadata():
    """Loads hostname and description from the device metadata file"""
    meta_file = os.path.join(BASE_DIR, "device_metadata.json")
    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            return json.load(f)
    return {"hostname": socket.gethostname(), "description": "N/A"}

def get_interface():
    """Returns the name of the active network interface (wlan0, eth0, etc.)"""
    try:
        import netifaces
        gateways = netifaces.gateways()
        default_iface = gateways['default'][netifaces.AF_INET][1]
        return default_iface
    except Exception:
        return "Unknown"

def save_log():
    metadata = load_metadata()
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "mac": get_mac(),
        "ip": get_ip(),
        "interface": get_interface(),  # ← add this line
        "hostname": metadata["hostname"],
        "description": metadata["description"]
    }

    filename = os.path.join(HISTORY_DIR, f"{metadata['hostname']}_Network_ID.json")

    try:
        # Overwrite with single latest entry
        with open(filename, "w") as f:
            json.dump(log_entry, f, indent=4)

        print(f"[{datetime.now().isoformat()}] Log saved to: {filename}")

        if UPLOAD_TO_DRIVE:
            upload_file_to_drive(filename, GOOGLE_CREDENTIALS)

    except Exception as e:
        print(f"❌ Error saving log: {e}")

def main():
    print(f"📡 Network logger starting, waiting {DELAY_AT_STARTUP_SEC} seconds for network...")
    time.sleep(DELAY_AT_STARTUP_SEC)
    print("✅ Starting hourly logging loop...")

    while True:
        save_log()
        time.sleep(1800)  # Log every 1/2 hour

if __name__ == "__main__":
    main()
