from googleapiclient.discovery import build
from config import APIConfig

# Initialize config
config = APIConfig()
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def search_youtube_trailers(query):
    youtube = build(
        YOUTUBE_API_SERVICE_NAME, 
        YOUTUBE_API_VERSION, 
        developerKey=config.youtube_key
    )

    search_response = youtube.search().list(
        q=query + ' official trailer',
        part='id,snippet',
        maxResults=3,
        type='video'
    ).execute()

    videos = []

    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append((
                search_result['snippet']['title'],
                f"https://www.youtube.com/watch?v={search_result['id']['videoId']}",
                search_result['snippet']['thumbnails']['high']['url']
            ))

    return videos

def main():
    query = input("Enter the name of the movie to search for official trailers: ").strip()
    results = search_youtube_trailers(query)

    if results:
        print("Top 3 official trailer results:")
        for idx, (title, link, thumbnail) in enumerate(results, start=1):
            print(f"{idx}. {title}")
            print(f"   Link: {link}")
            print(f"   Thumbnail: {thumbnail}\n")
    else:
        print("No official trailers found.")

if __name__ == '__main__':
    main()
