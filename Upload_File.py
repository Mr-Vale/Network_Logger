import os
import pickle
import mimetypes
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_NAME = "Raspberry_PI_Network_Identification"

# All project files stored under ~/Network_Logger
BASE_DIR = os.path.expanduser("~/Network_Logger")
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

def authenticate_google_drive():
    """Authenticate using pre-generated token & credentials, no browser fallback."""
    if not os.path.exists(TOKEN_PATH):
        raise RuntimeError(f"❌ token.pickle not found at: {TOKEN_PATH}")
    if not os.path.exists(CREDS_PATH):
        raise RuntimeError(f"❌ credentials.json not found at: {CREDS_PATH}")

    with open(TOKEN_PATH, 'rb') as token:
        creds = pickle.load(token)

    if creds and creds.expired:
        if creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError("❌ Token expired and no refresh token available.")

    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name):
    """Find existing folder or create a new one on Google Drive."""
    results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed = false",
        spaces='drive',
        fields='files(id, name)',
    ).execute()
    items = results.get('files', [])

    if items:
        return items[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def upload_file_to_drive(file_path, skip_if_exists=False):
    try:
        service = authenticate_google_drive()
        folder_id = get_or_create_folder(service, FOLDER_NAME)
        file_name = os.path.basename(file_path)

        # Check for existing file in Drive folder
        results = service.files().list(
            q=f"name='{file_name}' and '{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name)',
        ).execute()
        items = results.get('files', [])

        if skip_if_exists and items:
            print(f"⚠️ Skipping upload: '{file_name}' already exists in Google Drive folder.")
            return

        # Delete old file (for JSON or EXE if allowed)
        for file in items:
            service.files().delete(fileId=file['id']).execute()
            print(f"🗑️ Deleted existing file: {file['name']} (ID: {file['id']})")

        # Upload new file
        mime_type, _ = mimetypes.guess_type(file_path)
        media = MediaFileUpload(file_path, mimetype=mime_type)

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"✅ Uploaded {file_name} to Google Drive folder '{FOLDER_NAME}' (ID: {uploaded.get('id')})")

    except HttpError as error:
        print(f"❌ HTTP error occurred: {error}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

def main():
    hostname = os.uname().nodename
    json_file = os.path.join(BASE_DIR, f"{hostname}_Network_ID.json")
    exe_file = os.path.join(BASE_DIR, "RaspPI Network Info Viewer.exe")

    # Always upload and replace the JSON file
    upload_file_to_drive(json_file)

    # Only upload the EXE file if not already present
    if os.path.exists(exe_file):
        upload_file_to_drive(exe_file, skip_if_exists=True)
    else:
        print(f"ℹ️ Skipped EXE upload: '{exe_file}' not found.")

if __name__ == "__main__":
    main()
