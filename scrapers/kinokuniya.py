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
            book_isbn_formatted = book_isbn.replace("-", "")
            url = f"https://singapore.kinokuniya.com/products?utf8=%E2%9C%93&is_searching=true&restrictBy%5Bavailable_only%5D=1&keywords={book_isbn_formatted}&taxon=&x=0&y=0"
            driver.get(url)

            #notes: kinokuniya has a different way of displaying prices - its span class is dynamic and changes with each search

            try:
                WebDriverWait(driver, timeout).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.ID, f"search_product_image_online_price_{book_isbn_formatted}")),
                        EC.presence_of_element_located((By.CLASS_NAME, "errors"))
                    )
                )

                price_element = driver.find_element(By.ID, f"search_product_image_online_price_{book_isbn_formatted}")
                price_text = price_element.text.strip().replace("S$", "").replace(",", "")
                return f"{float(price_text):0.2f}"
            
            except (TimeoutException, NoSuchElementException):
                return "Price not found"             
        else:
            return "Invalid ISBN-13"
    finally:
        driver.quit()

def scrape_kinokuniya_prices(book_isbns, timeout, threads):
    results = {}

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scrape_price, isbn, timeout): isbn for isbn in book_isbns}

        for future in tqdm(as_completed(futures), total=len(book_isbns), desc="\n------------------------\nScraping Kinokuniya Prices"):
            isbn = futures[future]
            try:
                results[isbn] = future.result()
            except Exception as e:
                results[isbn] = "Error"

    return results

def kinokuniya(inputname, outputname, timeout, threads):
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
        kinokuniya_index = header.index("Kinokuniya") if "Kinokuniya" in header else len(header)

        for row in reader:
            book_data.append(row)
            if len(row) > isbn_index and row[isbn_index]:
                book_isbns.append(row[isbn_index])

    kinokuniya_prices = scrape_kinokuniya_prices(book_isbns, timeout, threads)

    for row in book_data:
        if len(row) > isbn_index and row[isbn_index] in kinokuniya_prices:
            if kinokuniya_index >= len(row):
                row.append(kinokuniya_prices[row[isbn_index]])
            else:
                row[kinokuniya_index] = kinokuniya_prices[row[isbn_index]]

    with open(outputname, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if "Kinokuniya" not in header:
            header.append("Kinokuniya")
        writer.writerow(header)
        writer.writerows(book_data)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    print(f"Kinokuniya script executed in {elapsed_time:.2f} seconds")
    print(f"Kinokuniya prices loaded in {outputname}")
