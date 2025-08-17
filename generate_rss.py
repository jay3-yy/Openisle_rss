import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

def main():
    api_url = "https://www.open-isle.com/api/posts"
    res = requests.get(api_url)
    posts = res.json()

    fg = FeedGenerator()
    fg.title("Open-Isle 最新文章")
    fg.link(href="https://www.open-isle.com", rel="alternate")
    fg.description("通过 API 自动生成的 RSS 订阅源")
    fg.lastBuildDate(datetime.now(timezone.utc))  # ✅ 修复时区问题

    for post in posts:
        fe = fg.add_entry()
        fe.id(str(post.get("id")))
        fe.title(post.get("title"))
        fe.link(href=f"https://www.open-isle.com/posts/{post.get('id')}")
        fe.description(post.get("excerpt") or "")
        if post.get("date"):
            fe.pubDate(post.get("date"))

    fg.rss_file("feed.xml")
    print("✅ RSS 文件已更新：feed.xml")

if __name__ == "__main__":
    main()
