from __future__ import annotations

from collections import Counter
import random

from .types import (
    BOSS_ENEMY_ATTACK_PER_LEVEL,
    BOSS_ENEMY_DEFENSE_PER_LEVEL,
    BOSS_ENEMY_HP_PER_LEVEL,
    HIT_CHANCE_BASE,
    HIT_CHANCE_MAX,
    HIT_CHANCE_MIN,
    HIT_SCORE_STEP,
    RESPAWN_ROLL_SIDES,
    STANDARD_ENEMY_ATTACK_PER_LEVEL,
    STANDARD_ENEMY_DEFENSE_PER_LEVEL,
    STANDARD_ENEMY_HP_PER_LEVEL,
)
from ..models import EnemyState


class EngineRoomStateMixin:
    def _current_room(self):
        return self.world.rooms[self.progress.current_room]

    def _has_story_flag(self, flag: str | None) -> bool:
        if flag is None:
            return True
        return flag in self.progress.story_flags

    def _set_story_flags(self, flags: list[str]) -> list[str]:
        added_flags: list[str] = []
        for flag in flags:
            if flag not in self.progress.story_flags:
                self.progress.story_flags.append(flag)
                added_flags.append(flag)
        return added_flags

    def _available_exits(self, room=None) -> dict[str, str]:
        room = room or self._current_room()
        exits = dict(room.exits)
        for direction, hidden_exit in room.hidden_exits.items():
            if self._has_story_flag(hidden_exit.required_flag):
                exits[direction] = hidden_exit.target_room
        return exits

    def _visible_room_interactions(self, room=None):
        room = room or self._current_room()
        return {
            interaction_id: interaction
            for interaction_id, interaction in room.interactions.items()
            if self._has_story_flag(interaction.required_flag)
        }

    def _match_room_interaction(self, query: str) -> str | None:
        return self._match_from_names(
            query,
            {
                interaction_id: interaction.name
                for interaction_id, interaction in self._visible_room_interactions().items()
            },
        )

    def _room_items(self) -> list[str]:
        return self.progress.room_items.setdefault(self.progress.current_room, [])

    def _room_enemies(self) -> list[EnemyState]:
        return self._scaled_room_enemies(self.progress.current_room)

    def _has_active_threats(self) -> bool:
        return bool(self._room_enemies())

    def _enemy_level_gap(self, enemy) -> int:
        return max(0, self.player.level - enemy.level)

    def _enemy_scaling_rates(self, enemy) -> tuple[int, int, int]:
        if enemy.respawns:
            return (
                STANDARD_ENEMY_HP_PER_LEVEL,
                STANDARD_ENEMY_ATTACK_PER_LEVEL,
                STANDARD_ENEMY_DEFENSE_PER_LEVEL,
            )
        return (
            BOSS_ENEMY_HP_PER_LEVEL,
            BOSS_ENEMY_ATTACK_PER_LEVEL,
            BOSS_ENEMY_DEFENSE_PER_LEVEL,
        )

    def _enemy_max_hp(self, enemy) -> int:
        hp_per_level, _, _ = self._enemy_scaling_rates(enemy)
        return enemy.max_hp + (self._enemy_level_gap(enemy) * hp_per_level)

    def _enemy_attack_score(self, enemy) -> int:
        _, attack_per_level, _ = self._enemy_scaling_rates(enemy)
        return enemy.attack + (self._enemy_level_gap(enemy) * attack_per_level)

    def _enemy_defense_score(self, enemy) -> int:
        _, _, defense_per_level = self._enemy_scaling_rates(enemy)
        return enemy.defense + (self._enemy_level_gap(enemy) * defense_per_level)

    def _enemy_level_score(self, enemy) -> int:
        return max(enemy.level, self.player.level)

    def _scaled_room_enemies(self, room_id: str) -> list[EnemyState]:
        room_enemies = self.progress.room_enemies.setdefault(room_id, [])
        for state in room_enemies:
            self._ensure_enemy_state_scaled(state)
        return room_enemies

    def _ensure_enemy_state_scaled(self, state: EnemyState) -> None:
        enemy = self.world.enemies[state.enemy_id]
        scaled_max_hp = self._enemy_max_hp(enemy)
        old_max_hp = state.max_hp or enemy.max_hp
        if state.max_hp == scaled_max_hp and state.scaled_level == self.player.level:
            return

        if state.current_hp >= old_max_hp:
            state.current_hp = scaled_max_hp
        else:
            state.current_hp = max(
                1,
                (state.current_hp * scaled_max_hp + old_max_hp - 1) // old_max_hp,
            )
        state.max_hp = scaled_max_hp
        state.scaled_level = self.player.level

    def _spawn_enemy_state(self, enemy_id: str) -> EnemyState:
        enemy = self.world.enemies[enemy_id]
        max_hp = self._enemy_max_hp(enemy)
        return EnemyState(
            enemy_id=enemy_id,
            current_hp=max_hp,
            max_hp=max_hp,
            scaled_level=self.player.level,
        )

    def _choose_enemy_from_pool(self, pool_id: str) -> str:
        pool = self.world.monster_pools[pool_id]
        total_weight = sum(entry.weight for entry in pool.entries)
        roll = random.randint(1, total_weight)
        running_total = 0
        for entry in pool.entries:
            running_total += entry.weight
            if roll <= running_total:
                return entry.enemy_id
        return pool.entries[-1].enemy_id

    def _initial_enemy_states_for_room(self, room) -> list[EnemyState]:
        if room.monster_pool_id:
            return [
                self._spawn_enemy_state(self._choose_enemy_from_pool(room.monster_pool_id))
                for _ in range(room.monster_count)
            ]
        return [self._spawn_enemy_state(enemy_id) for enemy_id in room.enemy_ids]

    def _hit_chance(self, attacker_score: int, defender_score: int) -> int:
        chance = HIT_CHANCE_BASE + ((attacker_score - defender_score) * HIT_SCORE_STEP)
        return max(HIT_CHANCE_MIN, min(HIT_CHANCE_MAX, chance))

    def _hit_lands(self, attacker_score: int, defender_score: int) -> bool:
        return random.randint(1, 100) <= self._hit_chance(attacker_score, defender_score)

    def _entry_block_message(self, room_id: str) -> str | None:
        room = self.world.rooms[room_id]
        if room_id in self.progress.sealed_rooms:
            return room.sealed_message or f"{room.name} has sealed shut behind you. There is no way back."
        if room.required_item and self.progress.inventory.get(room.required_item, 0) <= 0:
            if room.locked_message:
                return room.locked_message
            required_item_name = self.world.items[room.required_item].name
            return f"{room.name} is locked. You need {required_item_name}."
        return None

    def _seal_room_on_departure(self, room_id: str, target_room_id: str | None = None) -> list[str]:
        room = self.world.rooms[room_id]
        if not room.locks_on_exit or room_id in self.progress.sealed_rooms:
            return []
        if (
            target_room_id is not None
            and self.progress.previous_room is not None
            and target_room_id == self.progress.previous_room
        ):
            return []
        self.progress.sealed_rooms.append(room_id)
        return [f"With a final echo, {room.name} seals behind you."]

    def _respawn_enemies_for_room(self, room_id: str) -> list[str]:
        room = self.world.rooms[room_id]
        room_enemies = self._scaled_room_enemies(room_id)
        present_counts = Counter(state.enemy_id for state in room_enemies)
        respawned: list[str] = []

        if room.monster_pool_id:
            respawned.extend(self._respawn_missing_pool_enemies(room, room_enemies, present_counts))
        else:
            respawned.extend(self._respawn_missing_static_enemies(room, room_enemies, present_counts))

        if self.progress.faction_id:
            respawned.extend(self._respawn_faction_enemies(room, room_enemies, present_counts))

        return respawned

    def _respawn_missing_pool_enemies(self, room, room_enemies, present_counts: Counter[str]) -> list[str]:
        pool_enemy_ids = {
            entry.enemy_id for entry in self.world.monster_pools[room.monster_pool_id].entries
        }
        present_pool_count = sum(
            count for enemy_id, count in present_counts.items() if enemy_id in pool_enemy_ids
        )
        missing_count = max(0, room.monster_count - present_pool_count)
        respawned: list[str] = []

        for _ in range(missing_count):
            if random.randint(1, RESPAWN_ROLL_SIDES) != 1:
                continue
            enemy_id = self._choose_enemy_from_pool(room.monster_pool_id)
            enemy = self.world.enemies[enemy_id]
            if not enemy.respawns:
                continue
            self._append_respawned_enemy(room_enemies, present_counts, respawned, enemy_id)

        return respawned

    def _respawn_missing_static_enemies(self, room, room_enemies, present_counts: Counter[str]) -> list[str]:
        respawned: list[str] = []
        desired_counts = Counter(room.enemy_ids)
        for enemy_id, desired_count in desired_counts.items():
            enemy = self.world.enemies[enemy_id]
            if not enemy.respawns:
                continue

            missing_count = max(0, desired_count - present_counts.get(enemy_id, 0))
            for _ in range(missing_count):
                if random.randint(1, RESPAWN_ROLL_SIDES) == 1:
                    self._append_respawned_enemy(room_enemies, present_counts, respawned, enemy_id)
        return respawned

    def _respawn_faction_enemies(self, room, room_enemies, present_counts: Counter[str]) -> list[str]:
        respawned: list[str] = []
        for faction_spawn in room.faction_enemy_spawns:
            if faction_spawn.faction_id != self.progress.faction_id:
                continue
            enemy = self.world.enemies[faction_spawn.enemy_id]
            if not enemy.respawns:
                continue
            missing_count = max(
                0,
                faction_spawn.count - present_counts.get(faction_spawn.enemy_id, 0),
            )
            for _ in range(missing_count):
                if random.randint(1, RESPAWN_ROLL_SIDES) == 1:
                    self._append_respawned_enemy(
                        room_enemies,
                        present_counts,
                        respawned,
                        faction_spawn.enemy_id,
                    )
        return respawned

    def _append_respawned_enemy(
        self,
        room_enemies: list[EnemyState],
        present_counts: Counter[str],
        respawned: list[str],
        enemy_id: str,
    ) -> None:
        room_enemies.append(self._spawn_enemy_state(enemy_id))
        present_counts[enemy_id] += 1
        respawned.append(self.world.enemies[enemy_id].name)

    def _respawn_mining_items_for_room(self, room_id: str) -> list[str]:
        room = self.world.rooms[room_id]
        if not room.mining_drops:
            return []

        room_items = self.progress.room_items.setdefault(room_id, [])
        mining_item_ids = {drop.item_id for drop in room.mining_drops}
        if any(item_id in mining_item_ids for item_id in room_items):
            return []
        if random.randint(1, RESPAWN_ROLL_SIDES) != 1:
            return []

        spawned_counts: Counter[str] = Counter()
        for drop in room.mining_drops:
            amount = random.randint(drop.min_quantity, drop.max_quantity)
            room_items.extend([drop.item_id] * amount)
            spawned_counts[drop.item_id] += amount

        return [
            f"{self.world.items[item_id].name} x{amount}"
            if amount > 1
            else self.world.items[item_id].name
            for item_id, amount in spawned_counts.items()
        ]

    def _mining_spawn_message(self, room_id: str, spawned_items: list[str]) -> str:
        room = self.world.rooms[room_id]
        item_text = ", ".join(spawned_items)
        if room.mining_message:
            return f"{room.mining_message} Found: {item_text}."
        return f"You uncover fresh resources: {item_text}."

    def _visible_item_pool(self) -> dict[str, str]:
        item_ids: set[str] = set(self.progress.inventory)
        item_ids.update(self._room_items())
        if self._current_room().has_storage:
            item_ids.update(self.progress.storage)
        for vendor_id in self._current_room().vendor_ids:
            item_ids.update(self.world.vendors[vendor_id].stock)
        return {item_id: self.world.items[item_id].name for item_id in item_ids}
