import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from urllib.parse import quote
import html  # for unescaping HTML entities

def get_best_user_agent():
    """Returns a random user agent from a predefined list."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return user_agents[0]  # You can add logic to randomly select one if needed.

def search_imdb():
    """Searches IMDb for a movie/series and returns a list of top results (title, year, and URL)."""
    search_term = input("Enter movie/series name: ").strip()
    encoded_query = quote(search_term)
    best_ua = get_best_user_agent()
    
    headers = {
        'User-Agent': best_ua,
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    search_url = f"https://www.imdb.com/find?q={encoded_query}&s=tt&ttype=ft,tv,vg"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"🚨 Connection Error: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    # Extract the top 3 results
    for item in soup.select('.ipc-metadata-list-summary-item')[:3]:
        try:
            title_element = item.select_one('a.ipc-metadata-list-summary-item__t')
            title = title_element.text.strip()
            
            movie_url = "https://www.imdb.com" + title_element['href'].split('?')[0]
            
            # Use the provided function to extract the year from the title page
            year = extract_year_from_title_page(movie_url)
            
            results.append({'title': title, 'year': year, 'url': movie_url})
        except Exception as e:
            print(f"Error processing result: {e}")
            continue
    
    if not results:
        print("No results found!")
        return None
    
    print("\nTop Results:")
    for idx, result in enumerate(results, 1):
        print(f"{idx}. {result['title']} ({result['year']}) - {result['url']}")
    
    # Prompt user to choose one manually
    while True:
        choice = input("\nSelect a movie/series (enter number 1-3): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(results):
            return results[int(choice) - 1]['url']
        print("Invalid selection. Try again.")

def extract_year_from_title_page(movie_url):
    """
    Loads the IMDb title page and extracts the release year.
    It looks for a link or span that contains the release year.
    """
    best_ua = get_best_user_agent()
    headers = {
        'User-Agent': best_ua,
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(movie_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the release year in the title block
        year_elem = soup.find('a', href=re.compile(r'releaseinfo'))
        if year_elem:
            match = re.search(r'\d{4}', year_elem.get_text())
            if match:
                return match.group()
        
        # Fallback: try to find any text in a span that looks like a year.
        span_year = soup.find('span', text=re.compile(r'\d{4}'))
        if span_year:
            match = re.search(r'\d{4}', span_year.get_text())
            if match:
                return match.group()
    except requests.exceptions.RequestException as e:
        print(f"Error extracting year from {movie_url}: {e}")
    
    return "Unknown"

def get_trailer_url(movie_url):
    """
    Loads the movie/series page and extracts the trailer page URL.
    Typically, this is an <a> tag with an href containing '/video/'.
    """
    best_ua = get_best_user_agent()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"user-agent={best_ua}")
    
    driver = webdriver.Chrome(options=chrome_options)
    trailer_url = None
    
    try:
        driver.get(movie_url)
        # Wait for the trailer element to load
        trailer_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/video/']"))
        )
        trailer_url = trailer_element.get_attribute("href")
    except Exception as e:
        print(f"Error locating trailer link: {e}")
    finally:
        driver.quit()
    
    return trailer_url

def get_best_video_link(trailer_url):
    """
    Loads the trailer page and extracts a direct MP4 link.
    Searches the page source for a URL ending in .mp4 (with query parameters)
    and then unescapes HTML entities to get a proper URL.
    """
    best_ua = get_best_user_agent()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"user-agent={best_ua}")
    
    driver = webdriver.Chrome(options=chrome_options)
    best_video = None
    
    try:
        driver.get(trailer_url)
        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_source = driver.page_source
        
        # Look for MP4 links (including query parameters)
        mp4_links = re.findall(r'https?://[^"\s]+\.mp4(?:\?[^"\s]+)?', page_source)
        if mp4_links:
            best_video = html.unescape(mp4_links[0])
    except Exception as e:
        print(f"❌ Error fetching video link: {e}")
    finally:
        driver.quit()
    
    return best_video

if __name__ == "__main__":
    movie_url = search_imdb()
    if movie_url:
        print("\nSelected Movie/Series URL:")
        print(movie_url)
        trailer_url = get_trailer_url(movie_url)
        if trailer_url:
            print("\nTrailer Page URL:")
            print(trailer_url)
            video_link = get_best_video_link(trailer_url)
            if video_link:
                print("\n🎥 Direct MP4 Video Link (Best Quality):")
                print(video_link)
            else:
                print("❌ No direct MP4 link found on the trailer page.")
        else:
            print("❌ Unable to extract trailer URL from the movie page.")
