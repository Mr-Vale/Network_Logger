
# 📡 Network_Logger

**Network_Logger** is a lightweight Raspberry Pi-based network identification logger. It records key details about the device (MAC address, IP address, hostname, and a user-provided description) every hour and optionally uploads this information to Google Drive.

This is useful for managing multiple Raspberry Pi units across a network or property, especially when each device has a unique role or physical location.

## ⚙️ Features

- Logs:
  - MAC address
  - IP address
  - Hostname
  - Description
  - Timestamp
- Stores logs in a device-specific JSON file
- Designed to run automatically at boot via `systemd`
- Placeholder uploader module for future Google Drive support
- Works as a dependency in other Raspberry Pi install scripts

## 🚀 Installation

Run the install script on your Raspberry Pi:

```bash
bash <(curl -s https://raw.githubusercontent.com/Mr-Vale/Network_Logger/main/Network_Logger_Install.sh)
```

The script will:

1. Create the `~/Network_Logger` folder and subdirectories
2. Clone this repository
3. Ask you to set a new hostname
4. Ask you for a device description
5. Save metadata and create a `systemd` service
6. Enable and start the logger at boot (after a 2-minute delay)

## 🕒 Logging Behavior

Once installed, `01_network_logger.py` will run at boot (after ~120 seconds) and log network data every hour to:

```
~/Network_Logger/network_history/<hostname>_Network_ID.json
```

## ☁️ Google Drive Upload (Future Support)

The script currently includes a placeholder upload module (`02_Upload_file.py`). Google Drive integration will be available in a future release using OAuth2 or service accounts.

To simulate uploads, you can set this flag in `01_network_logger.py`:

```python
UPLOAD_TO_DRIVE = True
```

## 📌 Use as a Dependency

To include this logger in other installation scripts, simply run:

```bash
bash ~/Network_Logger/Network_Logger_Install.sh
```

Or clone and call it from your own repo like:

```bash
git clone https://github.com/Mr-Vale/Network_Logger ~/Network_Logger
bash ~/Network_Logger/Network_Logger_Install.sh
```

---

## 📁 Directory Structure

```
~/Network_Logger/
├── 01_network_logger.py       # Main hourly logging script
├── Upload_File.py          # (Optional) Google Drive uploader scaffold
├── Network_Logger_Install.sh  # Setup and installation script
├── device_metadata.json       # Stores hostname and description
└── network_history/           # Folder for JSON logs
```
---

## 📄 License

MIT License – free for personal or commercial use.
