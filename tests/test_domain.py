"""
Tests pour le domaine (entities)
"""
import pytest
from domain.entities import Artist, Track, Playlist


class TestArtist:
    """Tests pour l'entité Artist"""
    
    def test_artist_creation(self):
        """Test de création d'un artiste"""
        artist = Artist(name="Test Artist", spotify_id="123", found_name="Test Artist")
        assert artist.name == "Test Artist"
        assert artist.spotify_id == "123"
        assert artist.found_name == "Test Artist"
    
    def test_artist_minimal(self):
        """Test de création minimale d'un artiste"""
        artist = Artist(name="Test Artist")
        assert artist.name == "Test Artist"
        assert artist.spotify_id is None
        assert artist.found_name is None


class TestTrack:
    """Tests pour l'entité Track"""
    
    def test_track_creation(self):
        """Test de création d'un morceau"""
        track = Track(uri="spotify:track:123", name="Test Track", artist="Test Artist")
        assert track.uri == "spotify:track:123"
        assert track.name == "Test Track"
        assert track.artist == "Test Artist"
    
    def test_track_minimal(self):
        """Test de création minimale d'un morceau"""
        track = Track(uri="spotify:track:123")
        assert track.uri == "spotify:track:123"
        assert track.name is None
        assert track.artist is None


class TestPlaylist:
    """Tests pour l'entité Playlist"""
    
    def test_playlist_creation(self):
        """Test de création d'une playlist"""
        tracks = [Track(uri="spotify:track:1"), Track(uri="spotify:track:2")]
        playlist = Playlist(
            name="Test Playlist",
            description="Test Description",
            spotify_id="playlist123",
            tracks=tracks
        )
        assert playlist.name == "Test Playlist"
        assert playlist.description == "Test Description"
        assert playlist.spotify_id == "playlist123"
        assert len(playlist.tracks) == 2
    
    def test_playlist_default_tracks(self):
        """Test que les tracks sont initialisés par défaut"""
        playlist = Playlist(name="Test", description="Test")
        assert playlist.tracks == []

