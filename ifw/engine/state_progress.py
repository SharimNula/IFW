from __future__ import annotations

from ..models import WorldProgress


class EngineProgressStateMixin:
    def _prepare_world_progress(self) -> tuple[WorldProgress, list[str]]:
        welcome_lines: list[str] = []
        progress = self.player.world_states.get(self.world.world_id)
        first_visit = progress is None
        if progress is None:
            progress = WorldProgress(
                current_room=self.world.start_room,
                room_items={
                    room_id: list(room.item_ids) for room_id, room in self.world.rooms.items()
                },
                room_enemies={
                    room_id: self._initial_enemy_states_for_room(room)
                    for room_id, room in self.world.rooms.items()
                },
            )
            self.player.world_states[self.world.world_id] = progress

        # Initialization helpers use normal engine state accessors, including charged equipment.
        self.progress = progress

        if progress.current_room not in self.world.rooms:
            progress.current_room = self.world.start_room

        welcome_lines.extend(self._sanitize_companion_states(progress))

        if first_visit:
            starter_items = self._starter_items_for_player()
            starter_spells = self._starter_spells_for_player()
            self._grant_starter_items(progress, starter_items)
            self._grant_starter_spells(progress, starter_spells)
            welcome_lines.extend(self._starter_welcome_lines(starter_items, starter_spells))
            self._equip_first_starter_weapon_and_armor(progress, starter_items)

        progress.learned_spells = [
            spell_id
            for spell_id in progress.learned_spells
            if spell_id in self.world.spells and self._spell_allowed_for_player(spell_id)
        ]
        progress.unlocked_recipes = [
            recipe_id for recipe_id in progress.unlocked_recipes if recipe_id in self.world.recipes
        ]
        welcome_lines.extend(self._unequip_items_above_player_level(progress))
        return progress, welcome_lines

    def _starter_items_for_player(self) -> list[str]:
        starter_items = list(self.world.starter_items.get("all", []))
        starter_items.extend(self.world.starter_items.get(self.player.player_class.lower(), []))
        return starter_items

    def _starter_spells_for_player(self) -> list[str]:
        starter_spells = list(self.world.starter_spells.get("all", []))
        starter_spells.extend(self.world.starter_spells.get(self.player.player_class.lower(), []))
        return [spell_id for spell_id in starter_spells if self._spell_allowed_for_player(spell_id)]

    def _grant_starter_items(self, progress: WorldProgress, starter_items: list[str]) -> None:
        for item_id in starter_items:
            progress.add_item(item_id)

    def _grant_starter_spells(self, progress: WorldProgress, starter_spells: list[str]) -> None:
        for spell_id in starter_spells:
            if spell_id not in progress.learned_spells:
                progress.learned_spells.append(spell_id)

    def _starter_welcome_lines(self, starter_items: list[str], starter_spells: list[str]) -> list[str]:
        lines = ["A new world journal has been opened for this character."]
        if starter_items:
            lines.append(
                "Starter gear: "
                + ", ".join(self.world.items[item_id].name for item_id in starter_items)
            )
        if starter_spells:
            lines.append(
                "Starter spells: "
                + ", ".join(self.world.spells[spell_id].name for spell_id in starter_spells)
            )
        return lines

    def _equip_first_starter_weapon_and_armor(
        self, progress: WorldProgress, starter_items: list[str]
    ) -> None:
        if progress.weapon_id is None:
            progress.weapon_id = self._first_starter_item_of_type(starter_items, "weapon")
        if progress.armor_id is None:
            progress.armor_id = self._first_starter_item_of_type(starter_items, "armor")

    def _first_starter_item_of_type(self, starter_items: list[str], item_type: str) -> str | None:
        for item_id in starter_items:
            if self.world.items[item_id].item_type == item_type:
                return item_id
        return None

    def _unequip_items_above_player_level(self, progress: WorldProgress) -> list[str]:
        removed: list[str] = []
        if progress.weapon_id and not self._player_meets_item_level_requirement(progress.weapon_id):
            removed.append(self.world.items[progress.weapon_id].name)
            progress.weapon_id = None
        if progress.armor_id and not self._player_meets_item_level_requirement(progress.armor_id):
            removed.append(self.world.items[progress.armor_id].name)
            progress.armor_id = None

        kept_accessories: list[str] = []
        for item_id in progress.accessory_ids:
            if self._player_meets_item_level_requirement(item_id):
                kept_accessories.append(item_id)
            else:
                removed.append(self.world.items[item_id].name)
        progress.accessory_ids = kept_accessories

        if not removed:
            return []
        return ["Unequipped items above your level: " + ", ".join(removed) + "."]

    def _player_meets_item_level_requirement(self, item_id: str) -> bool:
        item = self.world.items[item_id]
        return item.required_level <= self.player.level
