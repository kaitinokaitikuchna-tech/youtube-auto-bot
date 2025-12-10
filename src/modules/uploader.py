import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# YouTube Data API Scope
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """
    GitHub Actions上での実行を想定し、環境変数または保存されたトークンから認証情報を復元する。
    """
    creds = None
    
    # 1. 環境変数 (GitHub Secrets) からリフレッシュトークンをロード
    # 実際には client_id, client_secret, refresh_token を JSON形式で保存しておくのが楽
    api_service_name = "youtube"
    api_version = "v3"
    
    # ここではローカルのtoken.jsonがあるか、環境変数があるかで分岐
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    elif os.getenv("YOUTUBE_REFRESH_TOKEN"):
        info = {
            "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
            "refresh_token": os.getenv("YOUTUBE_REFRESH_TOKEN"),
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        creds = Credentials.from_authorized_user_info(info, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 初回ログイン (ローカルで実行してtoken.jsonを作る必要がある)
            print("No valid credentials found. Please run local_login_setup.py first.")
            return None

    return build(api_service_name, api_version, credentials=creds)

def upload_to_youtube(file_path, title, description, category="news"):
    youtube = get_authenticated_service()
    if not youtube:
        return

    # カテゴリID (25=News, 20=Gaming)
    category_id = "25" 
    if category == "game":
        category_id = "20"

    body = {
        'snippet': {
            'title': title[:100],
            'description': description + "\n\n(This video was created using AI technology / この動画はAI技術を使用して作成されました)",
            'tags': ['Sora2', 'AI', 'ToyPoodle', category],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'private', # 最初は非公開または非公開推奨
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    print(f"Uploading {file_path} to YouTube...")
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print(f"Upload Complete! Video ID: {response.get('id')}")
