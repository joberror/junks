import requests

# Replace 'your_api_key_here' with your TMDB API key
API_KEY = '75e3dda3b0e26622248eefdaa1015c82'
BASE_URL = 'https://api.themoviedb.org/3'

def search_movie_or_series(query):
    """Search for a movie or series by name."""
    url = f"{BASE_URL}/search/multi"
    params = {
        'api_key': API_KEY,
        'query': query,
        'language': 'en-US',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            for result in results:
                year = result.get('release_date', result.get('first_air_date', 'Unknown'))[:4]
                result['year'] = year
            return results  # Return all results with year included
        else:
            print("No results found.")
            return None
    else:
        print("Failed to fetch data:", response.status_code)
        return None

def get_detailed_info(media_type, media_id):
    """Get detailed information about a movie or series."""
    url = f"{BASE_URL}/{media_type}/{media_id}"
    params = {
        'api_key': API_KEY,
        'language': 'en-US',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch details:", response.status_code)
        return None

def get_streaming_platforms(media_type, media_id):
    """Get streaming platforms for a movie or series."""
    url = f"{BASE_URL}/{media_type}/{media_id}/watch/providers"
    params = {
        'api_key': API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        providers = response.json().get('results', {}).get('US', {}).get('flatrate', [])
        if providers:
            return ', '.join([provider['provider_name'] for provider in providers])
        else:
            return "Not available"
    else:
        print("Failed to fetch streaming platforms:", response.status_code)
        return "Unknown"

def format_and_display_info(data, media_type):
    """Display formatted output with title, rating, year, genres, NFO, and streaming platforms."""
    title = data.get('title') or data.get('name')
    year = data.get('release_date', data.get('first_air_date', 'Unknown'))[:4]
    rating = f"⭐️ {data.get('vote_average', 'N/A')}"
    genres = data.get('genres', [])
    genre_tags = ' '.join([f"#{genre['name'].replace(' ', '')}" for genre in genres]) if genres else "No genres available"
    movie_link = f"https://www.themoviedb.org/{media_type}/{data.get('id')}"

    # For series, append number of episodes
    total_episodes = data.get('number_of_episodes', None)
    if media_type == "tv" and total_episodes:
        title += f" | {total_episodes} scenes"

    # Determine type: Movie or Series
    type_label = "🎥 Movie" if media_type == "movie" else "🎥 Series"

    # Get streaming platforms
    streaming_platforms = get_streaming_platforms(media_type, data.get('id'))

    # Formatted output
    print(f"{type_label}\n")
    print(f"¤ Title: {title}")
    print(f"¤ Year: {year}")
    print(f"¤ Rating: {rating}")
    print(f"¤ Genres: {genre_tags}")
    print(f"¤ Streaming On: {streaming_platforms}")
    print(f"¤ NFO: {movie_link}")

def main():
    query = input("Enter the name of a movie or series: ").strip()
    search_results = search_movie_or_series(query)
    if search_results:
        print("Select the exact match from the list below:")
        for idx, result in enumerate(search_results, start=1):
            year = result.get('release_date', result.get('first_air_date', 'Unknown'))[:4]
            print(f"{idx}. {result.get('title') or result.get('name')} ({year}) ({result.get('media_type')})")
        selection = int(input("Enter the number of your selection: ").strip()) - 1
        if 0 <= selection < len(search_results):
            selected_result = search_results[selection]
            media_type = selected_result.get('media_type', 'movie')
            media_id = selected_result.get('id')
            details = get_detailed_info(media_type, media_id)
            if details:
                format_and_display_info(details, media_type)
        else:
            print("Invalid selection.")

if __name__ == '__main__':
    main()
