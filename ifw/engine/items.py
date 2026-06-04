from __future__ import annotations

from collections import Counter

from .types import MAX_ACCESSORIES
from ..models import Recipe


class EngineItemMixin:
    def _require_item_match(self, query: str, pool: dict[str, int]) -> str:
        item_id = self._match_from_names(query, {candidate: self.world.items[candidate].name for candidate in pool})
        if item_id is None:
            raise ValueError("That item is not available.")
        return item_id

    def _take_item(self, query: str) -> list[str]:
        if not query:
            return ["Take what?"]
        if self._has_active_threats():
            return ["You cannot grab items while threats are active in the room."]
        room_items = self._room_items()
        if query.lower() in {"all", "everything"}:
            if not room_items:
                return ["There is nothing here to take."]
            taken_items = list(room_items)
            room_items.clear()
            for item_id in taken_items:
                self.progress.add_item(item_id)
            item_names = ", ".join(self.world.items[item_id].name for item_id in taken_items)
            lines = [f"You take everything: {item_names}."]
            lines.extend(self._check_quest_completion())
            return lines
        item_id = self._match_from_names(
            query, {candidate: self.world.items[candidate].name for candidate in room_items}
        )
        if item_id is None:
            return ["That item is not in this room."]
        room_items.remove(item_id)
        self.progress.add_item(item_id)
        lines = [f"You take the {self.world.items[item_id].name}."]
        lines.extend(self._check_quest_completion())
        return lines

    def _drop_item(self, query: str) -> list[str]:
        if not query:
            return ["Drop what?"]
        item_id = self._require_item_match(query, self.progress.inventory)
        self.progress.remove_item(item_id)
        self._room_items().append(item_id)
        return [f"You drop the {self.world.items[item_id].name}."]

    def _equip_item(self, query: str) -> list[str]:
        if not query:
            return ["Equip what?"]
        companion_equip = self._split_companion_equip_query(query)
        if companion_equip is not None:
            item_query, companion_query = companion_equip
            return self._equip_companion_item(item_query, companion_query)
        item_id = self._require_item_match(query, self.progress.inventory)
        item = self.world.items[item_id]
        if item.item_type in {"weapon", "armor", "accessory"} and not self._player_meets_item_level_requirement(item_id):
            return [
                f"{item.name} requires level {item.required_level}. "
                f"You are level {self.player.level}."
            ]
        previous_max_hp = self._player_max_hp()
        previous_max_mp = self._player_max_mp()
        if item.item_type == "weapon":
            self.progress.weapon_id = item_id
            self._sync_resources_to_effective_max(previous_max_hp, previous_max_mp)
            return [f"You equip {item.name} as your weapon."]
        if item.item_type == "armor":
            self.progress.armor_id = item_id
            self._sync_resources_to_effective_max(previous_max_hp, previous_max_mp)
            return [f"You equip {item.name} as your armor."]
        if item.item_type == "accessory":
            if len(self.progress.accessory_ids) >= MAX_ACCESSORIES:
                return [f"You can equip at most {MAX_ACCESSORIES} accessories."]
            if self.progress.accessory_ids.count(item_id) >= self.progress.inventory.get(item_id, 0):
                return [f"All copies of {item.name} are already equipped."]
            self.progress.accessory_ids.append(item_id)
            self._sync_resources_to_effective_max(previous_max_hp, previous_max_mp)
            return [
                f"You equip {item.name} as an accessory "
                f"({len(self.progress.accessory_ids)}/{MAX_ACCESSORIES})."
            ]
        return ["Only weapons, armor, and accessories can be equipped."]

    def _unequip_item(self, query: str) -> list[str]:
        slot = query.lower()
        previous_max_hp = self._player_max_hp()
        previous_max_mp = self._player_max_mp()
        if slot == "weapon":
            self.progress.weapon_id = None
            self._sync_resources_to_effective_max(previous_max_hp, previous_max_mp)
            return ["Weapon slot cleared."]
        if slot == "armor":
            self.progress.armor_id = None
            self._sync_resources_to_effective_max(previous_max_hp, previous_max_mp)
            return ["Armor slot cleared."]
        if slot in {"accessory", "accessories"}:
            if not self.progress.accessory_ids:
                return ["No accessories are equipped."]
            removed = ", ".join(self._equipped_accessory_names())
            self.progress.accessory_ids.clear()
            self._sync_resources_to_effective_max(previous_max_hp, previous_max_mp)
            return [f"Accessory slots cleared: {removed}."]
        accessory_id = self._match_from_names(
            query, {item_id: self.world.items[item_id].name for item_id in self.progress.accessory_ids}
        )
        if accessory_id:
            self.progress.accessory_ids.remove(accessory_id)
            self._sync_resources_to_effective_max(previous_max_hp, previous_max_mp)
            return [f"You remove {self.world.items[accessory_id].name}."]
        return ["Use 'unequip weapon', 'unequip armor', 'unequip accessory', or 'unequip <accessory>'."]

    def _use_item(self, query: str) -> list[str]:
        if not query:
            return ["Use what?"]
        targeted_use = self._split_targeted_use_query(query)
        if targeted_use is not None:
            item_query, target_query = targeted_use
            companion = self._match_active_companion(target_query)
            if companion is not None:
                return self._use_consumable_on_companion(item_query, companion)
            interaction_id = self._match_room_interaction(target_query)
            if interaction_id is not None:
                return self._use_item_on_room_interaction(item_query, interaction_id)
            recruitable_npc_id = self._match_from_names(
                target_query,
                {
                    npc_id: npc.name
                    for npc_id, npc in self.world.npcs.items()
                    if npc.can_recruit
                },
            )
            if recruitable_npc_id is not None:
                return ["That companion is not traveling with you."]
            target_item_id = self._match_recharge_target_item(target_query)
            if target_item_id is not None:
                return self._use_recharge_item_on_item(item_query, target_item_id)
            return ["There is no companion or room object by that name here."]
        item_id = self._require_item_match(query, self.progress.inventory)
        item = self.world.items[item_id]
        if item.item_type == "spellbook":
            if item.teaches_spell is None:
                return ["That spellbook is blank and teaches nothing."]
            spell = self.world.spells[item.teaches_spell]
            if not self._spell_allowed_for_player(item.teaches_spell):
                return [self._spell_restriction_message(spell, "learned")]
            if not self._learn_spell(item.teaches_spell):
                return [f"You already know {spell.name}."]
            self.progress.remove_item(item_id)
            return [
                f"You study {item.name}.",
                f"Spell learned: {spell.name}.",
            ]
        if item.item_type != "consumable" or item.effect is None:
            return ["That item cannot be used directly."]
        only_cures_poison = (
            item.effect.cure_poison
            and not any(
                (
                    item.effect.hp_restore,
                    item.effect.mp_restore,
                    item.effect.attack_bonus,
                    item.effect.defense_bonus,
                    item.effect.recharge_charges,
                )
            )
        )
        if only_cures_poison and not self.progress.player_poisoned:
            return ["You are not poisoned."]
        if self._room_enemies() and not item.effect.cure_poison:
            turn_lines, defeated_by_poison = self._start_player_combat_turn()
            if defeated_by_poison:
                return turn_lines
        else:
            turn_lines = []
        if item.effect.recharge_charges:
            return [f"Use {item.name} on a charged item to recharge it."]
        self.progress.remove_item(item_id)
        healed_hp = min(item.effect.hp_restore, self._player_max_hp() - self.player.hp)
        healed_mp = min(item.effect.mp_restore, self._player_max_mp() - self.player.mp)
        self.player.hp += healed_hp
        self.player.mp += healed_mp
        parts = [f"You use {item.name}."]
        if healed_hp:
            parts.append(f"HP +{healed_hp}")
        if healed_mp:
            parts.append(f"MP +{healed_mp}")
        parts.extend(self._apply_consumable_buffs(item_id, item))
        if item.effect.cure_poison and self.progress.player_poisoned:
            self.progress.player_poisoned = False
            parts.append("Poison cured.")
        return [*turn_lines, " ".join(parts)]

    def _split_targeted_use_query(self, query: str) -> tuple[str, str] | None:
        lower_query = query.lower()
        for delimiter in (" on ", " for "):
            if delimiter in lower_query:
                split_at = lower_query.index(delimiter)
                return query[:split_at].strip(), query[split_at + len(delimiter):].strip()
        return None

    def _match_recharge_target_item(self, query: str) -> str | None:
        inventory_items = {
            item_id: self.world.items[item_id].name
            for item_id in self.progress.inventory
        }
        return self._match_from_names(query, inventory_items)

    def _use_recharge_item_on_item(self, item_query: str, target_item_id: str) -> list[str]:
        item_id = self._require_item_match(item_query, self.progress.inventory)
        item = self.world.items[item_id]
        if item.effect is None or not item.effect.recharge_charges:
            return [f"{item.name} cannot recharge magical items."]
        if self._item_max_charges(target_item_id) <= 0:
            return [f"{self.world.items[target_item_id].name} does not hold magical charges."]
        if self._item_charges(target_item_id) >= self._item_max_charges(target_item_id):
            return [f"{self.world.items[target_item_id].name} is already fully charged."]

        previous_max_hp = self._player_max_hp()
        previous_max_mp = self._player_max_mp()
        companion_maxes = [
            (companion, self._companion_max_hp(companion), self._companion_max_mp(companion))
            for companion in self.progress.companions
            if companion.weapon_id == target_item_id or companion.armor_id == target_item_id
        ]
        self.progress.remove_item(item_id)
        self._recharge_item(target_item_id)
        self._sync_resources_to_effective_max(previous_max_hp, previous_max_mp)
        for companion, previous_max_hp, previous_max_mp in companion_maxes:
            self._sync_companion_resources(companion, previous_max_hp, previous_max_mp)
        return [
            f"You use {item.name} on {self.world.items[target_item_id].name}.",
            f"{self.world.items[target_item_id].name} is fully recharged.",
        ]

    def _use_item_on_room_interaction(self, item_query: str, interaction_id: str) -> list[str]:
        item_id = self._require_item_match(item_query, self.progress.inventory)
        item = self.world.items[item_id]
        interaction = self._current_room().interactions[interaction_id]
        if item.item_type not in {"utility", "misc"} and interaction.required_item != item_id:
            return ["Only matching utility or misc items can be used on room events."]
        return self._interact_with_room_object_using_item(item_id, interaction_id)

    def _use_consumable_on_companion(self, item_query: str, companion) -> list[str]:
        item_id = self._require_item_match(item_query, self.progress.inventory)
        item = self.world.items[item_id]
        if item.item_type != "consumable" or item.effect is None:
            return ["Only consumables can be used on companions."]
        if self._room_enemies() and self.progress.player_poisoned:
            turn_lines, defeated_by_poison = self._start_player_combat_turn(
                skip_poison=item.effect.cure_poison
            )
            if defeated_by_poison:
                return turn_lines
        else:
            turn_lines = []

        self.progress.remove_item(item_id)
        companion_name = self._companion_name(companion)
        missing_hp = max(0, self._companion_max_hp(companion) - companion.current_hp)
        missing_mp = max(0, self._companion_max_mp(companion) - companion.current_mp)
        restored_hp = min(item.effect.hp_restore, missing_hp)
        restored_mp = min(item.effect.mp_restore, missing_mp)
        companion.current_hp += restored_hp
        companion.current_mp += restored_mp
        parts = [f"You use {item.name} on {companion_name}."]
        if restored_hp:
            parts.append(f"{companion_name} HP +{restored_hp}")
        if restored_mp:
            parts.append(f"{companion_name} MP +{restored_mp}")
        parts.extend(self._apply_consumable_buffs(item_id, item, target_id=companion.npc_id))
        return [*turn_lines, " ".join(parts)]

    def _apply_consumable_buffs(self, item_id: str, item, target_id: str = "player") -> list[str]:
        effect = item.effect
        if effect is None:
            return []

        lines: list[str] = []
        has_attack_bonus = bool(effect.attack_bonus)
        has_defense_bonus = bool(effect.defense_bonus)
        if has_attack_bonus:
            buff_name = item.name if not has_defense_bonus else f"{item.name} Attack"
            lines.append(
                self._apply_named_combat_buff(
                    buff_id=f"item:{item_id}:attack",
                    name=buff_name,
                    attack_bonus=effect.attack_bonus,
                    armor_bonus=0,
                    duration=effect.duration,
                    tick_on="player_attack",
                    apply_message=f"Attack +{effect.attack_bonus} for {effect.duration} attacks",
                    target_id=target_id,
                )
            )
        if has_defense_bonus:
            buff_name = item.name if not has_attack_bonus else f"{item.name} Defense"
            lines.append(
                self._apply_named_combat_buff(
                    buff_id=f"item:{item_id}:defense",
                    name=buff_name,
                    attack_bonus=0,
                    armor_bonus=effect.defense_bonus,
                    duration=effect.duration,
                    tick_on="enemy_turn",
                    apply_message=f"Defense +{effect.defense_bonus} for {effect.duration} enemy turns",
                    target_id=target_id,
                )
            )
        return lines

    def _has_ingredients(self, recipe: Recipe) -> bool:
        required = Counter(recipe.ingredients)
        return all(self.progress.inventory.get(item_id, 0) >= amount for item_id, amount in required.items())

    def _craft_from_recipe(self, recipe: Recipe) -> list[str]:
        if not self._has_ingredients(recipe):
            return ["You do not have the required crafting materials."]
        for item_id in recipe.ingredients:
            self.progress.remove_item(item_id)
        self.progress.add_item(recipe.result_item)
        crafted_item = self.world.items[recipe.result_item]
        return [f"You craft {crafted_item.name}."]

    def _craft_item(self, query: str) -> list[str]:
        if not query:
            return ["Craft what?"]
        known_recipes = self._known_recipes()
        if not known_recipes:
            return ["You have not unlocked any recipes yet."]
        candidates = {
            recipe.recipe_id: recipe.name for recipe in known_recipes
        }
        recipe_id = self._match_from_names(query, candidates)
        if recipe_id is None:
            return ["No known recipe makes that item."]
        recipe = self.world.recipes[recipe_id]
        return self._craft_from_recipe(recipe)

    def _combine_items(self, query: str) -> list[str]:
        lower_query = query.lower()
        if " with " not in lower_query:
            return ["Use the format: combine <item one> with <item two>."]
        split_at = lower_query.index(" with ")
        left = query[:split_at]
        right = query[split_at + len(" with "):]
        left_id = self._require_item_match(left.strip(), self.progress.inventory)
        right_id = self._require_item_match(right.strip(), self.progress.inventory)
        desired = Counter([left_id, right_id])
        for recipe in self._known_recipes():
            if Counter(recipe.ingredients) == desired:
                return self._craft_from_recipe(recipe)
        return ["Those items do not combine into any known recipe."]

    def _store_item(self, query: str) -> list[str]:
        if not self._current_room().has_storage:
            return ["There is no player storage access in this room."]
        if not query:
            return ["Store what?"]
        item_id = self._require_item_match(query, self.progress.inventory)
        self.progress.remove_item(item_id)
        self.progress.add_storage_item(item_id)
        return [f"You place {self.world.items[item_id].name} into storage."]

    def _retrieve_item(self, query: str) -> list[str]:
        if not self._current_room().has_storage:
            return ["There is no player storage access in this room."]
        if not query:
            return ["Retrieve what?"]
        item_id = self._require_item_match(query, self.progress.storage)
        self.progress.remove_storage_item(item_id)
        self.progress.add_item(item_id)
        return [f"You retrieve {self.world.items[item_id].name} from storage."]
