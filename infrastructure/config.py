"""
Configuration de l'application
"""
import os
from dotenv import load_dotenv


class SpotifyConfig:
    """Configuration pour l'authentification Spotify"""
    
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = 'http://127.0.0.1:8888/callback'
        self.scope = 'playlist-modify-public playlist-modify-private'
        self.cache_path = '.spotify_cache'
    
    def is_valid(self) -> bool:
        """Vérifie si la configuration est valide"""
        return bool(self.client_id and self.client_secret)

