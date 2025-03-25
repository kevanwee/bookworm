from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import csv
import time
from tqdm import tqdm

def scrape_price(book_isbn, timeout):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--silent')
    driver = webdriver.Chrome(options=options)

    try:
        if sum(char.isdigit() for char in book_isbn) == 13 and (book_isbn.startswith("978") or book_isbn.startswith("979")):
            book_isbn_formatted = book_isbn.replace("-", "")

            url = f'https://thryft.asia/search?options%5Bprefix%5D=last&q="{book_isbn_formatted}"'
            driver.get(url)

            # note: thryft's search is more sensitive and requires "" around the isbn to get the exact match

            try:
                WebDriverWait(driver, timeout).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "product-item__price-main")),
                        EC.presence_of_element_located((By.CLASS_NAME, "sale")),
                        EC.presence_of_element_located((By.CLASS_NAME, "search__empty"))
                    )
                )

                try:
                    price_element = driver.find_element(By.CLASS_NAME, "sale")
                    price_text = price_element.text.strip().replace("$", "")
                    return f"{float(price_text):0.2f}"
                except NoSuchElementException:
                    try:
                        price_element = driver.find_element(By.CLASS_NAME, "product-item__price-main")
                        price_text = price_element.text.strip().replace("$", "")
                        return f"{float(price_text):0.2f}"
                    except NoSuchElementException:
                        return "Price not found"

                

            except TimeoutException:
                return "Price not found"

        else:
            return "Invalid ISBN-13"

    finally:
        driver.quit()

def scrape_thryft_prices(book_isbns, timeout, threads):
    results = {}

    with ThreadPoolExecutor(max_workers=threads) as executor: 
        futures = {executor.submit(scrape_price, isbn, timeout): isbn for isbn in book_isbns}

        for future in tqdm(as_completed(futures), total=len(book_isbns), desc="\n------------------------\nScraping Thryft Prices"):
            isbn = futures[future]
            try:
                results[isbn] = future.result()
            except Exception as e:
                results[isbn] = "Error"

    return results

def thryft(inputname, outputname, timeout, threads):
    start_time = time.perf_counter()
    book_data = []
    book_isbns = []

    with open(inputname, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)

        if "isbn13" not in header:
            print("Error: No 'ISBN-13' column found in the CSV file.")
            exit()

        isbn_index = header.index("isbn13")
        thryft_index = header.index("Thryft") if "Thryft" in header else len(header)

        for row in reader:
            book_data.append(row)
            if len(row) > isbn_index and row[isbn_index]:
                book_isbns.append(row[isbn_index])

    thryft_prices = scrape_thryft_prices(book_isbns, timeout, threads)

    for row in book_data:
        if len(row) > isbn_index and row[isbn_index] in thryft_prices:
            if thryft_index >= len(row):
                row.append(thryft_prices[row[isbn_index]])
            else:
                row[thryft_index] = thryft_prices[row[isbn_index]]

    with open(outputname, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if "Thryft" not in header:
            header.append("Thryft")
        writer.writerow(header)
        writer.writerows(book_data)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    print(f"Thryft script executed in {elapsed_time:.2f} seconds")
    print(f"Thryft prices loaded in {outputname}")
