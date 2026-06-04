from __future__ import annotations

from pathlib import Path
import json
import re

from .models import Player


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORLD_DIR = PROJECT_ROOT / "worlds"
PLAYER_DIR = PROJECT_ROOT / "players"
WORLD_METADATA_FILE = "world.xml"


def ensure_data_directories() -> None:
    WORLD_DIR.mkdir(parents=True, exist_ok=True)
    PLAYER_DIR.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "player"


def player_save_path(name: str, directory: Path = PLAYER_DIR) -> Path:
    return directory / f"{slugify(name)}.json"


def _is_split_world_directory(path: Path) -> bool:
    return path.is_dir() and (path / WORLD_METADATA_FILE).is_file()


def _world_sort_key(path: Path) -> str:
    return slugify(path.name if path.is_dir() else path.stem)


def list_world_files(directory: Path = WORLD_DIR) -> list[Path]:
    split_worlds = [
        path for path in directory.iterdir()
        if _is_split_world_directory(path)
    ] if directory.is_dir() else []
    split_world_keys = {slugify(path.name) for path in split_worlds}
    single_file_worlds = [
        path for path in directory.glob("*.xml")
        if slugify(path.stem) not in split_world_keys
    ]
    return sorted([*split_worlds, *single_file_worlds], key=_world_sort_key)


def find_world_file(query: str, directory: Path = WORLD_DIR) -> Path | None:
    candidate = Path(query)
    if _is_split_world_directory(candidate):
        return candidate
    if candidate.is_file():
        return candidate

    if not candidate.suffix:
        direct_directory = directory / query
        if _is_split_world_directory(direct_directory):
            return direct_directory
        direct = directory / f"{query}.xml"
        if direct.is_file():
            return direct

    query_key = slugify(Path(query).stem)
    for path in list_world_files(directory):
        if slugify(path.stem) == query_key:
            return path
    return None


def load_player(name: str, directory: Path = PLAYER_DIR) -> Player | None:
    path = player_save_path(name, directory)
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return Player.from_dict(payload)


def save_player(player: Player, directory: Path = PLAYER_DIR) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = player_save_path(player.name, directory)
    path.write_text(json.dumps(player.to_dict(), indent=2), encoding="utf-8")
    return path
