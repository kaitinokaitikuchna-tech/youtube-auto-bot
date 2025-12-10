import os
import datetime
import pytz
from modules.fetcher import get_trend_topic
from modules.prompt import generate_prompts
from modules.generator import generate_videos
from modules.editor import create_final_video
from modules.uploader import upload_to_youtube

def main():
    # 日本時間を取得
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(jst)
    current_hour = now.hour

    print(f"Current time (JST): {now}")

    # 時間帯によるジャンル分け (すべてショート動画として作成)
    if 5 <= current_hour < 9:
        category = "news"
        print("Mode: NEWS (Shorts) (06:00)")
    elif 11 <= current_hour < 15:
        category = "shorts_trend"
        print("Mode: SHORTS TREND (Shorts) (12:00)")
    elif 18 <= current_hour < 22:
        category = "game"
        print("Mode: GAME (Shorts) (19:00)")
    else:
        # テスト実行用など
        category = "news"
        print("Mode: DEFAULT (NEWS Shorts)")

    # 1. ネタ選定
    topic_data = get_trend_topic(category)
    print(f"Topic: {topic_data['title']}")

    # 2. プロンプト生成 (トイプードル化)
    # Sora2プロンプトと、字幕用テキスト、タイトルなどが返る
    script_data = generate_prompts(topic_data)
    print("Prompts generated.")

    # 3. 動画生成 (Sora2 API)
    # 2本の動画パスが返る
    video_paths = generate_videos(script_data['scene_prompts'])
    print(f"Videos generated: {video_paths}")

    # 4. 動画編集 (結合・字幕)
    final_video_path = create_final_video(video_paths, script_data['subtitle_text'], script_data['audio_text'])
    print(f"Final video created: {final_video_path}")

    # 5. YouTubeアップロード
    upload_to_youtube(final_video_path, script_data['title'], script_data['description'], category)
    print("Upload completed.")

if __name__ == "__main__":
    main()
