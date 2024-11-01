import requests
import re

# Constants for TMDb API
API_KEY = '75e3dda3b0e26622248eefdaa1015c82'
API_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'  # Base URL for images

def get_movie_cover(movie_name, api_key):
    # Search for the movie to get its ID and poster path
    response = requests.get(f"{API_URL}/search/movie", params={"api_key": api_key, "query": movie_name})
    response.raise_for_status()
    movies = response.json().get('results', [])
    
    if not movies:
        print("Movie not found.")
        return None
    
    # Return the poster path of the first matching movie
    poster_path = movies[0].get('poster_path')
    return f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None

def parse_input_for_episode_range(user_input):
    # Regular expression to match patterns like "<show name> S<season>E<start>-E<end>"
    match = re.match(r"(.+?)\s+[sS](\d+)[eE](\d+)(?:\s*-\s*[eE](\d+))?", user_input)
    if match:
        series_name = match.group(1).strip()
        season_number = int(match.group(2))
        start_episode = int(match.group(3))
        end_episode = int(match.group(4)) if match.group(4) else start_episode
        return series_name, season_number, start_episode, end_episode
    else:
        return user_input.strip(), None, None, None

def search_series(series_name, api_key):
    # Search for the series to get its ID
    response = requests.get(f"{API_URL}/search/tv", params={"api_key": api_key, "query": series_name})
    response.raise_for_status()
    results = response.json().get('results', [])
    
    if not results:
        print("Series not found.")
        return None
    
    # Return the first matching series ID
    return results[0]['id']

def get_episode_details(series_id, season_number, episode_number, api_key):
    # Retrieve the episode details to get the title and cover image
    response = requests.get(f"{API_URL}/tv/{series_id}/season/{season_number}/episode/{episode_number}", params={"api_key": api_key})
    response.raise_for_status()
    episode_data = response.json()
    
    # Extract title and cover image URL if available
    title = episode_data.get('name')
    poster_path = episode_data.get('still_path')
    cover_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None
    return title, cover_url

def main():
    # Prompt user to select an option
    print("Select an option:")
    print("1. Movie cover")
    print("2. Episode cover and title")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        # Movie cover
        movie_name = input("Enter movie name (e.g., 'Uprising 2024'): ").strip()
        cover_url = get_movie_cover(movie_name, API_KEY)
        if cover_url:
            print("Movie Cover URL:", cover_url)
        else:
            print("Cover image not found.")

    elif choice == "2":
        # Episode cover and title
        user_input = input("Enter series name with season and episode range (e.g., 'Breaking Bad S1E1 - E8'): ").strip()
        series_name, season_number, start_episode, end_episode = parse_input_for_episode_range(user_input)

        if season_number is None or start_episode is None:
            print("Invalid input format. Please use 'Show Name S<season>E<start>-E<end>' format.")
            return

        # Search for the series ID
        series_id = search_series(series_name, API_KEY)
        if not series_id:
            return

        # Loop over the range of episodes and print both title and cover URL
        for episode_number in range(start_episode, end_episode + 1):
            title, cover_url = get_episode_details(series_id, season_number, episode_number, API_KEY)
            if title:
                print(f"Episode {episode_number} Title:", title)
            else:
                print(f"Title not found for Episode {episode_number}.")
            
            if cover_url:
                print(f"Episode {episode_number} Cover URL:", cover_url)
            else:
                print(f"Cover image not found for Episode {episode_number}.")

    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
