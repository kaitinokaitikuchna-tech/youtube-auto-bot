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
    You are an AI assistant. Output ONLY valid JSON. No markdown, no explanations.
    Analyze the topic and generate video prompts.
    
    Output Format:
    {
        "scene_prompts": [
            {"positive": "...", "negative": "..."},
            {"positive": "...", "negative": "..."}
        ],
        "title": "...",
        "description": "...",
        "audio_text": "...",
        "subtitle_text": "..."
    }
    """

    user_content = f"""
    Topic: {topic_data['title']}
    Details: {topic_data['description']}
    
    Character: {character_prompt['positive_prompt']}
    Constraint: Generate 2 scenes for a YouTube Short (vertical 9:16).
    Language: Japanese for text, English for prompts.
    Content: A specific Toy Poodle character explaining the news.
    """

    # Pollinations Text API (GET request strategy)
    # Adding a random seed to ensure freshness if supported, or just the prompt
    full_prompt = f"{system_instruction}\n\n{user_content}"
    
    # We construct the URL with the prompt. 
    # Pollinations text API: https://text.pollinations.ai/{prompt}
    # It returns raw text.
    print("Generating prompts via Pollinations AI...")
    
    try:
        url = f"https://text.pollinations.ai/{requests.utils.quote(full_prompt)}"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        text_response = response.text
        
        # Clean up potential markdown code blocks if the model adds them
        text_response = text_response.strip()
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "").replace("```", "")
        
        result = json.loads(text_response)
        return result
        
    except Exception as e:
        print(f"Pollinations API Error: {e}")
        # Fallback dummy data if API fails
        return {
            "scene_prompts": [
                {"positive": character_prompt['positive_prompt'] + ", reading news paper", "negative": character_prompt['negative_prompt']},
                {"positive": character_prompt['positive_prompt'] + ", looking surprised", "negative": character_prompt['negative_prompt']}
            ],
            "title": f"ニュース: {topic_data['title'][:10]}",
            "description": "AI生成動画です。",
            "audio_text": "今日は新しいニュースが入ってきたワン！",
            "subtitle_text": "今日は新しいニュースが入ってきたワン！"
        }
