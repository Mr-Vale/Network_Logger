import os
import pickle
import mimetypes
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Google Drive API settings
SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = '1my_IEvjcIxUgUBlKN-GCfrOMm3_0Cpu9'  # Upload target folder ID

# All project files stored under ~/Network_Logger
BASE_DIR = os.path.expanduser("~/Network_Logger")
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

def authenticate_google_drive():
    """Authenticate with Google Drive using only token.pickle (no credentials.json)."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "token.pickle")

    # Load existing token
    if os.path.exists(token_path):
        print(f"🔑 Using token from {token_path}")
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    else:
        raise FileNotFoundError(
            f"❌ token.pickle not found at {token_path}\n"
            "Run the OAuth flow on another machine to generate it, "
            "then copy it here."
        )

    # Build the service
    try:
        service = build("drive", "v3", credentials=creds)
        return service
    except Exception as e:
        raise RuntimeError(f"Google Drive authentication failed: {e}")

def upload_file_to_drive(file_path):
    """Uploads a file to the specific Google Drive folder. Overwrites if exists."""
    try:
        service = authenticate_google_drive()
        file_name = os.path.basename(file_path)

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        media = MediaFileUpload(file_path, mimetype=mime_type)

        # Look for existing file with same name in the target folder
        results = service.files().list(
            q=f"name='{file_name}' and '{FOLDER_ID}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name)',
        ).execute()

        existing_files = results.get('files', [])

        if existing_files:
            # Update (overwrite) the existing file
            file_id = existing_files[0]['id']
            updated = service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            print(f"♻️ Overwritten: {file_name} (ID: {updated.get('id')})")
        else:
            # Upload as a new file in the folder
            file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
            uploaded = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"✅ Uploaded new file: {file_name} (ID: {uploaded.get('id')})")

    except HttpError as error:
        print(f"❌ An HTTP error occurred: {error}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
