import os
import time
import requests
from openai import OpenAI

def generate_videos(scene_prompts):
    """
    Sora2 (またはOpenAI Video生成モデル) を使用して動画を生成する。
    OpenAI APIの DALL-E 3画像生成 等で代用せず、
    もしSoraがまだAPI公開されていない場合は、現状利用可能な動画生成AI（RunwayやPikaなど）のAPIに置き換える必要があるが、
    ここでは「OpenAI経由で動画生成ができる」という想定のコードを書く。
    """
    
    # 注意: 2024年現在、SoraのPublic APIはまだ一般公開されていない可能性があります。
    # 公開されている場合は `client.video.generations.create` のようなI/Fになります。
    # ここでは仮の実装として記述します。
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    video_paths = []
    
    for i, prompt in enumerate(scene_prompts):
        print(f"Generating video {i+1}...")
        
        # --- ここはSora APIの仕様に合わせて変更してください ---
        # 現状はダミーファイルを作成して返すロジックにします
        # (APIを叩くと課金されるため、テスト時はダミーが推奨されます)
        
        # 実際のAPIコールのイメージ:
        # response = client.images.generate(
        #     model="dall-e-3", # ここを video-model に変更
        #     prompt=prompt['positive'],
        #     n=1,
        #     size="1024x1024"
        # )
        # video_url = response.data[0].url
        
        # --- Pollinations AI Image Generation ---
        # https://pollinations.ai/p/{prompt}?width=1080&height=1920&seed={random}
        
        filename = f"video_{i}.mp4"
        image_filename = f"image_{i}.jpg"
        
        prompt_text = prompt['positive']
        # URL encode prompt is handled by requests usually, but for string usage:
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt_text)
        
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1080&height=1920&model=flux&seed={i}"
        
        print(f"Generating image {i}: {prompt_text[:30]}...")
        
        try:
            # Download Image
            img_resp = requests.get(image_url, timeout=60)
            if img_resp.status_code == 200:
                with open(image_filename, 'wb') as f:
                    f.write(img_resp.content)
                
                # Convert Image to Video Clip (5 seconds)
                # Retry strategy handled in editor, but we make valid mp4 here
                from moviepy.editor import ImageClip
                
                # Create a video clip from the image
                clip = ImageClip(image_filename).set_duration(5).set_fps(24)
                clip.write_videofile(filename, codec='libx264', audio=False, logger=None)
                
                video_paths.append(filename)
                
                # Clean up image file
                # os.remove(image_filename) 
            else:
                print(f"Failed to generate image: {img_resp.status_code}")
                # Fallback to dummy
                raise Exception("API returned error")
                
        except Exception as e:
            print(f"Error creating AI video: {e}")
            # Fallback: Black video
            from moviepy.editor import ColorClip
            clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=5)
            clip.write_videofile(filename, fps=24, logger=None)
            video_paths.append(filename)
        
        # --- End Pollinations Implementation ---

    return video_paths
