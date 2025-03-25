import os
import isbnformat
from scrapers import amazon, kinokuniya, thryft

timeout = 5
threads = 25 # webscraping is i/o based so depends on user's ram generally can try anywhere between 20-50

# note: for threads, thryft seems to have a rate limit, 5 tentatively seems to work

#inputs for user
while True:
    inputname = input("Enter the input CSV/XLSX file name (including .csv or .xlsx): ")
    if os.path.isfile(inputname):
        break
    else:
        print(f"File '{inputname}' does not exist. Please try again.")

while True:
    outputname = input("Name your output file (including .csv): ")
    if outputname.endswith(".csv"):
        break
    else:
        print("Output file name must end with '.csv'. Please try again.")

print("/n formatting isbn13...")
isbnformat.isbnformat(inputname, outputname)

print("\nstarting amazon price scraping...")
amazon.amazon(outputname, outputname, timeout, threads)

print("\nstarting kinokuniya price scraping...")
kinokuniya.kinokuniya(outputname, outputname, timeout, threads)

# thryft rate limits to a max of 5 threads...
print("\nstarting thryft price scraping...")
thryft.thryft(outputname, outputname, timeout, 5)

print("\nscraping completed! \nresults saved to:", outputname)
