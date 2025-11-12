"""
Repository Spotify - Implémentation des interactions avec l'API Spotify
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Optional
from domain.entities import Artist, Track, Playlist
from domain.repositories import ISpotifyRepository
from infrastructure.config import SpotifyConfig


class SpotifyRepository(ISpotifyRepository):
    """Implémentation du repository Spotify"""
    
    def __init__(self, config: SpotifyConfig):
        """
        Initialise le repository Spotify
        
        Args:
            config: Configuration Spotify
        """
        self.config = config
        self._client: Optional[spotipy.Spotify] = None
    
    def connect(self) -> None:
        """
        Établit la connexion avec Spotify
        
        Raises:
            Exception: Si l'authentification échoue
        """
        auth_manager = SpotifyOAuth(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            redirect_uri=self.config.redirect_uri,
            scope=self.config.scope,
            cache_path=self.config.cache_path,
            open_browser=True,
            show_dialog=True
        )
        
        # Vérifier si on a déjà un token en cache
        token_info = auth_manager.get_cached_token()
        if token_info:
            print("✓  Token d'authentification trouvé dans le cache")
            # Vérifier si le token est expiré
            if auth_manager.is_token_expired(token_info):
                print("⚠️  Token expiré, nouvelle authentification nécessaire...")
                token_info = None
        
        if not token_info:
            print("\n📱 Authentification requise...")
            print("   Le navigateur va s'ouvrir automatiquement.")
            print("   ⚠️  IMPORTANT: Après avoir autorisé, vous serez redirigé vers une page.")
            print("   Cette page peut afficher une erreur - c'est NORMAL !")
            print("   Revenez simplement ici et attendez quelques secondes...")
            print("\n   ⏳ En attente de l'autorisation...")
        
        try:
            self._client = spotipy.Spotify(auth_manager=auth_manager)
            # Tester la connexion
            self._client.current_user()
        except Exception as e:
            print(f"\n❌ Erreur lors de l'authentification: {str(e)}")
            print("\n💡 Si l'application reste bloquée:")
            print("   1. Autorisez l'application dans le navigateur")
            print("   2. Attendez 10-15 secondes")
            print("   3. Si ça ne fonctionne pas, appuyez sur Ctrl+C et réessayez")
            raise
    
    @property
    def _spotify_client(self) -> spotipy.Spotify:
        """Retourne le client Spotify (se connecte si nécessaire)"""
        if self._client is None:
            self.connect()
        return self._client
    
    def get_current_user(self) -> dict:
        """Récupère les informations de l'utilisateur actuel"""
        return self._spotify_client.current_user()
    
    def find_artist(self, artist_name: str) -> Optional[Artist]:
        """
        Recherche un artiste sur Spotify
        
        Args:
            artist_name: Nom de l'artiste à rechercher
        
        Returns:
            Entité Artist si trouvé, None sinon
        """
        artist_name_clean = artist_name.strip()
        search_queries = [
            f'artist:{artist_name_clean}',
            artist_name_clean,
        ]
        
        for query in search_queries:
            try:
                results = self._spotify_client.search(q=query, type='artist', limit=5)
                
                if not results['artists']['items']:
                    continue
                
                # Chercher une correspondance exacte
                for item in results['artists']['items']:
                    if item['name'].lower() == artist_name_clean.lower():
                        return Artist(
                            name=artist_name_clean,
                            spotify_id=item['id'],
                            found_name=item['name']
                        )
                
                # Si pas de correspondance exacte, prendre le premier résultat
                first_item = results['artists']['items'][0]
                return Artist(
                    name=artist_name_clean,
                    spotify_id=first_item['id'],
                    found_name=first_item['name']
                )
            except Exception:
                continue
        
        return None
    
    def get_artist_top_tracks(self, artist: Artist, max_tracks: int = 10) -> List[Track]:
        """
        Récupère les morceaux les plus populaires d'un artiste
        
        Args:
            artist: Entité Artist
            max_tracks: Nombre maximum de morceaux à récupérer
        
        Returns:
            Liste des morceaux
        """
        if not artist.spotify_id:
            return []
        
        try:
            top_tracks = self._spotify_client.artist_top_tracks(artist.spotify_id)
            
            if not top_tracks['tracks']:
                return []
            
            tracks = []
            for track_data in top_tracks['tracks'][:max_tracks]:
                tracks.append(Track(
                    uri=track_data['uri'],
                    name=track_data['name'],
                    artist=track_data['artists'][0]['name'] if track_data['artists'] else None
                ))
            
            return tracks
        except Exception:
            return []
    
    def find_playlist_by_name(self, playlist_name: str) -> Optional[str]:
        """
        Cherche une playlist existante par son nom
        
        Args:
            playlist_name: Nom de la playlist à chercher
        
        Returns:
            ID de la playlist si trouvée, None sinon
        """
        playlists = []
        offset = 0
        limit = 50
        
        while True:
            results = self._spotify_client.current_user_playlists(limit=limit, offset=offset)
            playlists.extend(results['items'])
            if results['next']:
                offset += limit
            else:
                break
        
        for playlist in playlists:
            if playlist['name'] == playlist_name:
                return playlist['id']
        
        return None
    
    def create_playlist(self, playlist: Playlist) -> str:
        """
        Crée une nouvelle playlist
        
        Args:
            playlist: Entité Playlist
        
        Returns:
            ID de la playlist créée
        """
        user_id = self._spotify_client.current_user()['id']
        created = self._spotify_client.user_playlist_create(
            user=user_id,
            name=playlist.name,
            description=playlist.description,
            public=True
        )
        return created['id']
    
    def update_playlist(self, playlist_id: str, playlist: Playlist) -> None:
        """
        Met à jour une playlist existante
        
        Args:
            playlist_id: ID de la playlist
            playlist: Entité Playlist avec les nouvelles données
        """
        self._spotify_client.playlist_change_details(playlist_id, description=playlist.description)
    
    def clear_playlist(self, playlist_id: str) -> None:
        """
        Vide une playlist de tous ses morceaux
        
        Args:
            playlist_id: ID de la playlist à vider
        """
        tracks = []
        offset = 0
        limit = 100
        
        while True:
            results = self._spotify_client.playlist_items(playlist_id, limit=limit, offset=offset)
            items = results['items']
            if not items:
                break
            
            track_uris = [item['track']['uri'] for item in items if item['track']]
            if track_uris:
                tracks.extend(track_uris)
            
            if results['next']:
                offset += limit
            else:
                break
        
        if tracks:
            batch_size = 100
            for i in range(0, len(tracks), batch_size):
                batch = tracks[i:i + batch_size]
                self._spotify_client.playlist_remove_all_occurrences_of_items(playlist_id, batch)
            print(f"  ✓  {len(tracks)} morceau(x) supprimé(s) de la playlist existante")
    
    def add_tracks_to_playlist(self, playlist_id: str, tracks: List[Track]) -> None:
        """
        Ajoute des morceaux à une playlist
        
        Args:
            playlist_id: ID de la playlist
            tracks: Liste des morceaux à ajouter
        """
        track_uris = [track.uri for track in tracks]
        batch_size = 100
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i + batch_size]
            self._spotify_client.playlist_add_items(playlist_id, batch)
            print(f"  ✓  Ajouté {len(batch)} morceau(x) à la playlist")

