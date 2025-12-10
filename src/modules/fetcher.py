import requests
import os
import random

def get_trend_topic(category):
    """
    カテゴリに基づいてトレンド情報を取得する。
    現状はモック（ダミーデータ）または簡易APIコールのみ実装。
    """
    api_key_news = os.getenv("NEWS_API_KEY") # NewsAPI Key if available
    
    topic = {
        "title": "Default Topic",
        "description": "This is a default description.",
        "url": ""
    }

    if category == "news":
        # 簡易的にNewsAPIを使う場合 (要APIキー)
        # url = f"https://newsapi.org/v2/top-headlines?country=jp&apiKey={api_key_news}"
        # resp = requests.get(url)
        # if resp.status_code == 200:
        #     data = resp.json()
        #     ...
        
        # モックデータ
        trends = [
            {"title": "新しいAI技術が発表され、生活が便利に", "desc": "最新のAIアシスタントが掃除も洗濯もしてくれる未来が到来。"},
            {"title": "季節外れの桜が開花、気候変動の影響か", "desc": "都内の公園で12月なのに桜が咲いているのが発見されました。"},
            {"title": "円安が進行、海外旅行客が増加", "desc": "円安の影響で日本への観光客が過去最高を記録しています。"}
        ]
        topic_raw = random.choice(trends)
        topic["title"] = topic_raw["title"]
        topic["description"] = topic_raw["desc"]

    elif category == "shorts_trend":
        # 本来はYouTube Data APIで急上昇を取得
        topic["title"] = "誰も知らないライフハック術！"
        topic["description"] = "日常で使える便利な裏技を紹介。"

    elif category == "game":
        topic["title"] = "期待の新作RPGの発売日が決定！"
        topic["description"] = "ファン待望の大型RPG、ついに来月発売へ。"

    return topic
