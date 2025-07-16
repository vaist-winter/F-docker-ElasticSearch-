import requests
from bs4 import BeautifulSoup
import json
import time
import re

def extract_movie_info(html_content):
    """从电影详细页HTML中提取信息"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取标题
    title_tag = soup.find('h1')
    title = title_tag.find('span', property='v:itemreviewed').text.strip() if title_tag else ""
    
    # 提取导演（作为author）
    director = ""
    director_tag = soup.find('span', text='导演')
    if director_tag:
        director = director_tag.find_next('a').text.strip()
    
    # 提取上映日期
    date = ""
    date_tag = soup.find('span', text='上映日期:')
    if date_tag:
        date = date_tag.next_sibling.strip().split('(')[0]  # 取第一个日期
    
    # 提取剧情简介
    content = ""
    content_div = soup.find('div', class_='related-info')
    if content_div:
        short_span = content_div.find('span', class_='short')
        if short_span:
            content = short_span.get_text(separator="\n", strip=True)
            # 移除"(展开全部)"等无关文本
            content = re.sub(r'\(展开全部\)', '', content)
    
    return {
        "title": title,
        "author": director,
        "date": date,
        "content": content
    }

def crawl_douban_top250():
    base_url = "https://movie.douban.com/top250"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    documents = []
    movie_count = 0
    
    # 处理分页（共10页）
    for start in range(0, 250, 25):
        url = f"{base_url}?start={start}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取当前页所有电影链接
            movie_items = soup.select('ol.grid_view li .info a')
            for item in movie_items:
                movie_url = item['href']
                movie_count += 1
                print(f"正在爬取电影 #{movie_count}: {movie_url}")
                
                try:
                    # 请求电影详细页
                    movie_response = requests.get(movie_url, headers=headers)
                    movie_response.raise_for_status()
                    
                    # 提取电影信息
                    movie_info = extract_movie_info(movie_response.text)
                    if movie_info["title"]:  # 确保有有效数据
                        documents.append({
                            "_id": str(movie_count),
                            "_source": movie_info
                        })
                    
                    # 礼貌爬取，避免被封
                    time.sleep(2)
                
                except Exception as e:
                    print(f"爬取电影详情失败: {e}")
                    continue
        
        except Exception as e:
            print(f"爬取列表页失败: {e}")
            continue
    
    return documents

if __name__ == "__main__":
    # 执行爬取
    movie_data = crawl_douban_top250()
    
    # 保存为JSON文件
    with open('douban_top250_movies.json', 'w', encoding='utf-8') as f:
        json.dump(movie_data, f, ensure_ascii=False, indent=2)
    
    print(f"爬取完成，共保存 {len(movie_data)} 部电影信息")
