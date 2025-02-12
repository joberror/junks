from googleapiclient.discovery import build
import os

# Replace 'YOUR_API_KEY' with your actual YouTube API key
API_KEY = os.environ.get('YOUTUBE_API_KEY').strip()
if not API_KEY:
  raise ValueError("No API key found. Please set the YOUTUBE_API_KEY environment variable.")
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def search_youtube_trailers(query):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

  search_response = youtube.search().list(
    q=query + ' official trailer',
    part='id,snippet',
    maxResults=3,
    type='video'
  ).execute()

  videos = []

  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videos.append((search_result['snippet']['title'],
               f"https://www.youtube.com/watch?v={search_result['id']['videoId']}"))

  return videos

def main():
  query = input("Enter the name of the movie to search for official trailers: ").strip()
  results = search_youtube_trailers(query)

  if results:
    print("Top 3 official trailer results:")
    for idx, (title, link) in enumerate(results, start=1):
      print(f"{idx}. {title}")
      print(f"   Link: {link}\n")
  else:
    print("No official trailers found.")

if __name__ == '__main__':
  main()
