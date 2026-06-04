from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from ..models import Item, ItemEffect, Recipe
from ..world_loader_xml import (
    _first_attr,
    _optional_text,
    _parse_bool,
    _parse_int,
    _required_attr,
)
from .common import optional_int_attr


def parse_items(root: ET.Element) -> dict[str, Item]:
    items: dict[str, Item] = {}
    for item_element in root.findall("./items/item"):
        item_id = _required_attr(item_element, "id")
        effect_element = item_element.find("effect")
        effect = None
        if effect_element is not None:
            effect = ItemEffect(
                hp_restore=_parse_int(effect_element.get("hp_restore")),
                mp_restore=_parse_int(effect_element.get("mp_restore")),
                attack_bonus=_parse_int(effect_element.get("attack_bonus")),
                defense_bonus=_parse_int(effect_element.get("defense_bonus")),
                duration=_parse_int(effect_element.get("duration")),
                recharge_charges=_parse_bool(
                    _first_attr(
                        effect_element,
                        "recharge_charges",
                        "recharge_uses",
                        "recharge",
                        "restores_charges",
                    ),
                    default=False,
                ),
                cure_poison=_parse_bool(
                    _first_attr(
                        effect_element,
                        "cure_poison",
                        "cures_poison",
                        "remove_poison",
                        "removes_poison",
                        "antidote",
                    ),
                    default=False,
                ),
            )
        magical = _parse_bool(_first_attr(item_element, "magical", "magic"), default=False)
        max_charges = _parse_int(
            _first_attr(
                item_element,
                "charges",
                "max_charges",
                "uses",
                "max_uses",
                "magic_uses",
            ),
            default=3 if magical else 0,
        )
        items[item_id] = Item(
            item_id=item_id,
            name=_required_attr(item_element, "name"),
            description=_optional_text(item_element.find("description")),
            item_type=_required_attr(item_element, "type").lower(),
            attack_bonus=_parse_int(item_element.get("attack_bonus")),
            defense_bonus=_parse_int(item_element.get("defense_bonus")),
            hp_bonus=_parse_int(item_element.get("hp_bonus")),
            mp_bonus=_parse_int(item_element.get("mp_bonus")),
            pickpocket_bonus=_parse_int(
                _first_attr(item_element, "pickpocket_bonus", "pickpocket")
            ),
            lockpick_bonus=_parse_int(
                _first_attr(item_element, "lockpick_bonus", "lockpick")
            ),
            required_level=_parse_int(
                item_element.get("required_level")
                or item_element.get("level_required")
                or item_element.get("level_requirement"),
                default=1,
            ),
            value=_parse_int(item_element.get("value")),
            stackable=_parse_bool(item_element.get("stackable"), default=True),
            effect=effect,
            teaches_spell=item_element.get("teaches_spell"),
            magical=magical or max_charges > 0,
            max_charges=max_charges,
            depleted_attack_bonus=optional_int_attr(item_element, "depleted_attack_bonus"),
            depleted_defense_bonus=optional_int_attr(item_element, "depleted_defense_bonus"),
            depleted_hp_bonus=optional_int_attr(item_element, "depleted_hp_bonus"),
            depleted_mp_bonus=optional_int_attr(item_element, "depleted_mp_bonus"),
        )
    return items


def parse_recipes(root: ET.Element, items: dict[str, Item], source: Path) -> dict[str, Recipe]:
    recipes: dict[str, Recipe] = {}
    recipe_elements = root.findall("./crafting/recipe") + root.findall("./items/crafting/recipe")
    for recipe_element in recipe_elements:
        result_item = _required_attr(recipe_element, "result")
        recipe_id = recipe_element.get("id", "").strip() or result_item
        recipe_name = recipe_element.get("name", "").strip() or f"{items[result_item].name} Recipe"
        ingredients: list[str] = []
        for ingredient_element in recipe_element.findall("./ingredient"):
            ingredient_id = _required_attr(ingredient_element, "item")
            quantity = _parse_int(ingredient_element.get("quantity"), default=1)
            if quantity < 1:
                raise ValueError(
                    f"{source}: recipe '{recipe_id}' uses invalid quantity "
                    f"{quantity} for ingredient '{ingredient_id}'."
                )
            ingredients.extend([ingredient_id] * quantity)
        recipe = Recipe(
            recipe_id=recipe_id,
            name=recipe_name,
            result_item=result_item,
            ingredients=ingredients,
            description=_optional_text(recipe_element.find("description")),
        )
        recipes[recipe.recipe_id] = recipe
    return recipes
