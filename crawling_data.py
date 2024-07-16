import requests
from bs4 import BeautifulSoup
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
# Đường dẫn đến ChromeDriver
driver_path = 'path/to/chromedriver'
# Khởi động ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Truy cập trang web
url = 'https://www.imdb.com/search/title/?title=axel&title_type=feature&release_date=2022-01-01,2024-07-10&sort=year,desc'
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
            
            # Đợi cho đến khi nút "More" có thể click được
            more_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'ipc-see-more__text')))
            more_button.click()
            time.sleep(2)  # Đợi một chút để nội dung mới tải xong
        except Exception as e:
            print(f'Error: {e}')
            break
# Gọi hàm để cuộn trang và click vào nút "More"
load_more_content(driver)
# lấy data cua toan bo cac bo phim trong trang web
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
        # Lấy text từ thẻ <h3> bên trong thẻ <a>
        title_film = link.find('h3', class_='ipc-title__text').text.strip()
        first_dot_index = title_film.find('.')
        if first_dot_index != -1:
        # Loại bỏ số đầu và dấu chấm
            new_title = title_film[first_dot_index + 2:].strip()
        else:
            new_title = title_film  # Nếu không có dấu chấm, giữ nguyên tiêu đề
        # In ra tên phim và liên kết
        print(cout,new_title, 'https://www.imdb.com' + link_film)
        cout += 1

# Truy cập trang web
for i in link_film_acc:
    url_film = f'https://www.imdb.com{i}'
    r_content = requests.get(url_film)
    soup_detail = BeautifulSoup(r_content.content, 'html.parser')
    divs_detail = soup_detail.find_all('div', class_='ipc-metadata-list-item__label')
    print(divs_detail)