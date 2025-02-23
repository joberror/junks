import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote

def get_best_user_agent():
    """Returns a random user agent from a predefined list."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return user_agents[0]

def search_imdb():
    """Searches IMDb for a movie/series and returns a list of top results (title, year, type, and URL)."""
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
            
            # Determine if it's a movie or TV series
            media_type = "Movie"
            if "TV Series" in item.get_text():
                media_type = "TV Series"
            
            # Extract the year
            year_elem = item.find('span', class_='ipc-metadata-list-summary-item__li')
            year = year_elem.text.strip() if year_elem else "Unknown"
            
            results.append({'title': title, 'year': year, 'type': media_type, 'url': movie_url})
        except Exception as e:
            print(f"Error processing result: {e}")
            continue
    
    if not results:
        print("No results found!")
        return None
    
    print("\nTop Results:")
    for idx, result in enumerate(results, 1):
        print(f"{idx}. {result['title']} ({result['year']}) - {result['type']} - {result['url']}")
    
    # Prompt user to choose one manually
    while True:
        choice = input("\nSelect a movie/series (enter number 1-3): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(results):
            return results[int(choice) - 1]['url']
        print("Invalid selection. Try again.")

def extract_m3u_playlist(trailer_url):
    """
    Loads the IMDb trailer page and extracts the M3U playlist link with the best quality.
    """
    best_ua = get_best_user_agent()
    headers = {
        'User-Agent': best_ua,
        'Referer': trailer_url,
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(trailer_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for M3U playlist links
        m3u_links = re.findall(r'https?://[^"\s]+\.m3u8(?:\?[^"\s]+)?', response.text)
        if m3u_links:
            # Sort by quality (higher resolution first)
            m3u_links.sort(key=lambda x: int(re.search(r'(\d+)p', x).group(1)) if re.search(r'(\d+)p', x) else 0, reverse=True)
            best_m3u = m3u_links[0]
            return best_m3u
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching M3U playlist: {e}")
    
    return None

def exit_prompt():
    """Prompts the user to exit the script."""
    while True:
        choice = input("\nDo you want to exit? (yes/no): ").strip().lower()
        if choice == "yes":
            print("Exiting the script. Goodbye!")
            return True
        elif choice == "no":
            print("Continuing...")
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    while True:
        # Step 1: Search IMDb for a movie/series
        movie_url = search_imdb()
        if not movie_url:
            print("Failed to retrieve movie/series URL. Exiting...")
            break
        
        print("\nSelected Movie/Series URL:")
        print(movie_url)
        
        # Step 2: Extract M3U playlist
        trailer_url = input("\nEnter the IMDb trailer page URL: ").strip()
        m3u_playlist = extract_m3u_playlist(trailer_url)
        if m3u_playlist:
            print("\n🎥 Best Quality M3U Playlist Link:")
            print(m3u_playlist)
        else:
            print("❌ No M3U playlist found on the trailer page.")
        
        # Step 3: Exit prompt
        if exit_prompt():
            break











