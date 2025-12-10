import feedparser
import random
import requests
from bs4 import BeautifulSoup

def get_trend_topic(category):
    """
    カテゴリに基づいてトレンド情報を取得する。
    RSSフィードを使用してリアルタイムな情報を取得する。
    """
    topic = {
        "title": "Default Topic",
        "description": "情報が取得できませんでした。",
        "url": ""
    }

    rss_url = ""
    
    # カテゴリ別RSS URL設定
    if category == "news":
        # Google News Japan - Top Stories
        rss_url = "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
        
    elif category == "game":
        # Google News Japan - Search: Game
        rss_url = "https://news.google.com/rss/search?q=%E3%82%B2%E3%83%BC%E3%83%A0&hl=ja&gl=JP&ceid=JP:ja"
        
    elif category == "shorts_trend":
        # Google Trends Daily (Japan) - 近似的に「急上昇」として扱う
        # YouTubeのRSSはチャンネルごとなので、Google Trendsを利用
        rss_url = "https://trends.google.co.jp/trends/trendingsearches/daily/rss?geo=JP"

    try:
        feed = feedparser.parse(rss_url)
        
        if feed.entries:
            # ランダムに1つ選ぶ（毎回同じにならないようにトップ10から選ぶなど）
            # 記事としての質を保つため、descriptionがあるものや、タイトルが短すぎないものを選別したいが
            # ここではシンプルに上位10件からランダム選択
            candidates = feed.entries[:10]
            entry = random.choice(candidates)
            
            topic["title"] = entry.title
            topic["url"] = entry.link
            
            # Google NewsのdescriptionはHTMLが含まれることが多いため、クリーニングするか
            # シンプルにタイトルを使用する。詳細が必要な場合はリンク先をスクレイピングする手もあるが
            # 処理時間を考慮し、RSSのdescription (summary) を使う。
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            
            # HTMLタグの除去（簡易的）
            soup = BeautifulSoup(summary, "html.parser")
            topic["description"] = soup.get_text()[:200] + "..." # 長すぎる場合はカット
            
        else:
            print(f"No entries found for category: {category}")

    except Exception as e:
        print(f"Error fetching RSS for {category}: {e}")

    return topic
