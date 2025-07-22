#!/usr/bin/env python3

import os
import json
import time
import socket
import uuid
from datetime import datetime
from Upload_File import upload_file_to_drive  # Make sure this exists and is working

# CONFIGURATION
BASE_DIR = os.path.expanduser("~/Network_Logger")
HISTORY_DIR = os.path.join(BASE_DIR, "network_history")
UPLOAD_TO_DRIVE = True  # ⬅️ Set True to enable uploads
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")  # Location of your pre-generated token
DELAY_AT_STARTUP_SEC = 120

# Ensure folders exist
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unavailable"

def get_mac():
    try:
        mac = uuid.getnode()
        return ':'.join(f'{(mac >> ele) & 0xff:02x}' for ele in range(40, -8, -8))
    except:
        return "Unavailable"

def load_metadata():
    meta_file = os.path.join(BASE_DIR, "device_metadata.json")
    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            return json.load(f)
    return {"hostname": socket.gethostname(), "description": "N/A"}

def get_interface():
    try:
        import netifaces
        gateways = netifaces.gateways()
        return gateways['default'][netifaces.AF_INET][1]
    except Exception:
        return "Unknown"

def save_log():
    metadata = load_metadata()
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "mac": get_mac(),
        "ip": get_ip(),
        "interface": get_interface(),
        "hostname": metadata["hostname"],
        "description": metadata["description"]
    }

    filename = os.path.join(HISTORY_DIR, f"{metadata['hostname']}_Network_ID.json")

    try:
        with open(filename, "w") as f:
            json.dump(log_entry, f, indent=4)
        print(f"[{datetime.now().isoformat()}] Log saved to: {filename}")

        if UPLOAD_TO_DRIVE:
            upload_file_to_drive(filename, TOKEN_PATH)

    except Exception as e:
        print(f"❌ Error during logging or upload: {e}")

def main():
    print(f"📡 Network logger starting, waiting {DELAY_AT_STARTUP_SEC} seconds for network...")
    time.sleep(DELAY_AT_STARTUP_SEC)
    print("✅ Starting hourly logging loop...")

    while True:
        save_log()
        time.sleep(1800)  # 30 minutes

if __name__ == "__main__":
    main()
