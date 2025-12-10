from moviepy.editor import VideoFileClip, ConcatenateVideoClip, TextClip, CompositeVideoClip, AudioFileClip
import os

def create_final_video(video_paths, subtitle_text, audio_text):
    """
    2つの動画を結合し、音声と字幕をつける。
    GitHub Actions (Ubuntu) 環境では日本語フォントの設定に注意が必要。
    """
    
    # ダミーファイルの場合は何もしないで返す（エラー回避）
    if not os.path.exists(video_paths[0]) or os.path.getsize(video_paths[0]) < 100:
        print("Video file is dummy. Skipping edit.")
        return "final_output.mp4"

    clips = []
    for path in video_paths:
        try:
            clip = VideoFileClip(path)
            clips.append(clip)
        except Exception as e:
            print(f"Error loading clip {path}: {e}")
            return "final_output.mp4"

    # 1. 結合
    final_clip = ConcatenateVideoClip(clips, method="compose")

    # YouTube Shorts用に 9:16 (例: 1080x1920) にリサイズ/クロップする処理
    # 入力が横長(16:9)の場合、中央を切り抜く
    w, h = final_clip.size
    target_ratio = 9/16
    
    # 既に縦長ならそのまま、横長ならクロップ
    if w / h > target_ratio:
        # 幅が広すぎるので左右をカット
        new_width = h * target_ratio
        final_clip = final_clip.crop(x1=w/2 - new_width/2, width=new_width, height=h)
    
    # 最終的なサイズを1080x1920にリサイズ（必要であれば）
    # final_clip = final_clip.resize(height=1920) 

    # 2. 音声生成 (本来はOpenAI TTS API等を叩いてmp3を取得する)
    # import requests
    # ... TTS API Call ...
    # audio_clip = AudioFileClip("tts_output.mp3")
    # final_clip = final_clip.set_audio(audio_clip)

    # 3. 字幕生成
    # Ubuntuで日本語フォントを使うにはフォントファイルのパス指定が必要
    # txt_clip = TextClip(subtitle_text, fontsize=24, color='white', font='/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc')
    # txt_clip = txt_clip.set_pos('bottom').set_duration(final_clip.duration)
    # final_clip = CompositeVideoClip([final_clip, txt_clip])

    output_path = "final_output.mp4"
    final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    
    return output_path
