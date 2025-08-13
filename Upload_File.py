import os
import pickle
import mimetypes
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.file']

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

def upload_file_to_drive(file_path):
    """Uploads a file to the root of Google Drive. Replaces JSON if it exists."""
    try:
        service = authenticate_google_drive()
        file_name = os.path.basename(file_path)

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        media = MediaFileUpload(file_path, mimetype=mime_type)

        if file_name.endswith("_Network_ID.json"):
            # Find and delete existing file in Drive root
            results = service.files().list(
                q=f"name='{file_name}' and trashed=false",
                spaces='drive',
                fields='files(id, name)',
            ).execute()
            for file in results.get('files', []):
                service.files().delete(fileId=file['id']).execute()
                print(f"🗑️ Deleted old JSON file: {file['name']}")

            # Upload new JSON
            file_metadata = {'name': file_name}
            uploaded = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"✅ Uploaded JSON: {file_name} (ID: {uploaded.get('id')})")
        else:
            print(f"⚠️ Skipped unknown file type: {file_name}")

    except HttpError as error:
        print(f"❌ An HTTP error occurred: {error}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
