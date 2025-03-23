import os
from scrapers import amazon, thryft

timeout = 5

#inputs for user
while True:
    inputname = input("Enter the input CSV file name (including .csv): ")
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

print("\nstarting amazon price scraping... (⊙ Д⊙ )")
amazon.amazon(inputname, outputname, timeout)

print("\nstarting thryft price scraping... |ω • ´)")
thryft.thryft(outputname, outputname, timeout)

print("\nscraping completed! (´・ω・｀) \nresults saved to:", outputname)
