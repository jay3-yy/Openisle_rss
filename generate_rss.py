import requests
import xml.etree.ElementTree as ET
from email.utils import format_datetime
from datetime import datetime, timezone

# API 的 URL
API_URL = "https://www.open-isle.com/api/posts"
# 你的网站的基本 URL
BASE_URL = "https://www.open-isle.com"

def create_rss_feed():
    """
    获取 API 数据并生成 RSS 2.0 格式的 XML 内容。
    """
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        posts = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching API data: {e}")
        return None
    except ValueError:
        print("Error: Failed to decode JSON from response")
        return None

    rss_element = ET.Element("rss", version="2.0", attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"})
    channel_element = ET.SubElement(rss_element, "channel")

    ET.SubElement(channel_element, "title").text = "Open Isle - Posts"
    ET.SubElement(channel_element, "link").text = BASE_URL
    ET.SubElement(channel_element, "description").text = "Latest posts from Open Isle"
    ET.SubElement(channel_element, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))
    
    ET.SubElement(channel_element, "atom:link", href="https://your-domain.com/rss.xml", rel="self", type="application/rss+xml")

    # 遍历从 API 获取的每篇文章
    for post in posts:
        # ===== 核心修复部分开始 =====
        slug = post.get("slug")
        # 检查 slug 是否存在且不为空。如果不存在，则跳过当前循环，处理下一篇文章。
        if not slug:
            print(f"Skipping post with missing slug. Title: {post.get('title')}")
            continue
        # ===== 核心修复部分结束 =====

        item_element = ET.SubElement(channel_element, "item")
        
        ET.SubElement(item_element, "title").text = post.get("title", "No Title")
        
        # 使用我们已经验证过的 slug 来构建链接
        post_link = f"{BASE_URL}/post/{slug}"
        ET.SubElement(item_element, "link").text = post_link
        
        ET.SubElement(item_element, "description").text = post.get("excerpt", "")
        
        try:
            pub_date_str = post.get("publishedAt")
            if pub_date_str: 
                if pub_date_str.endswith('Z'):
                    pub_date_str = pub_date_str[:-1] + '+00:00'
                dt_object = datetime.fromisoformat(pub_date_str)
                ET.SubElement(item_element, "pubDate").text = format_datetime(dt_object)
        except (TypeError, ValueError):
            pass

        guid = ET.SubElement(item_element, "guid", isPermaLink="true")
        guid.text = post_link

    xml_string = ET.tostring(rss_element, encoding='unicode')
    return xml_string

if __name__ == "__main__":
    rss_content = create_rss_feed()
    if rss_content:
        with open("rss.xml", "w", encoding="utf-8") as f:
            f.write(rss_content)
        print("RSS feed generated and saved to rss.xml")