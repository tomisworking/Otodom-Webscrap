# Otodom Real Estate Scraper

This project provides a fast and straightforward Python script to automatically scrape real estate listings from the Otodom portal. It bypasses tedious HTML parsing by extracting data directly from the hidden JSON payload (`__NEXT_DATA__`) loaded by the website in the background, ensuring 100% accuracy of the retrieved information.

## Quick Start in 3 Steps

1. **Install Requirements**
   Make sure you have Python installed. Create a virtual environment in the project directory and install the necessary packages:
   ```cmd
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Adjust Configuration (Optional)**
   Before running the script, you can easily tweak the scraping parameters in the `options.json` file. This file controls details such as the target city, district, and the number of pages you want to retrieve. See the [Settings Glossary](#-settings-glossary-optionsjson) below.

3. **Run the Script**
   ```cmd
   python scraper.py
   ```
   The script will print its progress in the console. The retrieved data (with duplicates removed) will be saved to a CSV file specified in your configuration (e.g., `wynajem_wroclaw.csv`).

---

## Settings Glossary (options.json)

The `options.json` file allows you to control the program's behavior without touching the python code. Here is what each parameter means:

*   **`"transaction"`**: Type of transaction. 
    *   *Possible values*: `"wynajem"` (for rent) or `"sprzedaz"` (for sale).
*   **`"estate"`**: Type of real estate. 
    *   *Possible values*: `"mieszkanie"` (apartment), `"dom"` (house), `"dzialka"` (plot), `"pokoj"` (room), etc.
*   **`"region"`**: Province/Region (lowercase, NO Polish characters). 
    *   *Example*: `"dolnoslaskie"`, `"mazowieckie"`.
*   **`"city"`**: City name (lowercase, NO Polish characters). 
    *   *Example*: `"wroclaw"`, `"warszawa"`.
*   **`"district"`**: (OPTIONAL) District within the chosen city. Leave it completely empty `""` to search across the entire city, or specify a particular district name.
    *   *Example*: `"krzyki"`, `"mokotow"`.
*   **`"pages"`**: How many pages of search results to iterate over. One page usually contains around 35 property listings.
    *   *Number*: e.g. `3` (retrieves ~100 offers), `50` (retrieves ~1750 offers).
*   **`"min_delay"` and `"max_delay"`**: The scraper imitates human browsing by taking short, randomized pauses when switching pages (in seconds). Keep the defaults (e.g., 1.5 and 3.5) to avoid rate-limiting or getting your IP address blocked by Otodom's servers.
*   **`"output_file"`**: The name of the final CSV file that will be created on your disk containing the data.
    *   *Example*: `"my_database.csv"`

### Example Configuration:

Fetching **apartments for sale in Warsaw's Mokotów** district, downloading the **first 10 pages** of search results (~350 offers).

```json
{
  "transaction": "sprzedaz",
  "estate": "mieszkanie",
  "region": "mazowieckie",
  "city": "warszawa",
  "district": "mokotow",
  "pages": 10,
  "min_delay": 1.5,
  "max_delay": 3.5,
  "output_file": "sales_warsaw_mokotow.csv"
}
```

## Script Output

Upon successful execution, you will receive a `.csv` file which can be opened in Excel or analyzed using Data Science environments (like Jupyter or Pandas). 
Here is the standard information extracted for each apartment listing:
`id`, `title`, `total_price`, `rent_price` (additional administration rent if applicable), `price_per_sqm`, `area` (in square meters), `rooms`, `floor`, and `location`.
