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
            url = f"https://www.amazon.sg/s?k={book_isbn}"
            driver.get(url)

            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "a-price-whole"))
                )
                price_whole = driver.find_element(By.CLASS_NAME, 'a-price-whole').text
                price_fraction = driver.find_element(By.CLASS_NAME, 'a-price-fraction').text
                return f"{float(f'{price_whole}.{price_fraction}'):0.2f}"
            
            except (TimeoutException, NoSuchElementException):
                return "Price not found"            
        else:
            return "Invalid ISBN-13"
    finally:
        driver.quit()

def scrape_amazon_prices(book_isbns, timeout, threads):
    results = {}

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scrape_price, isbn, timeout): isbn for isbn in book_isbns}

        for future in tqdm(as_completed(futures), total=len(book_isbns), desc="\n------------------------\nScraping Amazon Prices"):
            isbn = futures[future]
            try:
                results[isbn] = future.result()
            except Exception as e:
                results[isbn] = "Error"

    return results

def amazon(inputname, outputname, timeout, threads):
    start_time = time.perf_counter()
    book_data = []
    book_isbns = []

    # Read input CSV file
    with open(inputname, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader) 

        if "isbn13" not in header:
            print("Error: No 'ISBN-13' column found in the CSV file.")
            exit()

        isbn_index = header.index("isbn13")
        amazon_index = header.index("Amazon") if "Amazon" in header else len(header)

        for row in reader:
            book_data.append(row)
            if len(row) > isbn_index and row[isbn_index]:
                book_isbns.append(row[isbn_index])

    amazon_prices = scrape_amazon_prices(book_isbns, timeout, threads)

    for row in book_data:
        if len(row) > isbn_index and row[isbn_index] in amazon_prices:
            if amazon_index >= len(row):
                row.append(amazon_prices[row[isbn_index]])
            else:
                row[amazon_index] = amazon_prices[row[isbn_index]]

    with open(outputname, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if "Amazon" not in header:
            header.append("Amazon")
        writer.writerow(header)
        writer.writerows(book_data)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    print(f"Amazon script executed in {elapsed_time:.2f} seconds")
    print(f"Amazon prices loaded in {outputname}")
