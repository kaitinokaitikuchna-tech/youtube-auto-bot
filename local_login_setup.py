from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def main():
    """
    これをローカルのPCで一度だけ実行して、YouTubeアカウントにログインする。
    生成された token.json の中身（refresh_token）を GitHub API Keyとして使う。
    """
    if not os.path.exists('client_secret.json'):
        print("Error: 'client_secret.json' が見つかりません。Google Cloud Consoleからダウンロードしてこのフォルダに置いてください。")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("Authentication successful!")
    print("生成された 'token.json' を開いて、'refresh_token' の値を確認してください。")
    print("その値を GitHub Secrets の YOUTUBE_REFRESH_TOKEN に設定します。")

if __name__ == '__main__':
    main()
