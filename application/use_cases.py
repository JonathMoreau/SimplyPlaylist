"""
Use Cases - Logique applicative
"""
from typing import List, Optional
from domain.entities import Artist, Track, Playlist
from domain.repositories import ISpotifyRepository, IArtistFileRepository


class SearchArtistTracksUseCase:
    """Use case pour rechercher les morceaux d'un artiste"""
    
    def __init__(self, spotify_repo: ISpotifyRepository):
        """
        Initialise le use case
        
        Args:
            spotify_repo: Repository Spotify
        """
        self.spotify_repo = spotify_repo
    
    def execute(self, artist_name: str, max_tracks: int = 10) -> List[Track]:
        """
        Recherche un artiste et retourne ses morceaux les plus populaires
        
        Args:
            artist_name: Nom de l'artiste à rechercher
            max_tracks: Nombre maximum de morceaux à récupérer
        
        Returns:
            Liste des morceaux trouvés
        """
        try:
            artist_name_clean = artist_name.strip()
            artist = self.spotify_repo.find_artist(artist_name_clean)
            
            if not artist:
                print(f"  ⚠️  Artiste non trouvé: {artist_name}")
                return []
            
            # Si le nom trouvé est différent, l'afficher
            if artist.found_name and artist.found_name.lower() != artist_name_clean.lower():
                print(f"  ℹ️  Trouvé sous le nom: {artist.found_name}")
            
            # Récupérer les top tracks
            tracks = self.spotify_repo.get_artist_top_tracks(artist, max_tracks)
            
            if not tracks:
                print(f"  ⚠️  Aucun morceau trouvé pour: {artist_name}")
                return []
            
            print(f"  ✓  Trouvé {len(tracks)} morceau(x) pour: {artist.found_name or artist_name_clean}")
            return tracks
            
        except Exception as e:
            print(f"  ✗  Erreur pour {artist_name}: {str(e)}")
            return []


class CreatePlaylistFromArtistsUseCase:
    """Use case pour créer une playlist à partir d'une liste d'artistes"""
    
    def __init__(
        self,
        spotify_repo: ISpotifyRepository,
        artist_file_repo: IArtistFileRepository
    ):
        """
        Initialise le use case
        
        Args:
            spotify_repo: Repository Spotify
            artist_file_repo: Repository de fichiers d'artistes
        """
        self.spotify_repo = spotify_repo
        self.artist_file_repo = artist_file_repo
        self.search_use_case = SearchArtistTracksUseCase(spotify_repo)
    
    def execute(
        self,
        playlist_name: str,
        artists_file: str = 'hellfest_2026_artists.txt',
        max_tracks_per_artist: int = 10,
        require_confirmation: bool = True
    ) -> Optional[str]:
        """
        Crée une playlist à partir d'une liste d'artistes
        
        Args:
            playlist_name: Nom de la playlist à créer
            artists_file: Fichier contenant la liste des artistes
            max_tracks_per_artist: Nombre maximum de morceaux par artiste
            require_confirmation: Demander confirmation avant de créer
            
        Returns:
            URL de la playlist créée ou None en cas d'erreur
        """
        # Charger la liste des artistes
        print("\n📋 Chargement de la liste des artistes...")
        artist_names = self.artist_file_repo.load_artists(artists_file)
        print(f"✓  {len(artist_names)} artiste(s) chargé(s)")
        
        # Demander confirmation
        if require_confirmation:
            print(f"\n📝 Vous allez créer une playlist avec {len(artist_names)} groupes")
            print(f"   Chaque groupe aura jusqu'à {max_tracks_per_artist} morceaux populaires")
            response = input("\nContinuer ? (o/n): ").lower()
            if response != 'o':
                print("❌ Opération annulée")
                return None
        
        # Rechercher les morceaux pour chaque artiste
        print("\n🔍 Recherche des morceaux...")
        all_tracks = []
        found_count = 0
        
        for i, artist_name in enumerate(artist_names, 1):
            print(f"\n[{i}/{len(artist_names)}] Recherche: {artist_name}")
            tracks = self.search_use_case.execute(artist_name, max_tracks_per_artist)
            if tracks:
                all_tracks.extend(tracks)
                found_count += 1
        
        print("\n✓  Recherche terminée:")
        print(f"   - {found_count}/{len(artist_names)} artistes trouvés")
        print(f"   - {len(all_tracks)} morceaux au total")
        
        if not all_tracks:
            print("\n❌ Aucun morceau trouvé. Impossible de créer la playlist.")
            return None
        
        # Créer ou mettre à jour la playlist
        print("\n📝 Création/mise à jour de la playlist...")
        description = f"Playlist avec les groupes du Hellfest 2026 ({len(artist_names)} groupes)"
        
        try:
            # Vérifier si la playlist existe déjà
            existing_playlist_id = self.spotify_repo.find_playlist_by_name(playlist_name)
            is_update = existing_playlist_id is not None
            
            if existing_playlist_id:
                print(f"  ✓  Playlist existante trouvée: {playlist_name}")
                print("  🗑️  Vidage de la playlist...")
                self.spotify_repo.clear_playlist(existing_playlist_id)
                
                playlist = Playlist(
                    name=playlist_name,
                    description=description,
                    spotify_id=existing_playlist_id
                )
                self.spotify_repo.update_playlist(existing_playlist_id, playlist)
                playlist_id = existing_playlist_id
            else:
                playlist = Playlist(
                    name=playlist_name,
                    description=description
                )
                playlist_id = self.spotify_repo.create_playlist(playlist)
            
            if is_update:
                print(f"✓  Playlist mise à jour: {playlist_name}")
            else:
                print(f"✓  Playlist créée: {playlist_name}")
            
            # Ajouter les morceaux
            print("\n🎵 Ajout des morceaux à la playlist...")
            self.spotify_repo.add_tracks_to_playlist(playlist_id, all_tracks)
            
            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            if is_update:
                print("\n🎉 Playlist mise à jour avec succès !")
            else:
                print("\n🎉 Playlist créée avec succès !")
            print(f"🔗 {playlist_url}")
            
            return playlist_url
            
        except Exception as e:
            print(f"\n❌ Erreur lors de la création de la playlist: {str(e)}")
            return None

