import os
import pickle
import mimetypes
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_NAME = "Raspberry_PI_Network_Identification"

def authenticate_google_drive():
    creds = None
    base_dir = os.path.expanduser('~/Network_Logger')
    token_path = os.path.join(base_dir, 'token.pickle')
    creds_path = os.path.join(base_dir, 'credentials.json')

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif creds and creds.expired:
            raise RuntimeError("❌ Token expired and no refresh token available.")
    else:
        raise RuntimeError("❌ token.pickle not found. Please generate it and place it in ~/Network_Logger")

    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name):
    # Search for the folder
    results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed = false",
        spaces='drive',
        fields='files(id, name)',
    ).execute()
    items = results.get('files', [])

    if items:
        return items[0]['id']  # Return first match
    else:
        # Create the folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def upload_file_to_drive(file_path):
    try:
        service = authenticate_google_drive()
        folder_id = get_or_create_folder(service, FOLDER_NAME)
        file_name = os.path.basename(file_path)

        # Check if a file with the same name already exists in the folder
        results = service.files().list(
            q=f"name='{file_name}' and '{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name)',
        ).execute()
        items = results.get('files', [])

        # If file exists, delete it
        if items:
            for file in items:
                service.files().delete(fileId=file['id']).execute()
                print(f"🗑️ Deleted existing file: {file['name']} (ID: {file['id']})")

        # Upload the new file
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

        print(f"✅ Uploaded {file_name} to folder '{FOLDER_NAME}' (ID: {uploaded.get('id')})")

    except HttpError as error:
        print(f"❌ An HTTP error occurred: {error}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
