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

def parse_episode_input(input_str):
    """Parse different episode input formats.
    Returns: (season, start_episode, end_episode)
    Examples:
        S1 -> (1, 1, None)  # All episodes
        S2E1 -> (2, 1, 1)   # Single episode
        S4E3-7 -> (4, 3, 7) # Episode range
    """
    # Format: S1 (whole season)
    season_match = re.match(r"[sS](\d+)$", input_str)
    if season_match:
        return (int(season_match.group(1)), 1, None)

    # Format: S2E1 (single episode)
    single_ep_match = re.match(r"[sS](\d+)[eE](\d+)$", input_str)
    if single_ep_match:
        season = int(single_ep_match.group(1))
        episode = int(single_ep_match.group(2))
        return (season, episode, episode)

    # Format: S4E3-7 (episode range)
    range_match = re.match(r"[sS](\d+)[eE](\d+)-(\d+)$", input_str)
    if range_match:
        season = int(range_match.group(1))
        start_ep = int(range_match.group(2))
        end_ep = int(range_match.group(3))
        return (season, start_ep, end_ep)

    return None, None, None

def process_episodes(series_id, series_name, season, start_episode, end_episode):
    """Process and output episode information."""
    # For whole season, get season details first
    if end_episode is None:
        season_data = tmdb_client.request(f'/tv/{series_id}/season/{season}')
        if season_data and 'episodes' in season_data:
            end_episode = len(season_data['episodes'])
        else:
            print(f"Could not fetch season {season} details")
            return

    # Process episodes
    for episode_number in range(start_episode, (end_episode + 1)):
        episode_title, cover_url = get_episode_details(series_id, season, episode_number)
        if episode_title:
            generate_episode_output(series_name, season, episode_number, episode_title, cover_url)
        else:
            print(f"Details not found for Episode {episode_number}")
        time.sleep(0.25)

def handle_series_option():
    """Handle series search and episode processing."""
    # Step 1: Get series name
    series_name = input("Enter series name: ").strip()

    # Step 2: Search and display results
    series_list = search_series(series_name)
    if not series_list:
        print("No series found with that name.")
        return

    print("\nSelect the series from the list:")
    for i, series in enumerate(series_list):
        year = series.get('first_air_date', 'Unknown')[:4]
        series_id = series['id']
        print(f"{i + 1}. {series['name']} ({year}) - {series_id} (tv)")

    # Step 3: Get series selection
    try:
        selection = int(input("\nEnter the number of your choice: ").strip()) - 1
        if not (0 <= selection < len(series_list)):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    selected_series = series_list[selection]
    series_id = selected_series['id']
    series_name = selected_series['name']

    # Step 4: Get episode selection
    print("\nEnter episodes to process using one of these formats:")
    print("  S1    - All episodes of season 1")
    print("  S2E1  - Only episode 1 of season 2")
    print("  S4E3-7 - Episodes 3 to 7 of season 4")

    episode_input = input("\nEpisode selection: ").strip()
    season, start_ep, end_ep = parse_episode_input(episode_input)

    if season is None:
        print("Invalid episode format. Please use one of the shown formats.")
        return

    # Step 5: Process episodes
    process_episodes(series_id, series_name, season, start_ep, end_ep)

def handle_movie_option():
    """Handle movie search and output generation."""
    # Step 1: Get movie name
    movie_name = input("Enter movie name: ").strip()

    # Step 2: Search and display results
    movie_results = get_movie_details(movie_name)
    if not movie_results:
        print("No movies found with that name.")
        return

    print("\nSelect the movie from the list:")
    for i, movie in enumerate(movie_results):
        year = movie.get('release_date', 'Unknown')[:4]
        movie_id = movie['id']
        print(f"{i + 1}. {movie['title']} ({year}) - {movie_id}")

    # Step 3: Get movie selection
    try:
        selection = int(input("\nEnter the number of your choice: ").strip()) - 1
        if not (0 <= selection < len(movie_results)):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    selected_movie = movie_results[selection]
    title = selected_movie['title']
    poster_path = selected_movie.get('poster_path', '')
    cover_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else ""

    # Step 4: Generate output
    generate_movie_output(title, cover_url)

def main():
    while True:
        print("\nSelect an option:")
        print("1. Movie")
        print("2. Series")
        print("0. Exit")
        choice = input("Enter 1, 2, or 0: ").strip()

        if choice == "0":
            print("Exiting the program. Goodbye!")
            break
        elif choice == "1":
            handle_movie_option()
        elif choice == "2":
            handle_series_option()
        else:
            print("Invalid choice. Please enter 1, 2, or 0.")

if __name__ == "__main__":
    main()
