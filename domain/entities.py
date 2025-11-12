"""
Entités du domaine
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Artist:
    """Entité représentant un artiste"""
    name: str
    spotify_id: Optional[str] = None
    found_name: Optional[str] = None  # Nom trouvé sur Spotify si différent


@dataclass
class Track:
    """Entité représentant un morceau"""
    uri: str
    name: Optional[str] = None
    artist: Optional[str] = None


@dataclass
class Playlist:
    """Entité représentant une playlist"""
    name: str
    description: str
    spotify_id: Optional[str] = None
    tracks: List[Track] = field(default_factory=list)

