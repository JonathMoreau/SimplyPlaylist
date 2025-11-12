"""
Tests pour la couche application (use cases)
"""
import pytest
from unittest.mock import Mock, patch
from domain.entities import Artist, Track, Playlist
from application.use_cases import SearchArtistTracksUseCase, CreatePlaylistFromArtistsUseCase


class TestSearchArtistTracksUseCase:
    """Tests pour SearchArtistTracksUseCase"""
    
    def test_execute_success(self):
        """Test d'exécution réussie"""
        mock_repo = Mock()
        mock_artist = Artist(name="Test Artist", spotify_id="artist_id", found_name="Test Artist")
        mock_tracks = [
            Track(uri="spotify:track:1", name="Track 1"),
            Track(uri="spotify:track:2", name="Track 2")
        ]
        
        mock_repo.find_artist.return_value = mock_artist
        mock_repo.get_artist_top_tracks.return_value = mock_tracks
        
        use_case = SearchArtistTracksUseCase(mock_repo)
        tracks = use_case.execute("Test Artist", max_tracks=2)
        
        assert len(tracks) == 2
        mock_repo.find_artist.assert_called_once_with("Test Artist")
        mock_repo.get_artist_top_tracks.assert_called_once_with(mock_artist, 2)
    
    def test_execute_artist_not_found(self):
        """Test quand l'artiste n'est pas trouvé"""
        mock_repo = Mock()
        mock_repo.find_artist.return_value = None
        
        use_case = SearchArtistTracksUseCase(mock_repo)
        tracks = use_case.execute("Unknown Artist")
        
        assert tracks == []
        mock_repo.get_artist_top_tracks.assert_not_called()
    
    def test_execute_no_tracks(self):
        """Test quand l'artiste n'a pas de morceaux"""
        mock_repo = Mock()
        mock_artist = Artist(name="Test Artist", spotify_id="artist_id")
        mock_repo.find_artist.return_value = mock_artist
        mock_repo.get_artist_top_tracks.return_value = []
        
        use_case = SearchArtistTracksUseCase(mock_repo)
        tracks = use_case.execute("Test Artist")
        
        assert tracks == []
    
    def test_execute_exception(self):
        """Test de gestion d'exception"""
        mock_repo = Mock()
        mock_repo.find_artist.side_effect = Exception("API Error")
        
        use_case = SearchArtistTracksUseCase(mock_repo)
        tracks = use_case.execute("Test Artist")
        
        assert tracks == []
    
    def test_execute_different_found_name(self):
        """Test quand le nom trouvé est différent (ligne 42)"""
        mock_repo = Mock()
        mock_artist = Artist(
            name="Search Name",
            spotify_id="artist_id",
            found_name="Different Found Name"
        )
        mock_tracks = [Track(uri="spotify:track:1")]
        
        mock_repo.find_artist.return_value = mock_artist
        mock_repo.get_artist_top_tracks.return_value = mock_tracks
        
        use_case = SearchArtistTracksUseCase(mock_repo)
        tracks = use_case.execute("Search Name")
        
        assert len(tracks) == 1


