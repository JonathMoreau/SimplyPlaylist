"""
Tests pour l'infrastructure (repositories, config)
"""
import os
import pytest
from unittest.mock import Mock, patch, mock_open
from infrastructure.config import SpotifyConfig
from infrastructure.file_loader import ArtistFileRepository
from infrastructure.spotify_repository import SpotifyRepository
from domain.entities import Artist, Track, Playlist


class TestSpotifyConfig:
    """Tests pour SpotifyConfig"""
    
    @patch.dict(os.environ, {
        'SPOTIFY_CLIENT_ID': 'test_client_id',
        'SPOTIFY_CLIENT_SECRET': 'test_client_secret'
    })
    @patch('infrastructure.config.load_dotenv')
    def test_config_initialization(self, mock_load_dotenv):
        """Test de l'initialisation de la configuration"""
        config = SpotifyConfig()
        
        assert config.client_id == 'test_client_id'
        assert config.client_secret == 'test_client_secret'
        assert config.redirect_uri == 'http://127.0.0.1:8888/callback'
        assert config.scope == 'playlist-modify-public playlist-modify-private'
        assert config.cache_path == '.spotify_cache'
    
    @patch.dict(os.environ, {
        'SPOTIFY_CLIENT_ID': 'test_client_id',
        'SPOTIFY_CLIENT_SECRET': 'test_client_secret'
    })
    @patch('infrastructure.config.load_dotenv')
    def test_config_is_valid_with_credentials(self, mock_load_dotenv):
        """Test que is_valid retourne True avec des credentials valides"""
        config = SpotifyConfig()
        assert config.is_valid() is True
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('infrastructure.config.load_dotenv')
    def test_config_is_valid_without_credentials(self, mock_load_dotenv):
        """Test que is_valid retourne False sans credentials"""
        config = SpotifyConfig()
        assert config.is_valid() is False


class TestArtistFileRepository:
    """Tests pour ArtistFileRepository"""
    
    def test_load_artists_from_existing_file(self, tmp_path):
        """Test du chargement d'artistes depuis un fichier existant"""
        test_file = tmp_path / "test_artists.txt"
        test_file.write_text("Iron Maiden\nMetallica\nSlayer\n# Commentaire\n\nMegadeth")
        
        repo = ArtistFileRepository()
        artists = repo.load_artists(str(test_file))
        
        assert len(artists) == 4
        assert "Iron Maiden" in artists
        assert "Metallica" in artists
        assert "Slayer" in artists
        assert "Megadeth" in artists
        assert "# Commentaire" not in artists
    
    def test_load_artists_ignores_empty_lines(self, tmp_path):
        """Test que les lignes vides sont ignorées"""
        test_file = tmp_path / "test_artists.txt"
        test_file.write_text("Artist1\n\n\nArtist2\n")
        
        repo = ArtistFileRepository()
        artists = repo.load_artists(str(test_file))
        
        assert len(artists) == 2
        assert "Artist1" in artists
        assert "Artist2" in artists
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_artists_creates_file_if_not_exists(self, mock_file, mock_exists):
        """Test que le fichier est créé s'il n'existe pas"""
        mock_exists.return_value = False
        
        repo = ArtistFileRepository()
        artists = repo.load_artists('nonexistent.txt')
        
        assert len(artists) == 5
        assert "Iron Maiden" in artists
        assert "Metallica" in artists
        mock_file.assert_called()


