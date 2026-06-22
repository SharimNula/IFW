from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PlayerClass:
    class_id: str
    name: str
    description: str = ""
    max_hp: int = 42
    max_mp: int = 12
    gold: int = 35
    base_attack: int = 7
    base_defense: int = 4
    hp_per_level: int = 8
    mp_per_level: int = 4
    attack_per_level: int = 2
    defense_per_level: int = 1
    starting_currencies: dict[str, int] = field(default_factory=dict)
    pickpocket_chance: int = 0
    lockpick_chance: int = 0


@dataclass(slots=True)
class Faction:
    faction_id: str
    name: str
    description: str = ""


@dataclass(slots=True)
class PickpocketTarget:
    item_id: str
    difficulty: int = 0
    success_text: str = ""
    failure_text: str = ""


@dataclass(slots=True)
class LootDrop:
    item_id: str
    chance: float = 1.0


@dataclass(slots=True)
class BossEncounterChoice:
    choice_type: str
    label: str
    text: str = ""
    required_flags: list[str] = field(default_factory=list)
    required_item: str | None = None
    consume_item: bool = True
    success_chance: int = 0
    set_flag: str | None = None
    success_text: str = ""
    failure_text: str = ""


@dataclass(slots=True)
class BossEncounter:
    intro: str
    choices: list[BossEncounterChoice] = field(default_factory=list)


@dataclass(slots=True)
class Enemy:
    enemy_id: str
    name: str
    description: str
    level: int
    max_hp: int
    attack: int
    defense: int
    exp_reward: int
    gold_reward: int
    defeat_text: str = ""
    respawns: bool = True
    loot: list[LootDrop] = field(default_factory=list)
    prevent_attack_chance: int = 0
    prevent_attack_turns: int = 1
    prevent_attack_text: str = ""
    poison_chance: int = 0
    poison_text: str = ""
    boss_encounter: BossEncounter | None = None


@dataclass(slots=True)
class EnemyState:
    enemy_id: str
    current_hp: int
    max_hp: int = 0
    scaled_level: int = 0
    skip_turns: int = 0

    def to_dict(self) -> dict[str, int | str]:
        return {
            "enemy_id": self.enemy_id,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "scaled_level": self.scaled_level,
            "skip_turns": self.skip_turns,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, int | str]) -> "EnemyState":
        return cls(
            enemy_id=str(payload["enemy_id"]),
            current_hp=int(payload["current_hp"]),
            max_hp=int(payload.get("max_hp", 0)),
            scaled_level=int(payload.get("scaled_level", 0)),
            skip_turns=int(payload.get("skip_turns", 0)),
        )


@dataclass(slots=True)
class CompanionState:
    npc_id: str
    class_id: str
    origin_room: str
    current_hp: int
    current_mp: int
    weapon_id: str | None = None
    armor_id: str | None = None
    spell_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "npc_id": self.npc_id,
            "class_id": self.class_id,
            "origin_room": self.origin_room,
            "current_hp": self.current_hp,
            "current_mp": self.current_mp,
            "weapon_id": self.weapon_id,
            "armor_id": self.armor_id,
            "spell_ids": self.spell_ids,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "CompanionState":
        return cls(
            npc_id=str(payload["npc_id"]),
            class_id=str(payload["class_id"]),
            origin_room=str(payload["origin_room"]),
            current_hp=int(payload["current_hp"]),
            current_mp=int(payload["current_mp"]),
            weapon_id=payload.get("weapon_id") and str(payload["weapon_id"]),
            armor_id=payload.get("armor_id") and str(payload["armor_id"]),
            spell_ids=[str(spell_id) for spell_id in list(payload.get("spell_ids", []))],
        )


@dataclass(slots=True)
class NPC:
    npc_id: str
    name: str
    dialogue: str
    faction_id: str | None = None
    quest_id: str | None = None
    active_dialogue: str = ""
    completed_dialogue: str = ""
    dialogue_lines: list[str] = field(default_factory=list)
    quest_ids: list[str] = field(default_factory=list)
    can_recruit: bool = False
    companion_class: str | None = None
    recruit_required_item: str | None = None
    recruit_missing_item_text: str = ""
    consume_recruit_item: bool = True
    pickpocket_targets: list[PickpocketTarget] = field(default_factory=list)


@dataclass(slots=True)
class CurrencyExchangeRate:
    from_currency: str
    to_currency: str
    from_amount: int = 1
    to_amount: int = 1


@dataclass(slots=True)
class Vendor:
    vendor_id: str
    name: str
    dialogue: str
    stock: dict[str, int] = field(default_factory=dict)
    recipe_stock: dict[str, int] = field(default_factory=dict)
    spell_stock: dict[str, int] = field(default_factory=dict)
    buyback: float = 0.5
    accepted_currencies: list[str] = field(default_factory=list)
    stock_currencies: dict[str, str] = field(default_factory=dict)
    recipe_currencies: dict[str, str] = field(default_factory=dict)
    spell_currencies: dict[str, str] = field(default_factory=dict)
    exchange_rates: list[CurrencyExchangeRate] = field(default_factory=list)
    is_exchange: bool = False
    pickpocket_targets: list[PickpocketTarget] = field(default_factory=list)


@dataclass(slots=True)
class QuestEndingChoice:
    choice_id: str
    label: str
    text: str = ""
    ending_type: str = "custom"
    required_flags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class QuestFlagBranch:
    completion_text: str | None = None
    reward_gold: int | None = None
    reward_currency: str | None = None
    reward_amount: int | None = None
    reward_exp: int | None = None
    reward_item: str | None = None
    reward_recipe: str | None = None


@dataclass(slots=True)
class QuestFlagOutcome:
    flag: str
    when_true: QuestFlagBranch = field(default_factory=QuestFlagBranch)
    when_false: QuestFlagBranch = field(default_factory=QuestFlagBranch)


@dataclass(slots=True)
class Quest:
    quest_id: str
    name: str
    giver_id: str
    description: str
    completion_text: str
    offer_dialogue: str = ""
    active_dialogue: str = ""
    completed_dialogue: str = ""
    accept_item: str | None = None
    target_enemy: str | None = None
    required_item: str | None = None
    destination_room: str | None = None
    reward_gold: int = 0
    reward_currency: str = "gold"
    reward_amount: int | None = None
    reward_exp: int = 0
    reward_item: str | None = None
    reward_recipe: str | None = None
    ends_world: bool = False
    ending_text: str = ""
    ending_text_by_faction: dict[str, str] = field(default_factory=dict)
    ending_choices: list[QuestEndingChoice] = field(default_factory=list)
    flag_outcome: QuestFlagOutcome | None = None
