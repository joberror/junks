import requests
import re
import os
import time
from datetime import datetime, timedelta

# Constants for TMDb API
API_KEY = os.getenv('TMDB_API_KEY')
if not API_KEY:
  raise ValueError("No API key found. Please set the TMDB_API_KEY environment variable.")
API_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'  # Base URL for images

# Create a session to reuse connections
session = requests.Session()

def underscore_title(title):
    """Convert title to underscore-separated format."""
    return title.replace(" ", "_").lower()

def get_movie_details(movie_name):
    """Fetches movie cover URL and overview for a given movie name."""
    try:
        response = session.get(f"{API_URL}/search/movie", params={"api_key": API_KEY, "query": movie_name}, timeout=5)
        response.raise_for_status()
        movies = response.json().get('results', [])
        if not movies:
            print("Movie not found.")
            return None, None, None
        movie = movies[0]
        poster_path = movie.get('poster_path')
        cover_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None
        overview = movie.get('overview')
        title = movie.get('title')
        return title, cover_url, overview
    except requests.RequestException as e:
        print(f"Failed to retrieve movie details: {e}")
        return None, None, None

def parse_input_for_episode_range(user_input):
    """Parses user input to extract series name, season, and episode range."""
    match = re.match(r"(.+?)\s+[sS](\d+)[eE](\d+)(?:\s*-\s*[eE](\d+))?", user_input)
    if match:
        series_name = match.group(1).strip()
        season_number = int(match.group(2))
        start_episode = int(match.group(3))
        end_episode = int(match.group(4)) if match.group(4) else start_episode
        return series_name, season_number, start_episode, end_episode
    else:
        return user_input.strip(), None, None, None

def search_series(series_name):
    """Fetches the series ID for a given series name."""
    try:
        response = session.get(f"{API_URL}/search/tv", params={"api_key": API_KEY, "query": series_name}, timeout=5)
        response.raise_for_status()
        results = response.json().get('results', [])
        if not results:
            print("Series not found.")
            return None
        return results[0]['id']
    except requests.RequestException as e:
        print(f"Failed to retrieve series: {e}")
        return None

def get_episode_details(series_id, season_number, episode_number, retries=3):
    """Fetches title, cover URL, and overview for a specific episode."""
    for attempt in range(retries):
        try:
            response = session.get(f"{API_URL}/tv/{series_id}/season/{season_number}/episode/{episode_number}", params={"api_key": API_KEY}, timeout=5)
            response.raise_for_status()
            episode_data = response.json()
            title = episode_data.get('name')
            poster_path = episode_data.get('still_path')
            cover_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None
            overview = episode_data.get('overview')
            return title, cover_url, overview
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed to retrieve episode details: {e}")
            time.sleep(0.5)
    print(f"Failed to retrieve details for episode {episode_number} after {retries} attempts.")
    return None, None, None

def generate_output(id_name, title, cover_url, description):
    """Generates the required XML and M3U8 formatted output."""
    # Get the current time and future time (one year later)
    start_time = datetime.utcnow()
    stop_time = start_time + timedelta(days=365)

    # Format start and stop times to the required format
    start_time_str = start_time.strftime("%Y%m%d%H%M%S +0000")
    stop_time_str = stop_time.strftime("%Y%m%d%H%M%S +0000")

    # Generate the XML and M3U8 output
    print(f"""
<channel id="{id_name}">
    <display-name>{title}</display-name>
    <icon src="{cover_url}" />
</channel>

<programme start="{start_time_str}" stop="{stop_time_str}" channel="{id_name}">
    <title>{title}</title>
    <desc>{description}</desc>
</programme>

#EXTINF:-1 tvg-id="{id_name}" tvg-name="{title}" tvg-logo="{cover_url}", {title}
""")

def main():
    print("Select an option:")
    print("1. Movie cover and description")
    print("2. Episode cover, title, and description")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        # Movie cover and description
        movie_name = input("Enter movie name (e.g., 'Uprising 2024'): ").strip()
        title, cover_url, overview = get_movie_details(movie_name)
        if title and cover_url and overview:
            id_name = underscore_title(title)
            generate_output(id_name, title, cover_url, overview)
        else:
            print("Movie details not found.")

    elif choice == "2":
        # Episode cover, title, and description
        user_input = input("Enter series name with season and episode range (e.g., 'Breaking Bad S1E1 - E8'): ").strip()
        series_name, season_number, start_episode, end_episode = parse_input_for_episode_range(user_input)

        if season_number is None or start_episode is None:
            print("Invalid input format. Please use 'Show Name S<season>E<start>-E<end>' format.")
            return

        series_id = search_series(series_name)
        if not series_id:
            return

        # Loop over the range of episodes and print title, cover URL, and description
        for episode_number in range(start_episode, end_episode + 1):
            title, cover_url, overview = get_episode_details(series_id, season_number, episode_number)
            if title and cover_url and overview:
                id_name = underscore_title(f"{series_name} S{season_number}E{episode_number}")
                generate_output(id_name, title, cover_url, overview)
            else:
                print(f"Details not found for Episode {episode_number}.")

            time.sleep(0.25)

    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
