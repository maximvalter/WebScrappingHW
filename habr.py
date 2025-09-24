import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json
import re
import time
import random

URL = "https://habr.com/ru/articles/"
KEYWORDS = ['ИИ', 'Python', 'Хабр', 'AI', 'IT']

articles = []

def generate_headers():
    """Генерируем случайные headers для каждого запроса"""
    return Headers(browser="chrome", os="win").generate()

def matches_keywords(text, keywords):
    """Проверяем, есть ли ключевые слова как отдельные слова"""
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", text, flags=re.I):
            return True
    return False

# Загружаем главную страницу
resp = requests.get(URL, headers=generate_headers())
soup = BeautifulSoup(resp.text, "lxml")
article_tags = soup.find_all("article")

for tag in article_tags:
    try:
        time_tag = tag.find("time")
        h2_tag = tag.find("h2")
        a_tag = h2_tag.find("a")
        span_tag = a_tag.find("span")

        publication_time = time_tag["datetime"]
        absolute_article_link = a_tag["href"]
        if absolute_article_link.startswith("/"):
            absolute_article_link = "https://habr.com" + absolute_article_link

        article_title = span_tag.text.strip()

        # Загружаем саму статью с новыми headers, чтобы парсить весь её текст
        article_resp = requests.get(absolute_article_link, headers=generate_headers())
        article_soup = BeautifulSoup(article_resp.text, "lxml")
        content_tag = article_soup.find(id="post-content-body")

        # На случай непредвиденной ошибки / Изменения данных / Удаления статьи
        if not content_tag:
            continue

        full_text = content_tag.get_text(" ", strip=True)

        # Фильтруем по ключевым словам в заголовке и тексте статьи, лишнее убираем
        combined_text = article_title + " " + full_text
        if not matches_keywords(combined_text, KEYWORDS):
            continue

        article_dict = {
            "publication_time": publication_time,
            "absolute_article_link": absolute_article_link,
            "article_title": article_title,
            "article_text": full_text
        }
        articles.append(article_dict)

        # Вводим задержку между запросами во избежание бана
        time.sleep(random.uniform(1, 2))

    except Exception as e:
        print(f"Ошибка при парсинге статьи: {e}")

# Сохраняем в JSON
with open("articles.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Сохранено {len(articles)} статей в articles.json")
