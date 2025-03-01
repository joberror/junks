import time
import os
import re
from api_utils import TMDBClient

# Constants for TMDb API
API_KEY = os.environ.get('TMDB_API_KEY').strip()  # Strip any trailing whitespace or newline characters
if not API_KEY:
  raise ValueError("No API KEY found. TMDB_API_KEY must be obtained and set in your shell environment")
API_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'  # Base URL for images

# Initialize client
tmdb_client = TMDBClient(API_KEY)

def get_movie_details(movie_name):
    """Fetches movie cover URL and title for a given movie name."""
    results = tmdb_client.request('/search/movie', {"query": movie_name})
    if results and 'results' in results:
        return results['results']
    return None

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
    results = tmdb_client.request('/search/tv', {"query": series_name})
    if results and 'results' in results:
        return results['results']
    return None

def get_episode_details(series_id, season_number, episode_number):
    """Fetches title and cover URL for a specific episode."""
    episode_data = tmdb_client.request(
        f'/tv/{series_id}/season/{season_number}/episode/{episode_number}'
    )
    
    if episode_data:
        title = episode_data.get('name')
        poster_path = episode_data.get('still_path')
        cover_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else ""
        return title, cover_url
    return None, None

def generate_movie_output(title, cover_url):
    """Generates output format for movies."""
    print(f'#EXTINF:-1 group-title="{title}" tvg-logo="{cover_url}", {title}')

def generate_episode_output(series_name, season, episode, episode_title, cover_url):
    """Generates output format for episodes."""
    print(f'#EXTINF:-1 group-title="{series_name}" tvg-logo="{cover_url}", {series_name} | S{season}.E{episode} - {episode_title}')

def main():
    while True:
        print("Select an option:")
        print("1. Movie")
        print("2. Series")
        print("0. Exit")
        choice = input("Enter 1, 2, or 0: ").strip()

        if choice == "0":
            print("Exiting the program. Goodbye!")
            break

        if choice == "1":
            # Movie option
            movie_name = input("Enter movie name (e.g., 'The Outrun'): ").strip()
            movies = get_movie_details(movie_name)
            if movies:
                print("Select the movie from the list:")
                for i, movie in enumerate(movies):
                    year = movie.get('release_date', 'Unknown')[:4]
                    print(f"{i + 1}. {movie['title']} ({year}) (movie)")
                selection = int(input("Enter the number of your choice: ").strip()) - 1
                if 0 <= selection < len(movies):
                    selected_movie = movies[selection]
                    title = selected_movie.get('title')
                    poster_path = selected_movie.get('poster_path')
                    cover_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else ""
                    generate_movie_output(title, cover_url)
                else:
                    print("Invalid selection.")
            else:
                print("Movie details not found.")

        elif choice == "2":
            # Series option
            user_input = input("Enter series name with season and episode range (e.g., 'Nobody Wants This S1E1 - E3'): ").strip()
            series_name, season_number, start_episode, end_episode = parse_input_for_episode_range(user_input)

            if season_number is None or start_episode is None:
                print("Invalid input format. Please use 'Show Name S<season>E<start>-E<end>' format.")
                continue

            series_list = search_series(series_name)
            if series_list:
                print("Select the series from the list:")
                for i, series in enumerate(series_list):
                    year = series.get('first_air_date', 'Unknown')[:4]
                    print(f"{i + 1}. {series['name']} ({year}) (tv)")
                selection = int(input("Enter the number of your choice: ").strip()) - 1
                if 0 <= selection < len(series_list):
                    selected_series = series_list[selection]
                    series_id = selected_series['id']
                else:
                    print("Invalid selection.")
                    continue
            else:
                continue

            # Loop over the range of episodes and print formatted output
            for episode_number in range(start_episode, end_episode + 1):
                episode_title, cover_url = get_episode_details(series_id, season_number, episode_number)
                if episode_title:
                    generate_episode_output(series_name, season_number, episode_number, episode_title, cover_url)
                else:
                    print(f"Details not found for Episode {episode_number}.")

                time.sleep(0.25)

        else:
            print("Invalid choice. Please enter 1, 2, or 0.")

if __name__ == "__main__":
    main()
