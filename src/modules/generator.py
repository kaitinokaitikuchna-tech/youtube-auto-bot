import os
import time
import requests
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips
import urllib.parse

def generate_videos(scene_prompts):
    """
    Pollinations AI (Google Veo model) を使用して動画を生成する。
    4つのシーンを受け取り、それぞれ動画を生成して結合する。
    """
    
    video_clips = []
    temp_files = []
    
    # Pollinations AI Endpoint
    # Model: 'veo' (Google Veo)
    # Direct endpoint avoids redirector issues: https://image.pollinations.ai/prompt/...
    # Note: Even though it says 'image', it returns video for video models.
    model_name = "veo" 
    
    print(f"Starting video generation using model: {model_name}")

    for i, prompt in enumerate(scene_prompts):
        print(f"Generating scene {i+1}/{len(scene_prompts)}...")
        
        prompt_text = prompt['positive']
        # URL encode prompt
        encoded_prompt = urllib.parse.quote(prompt_text)
        
        # Random seed for variation
        seed = random.randint(0, 999999)
        
        # Construct URL
        # Using standard redirector endpoint which handles video routing best.
        # Removing nologo just in case it conflicts with video.
        # We try 'veo' first.
        video_url = f"https://pollinations.ai/p/{encoded_prompt}?model=veo&width=720&height=1280&seed={seed}"
        
        filename = f"scene_{i}.mp4"
        
        try:
            # Download content
            # Increase timeout for video generation (Veo can be slow)
            print(f"Requesting (Veo): {video_url}")
            resp = requests.get(video_url, timeout=120, allow_redirects=True) 
            
            # Helper to check if it's video
            def is_video_response(response):
                ctype = response.headers.get('Content-Type', '').lower()
                return 'video' in ctype or (len(response.content) > 500000) # Size heuristic
            
            if resp.status_code == 200 and is_video_response(resp):
                print(f"Success! Content-Type: {resp.headers.get('Content-Type')}")
                with open(filename, 'wb') as f:
                    f.write(resp.content)
            else:
                print(f"Veo returned non-video (Type: {resp.headers.get('Content-Type')}). Retrying with fallback model 'luma'...")
                # Retry with Luma
                fallback_url = f"https://pollinations.ai/p/{encoded_prompt}?model=luma&width=720&height=1280&seed={seed}"
                print(f"Requesting (Luma): {fallback_url}")
                resp_fb = requests.get(fallback_url, timeout=120, allow_redirects=True)
                
                if resp_fb.status_code == 200 and is_video_response(resp_fb):
                    print(f"Success (Luma)! Content-Type: {resp_fb.headers.get('Content-Type')}")
                    with open(filename, 'wb') as f:
                        f.write(resp_fb.content)
                else:
                    # Retry with Seedance (often more available)
                    print("Luma failed. Retrying with fallback model 'seedance'...")
                    seedance_url = f"https://pollinations.ai/p/{encoded_prompt}?model=seedance&width=720&height=1280&seed={seed}"
                    resp_sd = requests.get(seedance_url, timeout=120, allow_redirects=True)
                    
                    if resp_sd.status_code == 200 and is_video_response(resp_sd):
                         print(f"Success (Seedance)! Content-Type: {resp_sd.headers.get('Content-Type')}")
                         with open(filename, 'wb') as f:
                             f.write(resp_sd.content)
                    else:
                        # Final Fail: Fallback to static image to video
                        print("All video models failed. Creating static video from image.")
                        # Use whatever we got (likely an image from first or second request)
                        image_filename = f"scene_{i}.jpg"
                        with open(image_filename, 'wb') as f:
                            # Prefer Veo/Luma image over nothing
                            content_to_write = resp.content if len(resp.content) > 1000 else resp_fb.content
                            f.write(content_to_write)
                            
                        from moviepy.editor import ImageClip
                        # Add simple zoom effect if possible? For now just static 8s
                        clip = ImageClip(image_filename).set_duration(8).set_fps(24)
                        clip.write_videofile(filename, codec='libx264', audio=False, logger=None)
                        video_clips.append(VideoFileClip(filename))
                        temp_files.append(filename)
                        temp_files.append(image_filename)
                        continue

            # If we reached here, filename contains a valid video (Veo or Luma)
            try:
                clip = VideoFileClip(filename)
                print(f"Clip {i} duration: {clip.duration}s")
                video_clips.append(clip)
                temp_files.append(filename)
            except Exception as e:
                print(f"Error loading video clip {filename}: {e}")
                
        except Exception as e:
            print(f"Error generating video {i}: {e}")
                
        except Exception as e:
            print(f"Error generating video {i}: {e}")
    
    final_video_path = "final_video.mp4"
    
    if video_clips:
        print("Concatenating videos...")
        try:
            # Concatenate all clips
            final_clip = concatenate_videoclips(video_clips, method="compose")
            final_clip.write_videofile(final_video_path, codec='libx264', audio_codec='aac', fps=24)
            
            # Close clips to release resources
            final_clip.close()
            for clip in video_clips:
                clip.close()
                
            return [final_video_path]
            
        except Exception as e:
            print(f"Error concatenating videos: {e}")
            return []
    else:
        print("No videos generated successfully.")
        return []

    # Cleanup handled by caller or OS usually, but we keep temp files for debug now
    # for f in temp_files:
    #     try: os.remove(f)
    #     except: pass
