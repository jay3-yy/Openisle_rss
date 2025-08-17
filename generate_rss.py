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
        # 1. 发送 HTTP 请求获取数据
        response = requests.get(API_URL)
        response.raise_for_status()  # 如果请求失败 (例如 404, 500)，会抛出异常
        posts = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching API data: {e}")
        return None
    except ValueError:
        print("Error: Failed to decode JSON from response")
        return None

    # 2. 创建 RSS 的根元素
    rss_element = ET.Element("rss", version="2.0", attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"})
    channel_element = ET.SubElement(rss_element, "channel")

    # 3. 设置 Channel 的基本信息
    ET.SubElement(channel_element, "title").text = "Open Isle - Posts"
    ET.SubElement(channel_element, "link").text = BASE_URL
    ET.SubElement(channel_element, "description").text = "Latest posts from Open Isle"
    ET.SubElement(channel_element, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))
    
    # 添加 Atom self-link (可选，但推荐)
    # 假设你的 RSS feed 将会发布在 "https://your-domain.com/rss.xml"
    ET.SubElement(channel_element, "atom:link", href="https://your-domain.com/rss.xml", rel="self", type="application/rss+xml")


    # 4. 遍历从 API 获取的每篇文章，并创建 <item> 元素
    for post in posts:
        item_element = ET.SubElement(channel_element, "item")
        
        # 文章标题
        ET.SubElement(item_element, "title").text = post.get("title", "No Title")
        
        # 文章链接 - 根据 slug 构建
        post_link = f"{BASE_URL}/post/{post.get('slug')}"
        ET.SubElement(item_element, "link").text = post_link
        
        # 文章描述 (使用摘要 excerpt)
        ET.SubElement(item_element, "description").text = post.get("excerpt", "")
        
      # 发布日期
        try:
            pub_date_str = post.get("publishedAt")
            # 核心修复：在这里添加一个检查，确保 pub_date_str 不是 None
            if pub_date_str: 
                if pub_date_str.endswith('Z'):
                    pub_date_str = pub_date_str[:-1] + '+00:00'
                dt_object = datetime.fromisoformat(pub_date_str)
                ET.SubElement(item_element, "pubDate").text = format_datetime(dt_object)
        except (TypeError, ValueError):
            # 如果日期格式有问题或为空，则跳过，不添加 pubDate 标签
            pass

        # 全局唯一标识符 (GUID) - 通常使用文章链接
        guid = ET.SubElement(item_element, "guid", isPermaLink="true")
        guid.text = post_link

    # 5. 将 XML 树转换为字符串
    # encoding='unicode' 使其成为常规字符串，而不是字节串
    xml_string = ET.tostring(rss_element, encoding='unicode')

    return xml_string

if __name__ == "__main__":
    rss_content = create_rss_feed()
    if rss_content:
        # 将生成的 XML 内容保存到文件中
        with open("rss.xml", "w", encoding="utf-8") as f:
            f.write(rss_content)
        print("RSS feed generated and saved to rss.xml")
        
        # 或者直接打印到控制台
        # print(rss_content)