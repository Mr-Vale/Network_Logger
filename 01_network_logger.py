import os
import json
import time
import datetime
import socket
import uuid
import subprocess
from Upload_File import upload_file_to_drive  # Ensure this exists and works

# Base directory for the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_FILE = os.path.join(BASE_DIR, 'device_metadata.json')

# Delay at startup
print("⏳ Waiting 120 seconds before starting logging...")
time.sleep(120)

def get_mac_address():
    """Return the MAC address of the primary network interface."""
    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
    return ':'.join(mac_num[i:i+2] for i in range(0, 11, 2))

def get_ip_address():
    """Return the current IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_addr = s.getsockname()[0]
        s.close()
        return ip_addr
    except:
        return None

def get_interface():
    """Return the name of the network interface used for the IP."""
    try:
        output = subprocess.check_output("ip route get 8.8.8.8", shell=True).decode()
        return output.split("dev")[1].split()[0]
    except:
        return None

def load_metadata():
    """Load device metadata from file."""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {"hostname": "Unknown", "description": "Unknown device"}

def main():
    metadata = load_metadata()
    hostname = metadata.get("hostname", "Unknown")

    json_filename = f"{hostname}_Network_ID.json"
    json_filepath = os.path.join(BASE_DIR, json_filename)

    while True:
        data = {
            "hostname": hostname,
            "description": metadata.get("description", ""),
            "mac_address": get_mac_address(),
            "ip_address": get_ip_address(),
            "interface": get_interface(),
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Save JSON locally
        with open(json_filepath, "w") as f:
            json.dump(data, f, indent=4)

        print(f"✅ Network info saved to {json_filepath}")

        # Upload JSON to Google Drive (always overwrite)
        try:
            upload_file_to_drive(json_filepath, json_filename)
            print(f"☁️ Uploaded {json_filename} to Google Drive")
        except Exception as e:
            print(f"❌ Failed to upload {json_filename}: {e}")

        time.sleep(1800)  # Log every 30 minutes

if __name__ == "__main__":
    main()
