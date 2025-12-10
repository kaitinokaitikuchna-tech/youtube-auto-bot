import os
import json
from openai import OpenAI

def generate_prompts(topic_data):
    """
    トピックを受け取り、Sora2用のプロンプトとYouTube用のテキストを生成する。
    """
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # Comment out OpenAI
    import requests
    
    # ユーザー指定の固定プロンプト
    character_prompt = {
        "positive_prompt": "A portrait of a distinct toy poodle character. It has rich red-brown curly fur styled in a fluffy, slightly tousled teddy bear cut. The poodle is wearing oversized round tortoise-shell reading glasses perched on its nose, and a textured mustard-yellow corduroy bowtie. It has a curious, intelligent expression looking directly at the camera. Warm natural lighting, film photography grain, cozy atmosphere, shallow depth of field, highly detailed fur texture.",
        "negative_prompt": "shaved fur, standard poodle cut, plastic glasses, cartoon, 3d render, blurry, aggressive, sad face, human beings, text, watermark"
    }

    system_instruction = """
    You are an AI assistant for video content creation. Output ONLY valid JSON.
    
    Goal: Generate a script and video prompts for a YouTube Short (approx 30-40 sec total).
    
    CRITICAL RULE - COPYRIGHT SAFETY:
    - The visuals MUST be generic (except for the main character). DO NOT refer to specific copyrighted characters (e.g. Mario, Pikachu, Gundam, celebrities).
    - If the topic is "New Mario Game", the visual prompt should be "A cute red plumber character jumping in a colorful mushroom world, 3d platformer style" or simply "A person playing a colorful video game console".
    
    CRITICAL RULE - CHARACTER CONSISTENCY:
    - EVERY SCENE'S 'positive' prompt MUST START WITH the "Character Description" provided below.
    - The character (Toy Poodle) should be doing something related to the scene (e.g., reading a newspaper, looking surprised at a screen, jumping with joy).
    
    Output Format:
    {
        "scene_prompts": [
            {"positive": "(Character Description) reading a newspaper...", "negative": "..."},
            {"positive": "(Character Description) looking surprised...", "negative": "..."}
        ],
        "title": "YouTube Title",
        "description": "YouTube Description",
        "audio_text": "Full script for TTS (approx 30-40 secs when read)",
        "subtitle_text": "Subtitle text corresponding to the audio"
    }
    """

    user_content = f"""
    Topic: {topic_data['title']}
    Details: {topic_data['description']}
    
    Character Description (MUST BE INCLUDED IN EVERY PROMPT): {character_prompt['positive_prompt']}
    Negative Prompt (Append to all negative prompts): {character_prompt['negative_prompt']}
    
    Constraint: Generate exactly 4 scenes. Each scene corresponds to roughly 8 seconds of video.
    Language: Japanese for text/audio, English for video generation prompts.
    Content: A specific Toy Poodle character explaining the news/topic.
    """

    # Pollinations Text API (GET request strategy)
    full_prompt = f"{system_instruction}\n\n{user_content}"
    
    print("Generating prompts via Pollinations AI...")
    
    try:
        # Pollinations Text API can handle reasonably long prompts in URL, but POST is safer if supported.
        # For now, we continue with GET but ensure proper encoding.
        # Note: If the prompt is too long, this might fail. We mitigate by keeping system instruction concise.
        url = f"https://text.pollinations.ai/{requests.utils.quote(full_prompt)}"
        
        # Adding a random dummy param to bypass potential caching if needed, though prompt changes usually suffice
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        text_response = response.text
        
        # Clean up potential markdown code blocks
        text_response = text_response.strip()
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "").replace("```", "")
        
        result = json.loads(text_response)
        
        # Validation: Ensure 4 scenes
        if len(result.get("scene_prompts", [])) < 4:
            # Pad if missing
            while len(result["scene_prompts"]) < 4:
                result["scene_prompts"].append(result["scene_prompts"][-1])
                
        return result
        
    except Exception as e:
        print(f"Pollinations API Error: {e}")
        # Fallback dummy data
        return {
            "scene_prompts": [
                {"positive": character_prompt['positive_prompt'] + ", reading news", "negative": character_prompt['negative_prompt']},
                {"positive": character_prompt['positive_prompt'] + ", surprised expression", "negative": character_prompt['negative_prompt']},
                {"positive": character_prompt['positive_prompt'] + ", explaining details", "negative": character_prompt['negative_prompt']},
                {"positive": character_prompt['positive_prompt'] + ", happy conclusion", "negative": character_prompt['negative_prompt']}
            ],
            "title": f"ニュース: {topic_data['title'][:10]}...",
            "description": "AI生成動画です。",
            "audio_text": f"最新のニュースです。{topic_data['title']}についてお伝えします。{topic_data['description']}",
            "subtitle_text": "最新ニュースをお届けします！"
        }
