"""
Point d'entrée de l'application
"""
import spotipy.exceptions
from infrastructure.config import SpotifyConfig
from infrastructure.spotify_repository import SpotifyRepository
from infrastructure.file_loader import ArtistFileRepository
from application.use_cases import CreatePlaylistFromArtistsUseCase


def main():
    """Fonction principale"""
    print("=" * 60)
    print("🎸 Création de playlist Hellfest 2026 sur Spotify 🎸")
    print("=" * 60)
    
    # Vérifier les credentials
    config = SpotifyConfig()
    if not config.is_valid():
        print("\n❌ Erreur: CLIENT_ID et CLIENT_SECRET doivent être définis dans le fichier .env")
        print("\nPour obtenir ces credentials:")
        print("1. Allez sur https://developer.spotify.com/dashboard")
        print("2. Créez une nouvelle application")
        print("3. Copiez le CLIENT_ID et CLIENT_SECRET")
        print("4. Ajoutez-les dans un fichier .env:")
        print("   SPOTIFY_CLIENT_ID=votre_client_id")
        print("   SPOTIFY_CLIENT_SECRET=votre_client_secret")
        return
    
    # Se connecter à Spotify
    print("\n🔐 Connexion à Spotify...")
    try:
        print("   ⏳ Initialisation de l'authentification...")
        spotify_repo = SpotifyRepository(config)
        spotify_repo.connect()
        print("   ⏳ Vérification de l'authentification...")
        user = spotify_repo.get_current_user()
        print(f"✓  Connecté en tant que: {user['display_name']}")
    except spotipy.exceptions.SpotifyException as e:
        print(f"\n❌ Erreur Spotify: {str(e)}")
        if "INVALID_CLIENT" in str(e) or "redirect" in str(e).lower():  # pragma: no branch
            print("\n💡 Vérifiez que le Redirect URI dans le dashboard Spotify est exactement:")
            print(f"   {config.redirect_uri}")
        return
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
        print("   Si l'application était bloquée, c'est normal lors de la première authentification.")
        print("   Réessayez, le token sera en cache pour les prochaines fois.")
        return
    except Exception as e:
        print(f"\n❌ Erreur de connexion: {str(e)}")
        print("\n💡 Si l'application reste bloquée:")
        print("   1. Appuyez sur Ctrl+C plusieurs fois")
        print("   2. Vérifiez que le port 8888 n'est pas utilisé par une autre application")
        print("   3. Réessayez, le token sera sauvegardé après la première authentification")
        return
    
    # Créer la playlist
    artist_file_repo = ArtistFileRepository()
    use_case = CreatePlaylistFromArtistsUseCase(spotify_repo, artist_file_repo)
    use_case.execute(
        playlist_name="Hellfest 2026 - Tous les groupes",
        max_tracks_per_artist=10
    )


if __name__ == '__main__':  # pragma: no cover
    main()

