"""
Tests pour la couche présentation (main)
"""
import pytest
from unittest.mock import Mock, patch
import spotipy.exceptions
from presentation.main import main


class TestMain:
    """Tests pour la fonction main()"""
    
    @patch('presentation.main.SpotifyConfig')
    @patch('presentation.main.SpotifyRepository')
    @patch('presentation.main.ArtistFileRepository')
    @patch('presentation.main.CreatePlaylistFromArtistsUseCase')
    def test_main_success(self, mock_use_case_class, mock_file_repo_class, mock_spotify_repo_class, mock_config_class):
        """Test de main() avec succès"""
        mock_config = Mock()
        mock_config.is_valid.return_value = True
        mock_config.redirect_uri = 'http://127.0.0.1:8888/callback'
        mock_config_class.return_value = mock_config
        
        mock_spotify_repo = Mock()
        mock_user = {'display_name': 'Test User'}
        mock_spotify_repo.get_current_user.return_value = mock_user
        mock_spotify_repo_class.return_value = mock_spotify_repo
        
        mock_file_repo = Mock()
        mock_file_repo_class.return_value = mock_file_repo
        
        mock_use_case = Mock()
        mock_use_case.execute.return_value = 'https://open.spotify.com/playlist/123'
        mock_use_case_class.return_value = mock_use_case
        
        main()
        
        mock_spotify_repo.connect.assert_called_once()
        mock_use_case.execute.assert_called_once()
    
    @patch('presentation.main.SpotifyConfig')
    def test_main_invalid_config(self, mock_config_class):
        """Test de main() avec configuration invalide"""
        mock_config = Mock()
        mock_config.is_valid.return_value = False
        mock_config_class.return_value = mock_config
        
        main()
        
        mock_config.is_valid.assert_called_once()
    
    @patch('presentation.main.SpotifyConfig')
    @patch('presentation.main.SpotifyRepository')
    def test_main_spotify_exception(self, mock_spotify_repo_class, mock_config_class):
        """Test de main() avec exception Spotify"""
        mock_config = Mock()
        mock_config.is_valid.return_value = True
        mock_config.redirect_uri = 'http://127.0.0.1:8888/callback'
        mock_config_class.return_value = mock_config
        
        mock_spotify_repo = Mock()
        exception = spotipy.exceptions.SpotifyException(http_status=400, code=400, msg="INVALID_CLIENT error")
        mock_spotify_repo.connect.side_effect = exception
        mock_spotify_repo_class.return_value = mock_spotify_repo
        
        main()
        
        mock_spotify_repo.connect.assert_called_once()
    
    @patch('presentation.main.SpotifyConfig')
    @patch('presentation.main.SpotifyRepository')
    def test_main_spotify_exception_redirect(self, mock_spotify_repo_class, mock_config_class):
        """Test de main() avec exception Spotify (redirect)"""
        mock_config = Mock()
        mock_config.is_valid.return_value = True
        mock_config.redirect_uri = 'http://127.0.0.1:8888/callback'
        mock_config_class.return_value = mock_config
        
        mock_spotify_repo = Mock()
        exception = spotipy.exceptions.SpotifyException(http_status=400, code=400, msg="Error with redirect URI")
        mock_spotify_repo.connect.side_effect = exception
        mock_spotify_repo_class.return_value = mock_spotify_repo
        
        main()
        
        mock_spotify_repo.connect.assert_called_once()
    
    @patch('presentation.main.SpotifyConfig')
    @patch('presentation.main.SpotifyRepository')
    def test_main_spotify_exception_redirect_lowercase(self, mock_spotify_repo_class, mock_config_class):
        """Test de main() avec exception Spotify contenant 'redirect' en minuscules (branche 41->44)"""
        mock_config = Mock()
        mock_config.is_valid.return_value = True
        mock_config.redirect_uri = 'http://127.0.0.1:8888/callback'
        mock_config_class.return_value = mock_config
        
        mock_spotify_repo = Mock()
        # Utiliser 'redirect' en minuscules pour couvrir la branche str(e).lower()
        exception = spotipy.exceptions.SpotifyException(http_status=400, code=400, msg="redirect error")
        mock_spotify_repo.connect.side_effect = exception
        mock_spotify_repo_class.return_value = mock_spotify_repo
        
        main()
        
        mock_spotify_repo.connect.assert_called_once()
    
    @patch('presentation.main.SpotifyConfig')
    @patch('presentation.main.SpotifyRepository')
    def test_main_keyboard_interrupt(self, mock_spotify_repo_class, mock_config_class):
        """Test de main() avec KeyboardInterrupt"""
        mock_config = Mock()
        mock_config.is_valid.return_value = True
        mock_config_class.return_value = mock_config
        
        mock_spotify_repo = Mock()
        mock_spotify_repo.connect.side_effect = KeyboardInterrupt()
        mock_spotify_repo_class.return_value = mock_spotify_repo
        
        main()
        
        mock_spotify_repo.connect.assert_called_once()
    
    @patch('presentation.main.SpotifyConfig')
    @patch('presentation.main.SpotifyRepository')
    def test_main_generic_exception(self, mock_spotify_repo_class, mock_config_class):
        """Test de main() avec exception générique"""
        mock_config = Mock()
        mock_config.is_valid.return_value = True
        mock_config_class.return_value = mock_config
        
        mock_spotify_repo = Mock()
        mock_spotify_repo.connect.side_effect = Exception("Generic error")
        mock_spotify_repo_class.return_value = mock_spotify_repo
        
        main()
        
        mock_spotify_repo.connect.assert_called_once()

