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
    # ユーザー要望: 6時=ニュース, 14時=トレンド, 20時=ゲーム
    # 実行タイミングが多少ずれても良いように幅を持たせる
    
    if 5 <= current_hour < 10:
        # 朝 (06:00ターゲット)
        category = "news"
        print("Mode: NEWS (Shorts) (Target: 06:00)")
        
    elif 13 <= current_hour < 16:
        # 昼 (14:00ターゲット)
        category = "shorts_trend"
        print("Mode: SHORTS TREND (Shorts) (Target: 14:00)")
        
    elif 19 <= current_hour < 23:
        # 夜 (20:00ターゲット)
        category = "game"
        print("Mode: GAME (Shorts) (Target: 20:00)")
        
    else:
        # ターゲット時間外の場合のデフォルト挙動
        # テスト時などはニュースまたはランダムにするなどの運用
        category = "news"
        print("Mode: DEFAULT (Outside schedule, defaulting to NEWS)")

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
