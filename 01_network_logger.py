import os
import time
import datetime
import netifaces
import json
from Upload_File import upload_file_to_drive  # Ensure this exists and works

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_FILE = os.path.join(BASE_DIR, 'device_metadata.json')
STATE_FILE = os.path.join(BASE_DIR, 'last_network_state.json')

# Delay at startup
print("⏳ Waiting 60 seconds before starting logging...")
time.sleep(60)

def load_metadata():
    """Load device metadata from file."""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {"hostname": "Unknown", "description": "Unknown device"}

def get_all_connected_interfaces():
    """Returns list of dicts with info for all connected interfaces."""
    connected = []
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        mac = addrs.get(netifaces.AF_LINK, [{}])[0].get('addr', 'N/A')
        ip_info = addrs.get(netifaces.AF_INET, [{}])
        ip = ip_info[0].get('addr', None) if ip_info else None
        if ip and ip != '127.0.0.1':
            connected.append({
                'interface': iface,
                'mac': mac,
                'ip': ip
            })
    return connected

def load_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return []

def save_current_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def network_state_changed(current, previous):
    # Order-independent comparison
    return set(json.dumps(x, sort_keys=True) for x in current) != set(json.dumps(x, sort_keys=True) for x in previous)

def log_interfaces(current_state, hostname, metadata, log_filepath):
    with open(log_filepath, "a") as f:
        for iface_info in current_state:
            data_line = (
                f"-------------------------------------------------------------------------------\n"
                f"[{datetime.datetime.now().isoformat()}] "
                f"Host: {hostname}\n"
                f"Desc: {metadata.get('description','')}\n"
                f"Interface: {iface_info['interface']}, "
                f"MAC: {iface_info['mac']}, "
                f"IP: {iface_info['ip']}\n"
                f"-------------------------------------------------------------------------------\n"
            )
            f.write(data_line)

def main():
    metadata = load_metadata()
    hostname = metadata.get("hostname", "Unknown")
    log_filename = f"{hostname}_Network_Log.txt"
    log_filepath = os.path.join(BASE_DIR, log_filename)

    previous_state = load_last_state()
    current_state = get_all_connected_interfaces()

    # After startup delay, always log and upload, and update saved state
    log_interfaces(current_state, hostname, metadata, log_filepath)
    print(f"✅ Log written after startup delay to {log_filepath}")

    save_current_state(current_state)
    try:
        upload_file_to_drive(log_filepath)
        print(f"☁️ Uploaded {log_filename} to Google Drive")
    except Exception as e:
        print(f"❌ Failed to upload {log_filename}: {e}")

    # Main loop: only log/upload if state changes
    while True:
        time.sleep(900)  # Wait 15 minutes
        previous_state = load_last_state()
        current_state = get_all_connected_interfaces()
        if network_state_changed(current_state, previous_state):
            log_interfaces(current_state, hostname, metadata, log_filepath)
            print(f"✅ Network change detected; log written to {log_filepath}")
            save_current_state(current_state)
            try:
                upload_file_to_drive(log_filepath)
                print(f"☁️ Uploaded {log_filename} to Google Drive")
            except Exception as e:
                print(f"❌ Failed to upload {log_filename}: {e}")
        else:
            print(f"[{datetime.datetime.now().isoformat()}] No network changes detected.")

if __name__ == "__main__":
    main()
