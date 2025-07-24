#!/usr/bin/env python3

import os
import json
import time
import socket
import uuid
from datetime import datetime
from Upload_File import upload_file_to_drive  # Ensure this exists and is working

# CONFIGURATION
BASE_DIR = os.path.expanduser("~/Network_Logger")
HISTORY_DIR = BASE_DIR
UPLOAD_TO_DRIVE = True
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")
EXE_FILENAME = "RaspPI Network Info Viewer.exe"
DELAY_AT_STARTUP_SEC = 120


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
        "timestamp": int(time.time()),
        "mac": get_mac(),
        "ip": get_ip(),
        "interface": get_interface(),
        "hostname": metadata["hostname"],
        "description": metadata["description"]
    }

    json_filename = f"{metadata['hostname']}_Network_ID.json"
    json_path = os.path.join(HISTORY_DIR, json_filename)

    try:
        with open(json_path, "w") as f:
            json.dump(log_entry, f, indent=4)

        print(f"[{datetime.now().isoformat()}] ✅ Log saved to: {json_path}")

        if UPLOAD_TO_DRIVE:
            # Upload the JSON file (always replace)
            upload_file_to_drive(json_path, TOKEN_PATH)

            # Upload the EXE file only once if not already on Drive
            exe_path = os.path.join(BASE_DIR, EXE_FILENAME)
            if os.path.exists(exe_path):
                upload_file_to_drive(exe_path, TOKEN_PATH)

    except Exception as e:
        print(f"❌ Error during logging or upload: {e}")

def main():
    print(f"📡 Network logger starting, waiting {DELAY_AT_STARTUP_SEC} seconds for network...")
    time.sleep(DELAY_AT_STARTUP_SEC)
    print("✅ Starting 30-minute logging loop...")

    while True:
        save_log()
        time.sleep(1800)

if __name__ == "__main__":
    main()
