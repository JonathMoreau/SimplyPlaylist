"""
Repository pour le chargement des artistes depuis un fichier
"""
import os
from typing import List
from domain.repositories import IArtistFileRepository


class ArtistFileRepository(IArtistFileRepository):
    """Implémentation du repository de fichiers d'artistes"""
    
    DEFAULT_FILENAME = 'hellfest_2026_artists.txt'
    EXAMPLE_ARTISTS = [
        "Iron Maiden",
        "Metallica",
        "Slayer",
        "Megadeth",
        "Anthrax"
    ]
    
    def load_artists(self, filename: str = DEFAULT_FILENAME) -> List[str]:
        """
        Charge la liste des artistes depuis un fichier texte
        Un artiste par ligne
        
        Args:
            filename: Nom du fichier à charger
            
        Returns:
            Liste des noms d'artistes
        """
        if not os.path.exists(filename):
            self._create_example_file(filename)
            return self.EXAMPLE_ARTISTS.copy()
        
        artists = []
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Ignorer les lignes vides et les commentaires
                if line and not line.startswith('#'):
                    artists.append(line)
        return artists
    
    def _create_example_file(self, filename: str) -> None:
        """Crée un fichier exemple avec quelques groupes"""
        print(f"⚠️  Fichier {filename} non trouvé. Création d'un fichier exemple...")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.EXAMPLE_ARTISTS))
        print(f"✓  Fichier {filename} créé avec des exemples. Ajoutez vos 183 groupes !")

