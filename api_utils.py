import requests
import time
from functools import lru_cache
from typing import Optional, Dict, Any
import json
import os
from datetime import datetime, timedelta

class TMDBClient:
    def __init__(self, api_key: str, cache_dir: str = ".cache"):
        self.api_key = api_key
        self.base_url = 'https://api.themoviedb.org/3'
        self.cache_dir = cache_dir
        self.session = self._create_session()
        
        # Ensure cache directory exists
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _create_session(self) -> requests.Session:
        """Create a session with connection pooling"""
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=5,
            pool_maxsize=20,
            max_retries=3,
            pool_block=False
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate a unique cache key"""
        cache_key = f"{endpoint}_{json.dumps(params, sort_keys=True)}"
        return cache_key.replace('/', '_').replace('?', '_')

    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if it exists and is not expired"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                # Check if cache is still valid (24 hours)
                if datetime.fromtimestamp(cached_data['timestamp']) > datetime.now() - timedelta(hours=24):
                    return cached_data['data']
        return None

    def _cache_response(self, cache_key: str, data: Dict) -> None:
        """Cache the response data"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().timestamp(),
                'data': data
            }, f)

    def request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to TMDB API with caching"""
        if params is None:
            params = {}
            
        # Add API key to params
        params['api_key'] = self.api_key
        
        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        # Make the request if not cached
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Cache the response
            self._cache_response(cache_key, data)
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {endpoint}: {e}")
            return None

    def search_multi(self, query: str) -> Optional[Dict]:
        """Search for movies and TV shows"""
        return self.request('/search/multi', {'query': query})

    def get_details(self, media_type: str, media_id: int) -> Optional[Dict]:
        """Get detailed information about a movie or TV show"""
        return self.request(f'/{media_type}/{media_id}')

    def get_watch_providers(self, media_type: str, media_id: int) -> Optional[Dict]:
        """Get streaming platforms for a movie or TV show"""
        return self.request(f'/{media_type}/{media_id}/watch/providers')
