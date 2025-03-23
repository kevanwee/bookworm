import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def scrape_amazon_prices(book_isbns, timeout):
    # webdriver setup
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    results = {}

    try:
        for book_isbn in book_isbns:
            if sum(char.isdigit() for char in book_isbn) == 13 and (book_isbn.startswith("978") or book_isbn.startswith("979")):
                url = f"https://www.amazon.sg/s?k={book_isbn}"
                driver.get(url)

                try:
                    WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "a-price-whole"))
                    )

                    try:
                        price_whole = driver.find_element(By.CLASS_NAME, 'a-price-whole').text
                        price_fraction = driver.find_element(By.CLASS_NAME, 'a-price-fraction').text
                        results[book_isbn] = f"{float(f'{price_whole}.{price_fraction}'):0.2f}"

                    except NoSuchElementException:
                        results[book_isbn] = "Price not found"

                except TimeoutException:
                    results[book_isbn] = "Price not found"

            else:
                results[book_isbn] = "Invalid ISBN-13"

    finally:
        driver.quit()

    return results


def amazon(inputname, outputname, timeout):

    book_data = []
    book_isbns = []

    # read input
    with open(inputname, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader) 

        if "ISBN-13" not in header:
            print("Error: No 'ISBN-13' column found in the CSV file.")
            exit()

        isbn_index = header.index("ISBN-13")
        amazon_index = header.index("Amazon") if "Amazon" in header else len(header)

        for row in reader:
            book_data.append(row)
            if len(row) > isbn_index and row[isbn_index]:
                book_isbns.append(row[isbn_index])

    # run amazon scrape 
    amazon_prices = scrape_amazon_prices(book_isbns, timeout)

    # append data
    for row in book_data:
        if len(row) > isbn_index and row[isbn_index] in amazon_prices:
            if amazon_index >= len(row):
                row.append(amazon_prices[row[isbn_index]])
            else:
                row[amazon_index] = amazon_prices[row[isbn_index]]

    # write output
    with open(outputname, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if "Amazon" not in header:
            header.append("Amazon")
        writer.writerow(header)

        writer.writerows(book_data)

    print(f"Amazon prices loaded in {outputname}")