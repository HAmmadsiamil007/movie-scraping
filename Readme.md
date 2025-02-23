# Movie Scraper for Watch-Movies.com.pk

## Overview
This script scrapes the latest movies from the first page of [watch-movies.com.pk](https://www.watch-movies.com.pk), extracts movie details (title, poster, streaming, and download links), and updates a JSON file (`movies.json`) with new entries.

## Features
- Fetches the latest movies from the first page
- Extracts movie titles, posters, and download links
- Categorizes download links by server and quality
- Generates Streamtape embed links for streaming
- Stores data in `movies.json` while avoiding duplicates
- Implements retry mechanisms for failed requests

## Prerequisites
- Python 3.x
- Required dependencies:

```bash
pip install requests beautifulsoup4 lxml
```

## Configuration
The script uses the following constants:
- `BASE_URL`: Main URL of the movie website (`https://www.watch-movies.com.pk`)
- `MOVIES_DATA_FILE`: JSON file to store movie data (`movies.json`)
- `HEADERS`: HTTP headers for requests (to simulate a browser)

## How It Works
1. **Fetch Page**: Retrieves HTML content from the first page.
2. **Extract Movie URLs**: Identifies all movie links on the page.
3. **Parse Movie Details**: Extracts title, poster, streaming embed, and download links.
4. **Check for Duplicates**: Skips movies that already exist in `movies.json`.
5. **Save Data**: Updates `movies.json` with new movies.

## Usage
Run the script using:

```bash
python movie_scraper.py
```

## Functions Explained
### `fetch_page(url, retries=3)`
Fetches HTML content with retry logic for handling timeouts and errors.

### `parse_movie_list(html)`
Extracts movie URLs from the main page.

### `parse_movie_details(html, movie_url)`
Extracts movie metadata (title, poster, streaming, and downloads).

### `parse_download_links(soup)`
Categorizes download links based on server and quality.

### `extract_streamtape_embed(download_links)`
Generates Streamtape embed links from download URLs.

### `load_existing_movies()`
Loads stored movies from `movies.json`, handling errors.

### `save_movies_to_json(movies)`
Saves movie data safely with an atomic update method.

### `scrape_first_page()`
Main function that scrapes, processes, and saves new movies.

## Output Format
Movies are stored in `movies.json` in the following format:

```json
[
  {
    "title": "Example Movie",
    "poster_url": "https://example.com/poster.jpg",
    "download_links": {
      "PkSpeed": {"720p": ["https://link.com"]}
    },
    "streaming_embed": "https://streamtape.com/e/XXXX/"
  }
]
```

## Notes
- The script only scrapes the first page to keep updates efficient.
- If the scraper fails due to a website change, update the parsing logic accordingly.
- This script is for personal use. Scraping copyrighted content may violate terms of service.

## License
This script is open-source and free to use. Modify and use it at your own discretion.

