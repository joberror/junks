import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

class APIConfig:
    @staticmethod
    def get_key(key_name: str) -> Optional[str]:
        value = os.environ.get(key_name, '').strip()
        if not value:
            raise ValueError(f"No API key found. {key_name} must be set in environment")
        return value

    @property
    def tmdb_key(self) -> str:
        return self.get_key('TMDB_API_KEY')
    
    @property
    def youtube_key(self) -> str:
        return self.get_key('YOUTUBE_API_KEY')
