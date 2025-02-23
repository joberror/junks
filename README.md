# Movie Info & M3U Playlist Generator

A Python-based tool suite for gathering movie/TV show information and generating M3U playlists with metadata.

## 🎯 Features

- Search movies and TV shows using TMDb API
- Fetch detailed information including:
  - Release year
  - Rating
  - Genres
  - Streaming platforms availability
- Generate M3U playlists with movie metadata
- Search and fetch YouTube trailers
- IMDb integration for additional movie data
- Combine multiple M3U files into a single playlist

## 🚀 Getting Started

### Prerequisites

- Python 3.6+
- API keys for:
  - TMDb (The Movie Database)
  - YouTube Data API v3

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```
TMDB_API_KEY=your_tmdb_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

## 🛠️ Usage

### Movie Information Search
```bash
python info.py
```
- Enter a movie/series name
- Select from search results
- Get detailed information including streaming availability

### YouTube Trailer Search
```bash
python ytsearch.py
```
- Enter a movie name
- Get top 3 official trailer results with links

### M3U Playlist Generation
```bash
python movie_info.py
```
- Choose between movie or series
- Enter title and details
- Generate M3U entries with metadata

### Combine M3U Files
```bash
python combine_all_m3u.py
```
- Combines all M3U files from the `m3u` directory into a single `all.m3u` file

### IMDb Search
```bash
python imdb.py
```
- Search IMDb for movies/series
- Extract additional movie information

## 📁 Project Structure

- `info.py` - Main movie information fetcher
- `ytsearch.py` - YouTube trailer search
- `movie_info.py` - M3U playlist entry generator
- `imdb.py` - IMDb data scraper
- `combine_all_m3u.py` - M3U file combiner
- `config.py` - API configuration handler
- `api_utils.py` - API utility functions

## ⚙️ Configuration

The project uses environment variables for API keys. Create a `.env` file with:
```
TMDB_API_KEY=your_tmdb_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

## 🔑 API Keys

- TMDb API: Get your key at https://www.themoviedb.org/settings/api
- YouTube API: Get your key at https://console.cloud.google.com/apis/credentials

## 📝 Notes

- M3U files are stored in the `m3u` directory
- The combined playlist is saved as `all.m3u`
- Make sure to keep your API keys secure and never commit them to version control

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details