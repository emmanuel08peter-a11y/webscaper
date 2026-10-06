import os
import re
import time
import requests
import pandas as pd

from bs4 import BeautifulSoup
from urllib.parse import urljoin


# Website to scrape
BASE_URL = "https://books.toscrape.com/"


# User-Agent
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


# Create folder for book covers
os.makedirs("book_covers", exist_ok=True)


# Store all scraped books
books = []


def sanitize_filename(title):
    """
    Remove characters that are not safe in filenames.
    """
    filename = re.sub(r'[\\/:*?"<>|]', '', title)
    return filename.strip()


def scrape_page(url):
    """
    Scrape one page of books.
    """

    print(f"Scraping: {url}")

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    # Make sure the request was successful
    response.raise_for_status()

    # Check that the server returned 200 OK
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all book containers
    book_items = soup.select("article.product_pod")

    for book in book_items:

        # -------------------------
        # TITLE
        # -------------------------
        title = book.select_one("h3 a")["title"]

        # -------------------------
        # PRICE
        # -------------------------
        price_text = book.select_one(
            "p.price_color"
        ).get_text(strip=True)

        price = float(
        price_text.replace("£", "").replace("Â", "").strip()
        )

        # -------------------------
        # STAR RATING
        # -------------------------
        rating_element = book.select_one(
            "p.star-rating"
        )

        rating_classes = rating_element.get("class", [])

        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        rating = 0

        for rating_name, rating_number in rating_map.items():
            if rating_name in rating_classes:
                rating = rating_number
                break

        # -------------------------
        # AVAILABILITY
        # -------------------------
        availability = book.select_one(
            "p.instock.availability"
        ).get_text(" ", strip=True)

        # -------------------------
        # IMAGE URL
        # -------------------------
        image_tag = book.select_one("img")

        image_src = image_tag.get("src")

        image_url = urljoin(
            url,
            image_src
        )

        # -------------------------
        # DOWNLOAD IMAGE
        # -------------------------
        safe_title = sanitize_filename(title)

        image_path = os.path.join(
            "book_covers",
            safe_title + ".jpg"
        )

        try:

            image_response = requests.get(
                image_url,
                headers=headers,
                timeout=10
            )

            image_response.raise_for_status()

            with open(image_path, "wb") as image_file:
                image_file.write(
                    image_response.content
                )

            print(f"Downloaded: {title}")

        except requests.RequestException as error:

            print(
                f"Could not download image for "
                f"{title}: {error}"
            )

            image_path = ""

        # -------------------------
        # SAVE BOOK DATA
        # -------------------------
        books.append({
            "title": title,
            "price_gbp": price,
            "rating": rating,
            "availability": availability,
            "image_url": image_url,
            "local_image_path": image_path
        })


# ---------------------------------------
# PAGINATION
# ---------------------------------------

current_url = BASE_URL

while current_url:

    try:
        scrape_page(current_url)

    except requests.RequestException as error:

        print(
            f"Error accessing {current_url}: {error}"
        )

        break

    # Request throttling
    time.sleep(0.5)

    # Request the current page again
    response = requests.get(
        current_url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Find the next page
    next_link = soup.select_one(
        "li.next a"
    )

    if next_link:

        next_url = next_link.get("href")

        current_url = urljoin(
            current_url,
            next_url
        )

    else:

        current_url = None


# ---------------------------------------
# EXPORT DATA TO CSV
# ---------------------------------------

df = pd.DataFrame(books)

df.to_csv(
    "books_data.csv",
    index=False
)

print("\nScraping completed!")
print(f"Total books scraped: {len(books)}")
print("CSV file created: books_data.csv")
print("Images saved inside: book_covers/")