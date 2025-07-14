#!/usr/bin/env python3

import os
import json
import time
import socket
import uuid
from datetime import datetime
from Upload_File import upload_file_to_drive  # Import the uploader

# CONFIGURATION
BASE_DIR = os.path.expanduser("~/Network_Logger")
HISTORY_DIR = os.path.join(BASE_DIR, "network_history")
UPLOAD_TO_DRIVE = False  # Set to True once Google Drive integration is ready
GOOGLE_CREDENTIALS = None  # Placeholder for future credentials
DELAY_AT_STARTUP_SEC = 20  # Delay to allow network connection to stabilize

# Ensure folders exist
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
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

def save_log():
    metadata = load_metadata()
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "mac": get_mac(),
        "ip": get_ip(),
        "hostname": metadata["hostname"],
        "description": metadata["description"]
    }

    filename = os.path.join(HISTORY_DIR, f"{metadata['hostname']}_Network_ID.json")
    if os.path.exists(filename):
        with open(filename, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(log_entry)

    with open(filename, "w") as f:
        json.dump(history, f, indent=4)

    if UPLOAD_TO_DRIVE:
        upload_file_to_drive(filename, GOOGLE_CREDENTIALS)

def main():
    time.sleep(DELAY_AT_STARTUP_SEC)
    while True:
        save_log()
        time.sleep(10)  # Run hourly

if __name__ == "__main__":
    main()
