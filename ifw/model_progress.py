from __future__ import annotations

from dataclasses import dataclass, field

from .model_actors import CompanionState, EnemyState


@dataclass(slots=True)
class WorldProgress:
    current_room: str
    previous_room: str | None = None
    inventory: dict[str, int] = field(default_factory=dict)
    storage: dict[str, int] = field(default_factory=dict)
    weapon_id: str | None = None
    armor_id: str | None = None
    accessory_ids: list[str] = field(default_factory=list)
    learned_spells: list[str] = field(default_factory=list)
    unlocked_recipes: list[str] = field(default_factory=list)
    room_items: dict[str, list[str]] = field(default_factory=dict)
    room_enemies: dict[str, list[EnemyState]] = field(default_factory=dict)
    sealed_rooms: list[str] = field(default_factory=list)
    active_quests: list[str] = field(default_factory=list)
    completed_quests: list[str] = field(default_factory=list)
    defeated_enemies: list[str] = field(default_factory=list)
    npc_dialogue_indices: dict[str, int] = field(default_factory=dict)
    maze_progress: dict[str, int] = field(default_factory=dict)
    story_flags: list[str] = field(default_factory=list)
    faction_id: str | None = None
    companions: list[CompanionState] = field(default_factory=list)
    pending_ending_quest_id: str | None = None
    item_charges: dict[str, int] = field(default_factory=dict)
    player_poisoned: bool = False
    pickpocketed_targets: list[str] = field(default_factory=list)
    lockpick_failures: dict[str, int] = field(default_factory=dict)

    def add_item(self, item_id: str, amount: int = 1) -> None:
        self.inventory[item_id] = self.inventory.get(item_id, 0) + amount

    def remove_item(self, item_id: str, amount: int = 1) -> bool:
        current = self.inventory.get(item_id, 0)
        if current < amount:
            return False
        new_total = current - amount
        if new_total:
            self.inventory[item_id] = new_total
        else:
            self.inventory.pop(item_id, None)
            if self.weapon_id == item_id:
                self.weapon_id = None
            if self.armor_id == item_id:
                self.armor_id = None
            for companion in self.companions:
                if companion.weapon_id == item_id:
                    companion.weapon_id = None
                if companion.armor_id == item_id:
                    companion.armor_id = None
        while self.accessory_ids.count(item_id) > new_total:
            self.accessory_ids.remove(item_id)
        return True

    def add_storage_item(self, item_id: str, amount: int = 1) -> None:
        self.storage[item_id] = self.storage.get(item_id, 0) + amount

    def remove_storage_item(self, item_id: str, amount: int = 1) -> bool:
        current = self.storage.get(item_id, 0)
        if current < amount:
            return False
        new_total = current - amount
        if new_total:
            self.storage[item_id] = new_total
        else:
            self.storage.pop(item_id, None)
        return True

    def to_dict(self) -> dict[str, object]:
        return {
            "current_room": self.current_room,
            "previous_room": self.previous_room,
            "inventory": self.inventory,
            "storage": self.storage,
            "weapon_id": self.weapon_id,
            "armor_id": self.armor_id,
            "accessory_ids": self.accessory_ids,
            "learned_spells": self.learned_spells,
            "unlocked_recipes": self.unlocked_recipes,
            "room_items": self.room_items,
            "room_enemies": {
                room_id: [enemy.to_dict() for enemy in enemies]
                for room_id, enemies in self.room_enemies.items()
            },
            "sealed_rooms": self.sealed_rooms,
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests,
            "defeated_enemies": self.defeated_enemies,
            "npc_dialogue_indices": self.npc_dialogue_indices,
            "maze_progress": self.maze_progress,
            "story_flags": self.story_flags,
            "faction_id": self.faction_id,
            "companions": [companion.to_dict() for companion in self.companions],
            "pending_ending_quest_id": self.pending_ending_quest_id,
            "item_charges": self.item_charges,
            "player_poisoned": self.player_poisoned,
            "pickpocketed_targets": self.pickpocketed_targets,
            "lockpick_failures": self.lockpick_failures,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "WorldProgress":
        room_enemies = {
            room_id: [EnemyState.from_dict(enemy) for enemy in enemies]
            for room_id, enemies in dict(payload.get("room_enemies", {})).items()
        }
        return cls(
            current_room=str(payload["current_room"]),
            previous_room=payload.get("previous_room") and str(payload["previous_room"]),
            inventory={str(k): int(v) for k, v in dict(payload.get("inventory", {})).items()},
            storage={str(k): int(v) for k, v in dict(payload.get("storage", {})).items()},
            weapon_id=payload.get("weapon_id") and str(payload["weapon_id"]),
            armor_id=payload.get("armor_id") and str(payload["armor_id"]),
            accessory_ids=[str(item_id) for item_id in list(payload.get("accessory_ids", []))],
            learned_spells=[str(spell) for spell in list(payload.get("learned_spells", []))],
            unlocked_recipes=[
                str(recipe_id) for recipe_id in list(payload.get("unlocked_recipes", []))
            ],
            room_items={
                str(room_id): [str(item_id) for item_id in item_ids]
                for room_id, item_ids in dict(payload.get("room_items", {})).items()
            },
            room_enemies=room_enemies,
            sealed_rooms=[str(room_id) for room_id in list(payload.get("sealed_rooms", []))],
            active_quests=[str(quest_id) for quest_id in list(payload.get("active_quests", []))],
            completed_quests=[
                str(quest_id) for quest_id in list(payload.get("completed_quests", []))
            ],
            defeated_enemies=[
                str(enemy_id) for enemy_id in list(payload.get("defeated_enemies", []))
            ],
            npc_dialogue_indices={
                str(npc_id): int(index)
                for npc_id, index in dict(payload.get("npc_dialogue_indices", {})).items()
            },
            maze_progress={
                str(room_id): int(index)
                for room_id, index in dict(payload.get("maze_progress", {})).items()
            },
            story_flags=[str(flag) for flag in list(payload.get("story_flags", []))],
            faction_id=payload.get("faction_id") and str(payload["faction_id"]),
            companions=[
                CompanionState.from_dict(companion)
                for companion in list(payload.get("companions", []))
            ],
            pending_ending_quest_id=(
                payload.get("pending_ending_quest_id")
                and str(payload["pending_ending_quest_id"])
            ),
            item_charges={
                str(item_id): int(charges)
                for item_id, charges in dict(payload.get("item_charges", {})).items()
            },
            player_poisoned=bool(payload.get("player_poisoned", False)),
            pickpocketed_targets=[
                str(target_key) for target_key in list(payload.get("pickpocketed_targets", []))
            ],
            lockpick_failures={
                str(target_key): int(failures)
                for target_key, failures in dict(payload.get("lockpick_failures", {})).items()
            },
        )


@dataclass(slots=True)
class Player:
    name: str
    player_class: str
    level: int
    experience: int
    gold: int
    max_hp: int
    hp: int
    max_mp: int
    mp: int
    base_attack: int
    base_defense: int
    world_states: dict[str, WorldProgress] = field(default_factory=dict)
    wallet: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.wallet:
            self.wallet = {"gold": self.gold}
        else:
            self.wallet["gold"] = self.gold

    def experience_to_next_level(self) -> int:
        return 25 * self.level * (self.level + 3)

    def gain_experience(
        self,
        amount: int,
        hp_per_level: int = 8,
        mp_per_level: int = 4,
        attack_per_level: int = 2,
        defense_per_level: int = 1,
    ) -> list[str]:
        messages: list[str] = []
        self.experience += amount
        while self.experience >= self.experience_to_next_level():
            self.level += 1
            self.max_hp += hp_per_level
            self.max_mp += mp_per_level
            self.base_attack += attack_per_level
            self.base_defense += defense_per_level
            self.hp = self.max_hp
            self.mp = self.max_mp
            messages.append(
                f"You reached level {self.level}. Your strength and reserves surge back to full."
            )
        return messages

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "player_class": self.player_class,
            "level": self.level,
            "experience": self.experience,
            "gold": self.gold,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_mp": self.max_mp,
            "mp": self.mp,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "wallet": self.wallet,
            "world_states": {
                world_id: progress.to_dict() for world_id, progress in self.world_states.items()
            },
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "Player":
        return cls(
            name=str(payload["name"]),
            player_class=str(payload["player_class"]),
            level=int(payload["level"]),
            experience=int(payload["experience"]),
            gold=int(payload["gold"]),
            max_hp=int(payload["max_hp"]),
            hp=int(payload["hp"]),
            max_mp=int(payload["max_mp"]),
            mp=int(payload["mp"]),
            base_attack=int(payload["base_attack"]),
            base_defense=int(payload["base_defense"]),
            world_states={
                str(world_id): WorldProgress.from_dict(progress)
                for world_id, progress in dict(payload.get("world_states", {})).items()
            },
            wallet={
                str(currency_id): int(amount)
                for currency_id, amount in dict(
                    payload.get("wallet", {"gold": int(payload["gold"])})
                ).items()
            },
        )
