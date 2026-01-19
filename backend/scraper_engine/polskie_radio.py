from pathlib import Path
import os
import base64
import time
import re

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from storage.database import SessionLocal
from storage.schemas import Article
from scraper_engine.data_processor import process_article_data
from scraper_engine.browser_setup import create_driver


def gather_news(word: str, input_start_date: str, input_end_date: str):
    driver, wait = create_driver()
    driver.get('https://www.polityka.pl')

    try:
        cookies_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div/div[2]/button[4]")))
        cookies_btn.click()
        driver.get('https://www.polskieradio.pl/395,english-section')
        driver.set_page_load_timeout(5000)

        try:
            cookies_btn = driver.find_element(By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler')
            cookies_btn.click()
        except:
            pass

        search_btn = driver.find_element(
            By.CSS_SELECTOR, '.submenu-ext-category__actions--link.btn-search-toggle')
        search_btn.click()

        search_input = driver.find_element(By.ID, 'globalsearchExt')
        search_input.clear()
        search_input.send_keys(word)

        button = driver.find_element(By.XPATH, '//*[@id="searchBarExt"]/div/div')
        button.click()
        
        time.sleep(5)

        page_index = 1
        try:
            page_raw_list = driver.find_element(
                By.CSS_SELECTOR, 'ul.search-pagination').find_elements(By.CSS_SELECTOR, 'a')

            for i in page_raw_list:
                value = i.text.strip()
                if value.isdigit():
                    if int(value) > page_index:
                        page_index = int(value)
        except Exception:
            print("Pagination not found, defaulting to 1 page.")
            pass
        
        first_date = datetime.strptime(input_start_date, "%d.%m.%Y")
        second_date = datetime.strptime(input_end_date, "%d.%m.%Y")
        
        if page_index > 3:
            page_index = 3

        output_dict = {}
        index = 0
        for i in range(1, page_index + 1):
            list_elements = driver.find_element(
                By.CSS_SELECTOR, 'div.search-list').find_elements(By.CSS_SELECTOR, 'div.article-item__date')

            for item in list_elements:
                try:
                    date_text = item.text.strip()
                    print(f"Found article date: {date_text}")
                    date_value = datetime.strptime(date_text, "%d.%m.%Y")
                    
                    if first_date <= date_value <= second_date:
                        print(f"Date {date_text} is within range.")
                        article = item.find_element(By.XPATH, "..")
                        title = article.find_element(By.CSS_SELECTOR, "h2").text.strip()
                        link = article.find_element(By.CSS_SELECTOR, "a.article-item__photo").get_attribute('href').strip()
                        
                        output_dict[index] = {
                            "date": datetime.strftime(date_value, "%d.%m.%Y"),
                            "title": title,
                            "link": link
                        }
                        index += 1
                    else:
                        print(f"Date {date_text} out of range.")
                except ValueError as e:
                    print(f"Date parse error: {e}")
                    continue

            try:
                page_raw_list_next = driver.find_element(
                    By.CSS_SELECTOR, 'ul.search-pagination').find_elements(By.CSS_SELECTOR, 'li')
                for li in page_raw_list_next:
                    value = li.find_element(By.CSS_SELECTOR, 'a').text.strip()
                    if not value.isdigit():
                        continue
                    if int(value) == i+1:
                        li.click()
                        time.sleep(2)
                        break
            except Exception:
                pass

        os.makedirs("texts", exist_ok=True)
        os.makedirs("pdfs", exist_ok=True)

        response_data = []

        for key, value in output_dict.items():
            try:
                driver.get(value.get('link'))
                
                content_p = driver.find_element(By.CSS_SELECTOR, "div.content").find_elements(By.CSS_SELECTOR, "p")
                paragraphs = '\n'.join(p.text.strip() for p in content_p)
                
                # Sanitize title for filename
                safe_title = re.sub(r'[\/:*?"<>|]', "", value.get('title'))
                pdf_filename = f"{key}_{safe_title}.pdf"
                full_pdf_path = os.path.join("pdfs", pdf_filename)
                
                result = driver.execute_cdp_cmd("Page.printToPDF", {
                    "printBackground": True,
                    "paperWidth": 8.27,
                    "paperHeight": 11.69,
                })
                with open(full_pdf_path, "wb") as f:
                    f.write(base64.b64decode(result["data"]))
                
                article_data = {
                    "title": value.get('title'),
                    "link": value.get('link'),
                    "published_date": value.get('date'),
                    "author": "Polskie Radio"
                }

                saved_article = process_article_data(article_data, paragraphs, pdf_filename)
                response_data.append(saved_article)

            except Exception as e:
                print(e)

        return response_data
    finally:
        driver.quit()
