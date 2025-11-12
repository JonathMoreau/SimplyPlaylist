# Guide des Tests

Ce document explique comment utiliser les tests unitaires et la couverture de code pour ce projet.

## Installation des dépendances de test

```bash
pip install -r requirements.txt
```

Cela installera :
- `pytest` : Framework de tests
- `pytest-cov` : Extension pour la couverture de code
- `pytest-mock` : Extension pour les mocks

## Structure du code refactorisé

Le code a été refactorisé en classes pour améliorer la maintenabilité :

### Classes principales

1. **`SpotifyConfig`** : Gère la configuration Spotify (credentials, URIs, etc.)
2. **`ArtistFileLoader`** : Charge les artistes depuis un fichier texte
3. **`SpotifyPlaylistManager`** : Gère toutes les opérations Spotify (recherche, playlists, etc.)
4. **`PlaylistCreator`** : Orchestre la création de playlists à partir d'une liste d'artistes

### Avantages de la refactorisation

- **Séparation des responsabilités** : Chaque classe a un rôle clair
- **Testabilité** : Plus facile de mocker et tester chaque composant
- **Maintenabilité** : Code plus organisé et modulaire
- **Réutilisabilité** : Les classes peuvent être réutilisées dans d'autres contextes

## Lancer les tests

### Tests de base

```bash
# Lancer tous les tests
pytest

# Lancer avec affichage détaillé
pytest -v

# Lancer un fichier de test spécifique
pytest tests/test_app.py

# Lancer un test spécifique
pytest tests/test_app.py::TestSpotifyConfig::test_config_initialization
```

### Tests avec couverture

```bash
# Couverture dans le terminal
pytest --cov=app --cov-report=term-missing

# Générer le rapport HTML
pytest --cov=app --cov-report=html

# Ouvrir le rapport HTML
# Windows
start htmlcov/index.html
# Linux/Mac
open htmlcov/index.html
```

Le rapport HTML montre :
- Les lignes couvertes (vert)
- Les lignes non couvertes (rouge)
- Les lignes partiellement couvertes (jaune)
- Le pourcentage de couverture par fichier

### Configuration de la couverture

La configuration est dans `pytest.ini` :
- Couverture des branches activée (`--cov-branch`)
- Rapports multiples : terminal, HTML, XML
- Affichage des lignes manquantes

## Structure des tests

Les tests sont organisés par classe :

- `TestSpotifyConfig` : Tests de configuration
- `TestArtistFileLoader` : Tests de chargement de fichiers
- `TestSpotifyPlaylistManager` : Tests des opérations Spotify
- `TestPlaylistCreator` : Tests de création de playlists

### Utilisation des mocks

Tous les tests utilisent des mocks pour éviter les appels réels à l'API Spotify :
- `unittest.mock.Mock` : Pour créer des objets mock
- `@patch` : Pour patcher des dépendances externes
- `tmp_path` : Pour créer des fichiers temporaires

## Objectifs de couverture

- **Minimum recommandé** : 80% de couverture
- **Idéal** : 90%+ de couverture
- **Branches** : Tester tous les chemins conditionnels

## Amélioration continue

Pour améliorer la couverture :

1. Lancer `pytest --cov=app --cov-report=term-missing`
2. Identifier les lignes non couvertes
3. Ajouter des tests pour ces lignes
4. Relancer les tests pour vérifier que la couverture s'améliore

## Intégration CI/CD

Les rapports XML peuvent être utilisés dans les pipelines CI/CD :

```bash
pytest --cov=app --cov-report=xml
```

Le fichier `coverage.xml` peut être intégré dans :
- GitHub Actions
- GitLab CI
- Jenkins
- Autres outils CI/CD

