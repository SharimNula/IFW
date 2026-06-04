from __future__ import annotations

from dataclasses import dataclass, field

from .model_actors import Enemy, Faction, NPC, PlayerClass, Quest, Vendor
from .model_items import Item, Recipe, Spell


@dataclass(slots=True)
class Currency:
    currency_id: str
    name: str
    singular: str = ""
    plural: str = ""


@dataclass(slots=True)
class MonsterPoolEntry:
    enemy_id: str
    weight: int = 1


@dataclass(slots=True)
class MonsterPool:
    pool_id: str
    name: str = ""
    entries: list[MonsterPoolEntry] = field(default_factory=list)


@dataclass(slots=True)
class MiningDrop:
    item_id: str
    min_quantity: int = 1
    max_quantity: int = 3


@dataclass(slots=True)
class FactionEnemySpawn:
    faction_id: str
    enemy_id: str
    count: int = 1


@dataclass(slots=True)
class HiddenExit:
    direction: str
    target_room: str
    required_flag: str


@dataclass(slots=True)
class RoomInteraction:
    interaction_id: str
    name: str
    description: str = ""
    interact_text: str = ""
    completed_text: str = ""
    required_flag: str | None = None
    required_item: str | None = None
    missing_item_text: str = ""
    consume_required_item: bool = False
    set_flags: list[str] = field(default_factory=list)
    repeatable: bool = False
    lockpickable: bool = False
    lockpick_difficulty: int = 0
    lockpick_item: str = "lockpicks"
    lockpick_text: str = ""
    lockpick_failed_text: str = ""
    lockpick_missing_item_text: str = ""


@dataclass(slots=True)
class Room:
    room_id: str
    name: str
    description: str
    exits: dict[str, str] = field(default_factory=dict)
    hidden_exits: dict[str, HiddenExit] = field(default_factory=dict)
    interactions: dict[str, RoomInteraction] = field(default_factory=dict)
    item_ids: list[str] = field(default_factory=list)
    enemy_ids: list[str] = field(default_factory=list)
    faction_enemy_spawns: list[FactionEnemySpawn] = field(default_factory=list)
    monster_pool_id: str | None = None
    monster_count: int = 0
    npc_ids: list[str] = field(default_factory=list)
    vendor_ids: list[str] = field(default_factory=list)
    has_storage: bool = False
    can_rest: bool = False
    locks_on_exit: bool = False
    required_item: str | None = None
    locked_message: str = ""
    sealed_message: str = ""
    maze_sequence: list[str] = field(default_factory=list)
    maze_success_room: str | None = None
    maze_progress_message: str = ""
    maze_failure_message: str = ""
    maze_success_message: str = ""
    mining_drops: list[MiningDrop] = field(default_factory=list)
    mining_message: str = ""


@dataclass(slots=True)
class World:
    world_id: str
    name: str
    description: str
    start_room: str
    end_room: str | None
    items: dict[str, Item]
    spells: dict[str, Spell]
    enemies: dict[str, Enemy]
    monster_pools: dict[str, MonsterPool]
    npcs: dict[str, NPC]
    vendors: dict[str, Vendor]
    quests: dict[str, Quest]
    rooms: dict[str, Room]
    recipes: dict[str, Recipe]
    player_classes: dict[str, PlayerClass] = field(default_factory=dict)
    factions: dict[str, Faction] = field(default_factory=dict)
    starter_items: dict[str, list[str]] = field(default_factory=dict)
    starter_spells: dict[str, list[str]] = field(default_factory=dict)
    currencies: dict[str, Currency] = field(default_factory=dict)
    default_currency_id: str = "gold"
    jail_room: str | None = None
    jail_fee: int = 0
    jail_currency: str = "gold"
