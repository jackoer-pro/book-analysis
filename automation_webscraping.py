import requests
from bs4 import BeautifulSoup
import csv
import datetime
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt

# map star text -> number
rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

def log_error(url, e, logfile="errors.log"):
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] Lỗi khi scrape URL: {url}\n")
        f.write(f"Chi tiết lỗi: {str(e)}\n")
        f.write("-" * 40 + "\n")

base_url = "https://books.toscrape.com/catalogue/"
url = "https://books.toscrape.com/catalogue/page-1.html"
all_books = []

# chỉ tạo 1 session dùng chung
session = requests.Session()

def scrape_detail(link):
    """Hàm lấy chi tiết 1 cuốn sách"""
    try:
        detail_response = session.get(link, timeout=5)
        detail_response.raise_for_status()
        detail_soup = BeautifulSoup(detail_response.text, "html.parser")
        
        # description
        details = detail_soup.select_one("#product_description ~ p")
        description = details.text.strip() if details else "N/A"

        # availability
        availability = detail_soup.select_one("p.instock.availability").get_text(strip=True)

        # category (li trước .active)
        depicts = detail_soup.select("ul.breadcrumb li")  # lấy list
        if len(depicts) >= 3:
            category = depicts[2].get_text(strip=True)
        else:
            category = "N/A"

        return description, availability, category
    except Exception as e:
        log_error(link, e)
        return "N/A", "N/A", "N/A"

with open("book_store.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "price", "link", "rating", "opinion","description","available","category"])

    while url:
        book_tasks = []
        try:
            response = session.get(url, timeout=3)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")

            books = soup.find_all("article", class_="product_pod")
            for book in books:
                name = book.select_one("h3 a").text.strip()
                price_tag = book.select_one(".price_color")
                price = price_tag.text if price_tag else "N/A"
                link = urljoin(base_url, book.h3.a["href"])
                price_clean_str = price.replace("£", "").replace("Â", "").strip()
                price_clean = float(price_clean_str)

                rating_tag = book.select_one(".star-rating")
                rating = rating_tag["class"][1] if rating_tag else "N/A"

                # opinion
                if price_clean <= 20:
                    opinion = "cheap"
                elif price_clean <= 100:
                    opinion = "expensive"
                else:
                    opinion = "very expensive"

                book_tasks.append((name, price_clean, rating, opinion, link))

            if book_tasks:
                with ThreadPoolExecutor(max_workers=10) as executor:  # tối ưu 10 thread
                    futures = {
                        executor.submit(scrape_detail, link): (name, price_clean, rating, opinion, link)
                        for (name, price_clean, rating, opinion, link) in book_tasks
                    }

                    for future in as_completed(futures):
                        name, price_clean, rating, opinion, link = futures[future]
                        description, availability, category = future.result()
                        writer.writerow([
                            name, f"£{price_clean:.2f}", link, rating, opinion,
                            description, availability, category
                        ])
                        all_books.append(name)

            # next page
            next_btn = soup.select_one(".next a")
            if next_btn:
                next_page = next_btn["href"]
                url = urljoin(url, next_page)
            else:
                url = None

            print(f"✅ Scraped {len(all_books)} books so far...")
        except Exception as e:
            log_error(url, e)
            break

print(f"🎉 Done! Total books scraped: {len(all_books)}")

# summary function
def summary():
    with open("book_store.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)
        data = list(reader)

        # most popular categories
        category_list = [row[7].strip() for row in data]
        category_count = Counter(category_list)
        print("📊 Top categories:", category_count.most_common(3))

        # count expensive vs cheap
        exp_book = sum(1 for row in data if row[4] == "expensive")
        cheap_book = sum(1 for row in data if row[4] == "cheap")
        print("The amount of expensive books:", exp_book)
        print("The amount of cheap books:", cheap_book)

        # average price by rating
        sums, count = {}, {}
        for row in data:
            try:
                money = float(row[1].replace("£", "").strip())
            except ValueError:
                continue
            rate = row[3].strip()
            sums[rate] = sums.get(rate, 0) + money
            count[rate] = count.get(rate, 0) + 1

        print("Average money based on rating:")
        for r in sums:
            avg = sums[r] / count[r]
            print(f"- {r}: £{avg:.2f} ({count[r]} records)")
df=pd.read_csv("book_store.csv")
print(df.head())
