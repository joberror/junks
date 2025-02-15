import requests
from bs4 import BeautifulSoup
import re
import html  # for unescaping HTML entities
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_best_user_agent():
    """Returns a random user agent from a predefined list."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return user_agents[0]

def create_session_with_retries():
    """Creates a session with retry logic."""
    session = requests.Session()
    retries = Retry(
        total=5,  # Total number of retries
        backoff_factor=1,  # Exponential backoff (e.g., 1s, 2s, 4s, ...)
        status_forcelist=[429, 500, 502, 503, 504]  # Retry on these status codes
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def search_imdb(session):
    """Searches IMDb for a movie/series and returns a list of top results (title, year, and URL)."""
    search_term = input("Enter movie/series name: ").strip()
    encoded_query = quote(search_term)
    best_ua = get_best_user_agent()
    
    headers = {
        'User-Agent': best_ua,
        'Accept-Language': 'en-US,en;q=0.9'
    }
    session.headers.update(headers)
    
    search_url = f"https://www.imdb.com/find?q={encoded_query}&s=tt&ttype=ft,tv,vg"
    
    try:
        response = session.get(search_url, timeout=30)
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
            year = extract_year_from_title_page(session, movie_url)
            
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

def extract_year_from_title_page(session, movie_url):
    """
    Loads the IMDb title page and extracts the release year.
    It looks for a link or span that contains the release year.
    """
    try:
        response = session.get(movie_url, timeout=30)
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

def get_trailer_url(session, movie_url):
    """
    Loads the movie/series page and extracts the trailer page URL.
    Typically, this is an <a> tag with an href containing '/video/'.
    """
    try:
        response = session.get(movie_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the trailer link
        trailer_element = soup.find('a', href=re.compile(r'/video/'))
        if trailer_element:
            trailer_url = "https://www.imdb.com" + trailer_element['href']
            return trailer_url
    except requests.exceptions.RequestException as e:
        print(f"Error locating trailer link: {e}")
    
    return None

def get_best_video_link(session, trailer_url):
    """
    Uses requests to load the trailer page and extract a signed MP4 link.
    Searches the page source for a URL ending in .mp4 (with query parameters like Expires, Signature, Key-Pair-Id).
    Includes necessary headers to avoid 403 Forbidden errors.
    """
    best_ua = get_best_user_agent()
    headers = {
        'User-Agent': best_ua,
        'Referer': trailer_url,  # Set the Referer header to the trailer page URL
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    session.headers.update(headers)
    
    try:
        # Fetch the trailer page
        response = session.get(trailer_url, timeout=30)
        response.raise_for_status()
        page_source = response.text
        
        # Look for signed MP4 links (including query parameters like Expires, Signature, Key-Pair-Id)
        mp4_links = re.findall(r'https?://[^"\s]+\.mp4(?:\?Expires=\d+&Signature=[^&]+&Key-Pair-Id=[^"\s]+)', page_source)
        if mp4_links:
            best_video = html.unescape(mp4_links[0])  # Decode HTML entities
            return best_video
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching video link: {e}")
    
    return None

if __name__ == "__main__":
    # Create a session with retry logic
    session = create_session_with_retries()
    
    # Search IMDb for a movie/series
    movie_url = search_imdb(session)
    if movie_url:
        print("\nSelected Movie/Series URL:")
        print(movie_url)
        
        # Get the trailer URL
        trailer_url = get_trailer_url(session, movie_url)
        if trailer_url:
            print("\nTrailer Page URL:")
            print(trailer_url)
            
            # Use requests to extract the MP4 video link
            video_link = get_best_video_link(session, trailer_url)
            if video_link:
                print("\n🎥 Direct MP4 Video Link (Best Quality):")
                print(video_link)
                
                # Test the MP4 link with headers to ensure it works
                headers = {
                    'User-Agent': get_best_user_agent(),
                    'Referer': trailer_url,  # Include the Referer header
                    'Accept-Language': 'en-US,en;q=0.9'
                }
                try:
                    test_response = requests.head(video_link, headers=headers, timeout=30)
                    if test_response.status_code == 200:
                        print("\n✅ MP4 link is accessible!")
                    else:
                        print(f"\n❌ MP4 link returned status code: {test_response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"\n❌ Error testing MP4 link: {e}")
            else:
                print("❌ No direct MP4 link found on the trailer page.")
        else:
            print("❌ Unable to extract trailer URL from the movie page.")
