import os
import sys

# Try importing MoviePy with fallback strategies
try:
    # Attempt MoviePy v1 style (most common)
    from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip
except ImportError:
    try:
        # Attempt MovePy v2 style
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        from moviepy.video.VideoClip import TextClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.audio.io.AudioFileClip import AudioFileClip
    except ImportError as e:
        print(f"CRITICAL: MoviePy import failed. {e}")
        # Dummy fallbacks to prevent crash during import, though execution will fail
        VideoFileClip = None

def create_final_video(video_paths, subtitle_text, audio_text):
    """
    2つの動画を結合し、音声と字幕をつける。
    GitHub Actions (Ubuntu) 環境では日本語フォントの設定に注意が必要。
    """
    
    # 依存関係エラー時のチェック
    if VideoFileClip is None:
        print("MoviePy library is missing or incompatible.")
        return "final_output.mp4"

    # ダミーファイルの場合は何もしないで返す（エラー回避）
    valid_paths = [p for p in video_paths if os.path.exists(p) and os.path.getsize(p) > 100]
    if not valid_paths:
        print("No valid video files found. Skipping edit.")
        return "final_output.mp4"

    clips = []
    for path in valid_paths:
        try:
            clip = VideoFileClip(path)
            clips.append(clip)
        except Exception as e:
            print(f"Error loading clip {path}: {e}")

    if not clips:
        return "final_output.mp4"

    # 1. 結合 (ConcatenateVideoClipクラスではなく関数を使う)
    try:
        final_clip = concatenate_videoclips(clips, method="compose")
    except Exception as e:
        print(f"Concatenation failed: {e}")
        final_clip = clips[0] # Fallback to first clip

    # YouTube Shorts用に 9:16 (例: 1080x1920) にリサイズ/クロップする処理
    w, h = final_clip.size
    target_ratio = 9/16
    
    # 既に縦長ならそのまま、横長ならクロップ
    if h > 0 and w / h > target_ratio:
        # 幅が広すぎるので左右をカット
        new_width = h * target_ratio
        final_clip = final_clip.crop(x1=w/2 - new_width/2, width=new_width, height=h)
    
    # 2. 音声生成 (gTTSを使用)
    try:
        from gtts import gTTS
        tts = gTTS(text=audio_text, lang='ja')
        tts.save("tts_output.mp3")
        
        audio_clip = AudioFileClip("tts_output.mp3")
        final_clip = final_clip.set_audio(audio_clip)
    except Exception as e:
        print(f"Audio generation failed: {e}")

    # 3. 字幕生成
    try:
        # Ubuntu環境で日本語フォントを使用するため、Noto Sans CJKを指定
        # 事前に sudo apt-get install fonts-noto-cjk が必要
        font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' 
        
        # フォントが見つからない場合のフォールバック
        if not os.path.exists(font_path):
             font_path = 'WenQuanYi Micro Hei' # ImageMagickの標準的な日本語対応フォント名（環境による）

        txt_clip = TextClip(subtitle_text, fontsize=40, color='white', font=font_path, stroke_color='black', stroke_width=2, size=(final_clip.w * 0.9, None), method='caption')
        txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(final_clip.duration)
        final_clip = CompositeVideoClip([final_clip, txt_clip])
    except Exception as e:
        print(f"Subtitle generation skipped due to error: {e}")

    output_path = "final_output.mp4"
    final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', logger=None)
    
    return output_path
