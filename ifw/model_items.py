from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ItemEffect:
    hp_restore: int = 0
    mp_restore: int = 0
    attack_bonus: int = 0
    defense_bonus: int = 0
    duration: int = 0
    recharge_charges: bool = False
    cure_poison: bool = False


@dataclass(slots=True)
class Item:
    item_id: str
    name: str
    description: str
    item_type: str
    attack_bonus: int = 0
    defense_bonus: int = 0
    hp_bonus: int = 0
    mp_bonus: int = 0
    pickpocket_bonus: int = 0
    lockpick_bonus: int = 0
    required_level: int = 1
    value: int = 0
    stackable: bool = True
    effect: ItemEffect | None = None
    teaches_spell: str | None = None
    magical: bool = False
    max_charges: int = 0
    depleted_attack_bonus: int | None = None
    depleted_defense_bonus: int | None = None
    depleted_hp_bonus: int | None = None
    depleted_mp_bonus: int | None = None


@dataclass(slots=True)
class Spell:
    spell_id: str
    name: str
    description: str
    school: str
    mp_cost: int
    power: int = 0
    attack_bonus: int = 0
    armor_bonus: int = 0
    pickpocket_bonus: int = 0
    lockpick_bonus: int = 0
    duration: int = 0
    skip_turns: int = 0
    cure_poison: bool = False
    allowed_classes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Recipe:
    recipe_id: str
    name: str
    result_item: str
    ingredients: list[str]
    description: str = ""
