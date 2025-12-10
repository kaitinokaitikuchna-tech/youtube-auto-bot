import os
import json
from openai import OpenAI

def generate_prompts(topic_data):
    """
    トピックを受け取り、Sora2用のプロンプトとYouTube用のテキストを生成する。
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # ユーザー指定の固定プロンプト
    character_prompt = {
        "positive_prompt": "A portrait of a distinct toy poodle character. It has rich red-brown curly fur styled in a fluffy, slightly tousled teddy bear cut. The poodle is wearing oversized round tortoise-shell reading glasses perched on its nose, and a textured mustard-yellow corduroy bowtie. It has a curious, intelligent expression looking directly at the camera. Warm natural lighting, film photography grain, cozy atmosphere, shallow depth of field, highly detailed fur texture.",
        "negative_prompt": "shaved fur, standard poodle cut, plastic glasses, cartoon, 3d render, blurry, aggressive, sad face, human beings, text, watermark"
    }

    system_instruction = """
    あなたは動画クリエイターのアシスタントです。
    与えられたニュースやトピックをもとに、以下のJSON形式でデータを出力してください。
    
    1. 生成する動画のScene 1とScene 2のプロンプト (英語)
       - Aspect Ratio: 9:16 (Vertical) for YouTube Shorts.
       - 必ず指定されたキャラクター設定(Toy Poodle)を含めること。
       - ニュースの内容を視覚的に表現すること。
       - Sora2の規約（暴力・性表現禁止）を厳守すること。
    2. YouTube動画のタイトル (日本語, 30文字以内)
    3. 動画の説明欄 (日本語)
    4. 字幕/読み上げ用のスクリプト (日本語)
       - トイプードルのキャラクターになりきってください。
       - 「ワン！」「〜だワン」などの語尾を使うこと。
       - 内容はわかりやすく要約し、60秒以内に収まる長さにする。

    Output JSON Format:
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
    Topic Title: {topic_data['title']}
    Topic Description: {topic_data['description']}
    
    Required Character Prompt (Must be included/mixed into the positive prompt):
    {character_prompt['positive_prompt']}
    
    Required Negative Prompt:
    {character_prompt['negative_prompt']}
    """

    response = client.chat.completions.create(
        model="gpt-4o", # Changed from gpt-4-turbo for better availability
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    return result
