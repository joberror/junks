def validate_api_keys():
    """Validate all required API keys are present"""
    required_keys = {
        'TMDB_API_KEY': 'Get your key at https://www.themoviedb.org/settings/api',
        'YOUTUBE_API_KEY': 'Get your key at https://console.cloud.google.com/apis/credentials'
    }
    
    missing_keys = []
    for key, instructions in required_keys.items():
        if not os.environ.get(key):
            missing_keys.append(f"{key} - {instructions}")
    
    if missing_keys:
        raise ValueError("Missing API keys:\n" + "\n".join(missing_keys))