class TestCreatePlaylistFromArtistsUseCase:
    """Tests pour CreatePlaylistFromArtistsUseCase"""
    
    @pytest.fixture
    def mock_repos(self):
        """Crée des mocks pour les repositories"""
        spotify_repo = Mock()
        file_repo = Mock()
        return spotify_repo, file_repo
    
    @pytest.fixture
    def use_case(self, mock_repos):
        """Crée un use case avec des mocks"""
        spotify_repo, file_repo = mock_repos
        return CreatePlaylistFromArtistsUseCase(spotify_repo, file_repo)
    
    @patch('builtins.input', return_value='o')
    def test_execute_success(self, mock_input, use_case, mock_repos, tmp_path):
        """Test d'exécution réussie"""
        spotify_repo, file_repo = mock_repos
        
        test_file = tmp_path / "test_artists.txt"
        test_file.write_text("Test Artist")
        
        file_repo.load_artists.return_value = ["Test Artist"]
        
        mock_artist = Artist(name="Test Artist", spotify_id="artist_id")
        mock_tracks = [Track(uri="spotify:track:1")]
        
        spotify_repo.find_artist.return_value = mock_artist
        spotify_repo.get_artist_top_tracks.return_value = mock_tracks
        spotify_repo.find_playlist_by_name.return_value = None
        spotify_repo.create_playlist.return_value = "playlist123"
        
        url = use_case.execute(
            playlist_name="Test Playlist",
            artists_file=str(test_file),
            max_tracks_per_artist=1,
            require_confirmation=True
        )
        
        assert url == 'https://open.spotify.com/playlist/playlist123'
        spotify_repo.create_playlist.assert_called_once()
    
    @patch('builtins.input', return_value='n')
    def test_execute_cancelled(self, mock_input, use_case, mock_repos, tmp_path):
        """Test d'annulation"""
        spotify_repo, file_repo = mock_repos
        
        test_file = tmp_path / "test_artists.txt"
        test_file.write_text("Test Artist")
        file_repo.load_artists.return_value = ["Test Artist"]
        
        url = use_case.execute(
            playlist_name="Test Playlist",
            artists_file=str(test_file),
            require_confirmation=True
        )
        
        assert url is None
    
    def test_execute_no_tracks_found(self, use_case, mock_repos, tmp_path):
        """Test quand aucun morceau n'est trouvé"""
        spotify_repo, file_repo = mock_repos
        
        test_file = tmp_path / "test_artists.txt"
        test_file.write_text("Unknown Artist")
        file_repo.load_artists.return_value = ["Unknown Artist"]
        
        spotify_repo.find_artist.return_value = None
        
        url = use_case.execute(
            playlist_name="Test Playlist",
            artists_file=str(test_file),
            require_confirmation=False
        )
        
        assert url is None
    
    def test_execute_with_existing_playlist(self, use_case, mock_repos, tmp_path):
        """Test avec playlist existante"""
        spotify_repo, file_repo = mock_repos
        
        test_file = tmp_path / "test_artists.txt"
        test_file.write_text("Test Artist")
        file_repo.load_artists.return_value = ["Test Artist"]
        
        mock_artist = Artist(name="Test Artist", spotify_id="artist_id")
        mock_tracks = [Track(uri="spotify:track:1")]
        
        spotify_repo.find_artist.return_value = mock_artist
        spotify_repo.get_artist_top_tracks.return_value = mock_tracks
        spotify_repo.find_playlist_by_name.return_value = "existing_playlist_id"
        
        url = use_case.execute(
            playlist_name="Test Playlist",
            artists_file=str(test_file),
            require_confirmation=False
        )
        
        assert url == 'https://open.spotify.com/playlist/existing_playlist_id'
        spotify_repo.clear_playlist.assert_called_once_with("existing_playlist_id")
        spotify_repo.update_playlist.assert_called_once()
    
    def test_execute_with_exception(self, use_case, mock_repos, tmp_path):
        """Test de gestion d'exception lors de la création"""
        spotify_repo, file_repo = mock_repos
        
        test_file = tmp_path / "test_artists.txt"
        test_file.write_text("Test Artist")
        file_repo.load_artists.return_value = ["Test Artist"]
        
        mock_artist = Artist(name="Test Artist", spotify_id="artist_id")
        mock_tracks = [Track(uri="spotify:track:1")]
        
        spotify_repo.find_artist.return_value = mock_artist
        spotify_repo.get_artist_top_tracks.return_value = mock_tracks
        spotify_repo.find_playlist_by_name.side_effect = Exception("API Error")
        
        url = use_case.execute(
            playlist_name="Test Playlist",
            artists_file=str(test_file),
            require_confirmation=False
        )
        
        assert url is None

