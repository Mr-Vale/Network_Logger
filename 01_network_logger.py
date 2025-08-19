import os
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
print("⏳ Waiting 60 seconds before starting logging...")
time.sleep(60)

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
        import json
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {"hostname": "Unknown", "description": "Unknown device"}

def main():
    metadata = load_metadata()
    hostname = metadata.get("hostname", "Unknown")

    log_filename = f"{hostname}_Network_Log.txt"
    log_filepath = os.path.join(BASE_DIR, log_filename)

    last_ip = None  # Track last known IP

    while True:
        current_ip = get_ip_address()

        # Only log if IP has changed
        if current_ip != last_ip and current_ip is not None:
            data_line = (
                f"------------------------------------------------------------------------------- \n"
                f"[{datetime.datetime.now().isoformat()}] "
                f"Host: {hostname}\n"
                f"Desc: {metadata.get('description','')}\n"
                f"MAC: {get_mac_address()}, "
                f"IP: {current_ip}, "
                f"Interface: {get_interface()}\n"
                f"------------------------------------------------------------------------------- \n"
            )

            # Append to log file
            with open(log_filepath, "a") as f:
                f.write(data_line)

            print(f"✅ Logged change to {log_filepath}")

            # Upload updated log to Google Drive
            try:
                upload_file_to_drive(log_filepath)
                print(f"☁️ Uploaded {log_filename} to Google Drive")
            except Exception as e:
                print(f"❌ Failed to upload {log_filename}: {e}")

            last_ip = current_ip  # Update last known IP

        time.sleep(900)  # Check every 15 minutes

if __name__ == "__main__":
    main()
