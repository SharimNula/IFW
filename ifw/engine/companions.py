from __future__ import annotations

import random

from .types import MAX_COMPANIONS
from ..models import CompanionState, EnemyState


class EngineCompanionMixin:
    def _active_companion_ids(self) -> set[str]:
        return {companion.npc_id for companion in self.progress.companions}

    def _room_npc_ids(self, room=None) -> list[str]:
        room = room or self._current_room()
        active_companion_ids = self._active_companion_ids()
        return [npc_id for npc_id in room.npc_ids if npc_id not in active_companion_ids]

    def _match_active_companion(self, query: str) -> CompanionState | None:
        companion_id = self._match_from_names(
            query,
            {
                companion.npc_id: self.world.npcs[companion.npc_id].name
                for companion in self.progress.companions
                if companion.npc_id in self.world.npcs
            },
        )
        if companion_id is None:
            return None
        return next(
            companion
            for companion in self.progress.companions
            if companion.npc_id == companion_id
        )

    def _companion_name(self, companion: CompanionState) -> str:
        return self.world.npcs[companion.npc_id].name

    def _learn_companion_spell(self, companion: CompanionState, spell_id: str) -> bool:
        if spell_id not in self.world.spells:
            raise ValueError(f"Unknown spell '{spell_id}'.")
        spell = self.world.spells[spell_id]
        if not self._spell_allowed_for_class(spell_id, companion.class_id):
            raise ValueError(self._spell_restriction_message(spell, "learned"))
        if spell_id in companion.spell_ids:
            return False
        companion.spell_ids.append(spell_id)
        return True

    def _companion_class_definition(self, companion: CompanionState):
        return self.world.player_classes[companion.class_id]

    def _starter_items_for_class(self, class_id: str) -> list[str]:
        starter_items = list(self.world.starter_items.get("all", []))
        starter_items.extend(self.world.starter_items.get(class_id.lower(), []))
        return starter_items

    def _starter_spells_for_class(self, class_id: str) -> list[str]:
        starter_spells = list(self.world.starter_spells.get("all", []))
        starter_spells.extend(self.world.starter_spells.get(class_id.lower(), []))
        return [
            spell_id
            for spell_id in starter_spells
            if spell_id in self.world.spells and self._spell_allowed_for_class(spell_id, class_id)
        ]

    def _create_companion_state(self, npc_id: str, origin_room: str) -> CompanionState:
        npc = self.world.npcs[npc_id]
        class_id = (npc.companion_class or "").lower()
        starter_items = self._starter_items_for_class(class_id)
        companion = CompanionState(
            npc_id=npc_id,
            class_id=class_id,
            origin_room=origin_room,
            current_hp=0,
            current_mp=0,
            weapon_id=self._first_starter_item_of_type(starter_items, "weapon"),
            armor_id=self._first_starter_item_of_type(starter_items, "armor"),
            spell_ids=self._starter_spells_for_class(class_id),
        )
        companion.current_hp = self._companion_max_hp(companion)
        companion.current_mp = self._companion_max_mp(companion)
        return companion

    def _sanitize_companion_states(self, progress) -> list[str]:
        kept_companions: list[CompanionState] = []
        removed_names: list[str] = []
        for companion in progress.companions:
            npc = self.world.npcs.get(companion.npc_id)
            if npc is None or not npc.can_recruit:
                removed_names.append(companion.npc_id)
                continue
            companion.class_id = companion.class_id.lower()
            if companion.class_id not in self.world.player_classes:
                companion.class_id = (npc.companion_class or "").lower()
            if companion.class_id not in self.world.player_classes:
                removed_names.append(npc.name)
                continue
            if companion.origin_room not in self.world.rooms:
                companion.origin_room = self.world.start_room
            companion.spell_ids = [
                spell_id
                for spell_id in companion.spell_ids
                if spell_id in self.world.spells
                and self._spell_allowed_for_class(spell_id, companion.class_id)
            ]
            for spell_id in self._starter_spells_for_class(companion.class_id):
                if spell_id not in companion.spell_ids:
                    companion.spell_ids.append(spell_id)
            if not self._companion_item_is_valid(companion.weapon_id, "weapon"):
                companion.weapon_id = self._first_starter_item_of_type(
                    self._starter_items_for_class(companion.class_id),
                    "weapon",
                )
            if not self._companion_item_is_valid(companion.armor_id, "armor"):
                companion.armor_id = self._first_starter_item_of_type(
                    self._starter_items_for_class(companion.class_id),
                    "armor",
                )
            self._sync_companion_resources(companion)
            kept_companions.append(companion)

        progress.companions = kept_companions[:MAX_COMPANIONS]
        if removed_names:
            return ["Companion records removed: " + ", ".join(removed_names) + "."]
        return []

    def _companion_item_is_valid(self, item_id: str | None, item_type: str) -> bool:
        if item_id is None or item_id not in self.world.items:
            return False
        item = self.world.items[item_id]
        return item.item_type == item_type and item.required_level <= self.player.level

    def _companion_equipment_hp_bonus(self, companion: CompanionState) -> int:
        total = 0
        if companion.weapon_id:
            total += self._effective_item_bonus(companion.weapon_id, "hp_bonus")
        if companion.armor_id:
            total += self._effective_item_bonus(companion.armor_id, "hp_bonus")
        return total

    def _companion_equipment_mp_bonus(self, companion: CompanionState) -> int:
        total = 0
        if companion.weapon_id:
            total += self._effective_item_bonus(companion.weapon_id, "mp_bonus")
        if companion.armor_id:
            total += self._effective_item_bonus(companion.armor_id, "mp_bonus")
        return total

    def _companion_max_hp(self, companion: CompanionState) -> int:
        player_class = self._companion_class_definition(companion)
        level_gap = max(0, self.player.level - 1)
        return (
            player_class.max_hp
            + (level_gap * player_class.hp_per_level)
            + self._companion_equipment_hp_bonus(companion)
        )

    def _companion_max_mp(self, companion: CompanionState) -> int:
        player_class = self._companion_class_definition(companion)
        level_gap = max(0, self.player.level - 1)
        return (
            player_class.max_mp
            + (level_gap * player_class.mp_per_level)
            + self._companion_equipment_mp_bonus(companion)
        )

    def _sync_companion_resources(
        self,
        companion: CompanionState,
        previous_max_hp: int | None = None,
        previous_max_mp: int | None = None,
    ) -> None:
        max_hp = self._companion_max_hp(companion)
        max_mp = self._companion_max_mp(companion)
        if previous_max_hp is not None and companion.current_hp >= previous_max_hp:
            companion.current_hp = max_hp
        else:
            companion.current_hp = max(0, min(companion.current_hp, max_hp))
        if previous_max_mp is not None and companion.current_mp >= previous_max_mp:
            companion.current_mp = max_mp
        else:
            companion.current_mp = max(0, min(companion.current_mp, max_mp))

    def _sync_all_companion_resources(self) -> None:
        for companion in self.progress.companions:
            self._sync_companion_resources(companion)

    def _companion_attack_score(self, companion: CompanionState) -> int:
        player_class = self._companion_class_definition(companion)
        level_gap = max(0, self.player.level - 1)
        weapon_bonus = (
            self._effective_item_bonus(companion.weapon_id, "attack_bonus")
            if companion.weapon_id
            else 0
        )
        return (
            player_class.base_attack
            + (level_gap * player_class.attack_per_level)
            + weapon_bonus
            + self._buffed_attack_bonus(companion.npc_id)
            + self.player.level
        )

    def _companion_defense_score(self, companion: CompanionState) -> int:
        player_class = self._companion_class_definition(companion)
        level_gap = max(0, self.player.level - 1)
        armor_bonus = (
            self._effective_item_bonus(companion.armor_id, "defense_bonus")
            if companion.armor_id
            else 0
        )
        return (
            player_class.base_defense
            + (level_gap * player_class.defense_per_level)
            + armor_bonus
            + self._buffed_defense_bonus(companion.npc_id)
            + self.player.level // 2
        )

    def _companion_recruitment_item_lines(self, npc) -> tuple[bool, list[str]]:
        required_item_id = npc.recruit_required_item
        if not required_item_id:
            return True, []

        item = self.world.items[required_item_id]
        if self.progress.inventory.get(required_item_id, 0) <= 0:
            if npc.recruit_missing_item_text:
                return False, [npc.recruit_missing_item_text]
            return False, [f"{npc.name} will not join you without {item.name}."]

        if npc.consume_recruit_item:
            self.progress.remove_item(required_item_id)
            return True, [f"You give {item.name} to {npc.name}."]
        return True, [f"You show {item.name} to {npc.name}."]

    def _recruit_companion(self, query: str) -> list[str]:
        if not query:
            return ["Recruit whom?"]
        if self._has_active_threats():
            return ["You cannot recruit companions while threats are active in the room."]
        if len(self.progress.companions) >= MAX_COMPANIONS:
            return [f"You can travel with at most {MAX_COMPANIONS} companions."]

        room = self._current_room()
        npc_id = self._match_from_names(
            query,
            {npc_id: self.world.npcs[npc_id].name for npc_id in self._room_npc_ids(room)},
        )
        if npc_id is None:
            if self._match_active_companion(query):
                return ["That companion is already traveling with you."]
            return ["No recruitable person by that name is here."]

        npc = self.world.npcs[npc_id]
        if not npc.can_recruit:
            return [f"{npc.name} cannot be recruited as a companion."]
        if any(companion.npc_id == npc_id for companion in self.progress.companions):
            return ["That companion is already traveling with you."]

        requirement_met, requirement_lines = self._companion_recruitment_item_lines(npc)
        if not requirement_met:
            return requirement_lines

        companion = self._create_companion_state(npc_id, room.room_id)
        self.progress.companions.append(companion)
        lines = requirement_lines + [
            f"{npc.name} joins your party as a {self._class_label(companion.class_id)}.",
            (
                f"{npc.name} is ready with "
                f"HP {companion.current_hp}/{self._companion_max_hp(companion)} and "
                f"MP {companion.current_mp}/{self._companion_max_mp(companion)}."
            ),
        ]
        if companion.weapon_id or companion.armor_id:
            gear = [
                self.world.items[item_id].name
                for item_id in (companion.weapon_id, companion.armor_id)
                if item_id
            ]
            lines.append("Starter gear: " + ", ".join(gear) + ".")
        if companion.spell_ids:
            lines.append(
                "Starter spells: "
                + ", ".join(self.world.spells[spell_id].name for spell_id in companion.spell_ids)
                + "."
            )
        return lines

    def _dismiss_companion(self, query: str) -> list[str]:
        if not query:
            return ["Dismiss whom?"]
        companion = self._match_active_companion(query)
        if companion is None:
            return ["That companion is not traveling with you."]
        self.progress.companions.remove(companion)
        origin_name = self.world.rooms[companion.origin_room].name
        return [f"{self._companion_name(companion)} leaves your party and returns to {origin_name}."]

    def _show_companions(self) -> list[str]:
        lines = [f"Companions ({len(self.progress.companions)}/{MAX_COMPANIONS}):"]
        if not self.progress.companions:
            lines.append("  None")
            return lines
        for companion in self.progress.companions:
            weapon = self.world.items[companion.weapon_id].name if companion.weapon_id else "None"
            armor = self.world.items[companion.armor_id].name if companion.armor_id else "None"
            spells = (
                ", ".join(self.world.spells[spell_id].name for spell_id in companion.spell_ids)
                if companion.spell_ids
                else "None"
            )
            lines.append(
                f"  {self._companion_name(companion)} the {self._class_label(companion.class_id)}: "
                f"HP {companion.current_hp}/{self._companion_max_hp(companion)}  "
                f"MP {companion.current_mp}/{self._companion_max_mp(companion)}"
            )
            lines.append(f"    Weapon: {weapon}; Armor: {armor}; Spells: {spells}")
        return lines

    def _split_companion_equip_query(self, query: str) -> tuple[str, str] | None:
        lower_query = query.lower()
        if " with " in lower_query:
            split_at = lower_query.index(" with ")
            return query[split_at + len(" with "):].strip(), query[:split_at].strip()
        for delimiter in (" to ", " on ", " for "):
            if delimiter in lower_query:
                split_at = lower_query.index(delimiter)
                return query[:split_at].strip(), query[split_at + len(delimiter):].strip()
        return None

    def _equip_companion_item(self, item_query: str, companion_query: str) -> list[str]:
        companion = self._match_active_companion(companion_query)
        if companion is None:
            return ["That companion is not traveling with you."]
        item_id = self._require_item_match(item_query, self.progress.inventory)
        item = self.world.items[item_id]
        if item.item_type not in {"weapon", "armor"}:
            return ["Companions can only equip weapons and armor."]
        if item.required_level > self.player.level:
            return [
                f"{item.name} requires level {item.required_level}. "
                f"Your party is level {self.player.level}."
            ]

        previous_max_hp = self._companion_max_hp(companion)
        previous_max_mp = self._companion_max_mp(companion)
        if item.item_type == "weapon":
            companion.weapon_id = item_id
            slot_name = "weapon"
        else:
            companion.armor_id = item_id
            slot_name = "armor"
        self._sync_companion_resources(companion, previous_max_hp, previous_max_mp)
        return [f"{self._companion_name(companion)} equips {item.name} as {slot_name}."]

    def _living_companions(self) -> list[CompanionState]:
        return [companion for companion in self.progress.companions if companion.current_hp > 0]

    def _companion_turn(self) -> list[str]:
        companions = self._living_companions()
        if not companions or not self._room_enemies():
            return []
        lines = ["Companions act:"]
        for companion in companions:
            if not self._room_enemies():
                break
            lines.extend(self._companion_take_action(companion))
        return lines

    def _companion_take_action(self, companion: CompanionState) -> list[str]:
        healing_spell = self._best_companion_healing_spell(companion)
        if healing_spell is not None:
            return self._companion_cast_healing_spell(companion, healing_spell)
        offense_spell = self._best_companion_offense_spell(companion)
        if offense_spell is not None:
            return self._companion_cast_offense_spell(companion, offense_spell)
        return self._companion_attack(companion)

    def _best_companion_healing_spell(self, companion: CompanionState) -> str | None:
        if companion.current_hp > self._companion_max_hp(companion) // 2:
            return None
        for spell_id in companion.spell_ids:
            spell = self.world.spells[spell_id]
            if spell.school in {"healing", "heal"} and companion.current_mp >= spell.mp_cost:
                return spell_id
        return None

    def _best_companion_offense_spell(self, companion: CompanionState) -> str | None:
        for spell_id in companion.spell_ids:
            spell = self.world.spells[spell_id]
            if spell.school == "offense" and companion.current_mp >= spell.mp_cost:
                return spell_id
        return None

    def _companion_cast_healing_spell(self, companion: CompanionState, spell_id: str) -> list[str]:
        spell = self.world.spells[spell_id]
        companion.current_mp -= spell.mp_cost
        restored_hp = min(spell.power, self._companion_max_hp(companion) - companion.current_hp)
        companion.current_hp += restored_hp
        return [f"  {self._companion_name(companion)} casts {spell.name} and restores {restored_hp} HP."]

    def _companion_cast_offense_spell(self, companion: CompanionState, spell_id: str) -> list[str]:
        spell = self.world.spells[spell_id]
        target_state = self._room_enemies()[0]
        enemy = self.world.enemies[target_state.enemy_id]
        companion.current_mp -= spell.mp_cost
        spell_attack_score = spell.power + (self.player.level * 2)
        enemy_defense = self._enemy_defense_score(enemy)
        if not self._hit_lands(spell_attack_score, enemy_defense + self._enemy_level_score(enemy)):
            return [f"  {self._companion_name(companion)} casts {spell.name}, but it misses {enemy.name}."]
        damage = max(
            1,
            spell.power + (self.player.level * 2) + random.randint(0, 3) - enemy_defense // 2,
        )
        target_state.current_hp -= damage
        lines = [
            f"  {self._companion_name(companion)} casts {spell.name} on {enemy.name} "
            f"for {damage} damage."
        ]
        lines.extend(self._companion_enemy_result(target_state))
        return lines

    def _companion_attack(self, companion: CompanionState) -> list[str]:
        target_state = self._room_enemies()[0]
        enemy = self.world.enemies[target_state.enemy_id]
        enemy_defense = self._enemy_defense_score(enemy)
        if not self._hit_lands(
            self._companion_attack_score(companion),
            enemy_defense + self._enemy_level_score(enemy),
        ):
            lines = [f"  {self._companion_name(companion)} misses {enemy.name}."]
            self._tick_buffs(lines, tick_on="player_attack", target_id=companion.npc_id)
            return lines
        damage = max(
            1,
            self._companion_attack_score(companion) + random.randint(-2, 2) - enemy_defense,
        )
        target_state.current_hp -= damage
        lines = [f"  {self._companion_name(companion)} attacks {enemy.name} for {damage} damage."]
        lines.extend(self._companion_enemy_result(target_state))
        self._tick_buffs(lines, tick_on="player_attack", target_id=companion.npc_id)
        return lines

    def _companion_enemy_result(self, state: EnemyState) -> list[str]:
        enemy = self.world.enemies[state.enemy_id]
        if state.current_hp <= 0:
            return self._defeat_enemy(state)
        return [f"{enemy.name} has {state.current_hp} HP left."]

    def _companions_at_full_resources(self) -> bool:
        return all(
            companion.current_hp == self._companion_max_hp(companion)
            and companion.current_mp == self._companion_max_mp(companion)
            for companion in self.progress.companions
        )

    def _restore_companions(self) -> tuple[int, int]:
        restored_hp = 0
        restored_mp = 0
        for companion in self.progress.companions:
            max_hp = self._companion_max_hp(companion)
            max_mp = self._companion_max_mp(companion)
            restored_hp += max_hp - companion.current_hp
            restored_mp += max_mp - companion.current_mp
            companion.current_hp = max_hp
            companion.current_mp = max_mp
        return restored_hp, restored_mp
