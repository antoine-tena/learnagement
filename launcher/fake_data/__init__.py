"""Le générateur de données fictives : un fichier SQL reproductible, posé sur le jeu public.

`generate(size, seed)` redonne exactement le même texte pour la même taille et la même graine.
"""

from launcher.fake_data.generator import (
    DEFAULT_SEED,
    FAKE_DATA_FILE_NAME,
    FakeDataSize,
    generate,
)

__all__ = ["DEFAULT_SEED", "FAKE_DATA_FILE_NAME", "FakeDataSize", "generate"]
