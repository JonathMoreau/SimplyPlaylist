#!/usr/bin/env python3
"""
Application simple pour créer une playlist Spotify avec les groupes du Hellfest 2026

Ce fichier est conservé pour compatibilité. La nouvelle architecture DDD est dans :
- domain/ : Entités et interfaces
- infrastructure/ : Implémentations (SpotifyRepository, config, file_loader)
- application/ : Use cases
- presentation/ : Point d'entrée (main)
"""

# Import de la nouvelle architecture
from presentation.main import main

if __name__ == '__main__':
    main()
