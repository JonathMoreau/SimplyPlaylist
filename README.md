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

## 🧪 Tests

Le projet inclut une suite complète de tests unitaires avec vérification de la couverture de code.

### Lancer les tests

```bash
# Lancer tous les tests
pytest

# Lancer les tests avec affichage détaillé
pytest -v

# Lancer les tests avec couverture de code
pytest --cov=domain --cov=infrastructure --cov=application --cov=presentation --cov-report=html

# Ouvrir le rapport de couverture dans le navigateur
# (Windows)
start htmlcov/index.html
# (Linux/Mac)
open htmlcov/index.html
```

### Couverture de code

La couverture de code est configurée pour afficher :
- Le rapport dans le terminal avec les lignes manquantes
- Un rapport HTML détaillé dans `htmlcov/`
- Un rapport XML pour l'intégration CI/CD

```bash
# Voir la couverture dans le terminal
pytest --cov=domain --cov=infrastructure --cov=application --cov=presentation --cov-report=term-missing

# Générer le rapport HTML
pytest --cov=domain --cov=infrastructure --cov=application --cov=presentation --cov-report=html
```

### Structure des tests

Les tests sont organisés dans le dossier `tests/` :
- `tests/test_domain.py` : Tests pour les entités du domaine
- `tests/test_infrastructure.py` : Tests pour les repositories et la configuration
- `tests/test_application.py` : Tests pour les use cases
- `tests/test_presentation.py` : Tests pour le point d'entrée

Les tests utilisent des mocks pour éviter les appels réels à l'API Spotify.

### Tests avec Tox (CI/CD)

Tox est configuré pour tester sur plusieurs versions de Python dans le pipeline CI/CD. Pour le développement local, utilisez directement `pytest`.

```bash
# Pour tester localement, utilisez pytest directement
pytest

# Tox est principalement utilisé dans GitHub Actions
# Pour l'utiliser localement, vous devez avoir plusieurs versions de Python installées
tox
```

## 🛠️ Technologies utilisées

- **Python 3** (3.9+)
- **Spotipy** : Bibliothèque Python pour l'API Spotify
- **python-dotenv** : Gestion des variables d'environnement
- **pytest** : Framework de tests
- **pytest-cov** : Extension pour la couverture de code
- **tox** : Automatisation des tests multi-versions (CI/CD)

## 🏗️ Architecture

Le projet suit une architecture **Domain Driven Design (DDD)** :

- **Domain** : Entités métier (`Artist`, `Track`, `Playlist`) et interfaces de repositories
- **Infrastructure** : Implémentations (`SpotifyRepository`, `ArtistFileRepository`, `SpotifyConfig`)
- **Application** : Use cases (`SearchArtistTracksUseCase`, `CreatePlaylistFromArtistsUseCase`)
- **Presentation** : Point d'entrée (`main()`)
