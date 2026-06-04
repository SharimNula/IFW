from __future__ import annotations

import xml.etree.ElementTree as ET

from ..models import Currency, Faction, PlayerClass
from ..world_loader_xml import (
    _first_attr,
    _optional_text,
    _parse_int,
    _required_attr,
    _required_attr_any,
)


def parse_currencies(root: ET.Element) -> tuple[dict[str, Currency], str]:
    currencies_element = root.find("currencies")
    currencies: dict[str, Currency] = {}
    if currencies_element is not None:
        for currency_element in currencies_element.findall("./currency"):
            currency_id = _required_attr(currency_element, "id")
            name = currency_element.get("name", "").strip() or currency_id.replace("_", " ").title()
            singular = currency_element.get("singular", "").strip() or name.lower()
            plural = currency_element.get("plural", "").strip() or (
                singular if singular == "gold" else f"{singular}s"
            )
            currencies[currency_id] = Currency(
                currency_id=currency_id,
                name=name,
                singular=singular,
                plural=plural,
            )

    if "gold" not in currencies:
        currencies["gold"] = Currency("gold", "Gold", "gold", "gold")

    if currencies_element is not None:
        default_currency_id = (
            _first_attr(currencies_element, "default", "default_currency", "base")
            or next(iter(currencies))
        )
    else:
        default_currency_id = "gold"
    return currencies, default_currency_id


def parse_jail(root: ET.Element) -> tuple[str | None, int, str]:
    jail_element = root.find("jail")
    if jail_element is None:
        return None, 0, "gold"
    return (
        _required_attr_any(jail_element, "room", "room_id", "id"),
        _parse_int(_first_attr(jail_element, "fee", "cost", "bail"), default=0),
        _first_attr(jail_element, "currency", "currency_id") or "gold",
    )


def parse_player_classes(root: ET.Element) -> dict[str, PlayerClass]:
    player_classes: dict[str, PlayerClass] = {}
    class_elements = root.findall("./player_classes/class") + root.findall("./classes/class")
    for class_element in class_elements:
        class_id = _required_attr_any(class_element, "id", "name").lower()
        gold = _parse_int(_required_attr_any(class_element, "gold", "starting_gold"))
        player_classes[class_id] = PlayerClass(
            class_id=class_id,
            name=class_element.get("name", "").strip() or class_id.replace("_", " ").title(),
            description=_optional_text(class_element.find("description")),
            max_hp=_parse_int(_required_attr_any(class_element, "max_hp", "hp")),
            max_mp=_parse_int(_required_attr_any(class_element, "max_mp", "mp")),
            gold=gold,
            base_attack=_parse_int(_required_attr_any(class_element, "base_attack", "attack")),
            base_defense=_parse_int(_required_attr_any(class_element, "base_defense", "defense")),
            hp_per_level=_parse_int(_first_attr(class_element, "hp_per_level", "level_hp"), default=8),
            mp_per_level=_parse_int(_first_attr(class_element, "mp_per_level", "level_mp"), default=4),
            attack_per_level=_parse_int(
                _first_attr(class_element, "attack_per_level", "level_attack"),
                default=2,
            ),
            defense_per_level=_parse_int(
                _first_attr(class_element, "defense_per_level", "level_defense"),
                default=1,
            ),
            starting_currencies=parse_starting_currencies(class_element, gold),
            pickpocket_chance=_parse_int(
                _first_attr(
                    class_element,
                    "pickpocket_chance",
                    "pickpocket",
                    "pickpocket_skill",
                )
            ),
            lockpick_chance=_parse_int(
                _first_attr(
                    class_element,
                    "lockpick_chance",
                    "lockpick",
                    "lockpick_skill",
                )
            ),
        )
    return player_classes


def parse_starting_currencies(class_element: ET.Element, gold: int) -> dict[str, int]:
    starting_currencies = {"gold": gold}
    for currency_element in (
        class_element.findall("./currencies/currency")
        + class_element.findall("./starting_currencies/currency")
    ):
        currency_id = _required_attr_any(currency_element, "id", "currency")
        amount = _parse_int(_required_attr_any(currency_element, "amount", "value"))
        starting_currencies[currency_id] = amount
    return starting_currencies


def parse_factions(root: ET.Element) -> dict[str, Faction]:
    factions: dict[str, Faction] = {}
    for faction_element in root.findall("./factions/faction"):
        faction_id = _required_attr(faction_element, "id")
        factions[faction_id] = Faction(
            faction_id=faction_id,
            name=faction_element.get("name", "").strip() or faction_id.replace("_", " ").title(),
            description=_optional_text(faction_element.find("description")),
        )
    return factions


def parse_starter_items(root: ET.Element) -> dict[str, list[str]]:
    starter_items: dict[str, list[str]] = {}
    for class_element in root.findall("./starter_loadouts/class"):
        starter_items[_required_attr(class_element, "name").lower()] = [
            _required_attr(item_ref, "id") for item_ref in class_element.findall("./item_ref")
        ]
    return starter_items


def parse_starter_spells(root: ET.Element) -> dict[str, list[str]]:
    starter_spells: dict[str, list[str]] = {}
    for class_element in root.findall("./starter_spells/class"):
        starter_spells[_required_attr(class_element, "name").lower()] = [
            _required_attr(spell_ref, "id") for spell_ref in class_element.findall("./spell_ref")
        ]
    return starter_spells
