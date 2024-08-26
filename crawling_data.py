import requests
import json
import csv
import psycopg2
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from bs4 import BeautifulSoup
from psycopg2 import OperationalError
# Khởi động ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
# Truy cập trang web
url = 'https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-12-31&sort=year,desc'
driver.get(url)
# Đợi một chút để trang web tải xong
wait = WebDriverWait(driver, 10)
# Hàm để cuộn trang và click vào nút "More"
def load_more_content(driver):
    while True:
        try:
            # Cuộn xuống cuối trang
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Đợi một chút để nội dung mới tải xong
            # Kiểm tra sự tồn tại của nút "More"
            more_buttons = driver.find_elements(By.CLASS_NAME, 'ipc-see-more__text')
            if not more_buttons:
                print("Không còn nút 'More'. Dừng lại.")
                break
            # Đợi cho đến khi nút "More" có thể click được
            more_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'ipc-see-more__text')))
            more_button.click()
            time.sleep(2)  # Đợi một chút để nội dung mới tải xong
        except Exception as e:
            print(f'Error: {e}')
            break
# Gọi hàm để cuộn trang và click vào nút "More"
load_more_content(driver)
# Lấy data cua toan bo cac bo phim trong trang web
movie_elements = driver.find_elements(By.CSS_SELECTOR, '.ipc-metadata-list.ipc-metadata-list--dividers-between.sc-748571c8-0.jmWPOZ.detailed-list-view.ipc-metadata-list--base')
# Extract HTML nội dung từ mỗi element
html_content = []
for element in movie_elements:
    html_content.append(element.get_attribute('outerHTML'))
# Join all HTML content into a single string
html_str = ''.join(html_content)
# Đóng trình duyệt
driver.quit()
# Parse HTML with BeautifulSoup
soup = BeautifulSoup(html_str, 'html.parser')
link_film_acc = []
divs = soup.find_all('div', class_='ipc-title ipc-title--base ipc-title--title ipc-title-link-no-icon ipc-title--on-textPrimary sc-b189961a-9 iALATN dli-title')
cout = 1
# Lặp qua từng thẻ <div> để lấy tên phim và liên kết
for div in divs:
    # Tìm thẻ <a> trong thẻ <div>
    link = div.find('a', class_='ipc-title-link-wrapper') 
    # Kiểm tra nếu tìm thấy thẻ <a> và lấy href từ thuộc tính 'href'
    if link:
        link_film = link.get('href')
        link_film_acc.append(link_film)
        cout += 1
# Ket noi database
# Thong tin ket noi
hostname = 'localhost' 
port = 5432
database = 'postgres'
username = 'da'
password = 'da123@'
# Ket noi den database
try:
    connection = psycopg2.connect(
        host=hostname,
        port=port,
        database=database,
        user=username,
        password=password
    )
    cursor = connection.cursor()
    print("Kết nối thành công!")
except OperationalError as e:
    print(f"Lỗi kết nối: {e}")
# Gửi yêu cầu với User-Agent của trình duyệt thật
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
# Truy cập trang web va lay du lieu

for i in link_film_acc:
    url_film = f'https://www.imdb.com{i}'
    r_content = requests.get(url_film, headers=headers)
    soup_detail = BeautifulSoup(r_content.content, 'html.parser')
    # Title cua bo phim
    title_film_detail = soup_detail.find('span', class_='hero__primary-text')
    name_film = title_film_detail.text
    # Noi dung cua Detail
    detail_release_date = soup_detail.find('li', {'data-testid': 'title-details-releasedate'})
    # release_date_first
    release_date_html = detail_release_date.find('a', class_='ipc-metadata-list-item__list-content-item')
    release_date_str_full = release_date_html.text 
    release_date_str = release_date_str_full.split('(')[0].strip() 
    release_date_first = datetime.strptime(release_date_str, "%B %d, %Y")
    # Country of origin
    detail_country_origin = soup_detail.find('li', {'data-testid': 'title-details-origin'})
    find_country_origin = detail_country_origin.find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link') if detail_country_origin else None
    country_origin = find_country_origin.text if find_country_origin else None
    # IMDB Rating
    detail_rating = soup_detail.find('div', {'data-testid': 'hero-rating-bar__aggregate-rating__score'})
    rating_str = detail_rating.find('span',class_='sc-eb51e184-1 cxhhrI') if detail_rating else None
    rating = float(rating_str.text.strip()) if rating_str else None
    # Budget
    detail_budget = soup_detail.find('li', {'data-testid': 'title-boxoffice-budget'})
    budget_full = detail_budget.find('span',class_='ipc-metadata-list-item__list-content-item') if detail_budget else None
    budget_str = budget_full.text if budget_full else None
    budget = budget_str.split('(')[0].strip() if budget_str else None
    currency_budget = re.findall(r'\D+', budget)[0] if budget else None
    amount_bg = re.findall(r'\d+', budget_str) if budget_str else None
    amount_budget = int(''.join(amount_bg)) if amount_bg else None
    # Genres
    detail_genres = soup_detail.find('div', {'data-testid': 'genres'})
    genres_str = detail_genres.find('span',class_='ipc-chip__text') if detail_genres else None
    genres = genres_str.text if genres_str else None
    # print(url_film, title_film_detail.text, release_date_first, country_origin, rating, budget, currency_budget, amount_budget , genres)
    # insert du lieu vao database
    insert_query = '''
    insert into film (url_film, name_film, release_date_first, country_origin, rating, budget, currency_budget, amount_budget, genres)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    try:
        cursor.execute(insert_query,(url_film, name_film, release_date_first, country_origin, rating, budget, currency_budget, amount_budget, genres))
        # Lưu thay đổi
        connection.commit()
        # print("Da luu data thanh cong")
    except Exception as e:
        print(f"SQL Error for {url_film}: {e}")
        connection.rollback()
        
# Dong connection
cursor.close()
connection.close()
print("Kết nối PostgreSQL đã đóng")