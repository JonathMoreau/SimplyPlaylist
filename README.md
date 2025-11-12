# SimplyPlaylist - Créateur de Playlist Hellfest 2026

Application simple pour créer automatiquement une playlist Spotify avec les groupes du Hellfest 2026.

## 🚀 Installation

1. **Installer Python 3.8+** (si ce n'est pas déjà fait)

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Créer une application Spotify** :
   - Allez sur [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Cliquez sur "Create an app"
   - Remplissez le formulaire (nom, description)
   - Une fois créée, notez votre **Client ID** et **Client Secret**

4. **Configurer les credentials** :
   - Créez un fichier `.env` à la racine du projet
   - Ajoutez-y :
   ```
   SPOTIFY_CLIENT_ID=votre_client_id_ici
   SPOTIFY_CLIENT_SECRET=votre_client_secret_ici
   ```

5. **Ajouter la liste des groupes** :
   - Ouvrez le fichier `hellfest_2026_artists.txt`
   - Ajoutez un groupe par ligne (les 183 groupes du Hellfest 2026)
   - Les lignes commençant par `#` sont ignorées

## 📖 Utilisation

Lancez simplement :
```bash
python app.py
```

L'application va :
1. Se connecter à votre compte Spotify (ouvrira votre navigateur pour l'autorisation)
2. Charger la liste des groupes depuis `hellfest_2026_artists.txt`
3. Rechercher chaque groupe sur Spotify
4. Créer une playlist avec les morceaux les plus populaires de chaque groupe (jusqu'à 5 par groupe)
5. Vous donner le lien vers la playlist créée

## ⚙️ Configuration

- **Nombre de morceaux par groupe** : Modifiez le paramètre `max_tracks` dans la fonction `search_artist_tracks()` (par défaut: 5)
- **Nom de la playlist** : Modifiez la variable `playlist_name` dans la fonction `main()`

## 📝 Notes

- La première connexion ouvrira votre navigateur pour autoriser l'application
- Les credentials sont sauvegardés dans `.spotify_cache` pour les prochaines utilisations
- Si un groupe n'est pas trouvé sur Spotify, il sera ignoré avec un message d'avertissement

## 🛠️ Technologies utilisées

- **Python 3**
- **Spotipy** : Bibliothèque Python pour l'API Spotify
- **python-dotenv** : Gestion des variables d'environnement

