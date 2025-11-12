#!/usr/bin/env python3
"""
Application simple pour créer une playlist Spotify avec les groupes du Hellfest 2026
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import json

# Charger les variables d'environnement
load_dotenv()

# Configuration Spotify
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = 'playlist-modify-public playlist-modify-private'

def get_spotify_client():
    """Crée et retourne un client Spotify authentifié"""
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path='.spotify_cache',
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
        sp = spotipy.Spotify(auth_manager=auth_manager)
        # Tester la connexion
        sp.current_user()
        return sp
    except Exception as e:
        print(f"\n❌ Erreur lors de l'authentification: {str(e)}")
        print("\n💡 Si l'application reste bloquée:")
        print("   1. Autorisez l'application dans le navigateur")
        print("   2. Attendez 10-15 secondes")
        print("   3. Si ça ne fonctionne pas, appuyez sur Ctrl+C et réessayez")
        raise

def search_artist_tracks(sp, artist_name, max_tracks=10):
    """
    Recherche un artiste et retourne ses morceaux les plus populaires
    
    Args:
        sp: Client Spotify
        artist_name: Nom de l'artiste à rechercher
        max_tracks: Nombre maximum de morceaux à récupérer
    
    Returns:
        Liste des URIs des morceaux trouvés
    """
    try:
        # Nettoyer le nom de l'artiste (enlever les espaces en trop)
        artist_name_clean = artist_name.strip()
        
        # Essayer plusieurs méthodes de recherche
        search_queries = [
            f'artist:{artist_name_clean}',  # Recherche exacte avec artist:
            artist_name_clean,  # Recherche simple par nom
        ]
        
        artist = None
        for query in search_queries:
            try:
                results = sp.search(q=query, type='artist', limit=5)
                
                if results['artists']['items']:
                    # Chercher une correspondance exacte ou proche
                    for item in results['artists']['items']:
                        # Comparaison insensible à la casse
                        if item['name'].lower() == artist_name_clean.lower():
                            artist = item
                            break
                    
                    # Si pas de correspondance exacte, prendre le premier résultat
                    if not artist:
                        artist = results['artists']['items'][0]
                    
                    break
            except:
                continue
        
        if not artist:
            print(f"  ⚠️  Artiste non trouvé: {artist_name}")
            return []
        
        artist_id = artist['id']
        found_name = artist['name']
        
        # Si le nom trouvé est différent, l'afficher
        if found_name.lower() != artist_name_clean.lower():
            print(f"  ℹ️  Trouvé sous le nom: {found_name}")
        
        # Récupérer les top tracks de l'artiste
        top_tracks = sp.artist_top_tracks(artist_id)
        
        if not top_tracks['tracks']:
            print(f"  ⚠️  Aucun morceau trouvé pour: {artist_name}")
            return []
        
        track_uris = [track['uri'] for track in top_tracks['tracks'][:max_tracks]]
        print(f"  ✓  Trouvé {len(track_uris)} morceau(x) pour: {found_name}")
        return track_uris
        
    except Exception as e:
        print(f"  ✗  Erreur pour {artist_name}: {str(e)}")
        return []

def find_playlist_by_name(sp, playlist_name):
    """
    Cherche une playlist existante par son nom
    
    Args:
        sp: Client Spotify
        playlist_name: Nom de la playlist à chercher
    
    Returns:
        ID de la playlist si trouvée, None sinon
    """
    user_id = sp.current_user()['id']
    playlists = []
    offset = 0
    limit = 50
    
    # Récupérer toutes les playlists de l'utilisateur
    while True:
        results = sp.current_user_playlists(limit=limit, offset=offset)
        playlists.extend(results['items'])
        if results['next']:
            offset += limit
        else:
            break
    
    # Chercher la playlist par nom
    for playlist in playlists:
        if playlist['name'] == playlist_name:
            return playlist['id']
    
    return None

def clear_playlist(sp, playlist_id):
    """
    Vide une playlist de tous ses morceaux
    
    Args:
        sp: Client Spotify
        playlist_id: ID de la playlist à vider
    """
    # Récupérer tous les morceaux de la playlist
    tracks = []
    offset = 0
    limit = 100
    
    while True:
        results = sp.playlist_items(playlist_id, limit=limit, offset=offset)
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
    
    # Supprimer les morceaux par lots de 100
    if tracks:
        batch_size = 100
        for i in range(0, len(tracks), batch_size):
            batch = tracks[i:i + batch_size]
            sp.playlist_remove_all_occurrences_of_items(playlist_id, batch)
        print(f"  ✓  {len(tracks)} morceau(x) supprimé(s) de la playlist existante")

def create_or_update_playlist(sp, playlist_name, description=""):
    """
    Crée une nouvelle playlist ou met à jour une playlist existante
    
    Args:
        sp: Client Spotify
        playlist_name: Nom de la playlist
        description: Description de la playlist
    
    Returns:
        ID de la playlist (créée ou mise à jour)
    """
    # Chercher si la playlist existe déjà
    existing_playlist_id = find_playlist_by_name(sp, playlist_name)
    
    if existing_playlist_id:
        print(f"  ✓  Playlist existante trouvée: {playlist_name}")
        print("  🗑️  Vidage de la playlist...")
        clear_playlist(sp, existing_playlist_id)
        # Mettre à jour la description
        sp.playlist_change_details(existing_playlist_id, description=description)
        return existing_playlist_id
    else:
        # Créer une nouvelle playlist
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            description=description,
            public=True
        )
        return playlist['id']

def add_tracks_to_playlist(sp, playlist_id, track_uris):
    """
    Ajoute des morceaux à une playlist
    
    Args:
        sp: Client Spotify
        playlist_id: ID de la playlist
        track_uris: Liste des URIs des morceaux à ajouter
    """
    # Spotify limite à 100 morceaux par requête
    batch_size = 100
    for i in range(0, len(track_uris), batch_size):
        batch = track_uris[i:i + batch_size]
        sp.playlist_add_items(playlist_id, batch)
        print(f"  ✓  Ajouté {len(batch)} morceau(x) à la playlist")

def load_artists_from_file(filename='hellfest_2026_artists.txt'):
    """
    Charge la liste des artistes depuis un fichier texte
    Un artiste par ligne
    """
    if not os.path.exists(filename):
        print(f"⚠️  Fichier {filename} non trouvé. Création d'un fichier exemple...")
        # Créer un fichier exemple avec quelques groupes
        example_artists = [
            "Iron Maiden",
            "Metallica",
            "Slayer",
            "Megadeth",
            "Anthrax"
        ]
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(example_artists))
        print(f"✓  Fichier {filename} créé avec des exemples. Ajoutez vos 183 groupes !")
        return example_artists
    
    with open(filename, 'r', encoding='utf-8') as f:
        artists = []
        for line in f:
            line = line.strip()
            # Ignorer les lignes vides et les commentaires
            if line and not line.startswith('#'):
                artists.append(line)
    return artists

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🎸 Création de playlist Hellfest 2026 sur Spotify 🎸")
    print("=" * 60)
    
    # Vérifier les credentials
    if not CLIENT_ID or not CLIENT_SECRET:
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
        sp = get_spotify_client()
        print("   ⏳ Vérification de l'authentification...")
        user = sp.current_user()
        print(f"✓  Connecté en tant que: {user['display_name']}")
    except spotipy.exceptions.SpotifyException as e:
        print(f"\n❌ Erreur Spotify: {str(e)}")
        if "INVALID_CLIENT" in str(e) or "redirect" in str(e).lower():
            print("\n💡 Vérifiez que le Redirect URI dans le dashboard Spotify est exactement:")
            print(f"   {REDIRECT_URI}")
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
        print("   2. Vérifiez que le port 3000 n'est pas utilisé par une autre application")
        print("   3. Réessayez, le token sera sauvegardé après la première authentification")
        return
    
    # Charger la liste des artistes
    print("\n📋 Chargement de la liste des artistes...")
    artists = load_artists_from_file()
    print(f"✓  {len(artists)} artiste(s) chargé(s)")
    
    # Demander confirmation
    print(f"\n📝 Vous allez créer une playlist avec {len(artists)} groupes")
    print("   Chaque groupe aura jusqu'à 10 morceaux populaires")
    response = input("\nContinuer ? (o/n): ").lower()
    if response != 'o':
        print("❌ Opération annulée")
        return
    
    # Rechercher les morceaux pour chaque artiste
    print("\n🔍 Recherche des morceaux...")
    all_track_uris = []
    found_count = 0
    
    for i, artist in enumerate(artists, 1):
        print(f"\n[{i}/{len(artists)}] Recherche: {artist}")
        tracks = search_artist_tracks(sp, artist, max_tracks=10)
        if tracks:
            all_track_uris.extend(tracks)
            found_count += 1
    
    print(f"\n✓  Recherche terminée:")
    print(f"   - {found_count}/{len(artists)} artistes trouvés")
    print(f"   - {len(all_track_uris)} morceaux au total")
    
    if not all_track_uris:
        print("\n❌ Aucun morceau trouvé. Impossible de créer la playlist.")
        return
    
    # Créer ou mettre à jour la playlist
    print("\n📝 Création/mise à jour de la playlist...")
    playlist_name = "Hellfest 2026 - Tous les groupes"
    description = f"Playlist avec les groupes du Hellfest 2026 ({len(artists)} groupes)"
    
    try:
        # Vérifier si la playlist existe déjà
        existing_playlist_id = find_playlist_by_name(sp, playlist_name)
        is_update = existing_playlist_id is not None
        
        playlist_id = create_or_update_playlist(sp, playlist_name, description)
        
        if is_update:
            print(f"✓  Playlist mise à jour: {playlist_name}")
        else:
            print(f"✓  Playlist créée: {playlist_name}")
        
        # Ajouter les morceaux
        print("\n🎵 Ajout des morceaux à la playlist...")
        add_tracks_to_playlist(sp, playlist_id, all_track_uris)
        
        playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
        if is_update:
            print(f"\n🎉 Playlist mise à jour avec succès !")
        else:
            print(f"\n🎉 Playlist créée avec succès !")
        print(f"🔗 {playlist_url}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la création de la playlist: {str(e)}")

if __name__ == '__main__':
    main()

