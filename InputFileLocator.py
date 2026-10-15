from pathlib import Path
from typing import List


class InputFileLocator:
    """Znajduje plik wejściowy w folderze input projektu — lokalnie, w Dockerze (/app) i w folderze src."""

    def __init__(self, folder: str = "input"):
        self.folder = folder

    def locator(self) -> "InputFileLocator":
        return self

    def resolve(self, path: str) -> Path:
        """Ścieżka wskazana wprost (np. przez blok File content), a gdy jej nie ma — ten sam plik
        w folderze input projektu. W Dockerze ścieżka z Windows nie istnieje, nazwa pliku tak."""
        given = Path(path)
        if given.is_file():
            return given
        return self.find(str(path).replace("\\", "/").rsplit("/", 1)[-1])

    def find(self, file_name: str) -> Path:
        candidates = [root / self.folder / file_name for root in self._project_roots()]
        candidates += [root / file_name for root in self._project_roots()]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise FileNotFoundError(
            "Nie znaleziono pliku %s. Połóż go w folderze '%s' obok pliku .catnip. Szukano w: %s"
            % (file_name, self.folder, ", ".join(str(c.parent) for c in candidates[:3])))

    @staticmethod
    def _project_roots() -> List[Path]:
        """Najpierw foldery z plikiem .catnip, potem bieżący folder i folder modułu."""
        here = Path(__file__).resolve().parent
        roots = []
        for folder in (Path.cwd(), here, here.parent):
            if folder not in roots:
                roots.append(folder)
        return sorted(roots, key=lambda folder: not any(folder.glob("*.catnip")))
