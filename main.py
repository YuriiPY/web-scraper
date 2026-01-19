import base64
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


driver = webdriver.Chrome()

driver.get('https://www.polskieradio.pl/395,english-section')

driver.set_page_load_timeout(5000)

cookies_btn = driver.find_element(
    By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler')

print("HERE -> ", cookies_btn)
cookies_btn.click()

search_btn = driver.find_element(
    By.CSS_SELECTOR, '.submenu-ext-category__actions--link.btn-search-toggle')

search_btn.click()

search_input = driver.find_element(By.ID, 'globalsearchExt')
search_input.clear()

searching_input = input("Enter data: ")
search_input.send_keys(searching_input)

button = driver.find_element(By.XPATH, '//*[@id="searchBarExt"]/div/div')
button.click()

time.sleep(5)

page_raw_list = driver.find_element(
    By.CSS_SELECTOR, 'ul.search-pagination').find_elements(By.CSS_SELECTOR, 'a')


page_index = 1

for i in page_raw_list:
    value = i.text.strip()
    if value.isdigit():
        if int(value) > page_index:
            page_index = int(value)

output_dict = {}

first_date = datetime.strptime("01.10.2025", "%d.%m.%Y")
second_date = datetime.strptime("31.10.2025", "%d.%m.%Y")

index = 0

print(f"Pages found: {page_index}")

for i in range(1, page_index):
    print(f"Page index: {i}")

    list_elements = driver.find_element(
        By.CSS_SELECTOR, 'div.search-list').find_elements(By.CSS_SELECTOR, 'div.article-item__date')

    for item in list_elements:
        date_value = datetime.strptime(item.text.strip(), "%d.%m.%Y")

        article = item.find_element(By.XPATH, "..")

        if first_date <= date_value <= second_date:
            output_dict[index] = {
                "date": datetime.strftime(date_value, "%d.%m.%Y"),
                "title": article.find_element(By.CSS_SELECTOR, "h2").text.strip(),
                "link": article.find_element(By.CSS_SELECTOR, "a.article-item__photo").get_attribute('href').strip()
            }
            index += 1

    page_raw_list = driver.find_element(
        By.CSS_SELECTOR, 'ul.search-pagination').find_elements(By.CSS_SELECTOR, 'li')
    try:
        for li in page_raw_list:

            value = li.find_element(By.CSS_SELECTOR, 'a').text.strip()

            if not value.isdigit():
                continue

            if int(value) == i+1:
                li.click()
                time.sleep(2)
    except Exception:
        pass

os.makedirs("texts", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

try:
    for key, value in output_dict.items():
        driver.get(value.get('link'))

        paragraphs = '\n'.join(
            p.text.strip() for p in driver.find_element(By.CSS_SELECTOR, "div.content").find_elements(By.CSS_SELECTOR, "p"))
        text_file_path = os.path.join("texts", f"{key}.txt")
        with open(text_file_path, "w", encoding="utf-8") as file:
            file.write(paragraphs)

        pdf_file_path = os.path.join("pdfs", f"{key}.pdf")
        with open(pdf_file_path, "wb") as file:
            pdf = driver.execute_cdp_cmd("Page.printToPDF", {
                "printBackground": True,
                "paperWidth": 8.27,
                "paperHeight": 11.69,
            })
            file.write(base64.b64decode(pdf["data"]))

except Exception as e:
    print(e)

print(output_dict)

driver.close()