class TestSpotifyRepository:
    """Tests pour SpotifyRepository"""
    
    def test_find_artist_success(self):
        """Test de recherche réussie d'un artiste"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_artist_data = {
            'id': 'test_artist_id',
            'name': 'Test Artist'
        }
        mock_search_results = {
            'artists': {
                'items': [mock_artist_data]
            }
        }
        mock_client.search.return_value = mock_search_results
        repo._client = mock_client
        
        artist = repo.find_artist("Test Artist")
        
        assert artist is not None
        assert artist.name == "Test Artist"
        assert artist.spotify_id == "test_artist_id"
        assert artist.found_name == "Test Artist"
        mock_client.search.assert_called()
    
    def test_find_artist_not_found(self):
        """Test quand l'artiste n'est pas trouvé"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_client.search.return_value = {'artists': {'items': []}}
        repo._client = mock_client
        
        artist = repo.find_artist("Unknown Artist")
        
        assert artist is None
    
    def test_get_artist_top_tracks_success(self):
        """Test de récupération des top tracks"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_top_tracks = {
            'tracks': [
                {'uri': 'spotify:track:1', 'name': 'Track 1', 'artists': [{'name': 'Artist'}]},
                {'uri': 'spotify:track:2', 'name': 'Track 2', 'artists': [{'name': 'Artist'}]}
            ]
        }
        mock_client.artist_top_tracks.return_value = mock_top_tracks
        repo._client = mock_client
        
        artist = Artist(name="Test Artist", spotify_id="artist_id")
        tracks = repo.get_artist_top_tracks(artist, max_tracks=2)
        
        assert len(tracks) == 2
        assert all(isinstance(track, Track) for track in tracks)
        assert tracks[0].uri == 'spotify:track:1'
        assert tracks[0].name == 'Track 1'
    
    def test_get_artist_top_tracks_no_tracks(self):
        """Test quand l'artiste n'a pas de morceaux"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_client.artist_top_tracks.return_value = {'tracks': []}
        repo._client = mock_client
        
        artist = Artist(name="Test Artist", spotify_id="artist_id")
        tracks = repo.get_artist_top_tracks(artist)
        
        assert tracks == []
    
    def test_find_playlist_by_name_found(self):
        """Test de recherche de playlist trouvée"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_playlists = {
            'items': [
                {'id': 'playlist1', 'name': 'Playlist 1'},
                {'id': 'playlist2', 'name': 'Target Playlist'}
            ],
            'next': None
        }
        mock_client.current_user_playlists.return_value = mock_playlists
        repo._client = mock_client
        
        playlist_id = repo.find_playlist_by_name("Target Playlist")
        
        assert playlist_id == 'playlist2'
    
    def test_find_playlist_by_name_not_found(self):
        """Test quand la playlist n'est pas trouvée"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_client.current_user_playlists.return_value = {
            'items': [
                {'id': 'playlist1', 'name': 'Playlist 1'}
            ],
            'next': None
        }
        repo._client = mock_client
        
        playlist_id = repo.find_playlist_by_name("Nonexistent Playlist")
        
        assert playlist_id is None
    
    def test_create_playlist(self):
        """Test de création d'une playlist"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_client.current_user.return_value = {'id': 'user123'}
        mock_client.user_playlist_create.return_value = {'id': 'new_playlist_id'}
        repo._client = mock_client
        
        playlist = Playlist(name="New Playlist", description="Description")
        playlist_id = repo.create_playlist(playlist)
        
        assert playlist_id == 'new_playlist_id'
        mock_client.user_playlist_create.assert_called_once()
    
    def test_clear_playlist(self):
        """Test de vidage d'une playlist"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_items = {
            'items': [
                {'track': {'uri': 'spotify:track:1'}},
                {'track': {'uri': 'spotify:track:2'}}
            ],
            'next': None
        }
        mock_client.playlist_items.return_value = mock_items
        repo._client = mock_client
        
        repo.clear_playlist('playlist123')
        
        assert mock_client.playlist_remove_all_occurrences_of_items.called
    
    def test_add_tracks_to_playlist(self):
        """Test d'ajout de morceaux à une playlist"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        tracks = [
            Track(uri=f'spotify:track:{i}') for i in range(50)
        ]
        repo._client = mock_client
        
        repo.add_tracks_to_playlist('playlist123', tracks)
        
        mock_client.playlist_add_items.assert_called_once()
        # Vérifier que les URIs sont extraites
        call_args = mock_client.playlist_add_items.call_args
        assert len(call_args[0][1]) == 50
    
    def test_add_tracks_to_playlist_multiple_batches(self):
        """Test d'ajout de morceaux en plusieurs lots"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        tracks = [
            Track(uri=f'spotify:track:{i}') for i in range(250)
        ]
        repo._client = mock_client
        
        repo.add_tracks_to_playlist('playlist123', tracks)
        
        assert mock_client.playlist_add_items.call_count == 3
        for call in mock_client.playlist_add_items.call_args_list:
            assert len(call[0][1]) <= 100
    
    @patch('infrastructure.spotify_repository.SpotifyOAuth')
    @patch('spotipy.Spotify')
    def test_connect_with_cached_token(self, mock_spotify_class, mock_oauth_class):
        """Test de connexion avec un token en cache valide"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_auth_manager = Mock()
        mock_token_info = {'access_token': 'test_token', 'expires_at': 9999999999}
        mock_auth_manager.get_cached_token.return_value = mock_token_info
        mock_auth_manager.is_token_expired.return_value = False
        mock_oauth_class.return_value = mock_auth_manager
        
        mock_sp_instance = Mock()
        mock_sp_instance.current_user.return_value = {'id': 'user123'}
        mock_spotify_class.return_value = mock_sp_instance
        
        repo.connect()
        
        assert repo._client == mock_sp_instance
    
    @patch('infrastructure.spotify_repository.SpotifyOAuth')
    @patch('spotipy.Spotify')
    def test_connect_with_expired_token(self, mock_spotify_class, mock_oauth_class):
        """Test de connexion avec un token expiré"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_auth_manager = Mock()
        mock_token_info = {'access_token': 'expired_token', 'expires_at': 0}
        mock_auth_manager.get_cached_token.return_value = mock_token_info
        mock_auth_manager.is_token_expired.return_value = True
        mock_oauth_class.return_value = mock_auth_manager
        
        mock_sp_instance = Mock()
        mock_sp_instance.current_user.return_value = {'id': 'user123'}
        mock_spotify_class.return_value = mock_sp_instance
        
        repo.connect()
        
        assert repo._client == mock_sp_instance
    
    @patch('infrastructure.spotify_repository.SpotifyOAuth')
    @patch('spotipy.Spotify')
    def test_connect_no_cached_token(self, mock_spotify_class, mock_oauth_class):
        """Test de connexion sans token en cache"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_auth_manager = Mock()
        mock_auth_manager.get_cached_token.return_value = None
        mock_oauth_class.return_value = mock_auth_manager
        
        mock_sp_instance = Mock()
        mock_sp_instance.current_user.return_value = {'id': 'user123'}
        mock_spotify_class.return_value = mock_sp_instance
        
        repo.connect()
        
        assert repo._client == mock_sp_instance
    
    @patch('infrastructure.spotify_repository.SpotifyOAuth')
    @patch('spotipy.Spotify')
    def test_connect_authentication_error(self, mock_spotify_class, mock_oauth_class):
        """Test de gestion d'erreur d'authentification"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_auth_manager = Mock()
        mock_auth_manager.get_cached_token.return_value = None
        mock_oauth_class.return_value = mock_auth_manager
        
        mock_sp_instance = Mock()
        mock_sp_instance.current_user.side_effect = Exception("Authentication failed")
        mock_spotify_class.return_value = mock_sp_instance
        
        with pytest.raises(Exception):
            repo.connect()
    
    def test_spotify_client_property_auto_connect(self):
        """Test que _spotify_client se connecte automatiquement"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        repo._client = None
        
        mock_client = Mock()
        mock_client.current_user.return_value = {'id': 'user123'}
        
        with patch.object(repo, 'connect') as mock_connect:
            mock_connect.return_value = None
            repo._client = mock_client  # Simuler la connexion
            client = repo._spotify_client
            
            assert client == mock_client
    
    def test_spotify_client_property_connects_when_none(self):
        """Test que _spotify_client appelle connect() quand _client est None"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        repo._client = None
        
        mock_client = Mock()
        mock_client.current_user.return_value = {'id': 'user123'}
        
        with patch.object(repo, 'connect') as mock_connect:
            mock_connect.return_value = None
            # Simuler que connect() définit _client
            def set_client():
                repo._client = mock_client
            mock_connect.side_effect = set_client
            
            client = repo._spotify_client
            
            assert client == mock_client
            mock_connect.assert_called_once()
    
    def test_find_artist_no_exact_match(self):
        """Test _find_artist sans correspondance exacte"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_artist1 = {'id': 'artist1', 'name': 'Different Name'}
        mock_artist2 = {'id': 'artist2', 'name': 'Another Name'}
        mock_search_results = {
            'artists': {
                'items': [mock_artist1, mock_artist2]
            }
        }
        mock_client.search.return_value = mock_search_results
        repo._client = mock_client
        
        artist = repo.find_artist("Test Artist")
        
        # Devrait retourner le premier résultat
        assert artist is not None
        assert artist.spotify_id == 'artist1'
        assert artist.found_name == 'Different Name'
    
    def test_find_artist_with_exception(self):
        """Test _find_artist avec exception"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_client.search.side_effect = Exception("API Error")
        repo._client = mock_client
        
        artist = repo.find_artist("Test Artist")
        
        assert artist is None
    
    def test_get_artist_top_tracks_exception(self):
        """Test get_artist_top_tracks avec exception"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_client.artist_top_tracks.side_effect = Exception("API Error")
        repo._client = mock_client
        
        artist = Artist(name="Test Artist", spotify_id="artist_id")
        tracks = repo.get_artist_top_tracks(artist)
        
        assert tracks == []
    
    def test_get_artist_top_tracks_no_spotify_id(self):
        """Test get_artist_top_tracks sans spotify_id"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        artist = Artist(name="Test Artist", spotify_id=None)
        tracks = repo.get_artist_top_tracks(artist)
        
        assert tracks == []
    
    def test_find_playlist_by_name_pagination(self):
        """Test find_playlist_by_name avec pagination"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_playlists_page1 = {
            'items': [
                {'id': 'playlist1', 'name': 'Playlist 1'}
            ],
            'next': 'https://api.spotify.com/v1/me/playlists?offset=50'
        }
        mock_playlists_page2 = {
            'items': [
                {'id': 'playlist2', 'name': 'Target Playlist'}
            ],
            'next': None
        }
        mock_client.current_user_playlists.side_effect = [
            mock_playlists_page1,
            mock_playlists_page2
        ]
        repo._client = mock_client
        
        playlist_id = repo.find_playlist_by_name("Target Playlist")
        
        assert playlist_id == 'playlist2'
        assert mock_client.current_user_playlists.call_count == 2
    
    def test_clear_playlist_empty(self):
        """Test clear_playlist vide"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_client.playlist_items.return_value = {
            'items': [],
            'next': None
        }
        repo._client = mock_client
        
        repo.clear_playlist('playlist123')
        
        mock_client.playlist_remove_all_occurrences_of_items.assert_not_called()
    
    def test_clear_playlist_pagination(self):
        """Test clear_playlist avec pagination"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_items_page1 = {
            'items': [{'track': {'uri': f'spotify:track:{i}'}} for i in range(100)],
            'next': 'https://api.spotify.com/v1/playlists/123/tracks?offset=100'
        }
        mock_items_page2 = {
            'items': [{'track': {'uri': 'spotify:track:100'}}],
            'next': None
        }
        mock_client.playlist_items.side_effect = [mock_items_page1, mock_items_page2]
        repo._client = mock_client
        
        repo.clear_playlist('playlist123')
        
        assert mock_client.playlist_remove_all_occurrences_of_items.called
    
    def test_clear_playlist_with_none_tracks(self):
        """Test clear_playlist avec des tracks None"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_items = {
            'items': [
                {'track': {'uri': 'spotify:track:1'}},
                {'track': None},
                {'track': {'uri': 'spotify:track:2'}}
            ],
            'next': None
        }
        mock_client.playlist_items.return_value = mock_items
        repo._client = mock_client
        
        repo.clear_playlist('playlist123')
        
        assert mock_client.playlist_remove_all_occurrences_of_items.called
    
    def test_clear_playlist_all_none_tracks(self):
        """Test clear_playlist avec tous les tracks None (branche 233->236)"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_items = {
            'items': [
                {'track': None},
                {'track': None}
            ],
            'next': None
        }
        mock_client.playlist_items.return_value = mock_items
        repo._client = mock_client
        
        repo.clear_playlist('playlist123')
        
        # track_uris sera vide, donc la branche if track_uris ne sera pas exécutée
        # mais on doit quand même tester que ça ne plante pas
        mock_client.playlist_remove_all_occurrences_of_items.assert_not_called()
    
    def test_update_playlist(self):
        """Test update_playlist"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        repo._client = mock_client
        
        playlist = Playlist(name="Test Playlist", description="New Description")
        repo.update_playlist('playlist123', playlist)
        
        mock_client.playlist_change_details.assert_called_once_with(
            'playlist123',
            description="New Description"
        )
    
    def test_get_current_user(self):
        """Test get_current_user"""
        config = SpotifyConfig()
        repo = SpotifyRepository(config)
        
        mock_client = Mock()
        mock_user = {'id': 'user123', 'display_name': 'Test User'}
        mock_client.current_user.return_value = mock_user
        repo._client = mock_client
        
        user = repo.get_current_user()
        
        assert user == mock_user
        mock_client.current_user.assert_called_once()

