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
            return results[0]  # Return the first result
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
        'append_to_response': 'credits',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch details:", response.status_code)
        return None

def format_and_display_info(data, media_type):
    """Format and display movie or series details."""
    title = data.get('title') or data.get('name')
    description = data.get('overview', 'No description available.')
    year = data.get('release_date', data.get('first_air_date', 'Unknown'))[:4]
    rating = data.get('vote_average', 'N/A')
    poster_path = data.get('poster_path')
    cover_art_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "No cover art available."
    total_episodes = data.get('number_of_episodes', '')  # For series, episodes count if available
    tmdb_link = f"https://www.themoviedb.org/{media_type}/{data.get('id')}"

    # Get major cast members
    cast = data.get('credits', {}).get('cast', [])
    major_casts = ', '.join(
        [f"[{actor['name']}](https://www.themoviedb.org/person/{actor['id']})" for actor in cast[:5]]
    ) if cast else 'No cast information available.'
    additional_casts = f", +{len(cast) - 5}" if len(cast) > 5 else ""

    # Format the title
    if media_type == "movie":
        media_info = f"Movie: [{title}]({tmdb_link}) / {year} / {rating}".strip()  # Remove trailing "/"
    else:
        media_info = f"Movie: [{title}]({tmdb_link}) / {year} / {rating} / {total_episodes} Episodes"

    # Display output
    print(media_info)
    print(f"Description: {description}")
    print(f"Casts: {major_casts}{additional_casts}")
    print(f"Cover Art: {cover_art_url}")

def main():
    query = input("Enter the name of a movie or series: ").strip()
    search_result = search_movie_or_series(query)
    if search_result:
        media_type = search_result.get('media_type', 'movie')
        media_id = search_result.get('id')
        details = get_detailed_info(media_type, media_id)
        if details:
            format_and_display_info(details, media_type)

if __name__ == '__main__':
    main()
