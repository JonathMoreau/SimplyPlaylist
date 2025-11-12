"""
Interfaces des repositories (ports)
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import Artist, Track, Playlist


class ISpotifyRepository(ABC):
    """Interface pour le repository Spotify"""
    
    @abstractmethod
    def connect(self) -> None:  # pragma: no cover
        """Établit la connexion avec Spotify"""
        pass
    
    @abstractmethod
    def get_current_user(self) -> dict:  # pragma: no cover
        """Récupère les informations de l'utilisateur actuel"""
        pass
    
    @abstractmethod
    def find_artist(self, artist_name: str) -> Optional[Artist]:  # pragma: no cover
        """Recherche un artiste sur Spotify"""
        pass
    
    @abstractmethod
    def get_artist_top_tracks(self, artist: Artist, max_tracks: int = 10) -> List[Track]:  # pragma: no cover
        """Récupère les morceaux les plus populaires d'un artiste"""
        pass
    
    @abstractmethod
    def find_playlist_by_name(self, playlist_name: str) -> Optional[str]:  # pragma: no cover
        """Cherche une playlist existante par son nom"""
        pass
    
    @abstractmethod
    def create_playlist(self, playlist: Playlist) -> str:  # pragma: no cover
        """Crée une nouvelle playlist"""
        pass
    
    @abstractmethod
    def update_playlist(self, playlist_id: str, playlist: Playlist) -> None:  # pragma: no cover
        """Met à jour une playlist existante"""
        pass
    
    @abstractmethod
    def clear_playlist(self, playlist_id: str) -> None:  # pragma: no cover
        """Vide une playlist de tous ses morceaux"""
        pass
    
    @abstractmethod
    def add_tracks_to_playlist(self, playlist_id: str, tracks: List[Track]) -> None:  # pragma: no cover
        """Ajoute des morceaux à une playlist"""
        pass


class IArtistFileRepository(ABC):
    """Interface pour le repository de fichiers d'artistes"""
    
    @abstractmethod
    def load_artists(self, filename: str) -> List[str]:  # pragma: no cover
        """Charge la liste des artistes depuis un fichier"""
        pass

