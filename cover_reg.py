import requests
import re
import time

# Constants for TMDb API
API_KEY = '75e3dda3b0e26622248eefdaa1015c82'
API_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'  # Base URL for images

# Create a session to reuse connections
session = requests.Session()

def get_movie_cover(movie_name):
    try:
        response = session.get(f"{API_URL}/search/movie", params={"api_key": API_KEY, "query": movie_name}, timeout=5)
        response.raise_for_status()
        movies = response.json().get('results', [])
        if not movies:
            print("Movie not found.")
            return None
        poster_path = movies[0].get('poster_path')
        return f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None
    except requests.RequestException as e:
        print(f"Failed to retrieve movie cover: {e}")
        return None

def parse_input_for_episode_range(user_input):
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
    for attempt in range(retries):
        try:
            response = session.get(f"{API_URL}/tv/{series_id}/season/{season_number}/episode/{episode_number}", params={"api_key": API_KEY}, timeout=5)
            response.raise_for_status()
            episode_data = response.json()
            title = episode_data.get('name')
            poster_path = episode_data.get('still_path')
            cover_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None
            return title, cover_url
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed to retrieve episode details: {e}")
            time.sleep(0.5)  # Wait before retrying
    print(f"Failed to retrieve details for episode {episode_number} after {retries} attempts.")
    return None, None

def main():
    print("Select an option:")
    print("1. Movie cover")
    print("2. Episode cover and title")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        movie_name = input("Enter movie name (e.g., 'Uprising 2024'): ").strip()
        cover_url = get_movie_cover(movie_name)
        if cover_url:
            print("Movie Cover URL:", cover_url)
        else:
            print("Cover image not found.")

    elif choice == "2":
        user_input = input("Enter series name with season and episode range (e.g., 'Breaking Bad S1E1 - E8'): ").strip()
        series_name, season_number, start_episode, end_episode = parse_input_for_episode_range(user_input)

        if season_number is None or start_episode is None:
            print("Invalid input format. Please use 'Show Name S<season>E<start>-E<end>' format.")
            return

        series_id = search_series(series_name)
        if not series_id:
            return

        for episode_number in range(start_episode, end_episode + 1):
            title, cover_url = get_episode_details(series_id, season_number, episode_number)
            if title:
                print(f"Episode {episode_number} Title:", title)
            else:
                print(f"Title not found for Episode {episode_number}.")
            
            if cover_url:
                print(f"Episode {episode_number} Cover URL:", cover_url)
            else:
                print(f"Cover image not found for Episode {episode_number}.")

            time.sleep(0.25)  # Short delay to respect TMDb rate limits

    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
