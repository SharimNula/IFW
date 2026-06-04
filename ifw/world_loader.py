from __future__ import annotations

from pathlib import Path
import copy
import xml.etree.ElementTree as ET

from .models import World
from .world_loader_sections import parse_world
from .world_loader_validation import validate_world as _validate_world
from .world_loader_xml import (
    _first_attr,
    _optional_text,
    _parse_bool,
    _parse_classes,
    _parse_id_list,
    _parse_int,
    _required_attr,
    _required_attr_any,
)

__all__ = [
    "_first_attr",
    "_optional_text",
    "_parse_bool",
    "_parse_classes",
    "_parse_id_list",
    "_parse_int",
    "_required_attr",
    "_required_attr_any",
    "_validate_world",
    "load_world",
]


WORLD_METADATA_FILE = "world.xml"
SECTION_FILES: tuple[tuple[str, str], ...] = (
    ("items.xml", "items"),
    ("spells.xml", "spells"),
    ("enemies.xml", "enemies"),
    ("npcs.xml", "npcs"),
    ("vendors.xml", "vendors"),
    ("quests.xml", "quests"),
    ("rooms.xml", "rooms"),
)


def load_world(path: str | Path) -> World:
    xml_path = Path(path)
    if xml_path.is_dir():
        root = _load_world_directory(xml_path)
        source = xml_path
    elif xml_path.name.lower() == WORLD_METADATA_FILE and _has_split_sections(xml_path.parent):
        root = _load_world_directory(xml_path.parent)
        source = xml_path.parent
    else:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        source = xml_path

    if root.tag != "world":
        raise ValueError("World XML must have a <world> root element.")

    world = parse_world(root, source)
    _validate_world(world, source)
    return world


def _has_split_sections(directory: Path) -> bool:
    return any((directory / filename).is_file() for filename, _ in SECTION_FILES)


def _load_world_directory(directory: Path) -> ET.Element:
    metadata_path = directory / WORLD_METADATA_FILE
    if not metadata_path.is_file():
        raise ValueError(f"{directory}: split world folders must contain {WORLD_METADATA_FILE}.")

    tree = ET.parse(metadata_path)
    root = tree.getroot()
    if root.tag != "world":
        raise ValueError("World XML must have a <world> root element.")

    for filename, expected_tag in SECTION_FILES:
        section_path = directory / filename
        if not section_path.is_file():
            continue
        section = ET.parse(section_path).getroot()
        if section.tag != expected_tag:
            raise ValueError(
                f"{section_path}: expected <{expected_tag}> root element, "
                f"got <{section.tag}>."
            )
        root.append(copy.deepcopy(section))
    return root
