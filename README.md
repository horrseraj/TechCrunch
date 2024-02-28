# Genlib Scraper
# Description
This Python script is designed to scrape data from Genlib using a custom Spider and store the result books with all the related fields in desired format. It also stores all the process in the database.

# Prerequisites
Python 3.x
Scrapy library
PostgreSQL database (configured in local_settings.py)

# Installation
Clone the repository.
Install the required dependencies using pip install -r requirements.txt.
Configure the database connection details in local_settings.py.

# Usage
1. Run the script:

    ```bash
    python main.py -s "your_search_key" -f "output_format"
    ```
    -s, --key: Search key for Genlib Spider (required)
    -f, --format: Output format for scraped data (default: json, choices: json, csv, xml)

2. The script will create an output directory with timestamped folder containing scraped data and downloaded resources.

# Database Management
The script utilizes a PostgreSQL database to store information related to search keys, search results, authors, books, and book authors. Tables are created automatically upon script execution.

# Contact Information
For questions or feedback, you can contact the author at horrseraj@gmail.com.
