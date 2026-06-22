from __future__ import annotations

from .types import MAX_ACCESSORIES


ITEM_TYPE_ORDER = {
    "weapon": 0,
    "armor": 1,
    "accessory": 2,
    "consumable": 3,
    "spellbook": 4,
    "utility": 5,
    "misc": 6,
    "material": 7,
    "quest": 8,
    "key": 9,
}


class EngineViewMixin:
    def _item_type_label(self, item_id: str) -> str:
        return self.world.items[item_id].item_type.replace("_", " ").title()

    def _item_sort_key(self, item_id: str) -> tuple[int, str]:
        item = self.world.items[item_id]
        return (ITEM_TYPE_ORDER.get(item.item_type, 99), item.name)

    def _display_item_amounts(self, item_id: str, amount: int) -> list[int]:
        if self.world.items[item_id].stackable:
            return [amount]
        return [1] * amount

    def describe_current_room(self) -> list[str]:
        room = self._current_room()
        lines = [room.name, room.description]
        available_exits = self._available_exits(room)
        if available_exits:
            exits = ", ".join(
                f"{direction} -> {self.world.rooms[target].name}"
                for direction, target in available_exits.items()
            )
            lines.append(f"Exits: {exits}")
        visible_interactions = self._visible_room_interactions(room)
        if visible_interactions:
            object_names = ", ".join(interaction.name for interaction in visible_interactions.values())
            lines.append(f"Objects here: {object_names}")
        if room.maze_sequence:
            lines.append("This room is a maze. Movement directions trace its hidden pattern.")
        if self._room_items():
            items = ", ".join(self._item_name(item_id) for item_id in self._room_items())
            lines.append(f"Items here: {items}")
        npc_ids = self._room_npc_ids(room)
        if npc_ids:
            npc_names = ", ".join(self.world.npcs[npc_id].name for npc_id in npc_ids)
            lines.append(f"People here: {npc_names}")
        if self.progress.companions:
            companion_names = ", ".join(self._companion_name(companion) for companion in self.progress.companions)
            lines.append(f"Companions: {companion_names}")
        if room.vendor_ids:
            vendor_names = ", ".join(self.world.vendors[vendor_id].name for vendor_id in room.vendor_ids)
            lines.append(f"Vendors here: {vendor_names}")
        if self._room_enemies():
            enemy_names = ", ".join(
                f"{self.world.enemies[state.enemy_id].name} ({state.current_hp} HP)"
                for state in self._room_enemies()
            )
            lines.append(f"Threats: {enemy_names}")
        lines.extend(self._boss_encounter_lines())
        if room.has_storage:
            lines.append("A secure storage chest is available here.")
        if room.can_rest:
            lines.append("This is a safe place to rest and recover.")
        return lines

    def _look(self, query: str) -> list[str]:
        if query:
            return self._examine(query)
        return self.describe_current_room()

    def _show_inventory(self) -> list[str]:
        lines = ["Inventory:"]
        visible_inventory = {
            item_id: amount
            for item_id, amount in self.progress.inventory.items()
            if self.world.items[item_id].item_type != "key"
        }
        if not visible_inventory:
            lines.append("  Empty")
        else:
            for item_id, amount in sorted(
                visible_inventory.items(),
                key=lambda pair: self._item_sort_key(pair[0]),
            ):
                item = self.world.items[item_id]
                for display_amount in self._display_item_amounts(item_id, amount):
                    lines.append(
                        f"  [{self._item_type_label(item_id)}] {item.name} x{display_amount}"
                        f"{self._item_charge_display(item_id)}"
                    )
        weapon = self.world.items[self.progress.weapon_id].name if self.progress.weapon_id else "None"
        armor = self.world.items[self.progress.armor_id].name if self.progress.armor_id else "None"
        accessories = ", ".join(self._equipped_accessory_names()) if self.progress.accessory_ids else "None"
        lines.append(f"Equipped weapon: {weapon}")
        lines.append(f"Equipped armor: {armor}")
        lines.append(
            f"Equipped accessories ({len(self.progress.accessory_ids)}/{MAX_ACCESSORIES}): {accessories}"
        )
        return lines

    def _show_key_ring(self) -> list[str]:
        lines = ["Key ring:"]
        key_items = {
            item_id: amount
            for item_id, amount in self.progress.inventory.items()
            if self.world.items[item_id].item_type == "key"
        }
        if not key_items:
            lines.append("  No keys collected.")
            return lines

        for item_id, amount in sorted(key_items.items(), key=lambda pair: self.world.items[pair[0]].name):
            for display_amount in self._display_item_amounts(item_id, amount):
                lines.append(f"  {self.world.items[item_id].name} x{display_amount}")
        return lines

    def _examine(self, query: str) -> list[str]:
        if not query:
            return ["Examine what?"]
        if self._normalize(query) in {"room", "area", "around", "surroundings"}:
            return self._examine_room()

        interaction_id = self._match_room_interaction(query)
        if interaction_id is not None:
            return self._examine_room_interaction(interaction_id)
        spell_id = self._match_vendor_spell(query)
        if spell_id is not None:
            return self._examine_spell(spell_id)
        return self._examine_item(query)

    def _examine_room(self) -> list[str]:
        room = self._current_room()
        lines = [room.name, room.description or "There is nothing unusual about this place."]
        visible_interactions = self._visible_room_interactions(room)
        if visible_interactions:
            lines.append(
                "Notable objects: "
                + ", ".join(interaction.name for interaction in visible_interactions.values())
                + "."
            )
        else:
            lines.append("No notable objects stand out.")
        available_exits = self._available_exits(room)
        if available_exits:
            exits = ", ".join(
                f"{direction} -> {self.world.rooms[target].name}"
                for direction, target in available_exits.items()
            )
            lines.append(f"Visible exits: {exits}")
        else:
            lines.append("There are no obvious exits.")
        return lines

    def _examine_room_interaction(self, interaction_id: str) -> list[str]:
        interaction = self._current_room().interactions[interaction_id]
        lines = [
            interaction.name,
            interaction.description or "There is nothing more to learn by looking alone.",
        ]
        if interaction.required_item:
            item_name = self.world.items[interaction.required_item].name
            suffix = " (consumed)" if interaction.consume_required_item else ""
            lines.append(f"Requires item: {item_name}{suffix}")
        if interaction.password:
            lines.append("Requires password.")
        if interaction.lockpickable:
            lockpick_name = self.world.items[interaction.lockpick_item].name
            lines.append(
                f"Can be lockpicked with {lockpick_name} "
                f"(difficulty {interaction.lockpick_difficulty})."
            )
        return lines

    def _examine_item(self, query: str) -> list[str]:
        item_id = self._match_from_names(query, self._visible_item_pool())
        if item_id is None:
            return ["That item is not available to examine right now."]

        item = self.world.items[item_id]
        lines = [item.name, item.description or "No description is available.", f"Type: {item.item_type.title()}"]

        effects: list[str] = []
        if item.attack_bonus:
            effects.append(f"Attack bonus: +{item.attack_bonus}")
        if item.defense_bonus:
            effects.append(f"Defense bonus: +{item.defense_bonus}")
        if item.hp_bonus:
            effects.append(f"HP bonus: +{item.hp_bonus}")
        if item.mp_bonus:
            effects.append(f"MP bonus: +{item.mp_bonus}")
        if item.pickpocket_bonus:
            effects.append(f"Pickpocket bonus: +{item.pickpocket_bonus}%")
        if item.lockpick_bonus:
            effects.append(f"Lockpick bonus: +{item.lockpick_bonus}%")
        if item.item_type in {"weapon", "armor", "accessory"} and item.required_level > 1:
            effects.append(f"Requires level: {item.required_level}")
        if item.max_charges:
            effects.append(f"Charges: {self._item_charges(item_id)}/{item.max_charges}")
            depleted_effects: list[str] = []
            if item.depleted_attack_bonus is not None:
                depleted_effects.append(f"attack +{item.depleted_attack_bonus}")
            if item.depleted_defense_bonus is not None:
                depleted_effects.append(f"defense +{item.depleted_defense_bonus}")
            if item.depleted_hp_bonus is not None:
                depleted_effects.append(f"HP +{item.depleted_hp_bonus}")
            if item.depleted_mp_bonus is not None:
                depleted_effects.append(f"MP +{item.depleted_mp_bonus}")
            if depleted_effects:
                effects.append("When depleted: " + ", ".join(depleted_effects))
        if item.item_type == "utility":
            effects.append("Use: room events and environmental interactions")
        if item.item_type == "misc":
            effects.append("Use: story events and one-off room interactions")
        if item.effect is not None:
            if item.effect.hp_restore:
                effects.append(f"Restores HP: {item.effect.hp_restore}")
            if item.effect.mp_restore:
                effects.append(f"Restores MP: {item.effect.mp_restore}")
            if item.effect.attack_bonus:
                effects.append(f"Temporary attack bonus: +{item.effect.attack_bonus}")
            if item.effect.defense_bonus:
                effects.append(f"Temporary defense bonus: +{item.effect.defense_bonus}")
            if item.effect.duration and (item.effect.attack_bonus or item.effect.defense_bonus):
                effects.append(f"Duration: {item.effect.duration} turns")
            if item.effect.recharge_charges:
                effects.append("Use: recharges a charged magical item")
            if item.effect.cure_poison:
                effects.append("Use: cures poison")
        if item.teaches_spell:
            spell = self.world.spells[item.teaches_spell]
            effects.append(f"Teaches spell: {spell.name}")
            if spell.allowed_classes and "all" not in spell.allowed_classes:
                effects.append(f"Requires class: {self._spell_class_label(spell)}")

        if effects:
            lines.extend(effects)
        else:
            lines.append("Effects: none")

        if item.value:
            lines.append(f"Value: {self._format_currency(item.value, 'gold')}")
        lines.extend(self._equipment_comparison_lines(item_id))
        return lines

    def _match_vendor_spell(self, query: str) -> str | None:
        room = self._current_room()
        spell_ids = {
            spell_id
            for vendor_id in room.vendor_ids
            for spell_id in self.world.vendors[vendor_id].spell_stock
        }
        return self._match_from_names(
            query,
            {spell_id: self.world.spells[spell_id].name for spell_id in spell_ids},
        )

    def _examine_spell(self, spell_id: str) -> list[str]:
        spell = self.world.spells[spell_id]
        lines = [
            spell.name,
            spell.description or "No description is available.",
            f"School: {spell.school.replace('_', ' ').title()}",
            f"MP cost: {spell.mp_cost}",
            f"Power level: {spell.power}",
        ]
        if spell.allowed_classes and "all" not in spell.allowed_classes:
            lines.append(f"Classes: {self._spell_class_label(spell)}")
        return lines

    def _equipment_comparison_lines(self, item_id: str) -> list[str]:
        item = self.world.items[item_id]
        if item.item_type not in {"weapon", "armor"}:
            return []

        equipped_id = self.progress.weapon_id if item.item_type == "weapon" else self.progress.armor_id
        if equipped_id == item_id:
            return [f"Comparison: Currently equipped as your {item.item_type}."]
        if equipped_id is None:
            return [f"Comparison: Better than having no equipped {item.item_type}."]

        equipped = self.world.items[equipped_id]
        stats = (
            ("Attack", "attack_bonus"),
            ("Defense", "defense_bonus"),
            ("HP", "hp_bonus"),
            ("MP", "mp_bonus"),
        )
        deltas: list[int] = []
        lines = [f"Comparison to equipped {equipped.name}:"]
        for label, attribute in stats:
            candidate_value = self._effective_item_bonus(item_id, attribute)
            equipped_value = self._effective_item_bonus(equipped_id, attribute)
            delta = candidate_value - equipped_value
            deltas.append(delta)
            delta_text = "same" if delta == 0 else f"{delta:+d}"
            lines.append(
                f"  {label}: +{candidate_value} vs +{equipped_value} ({delta_text})"
            )

        if all(delta == 0 for delta in deltas):
            verdict = "Same"
        elif all(delta >= 0 for delta in deltas):
            verdict = "Better"
        elif all(delta <= 0 for delta in deltas):
            verdict = "Worse"
        else:
            verdict = "Mixed"
        lines.append(f"Overall comparison: {verdict}.")
        return lines

    def _show_wallet(self) -> list[str]:
        lines = ["Wallet:"]
        for currency_id, amount in self._wallet_entries():
            lines.append(f"  {self._format_currency(amount, currency_id)}")
        return lines

    def _show_storage(self) -> list[str]:
        if not self._current_room().has_storage:
            return ["There is no player storage access in this room."]
        lines = ["Storage:"]
        if not self.progress.storage:
            lines.append("  Empty")
        else:
            for item_id, amount in sorted(
                self.progress.storage.items(), key=lambda pair: self.world.items[pair[0]].name
            ):
                for display_amount in self._display_item_amounts(item_id, amount):
                    lines.append(f"  {self.world.items[item_id].name} x{display_amount}")
        return lines

    def _show_stats(self) -> list[str]:
        lines = [
            f"{self.player.name} the {self._player_class_name()}",
            f"Level {self.player.level}  EXP {self.player.experience}/{self.player.experience_to_next_level()}",
            f"HP {self.player.hp}/{self._player_max_hp()}  MP {self.player.mp}/{self._player_max_mp()}  Gold {self._currency_amount('gold')}",
            f"Attack {self._player_attack_score()}  Defense {self._player_defense_score()}",
            (
                f"Accessories ({len(self.progress.accessory_ids)}/{MAX_ACCESSORIES}): "
                + (", ".join(self._equipped_accessory_names()) if self.progress.accessory_ids else "None")
            ),
        ]
        if self.progress.faction_id:
            lines.append(f"Faction: {self._faction_name(self.progress.faction_id)}")
        extra_wallet = [
            self._format_currency(amount, currency_id)
            for currency_id, amount in self._wallet_entries()
            if currency_id != "gold" and amount > 0
        ]
        if extra_wallet:
            lines.append("Wallet: " + ", ".join(extra_wallet))
        if self.progress.companions:
            lines.append(
                "Companions: "
                + ", ".join(
                    f"{self._companion_name(companion)} "
                    f"({companion.current_hp}/{self._companion_max_hp(companion)} HP)"
                    for companion in self.progress.companions
                )
            )
        if self.buffs:
            lines.append(
                "Active magic: "
                + ", ".join(
                    f"{self._buff_display_name(buff)} ({buff.remaining_turns} turns)"
                    for buff in self.buffs
                )
            )
        if self.player_attack_block_turns:
            lines.append(f"Attack disrupted: {self.player_attack_block_turns} turn(s)")
        if self.progress.player_poisoned:
            lines.append("Status: Poisoned")
        player_class = self._player_class_definition()
        if player_class and (player_class.pickpocket_chance or player_class.lockpick_chance):
            lines.append(
                "Stealth: "
                f"Pickpocket {player_class.pickpocket_chance + self._equipped_pickpocket_bonus() + self._buffed_pickpocket_bonus()}%, "
                f"Lockpick {player_class.lockpick_chance + self._equipped_lockpick_bonus() + self._buffed_lockpick_bonus()}%"
            )
        return lines

    def _buff_display_name(self, buff) -> str:
        if buff.target_id == "player":
            return buff.name
        companion = next(
            (
                companion
                for companion in self.progress.companions
                if companion.npc_id == buff.target_id
            ),
            None,
        )
        if companion is None:
            return buff.name
        return f"{self._companion_name(companion)}: {buff.name}"

    def _game_over_stats(self) -> list[str]:
        return ["Final player stats:", *self._show_stats()]

    def _show_quests(self) -> list[str]:
        lines = ["Quest log:"]
        if self.progress.faction_id:
            lines.append(f"Faction pledge: {self._faction_name(self.progress.faction_id)}")
        if self.progress.active_quests:
            lines.append("Active:")
            for quest_id in self.progress.active_quests:
                quest = self.world.quests[quest_id]
                lines.append(f"  {quest.name}: {quest.description}")
        else:
            lines.append("Active: none")

        if self.progress.completed_quests:
            lines.append("Completed:")
            for quest_id in self.progress.completed_quests:
                lines.append(f"  {self.world.quests[quest_id].name}")
        else:
            lines.append("Completed: none")
        return lines

    def _show_spells(self) -> list[str]:
        lines = ["Spells:"]
        if not self.progress.learned_spells:
            lines.append("  You have not learned any spells in this world yet.")
            return lines
        for spell_id in self.progress.learned_spells:
            spell = self.world.spells[spell_id]
            class_note = ""
            if spell.allowed_classes and "all" not in spell.allowed_classes:
                class_note = f" [{self._spell_class_label(spell)} only]"
            effects: list[str] = []
            if spell.power and spell.school in {"healing", "heal"}:
                effects.append(f"heals {spell.power} HP")
            elif spell.power and spell.school not in {"control", "disable", "attack_block"}:
                effects.append(f"power {spell.power}")
            if spell.attack_bonus:
                effects.append(f"attack +{spell.attack_bonus}")
            if spell.armor_bonus:
                effects.append(f"defense +{spell.armor_bonus}")
            if spell.pickpocket_bonus:
                effects.append(f"pickpocket +{spell.pickpocket_bonus}%")
            if spell.lockpick_bonus:
                effects.append(f"lockpick +{spell.lockpick_bonus}%")
            if spell.skip_turns:
                effects.append(f"prevents attacks for {spell.skip_turns} turn(s)")
            if spell.cure_poison:
                effects.append("cures poison")
            if spell.duration:
                effects.append(f"{spell.duration} turns")
            effect_note = f" ({', '.join(effects)})" if effects else ""
            lines.append(
                f"  {spell.name} [{spell.school}]{class_note}{effect_note} - costs {spell.mp_cost} MP. "
                f"{spell.description}"
            )
        return lines

    def _show_recipes(self) -> list[str]:
        lines = ["Crafting recipes:"]
        known_recipes = self._known_recipes()
        if not known_recipes:
            lines.append("  No recipes unlocked yet. Buy one from a vendor or earn one as a quest reward.")
            return lines
        for recipe in known_recipes:
            ingredient_names = ", ".join(self.world.items[item_id].name for item_id in recipe.ingredients)
            result_name = self.world.items[recipe.result_item].name
            craftable = self._has_ingredients(recipe)
            suffix = "ready" if craftable else "missing parts"
            lines.append(f"  {recipe.name}: {ingredient_names} -> {result_name} [{suffix}]")
        return lines

    def _help_lines(self) -> list[str]:
        return [
            "Commands:",
            "  look, go <direction>, north/south/east/west/in/out, retreat",
            "  examine room|<object>|<item>|<vendor spell>, interact <object>, answer <object> with <password>",
            "  pickpocket <npc or vendor> for <item>, lockpick <object>, pay bail, escape jail",
            "  take <item>, take all, drop <item>, inventory, key ring, stats",
            "  wallet",
            "  rest",
            "  companions, recruit <npc>, dismiss <companion>",
            "  equip <item>, unequip weapon|armor|accessory|<accessory>, use <item or spellbook>",
            "  use <consumable> on <companion>, use <utility> on <object>",
            "  use <recharge item> on <charged item>",
            "  equip <item> to <companion>, equip <companion> with <item>",
            "  talk <npc or companion>, accept <npc or quest>, quests",
            "  choose ending <number>",
            "  shop, buy <item, recipe, or spell>, buy <spell or spellbook> for <companion>, sell <item>",
            "  rates, exchange <amount> <currency> to <currency>",
            "  attack <enemy>, cast <spell> [on <enemy>], spells",
            "  boss <1-4|fight|bypass|control|delay>",
            "  craft <item>, combine <item> with <item>, recipes",
            "  storage, store <item>, retrieve <item>",
            "  save, quit",
        ]
