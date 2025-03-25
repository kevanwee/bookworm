# 📚 Bookworm: Automated Book Price Scraper

Bookworm is a web scraper that retrieves book prices from Amazon and Thryft based on ISBN-13. It takes a CSV/XLSX file as input and outputs a new CSV with the scraped prices.

---

## 🛠 Installation

### Clone the Repository
```
git clone https://github.com/kevanwee/bookworm.git
cd bookworm
```

### Install Dependencies
This project requires Selenium for web scraping. Install it using:
```
pip install selenium
```

## 🚀 Running the Scraper

Run the script by executing:
```
python bookworm.py
```
(Note: Performance may vary based on the number of threads set in bookworm.py)

### How it Works:
1. Enter the input CSV file (must include an `ISBN-13` column). (Note that the ISBN-13 numbers should be input like 978-0571295715 with the hyphen)
2. Enter the output CSV file name (where scraped data will be saved).
3. At this point of time, this currently supports:
   - Amazon
   - Thryft
   - Stay tuned for more updates and more supported websites!
---

## 📋 Example Output in CSV:

| Title          | ISBN-13        | Amazon | Thryft | Kinokuniya |
|-----------------|----------------|--------|--------|--------|
| Example Book   | 978-1234567890  | 12.99  | 5.20 | 14.50  |
| Another Book   | 979-9876543210  | 8.99   | 4.30   | 9.20   |


---
(See testdata.csv/testdata2.xlsx for a sample of the format)

## 🐛 Troubleshooting

### ChromeDriver Issues?
- Make sure Google Chrome is updated.
- Download the correct ChromeDriver version.

### Website Blocking Requests?
- Try increasing the timeout to avoid detection.
- Use headless mode (enabled by default).
- Reduce the number of threads

---
