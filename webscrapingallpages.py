import os
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://www.watch-movies.com.pk"
MOVIES_DATA_FILE = "movies.json"
LAST_PAGE_FILE = "last_page.txt"  # File to store last scraped page
PAGES_PER_BATCH = 10  # Scrape 10 pages, then save

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_page(url, retries=3):
    """Fetch HTML content of a webpage with retry mechanism."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.Timeout:
            print(f"⚠️ Timeout: Retrying {attempt + 1}/{retries} for {url}")
        except requests.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            break  # Stop retrying for request errors (404, 403, etc.)
    
    return None  # Return None if all retries fail

def parse_total_pages(html):
    """Extract total number of pages safely from pagination."""
    soup = BeautifulSoup(html, 'lxml')
    pages_text = soup.find('span', class_='pages')
    if pages_text:
        try:
            return int(pages_text.text.split("of")[-1].strip().replace(',', ''))
        except ValueError:
            pass
    return 1  # Default to 1 page if no pagination found

def parse_movie_list(html):
    """Extract movie page URLs from the main page."""
    soup = BeautifulSoup(html, 'lxml')
    return [urljoin(BASE_URL, a['href']) 
            for a in soup.find_all('a', class_='thumnail-imagee') 
            if a.has_attr('href')]

def parse_movie_details(html, movie_url):
    """Extract movie title, image, streaming link, and download links."""
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('h1', itemprop='name')
    poster = soup.find('img', itemprop='image')
    download_links = parse_download_links(soup)

    # Extract Streamtape embed link
    embed_link = extract_streamtape_embed(download_links)

    return {
        'title': title.text.strip() if title else 'No Title',
        'poster_url': poster['src'] if poster else None,
        'download_links': download_links,
        'streaming_embed': embed_link
    }

def parse_download_links(soup):
    """Extract download links categorized by server and quality."""
    links = {}
    for link in soup.find_all('a', href=True):
        text = link.text.strip()
        href = link['href']
        
        server = next((s for s in ['PkSpeed', 'MixDrop', 'Streamtape'] if s in text), None)
        quality = '720p' if '720p' in text else '360p' if '360p' in text else None
        
        if server and quality:
            links.setdefault(server, {}).setdefault(quality, []).append(href)
    return links

def extract_streamtape_embed(download_links):
    """Extract Streamtape embed link from the download URL."""
    if "Streamtape" in download_links and "720p" in download_links["Streamtape"]:
        streamtape_url = download_links["Streamtape"]["720p"][0]
        
        # Convert download link to embed link
        video_id = streamtape_url.split("/")[-1]  # Extract video ID
        embed_url = f"https://streamtape.com/e/{video_id}/"

        return embed_url
    
    return "No link found"

def load_existing_movies():
    """Load existing movies from the JSON file safely."""
    if os.path.exists(MOVIES_DATA_FILE):
        try:
            with open(MOVIES_DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            print("⚠️ Error reading movies.json. Starting fresh.")
    return []

def save_movies_to_json(movies):
    """Safely save movies to a JSON file."""
    temp_file = MOVIES_DATA_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(movies, file, indent=2)
    os.replace(temp_file, MOVIES_DATA_FILE)  # Atomic file update

def load_last_scraped_page():
    """Load last scraped page from file."""
    if os.path.exists(LAST_PAGE_FILE):
        try:
            with open(LAST_PAGE_FILE, "r") as file:
                return int(file.read().strip())
        except ValueError:
            return 1
    return 1  # Start from page 1 if no file exists

def save_last_scraped_page(page):
    """Save last scraped page to file."""
    with open(LAST_PAGE_FILE, "w") as file:
        file.write(str(page))

def scrape_all_movies():
    """Scrape 10 pages at a time, save progress, and resume if stopped."""
    existing_movies = load_existing_movies()
    existing_titles = {movie['title'] for movie in existing_movies}

    first_page_html = fetch_page(f"{BASE_URL}/page/1/")
    total_pages = parse_total_pages(first_page_html) if first_page_html else 1
    print(f"📌 Total pages detected: {total_pages}")

    last_scraped_page = load_last_scraped_page()
    print(f"🔄 Resuming from page {last_scraped_page}")

    for page in range(last_scraped_page, total_pages + 1):
        print(f"🔍 Scraping page {page}/{total_pages}...")
        page_html = fetch_page(f"{BASE_URL}/page/{page}/")
        if not page_html:
            print(f"⚠️ Skipping page {page} due to fetch failure.")
            continue
        
        movie_urls = parse_movie_list(page_html)
        for movie_url in movie_urls:
            movie_html = fetch_page(movie_url)
            if not movie_html:
                print(f"⚠️ Skipping movie URL {movie_url} due to fetch failure.")
                continue
            
            movie_details = parse_movie_details(movie_html, movie_url)
            
            # Skip if movie is already in the database
            if movie_details['title'] in existing_titles:
                print(f"⏩ Skipping existing movie: {movie_details['title']}")
                continue
            
            existing_movies.append(movie_details)
            existing_titles.add(movie_details['title'])
            
            # Random delay to avoid getting blocked
            time.sleep(random.uniform(1, 3))
        
        # Save progress after every 10 pages
        if page % PAGES_PER_BATCH == 0 or page == total_pages:
            save_movies_to_json(existing_movies)
            save_last_scraped_page(page)
            print(f"✅ Progress saved! Last completed page: {page}")

    print("🎉 All pages scraped successfully!")

if __name__ == "__main__":
    scrape_all_movies()
