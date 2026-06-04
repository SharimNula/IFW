from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from ..models import World
from ..world_loader_xml import _first_attr, _optional_text, _required_attr
from .actors import parse_enemies, parse_monster_pools, parse_npcs, parse_spells, parse_vendors
from .items import parse_items, parse_recipes
from .metadata import (
    parse_currencies,
    parse_factions,
    parse_jail,
    parse_player_classes,
    parse_starter_items,
    parse_starter_spells,
)
from .quests import parse_quests
from .rooms import parse_rooms


def parse_world(root: ET.Element, source: Path) -> World:
    items = parse_items(root)
    currencies, default_currency_id = parse_currencies(root)
    jail_room, jail_fee, jail_currency = parse_jail(root)
    return World(
        world_id=_required_attr(root, "id"),
        name=_required_attr(root, "name"),
        description=_optional_text(root.find("description")),
        start_room=_required_attr(root, "start_room"),
        end_room=_first_attr(root, "end_room"),
        items=items,
        spells=parse_spells(root),
        enemies=parse_enemies(root),
        monster_pools=parse_monster_pools(root),
        npcs=parse_npcs(root),
        vendors=parse_vendors(root),
        quests=parse_quests(root),
        rooms=parse_rooms(root, source),
        recipes=parse_recipes(root, items, source),
        player_classes=parse_player_classes(root),
        factions=parse_factions(root),
        starter_items=parse_starter_items(root),
        starter_spells=parse_starter_spells(root),
        currencies=currencies,
        default_currency_id=default_currency_id,
        jail_room=jail_room,
        jail_fee=jail_fee,
        jail_currency=jail_currency,
    )
