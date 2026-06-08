from __future__ import annotations

from ..models import CurrencyExchangeRate, NPC, Quest, QuestEndingChoice, Vendor


class EngineSocialMixin:
    def _npc_idle_dialogue(self, npc) -> str:
        if not npc.dialogue_lines:
            return npc.dialogue
        current_index = self.progress.npc_dialogue_indices.get(npc.npc_id, 0) % len(npc.dialogue_lines)
        self.progress.npc_dialogue_indices[npc.npc_id] = (current_index + 1) % len(npc.dialogue_lines)
        return npc.dialogue_lines[current_index]

    def _npc_quest_chain(self, npc: NPC) -> list[str]:
        if npc.quest_ids:
            return npc.quest_ids
        if npc.quest_id:
            return [npc.quest_id]
        return [
            quest.quest_id
            for quest in self.world.quests.values()
            if quest.giver_id == npc.npc_id
        ]

    def _next_quest_id_for_npc(self, npc: NPC) -> str | None:
        for quest_id in self._npc_quest_chain(npc):
            if quest_id not in self.progress.completed_quests:
                return quest_id
        return None

    def _last_completed_quest_for_npc(self, npc: NPC) -> Quest | None:
        for quest_id in reversed(self._npc_quest_chain(npc)):
            if quest_id in self.progress.completed_quests:
                return self.world.quests[quest_id]
        return None

    def _npc_more_quests_hint(
        self,
        npc: NPC,
        quest_id: str,
        *,
        completed_now: bool = False,
    ) -> str:
        quest_chain = self._npc_quest_chain(npc)
        if len(quest_chain) < 2 or quest_id not in quest_chain:
            return ""
        quest_index = quest_chain.index(quest_id)
        if quest_index >= len(quest_chain) - 1:
            return ""
        next_quest = self.world.quests[quest_chain[quest_index + 1]]
        if completed_now:
            return f"This NPC has more quests available: {next_quest.name} is now available."
        current_quest = self.world.quests[quest_id]
        return f"This NPC has more quests available after you complete {current_quest.name}."

    def _quest_faction_id(self, quest: Quest) -> str | None:
        return self.world.npcs[quest.giver_id].faction_id

    def _faction_conflict_message(self, faction_id: str | None) -> str | None:
        if faction_id is None or self.progress.faction_id is None:
            return None
        if faction_id == self.progress.faction_id:
            return None
        return (
            f"You are pledged to {self._faction_name(self.progress.faction_id)} and cannot "
            f"accept quests for {self._faction_name(faction_id)}."
        )

    def _quest_needs_faction_confirmation(self, quest: Quest) -> bool:
        return self._quest_faction_id(quest) is not None and self.progress.faction_id is None

    def _faction_warning_lines(self, quest: Quest, accept_query: str | None = None) -> list[str]:
        faction_id = self._quest_faction_id(quest)
        if faction_id is None:
            return []
        lines = [
            (
                f"Faction warning: Accepting {quest.name} will pledge you to "
                f"{self._faction_name(faction_id)} and block quests from other factions."
            )
        ]
        if accept_query:
            lines.append(f"Use 'accept {accept_query} confirm' to make this commitment.")
        return lines

    def _lock_faction_for_quest(self, quest: Quest) -> list[str]:
        faction_id = self._quest_faction_id(quest)
        if faction_id is None or self.progress.faction_id is not None:
            return []
        self.progress.faction_id = faction_id
        return [f"Faction pledged: {self._faction_name(faction_id)}."]

    def _talk_to(self, query: str) -> list[str]:
        if not query:
            return ["Talk to whom?"]
        companion = self._match_active_companion(query)
        if companion is not None:
            return self._companion_room_dialogue(companion)
        room = self._current_room()
        npc_pool = {npc_id: self.world.npcs[npc_id].name for npc_id in self._room_npc_ids(room)}
        vendor_pool = {vendor_id: self.world.vendors[vendor_id].name for vendor_id in room.vendor_ids}
        npc_id = self._match_from_names(query, npc_pool)
        if npc_id:
            npc = self.world.npcs[npc_id]
            dialogue = npc.dialogue
            quest_chain = self._npc_quest_chain(npc)
            quest_id = self._next_quest_id_for_npc(npc)
            if quest_id:
                quest = self.world.quests[quest_id]
                if quest_id not in self.progress.active_quests:
                    dialogue = quest.offer_dialogue or dialogue
                    lines = [f"{npc.name}: {dialogue}"]
                    conflict_message = self._faction_conflict_message(self._quest_faction_id(quest))
                    if conflict_message:
                        lines.append(conflict_message)
                        return lines
                    if self._quest_needs_faction_confirmation(quest):
                        lines.extend(self._faction_warning_lines(quest, npc.name))
                    lines.append(f"Quest available: {quest.name}. Use 'accept {npc.name}'.")
                    more_quests_hint = self._npc_more_quests_hint(npc, quest_id)
                    if more_quests_hint:
                        lines.append(more_quests_hint)
                else:
                    dialogue = quest.active_dialogue or npc.active_dialogue or dialogue
                    lines = [f"{npc.name}: {dialogue}"]
                    if self._quest_is_complete(quest):
                        lines.extend(self._complete_quest(quest))
                        more_quests_hint = self._npc_more_quests_hint(
                            npc,
                            quest_id,
                            completed_now=True,
                        )
                        if more_quests_hint:
                            lines.append(more_quests_hint)
                    else:
                        lines.append(f"You are already working on: {quest.name}.")
                        more_quests_hint = self._npc_more_quests_hint(npc, quest_id)
                        if more_quests_hint:
                            lines.append(more_quests_hint)
                return lines
            if quest_chain:
                completed_quest = self._last_completed_quest_for_npc(npc)
                if completed_quest:
                    dialogue = completed_quest.completed_dialogue or npc.completed_dialogue or dialogue
                else:
                    dialogue = npc.completed_dialogue or dialogue
            else:
                dialogue = self._npc_idle_dialogue(npc)
            lines = [f"{npc.name}: {dialogue}"]
            return lines

        vendor_id = self._match_from_names(query, vendor_pool)
        if vendor_id:
            vendor = self.world.vendors[vendor_id]
            lines = [f"{vendor.name}: {vendor.dialogue}", "Use 'shop' to see what is for sale."]
            if vendor.exchange_rates:
                lines.append("Use 'rates' or 'exchange <amount> <currency> to <currency>'.")
            return lines
        return ["No one by that name is here."]

    def _accept_quest(self, query: str) -> list[str]:
        if not query:
            return ["Accept which quest or quest giver?"]
        query, confirmed = self._split_accept_confirmation(query)
        room = self._current_room()
        npc_id = self._match_from_names(
            query,
            {npc_id: self.world.npcs[npc_id].name for npc_id in self._room_npc_ids(room)},
        )
        quest_id = None
        if npc_id:
            npc = self.world.npcs[npc_id]
            quest_id = self._next_quest_id_for_npc(npc)
            if quest_id is None:
                if self._npc_quest_chain(npc):
                    return ["That quest giver has no new quests."]
                return ["No available quest matches that name."]
        if quest_id is None:
            quest_id = self._match_from_names(
                query, {quest_id: self.world.quests[quest_id].name for quest_id in self.world.quests}
            )
        if quest_id is None or quest_id not in self.world.quests:
            return ["No available quest matches that name."]
        quest = self.world.quests[quest_id]
        if quest.giver_id not in self._room_npc_ids(room):
            return ["The quest giver is not here."]
        giver = self.world.npcs[quest.giver_id]
        quest_chain = self._npc_quest_chain(giver)
        if quest_id not in quest_chain:
            return ["No available quest matches that name."]
        next_quest_id = self._next_quest_id_for_npc(giver)
        if quest_id != next_quest_id:
            if quest_id in self.progress.completed_quests:
                return ["You have already completed that quest."]
            if next_quest_id:
                return [
                    f"Complete {self.world.quests[next_quest_id].name} "
                    f"before {quest.name} is available."
                ]
            return ["That quest giver has no new quests."]
        if quest_id in self.progress.completed_quests:
            return ["You have already completed that quest."]
        if quest_id in self.progress.active_quests:
            return ["That quest is already active."]
        faction_id = self._quest_faction_id(quest)
        conflict_message = self._faction_conflict_message(faction_id)
        if conflict_message:
            return [conflict_message]
        if self._quest_needs_faction_confirmation(quest) and not confirmed:
            return self._faction_warning_lines(quest, query)
        self.progress.active_quests.append(quest_id)
        lines = [f"Quest accepted: {quest.name}", quest.description]
        lines.extend(self._lock_faction_for_quest(quest))
        if quest.accept_item:
            accept_item = self.world.items[quest.accept_item]
            giver = self.world.npcs[quest.giver_id]
            if self.progress.inventory.get(quest.accept_item, 0) <= 0:
                self.progress.add_item(quest.accept_item)
                lines.append(f"{giver.name} gives you {accept_item.name}.")
            else:
                lines.append(f"{giver.name} confirms that you already have {accept_item.name}.")
        lines.extend(self._check_quest_completion())
        return lines

    def _split_accept_confirmation(self, query: str) -> tuple[str, bool]:
        parts = query.rsplit(" ", 1)
        if len(parts) == 2 and parts[1].strip().lower() in {"confirm", "commit", "yes"}:
            return parts[0].strip(), True
        return query, False

    def _show_shop(self) -> list[str]:
        room = self._current_room()
        if not room.vendor_ids:
            return ["There is no vendor here."]
        vendor = self.world.vendors[room.vendor_ids[0]]
        lines = [f"{vendor.name}'s stock:"]
        lines.append(
            "Accepted currencies: "
            + ", ".join(
                self._currency_label(currency_id)
                for currency_id in self._vendor_accepted_currencies(vendor)
            )
            + "."
        )
        for item_id, price in sorted(vendor.stock.items(), key=lambda pair: self._item_sort_key(pair[0])):
            item = self.world.items[item_id]
            suffixes: list[str] = []
            if item.item_type in {"weapon", "armor", "accessory"} and item.required_level > 1:
                suffixes.append(f"requires level {item.required_level}")
            if item.teaches_spell:
                spell = self.world.spells[item.teaches_spell]
                if spell.allowed_classes and "all" not in spell.allowed_classes:
                    suffixes.append(f"spellbook, {self._spell_class_label(spell)} only")
            suffix = f" [{', '.join(suffixes)}]" if suffixes else ""
            currency_id = self._vendor_sale_currency(vendor, "item", item_id)
            lines.append(
                f"  [{self._item_type_label(item_id)}] "
                f"{item.name}{suffix} - {self._format_currency(price, currency_id)}"
            )
        for recipe_id, price in sorted(vendor.recipe_stock.items(), key=lambda pair: self._recipe_name(pair[0])):
            currency_id = self._vendor_sale_currency(vendor, "recipe", recipe_id)
            lines.append(
                f"  [Recipe] {self._recipe_name(recipe_id)} - "
                f"{self._format_currency(price, currency_id)}"
            )
        for spell_id, price in sorted(vendor.spell_stock.items(), key=lambda pair: self._spell_name(pair[0])):
            spell = self.world.spells[spell_id]
            suffix = ""
            if spell.allowed_classes and "all" not in spell.allowed_classes:
                suffix = f" [{self._spell_class_label(spell)} only]"
            currency_id = self._vendor_sale_currency(vendor, "spell", spell_id)
            lines.append(
                f"  [Spell] {spell.name}{suffix} - "
                f"{self._format_currency(price, currency_id)}"
            )
        if vendor.exchange_rates:
            lines.extend(self._exchange_rate_lines(vendor))
        lines.append(
            "Use 'buy <item, recipe, or spell>', "
            "'buy <spell or spellbook> for <companion>', or 'sell <item>'."
        )
        lines.append("Use 'examine <item or spell>' to inspect stock before buying.")
        if vendor.exchange_rates:
            lines.append("Use 'exchange <amount> <currency> to <currency>' to trade money.")
        return lines

    def _active_vendor(self) -> Vendor:
        room = self._current_room()
        if not room.vendor_ids:
            raise ValueError("There is no vendor here.")
        return self.world.vendors[room.vendor_ids[0]]

    def _buy_item(self, query: str) -> list[str]:
        if not query:
            return ["Buy what?"]
        vendor = self._active_vendor()
        companion_purchase = self._split_companion_purchase_query(query)
        if companion_purchase is not None:
            purchase_query, companion_query = companion_purchase
            companion = self._match_active_companion(companion_query)
            if companion is None:
                return ["That companion is not traveling with you."]
            return self._buy_for_companion(vendor, purchase_query, companion)

        item_id = self._match_from_names(
            query, {item_id: self.world.items[item_id].name for item_id in vendor.stock}
        )
        if item_id is not None:
            item = self.world.items[item_id]
            if item.teaches_spell and not self._spell_allowed_for_player(item.teaches_spell):
                spell = self.world.spells[item.teaches_spell]
                return [self._spell_restriction_message(spell, "learned")]
            price = vendor.stock[item_id]
            currency_id = self._vendor_sale_currency(vendor, "item", item_id)
            if not self._spend_currency(currency_id, price):
                return [self._not_enough_currency_message(currency_id)]
            self.progress.add_item(item_id)
            return [f"You buy {item.name} for {self._format_currency(price, currency_id)}."]

        recipe_id = self._match_from_names(
            query, {recipe_id: self._recipe_name(recipe_id) for recipe_id in vendor.recipe_stock}
        )
        if recipe_id is not None:
            if recipe_id in self.progress.unlocked_recipes:
                return [f"You already know {self._recipe_name(recipe_id)}."]
            price = vendor.recipe_stock[recipe_id]
            currency_id = self._vendor_sale_currency(vendor, "recipe", recipe_id)
            if not self._spend_currency(currency_id, price):
                return [self._not_enough_currency_message(currency_id)]
            self._unlock_recipe(recipe_id)
            result_name = self.world.items[self.world.recipes[recipe_id].result_item].name
            return [
                f"You buy {self._recipe_name(recipe_id)} for {self._format_currency(price, currency_id)}.",
                f"Recipe unlocked: {result_name}.",
            ]

        spell_id = self._match_from_names(
            query, {spell_id: self._spell_name(spell_id) for spell_id in vendor.spell_stock}
        )
        if spell_id is None:
            return ["That item, recipe, or spell is not sold here."]
        if not self._spell_allowed_for_player(spell_id):
            return [self._spell_restriction_message(self.world.spells[spell_id], "learned")]
        if spell_id in self.progress.learned_spells:
            return [f"You already know {self._spell_name(spell_id)}."]
        price = vendor.spell_stock[spell_id]
        currency_id = self._vendor_sale_currency(vendor, "spell", spell_id)
        if not self._spend_currency(currency_id, price):
            return [self._not_enough_currency_message(currency_id)]
        self._learn_spell(spell_id)
        return [
            f"You buy {self._spell_name(spell_id)} for {self._format_currency(price, currency_id)}.",
            f"Spell learned: {self._spell_name(spell_id)}.",
        ]

    def _split_companion_purchase_query(self, query: str) -> tuple[str, str] | None:
        lower_query = query.lower()
        for delimiter in (" for ", " to "):
            if delimiter in lower_query:
                split_at = lower_query.index(delimiter)
                return query[:split_at].strip(), query[split_at + len(delimiter):].strip()
        return None

    def _buy_for_companion(self, vendor, query: str, companion) -> list[str]:
        if not query:
            return ["Buy what for that companion?"]

        spell_id = self._match_from_names(
            query, {spell_id: self._spell_name(spell_id) for spell_id in vendor.spell_stock}
        )
        if spell_id is not None:
            return self._buy_vendor_spell_for_companion(vendor, spell_id, companion)

        item_id = self._match_from_names(
            query, {item_id: self.world.items[item_id].name for item_id in vendor.stock}
        )
        if item_id is not None:
            item = self.world.items[item_id]
            if not item.teaches_spell:
                return ["Only spells and spellbooks can be bought for companions."]
            return self._buy_spellbook_for_companion(vendor, item_id, companion)

        recipe_id = self._match_from_names(
            query, {recipe_id: self._recipe_name(recipe_id) for recipe_id in vendor.recipe_stock}
        )
        if recipe_id is not None:
            return ["Only spells and spellbooks can be bought for companions."]
        return ["That spell or spellbook is not sold here."]

    def _buy_vendor_spell_for_companion(self, vendor, spell_id: str, companion) -> list[str]:
        spell = self.world.spells[spell_id]
        companion_name = self._companion_name(companion)
        if not self._spell_allowed_for_class(spell_id, companion.class_id):
            return [self._spell_restriction_message(spell, "learned")]
        if spell_id in companion.spell_ids:
            return [f"{companion_name} already knows {spell.name}."]
        price = vendor.spell_stock[spell_id]
        currency_id = self._vendor_sale_currency(vendor, "spell", spell_id)
        if not self._spend_currency(currency_id, price):
            return [self._not_enough_currency_message(currency_id)]
        self._learn_companion_spell(companion, spell_id)
        return [
            f"You buy {spell.name} for {self._format_currency(price, currency_id)} and teach it to {companion_name}.",
            f"{companion_name} learned {spell.name}.",
        ]

    def _buy_spellbook_for_companion(self, vendor, item_id: str, companion) -> list[str]:
        item = self.world.items[item_id]
        assert item.teaches_spell is not None
        spell = self.world.spells[item.teaches_spell]
        companion_name = self._companion_name(companion)
        if not self._spell_allowed_for_class(item.teaches_spell, companion.class_id):
            return [self._spell_restriction_message(spell, "learned")]
        if item.teaches_spell in companion.spell_ids:
            return [f"{companion_name} already knows {spell.name}."]
        price = vendor.stock[item_id]
        currency_id = self._vendor_sale_currency(vendor, "item", item_id)
        if not self._spend_currency(currency_id, price):
            return [self._not_enough_currency_message(currency_id)]
        self._learn_companion_spell(companion, item.teaches_spell)
        return [
            f"You buy {item.name} for {self._format_currency(price, currency_id)} and give it to {companion_name}.",
            f"{companion_name} learned {spell.name}.",
        ]

    def _sell_item(self, query: str) -> list[str]:
        if not query:
            return ["Sell what?"]
        vendor = self._active_vendor()
        item_id = self._require_item_match(query, self.progress.inventory)
        item = self.world.items[item_id]
        value = max(1, int(item.value * vendor.buyback))
        currency_id = self._vendor_default_currency(vendor)
        self.progress.remove_item(item_id)
        self._add_currency(currency_id, value)
        return [f"You sell {item.name} for {self._format_currency(value, currency_id)}."]

    def _show_exchange_rates(self) -> list[str]:
        vendor = self._active_vendor()
        if not vendor.exchange_rates:
            return [f"{vendor.name} does not exchange currency."]
        return self._exchange_rate_lines(vendor)

    def _exchange_rate_lines(self, vendor: Vendor) -> list[str]:
        lines = [f"{vendor.name}'s exchange rates:"]
        for rate in vendor.exchange_rates:
            lines.append(
                "  "
                + self._format_currency(rate.from_amount, rate.from_currency)
                + " -> "
                + self._format_currency(rate.to_amount, rate.to_currency)
            )
        return lines

    def _exchange_currency(self, query: str) -> list[str]:
        if not query:
            return ["Exchange how much? Use 'exchange <amount> <currency> to <currency>'."]
        vendor = self._active_vendor()
        if not vendor.exchange_rates:
            return [f"{vendor.name} does not exchange currency."]
        parsed = self._parse_exchange_query(query)
        if parsed is None:
            return ["Use 'exchange <amount> <currency> to <currency>'."]
        amount, from_currency, to_currency = parsed
        if amount < 1:
            return ["Exchange amount must be at least 1."]
        rate = self._find_exchange_rate(vendor, from_currency, to_currency)
        if rate is None:
            return [
                f"{vendor.name} has no exchange rate from "
                f"{self._currency_label(from_currency)} to {self._currency_label(to_currency)}."
            ]
        if amount % rate.from_amount != 0:
            return [
                f"{vendor.name} exchanges {self._format_currency(rate.from_amount, from_currency)} "
                "at a time."
            ]
        received = (amount // rate.from_amount) * rate.to_amount
        if not self._spend_currency(from_currency, amount):
            return [self._not_enough_currency_message(from_currency)]
        self._add_currency(to_currency, received)
        return [
            f"You exchange {self._format_currency(amount, from_currency)} "
            f"for {self._format_currency(received, to_currency)}."
        ]

    def _parse_exchange_query(self, query: str) -> tuple[int, str, str] | None:
        amount_text, _, currency_query = query.strip().partition(" ")
        if not amount_text.isdigit() or not currency_query:
            return None
        lower_query = currency_query.lower()
        if " to " not in lower_query:
            return None
        split_at = lower_query.index(" to ")
        from_query = currency_query[:split_at].strip()
        to_query = currency_query[split_at + 4:].strip()
        from_currency = self._match_currency(from_query)
        to_currency = self._match_currency(to_query)
        if from_currency is None or to_currency is None:
            return None
        return int(amount_text), from_currency, to_currency

    def _match_currency(self, query: str) -> str | None:
        candidates: dict[str, str] = {}
        for currency_id, currency in self.world.currencies.items():
            candidates[currency_id] = " ".join(
                {
                    currency_id.replace("_", " "),
                    currency.name,
                    currency.singular,
                    currency.plural,
                }
            )
        return self._match_from_names(query, candidates)

    def _find_exchange_rate(
        self, vendor: Vendor, from_currency: str, to_currency: str
    ) -> CurrencyExchangeRate | None:
        for rate in vendor.exchange_rates:
            if rate.from_currency == from_currency and rate.to_currency == to_currency:
                return rate
        return None

    def _check_quest_completion(self) -> list[str]:
        lines: list[str] = []
        for quest_id in list(self.progress.active_quests):
            quest = self.world.quests[quest_id]
            if self._quest_is_complete(quest):
                lines.extend(self._complete_quest(quest))
        return lines

    def _quest_is_complete(self, quest: Quest) -> bool:
        if quest.target_enemy and quest.target_enemy not in self.progress.defeated_enemies:
            return False
        if quest.required_item and self.progress.inventory.get(quest.required_item, 0) <= 0:
            return False
        if quest.required_item and not quest.destination_room and not self._quest_giver_is_here(quest):
            return False
        if quest.destination_room and quest.destination_room != self.progress.current_room:
            return False
        return True

    def _quest_giver_is_here(self, quest: Quest) -> bool:
        return quest.giver_id in self._room_npc_ids() or quest.giver_id in self._active_companion_ids()

    def _complete_quest(self, quest: Quest) -> list[str]:
        self.progress.active_quests.remove(quest.quest_id)
        self.progress.completed_quests.append(quest.quest_id)
        if quest.required_item:
            self.progress.remove_item(quest.required_item)

        lines = [f"Quest complete: {quest.name}"]
        lines.extend(self._lock_faction_for_quest(quest))
        completion_text = self._quest_completion_text(quest)
        reward_money, reward_currency = self._quest_reward_money(quest)
        reward_exp = self._quest_reward_exp(quest)
        reward_item = self._quest_reward_item(quest)
        reward_recipe = self._quest_reward_recipe(quest)
        if completion_text:
            lines.append(completion_text)
        if reward_money:
            self._add_currency(reward_currency, reward_money)
            lines.append(f"Reward: {self._format_currency(reward_money, reward_currency)}")
        if reward_exp:
            lines.append(f"Reward: {reward_exp} experience")
            lines.extend(self._gain_player_experience(reward_exp))
        if reward_item:
            self.progress.add_item(reward_item)
            lines.append(f"Reward item: {self.world.items[reward_item].name}")
        if reward_recipe:
            if self._unlock_recipe(reward_recipe):
                lines.append(f"Reward recipe unlocked: {self._recipe_name(reward_recipe)}")
            else:
                lines.append(f"Reward recipe already known: {self._recipe_name(reward_recipe)}")
        if quest.ends_world:
            lines.extend(self._complete_ending_quest(quest))
        return lines

    def _quest_flag_branch(self, quest: Quest):
        if quest.flag_outcome is None:
            return None
        if self._has_story_flag(quest.flag_outcome.flag):
            return quest.flag_outcome.when_true
        return quest.flag_outcome.when_false

    def _quest_completion_text(self, quest: Quest) -> str:
        branch = self._quest_flag_branch(quest)
        if branch is not None and branch.completion_text is not None:
            return branch.completion_text
        return quest.completion_text

    def _quest_reward_gold(self, quest: Quest) -> int:
        amount, currency_id = self._quest_reward_money(quest)
        if currency_id != "gold":
            return 0
        return amount

    def _quest_reward_money(self, quest: Quest) -> tuple[int, str]:
        branch = self._quest_flag_branch(quest)
        currency_id = quest.reward_currency or "gold"
        if branch is not None:
            if branch.reward_currency:
                currency_id = branch.reward_currency
            if branch.reward_amount is not None:
                return branch.reward_amount, currency_id
            if branch.reward_gold is not None:
                return branch.reward_gold, currency_id
        if quest.reward_amount is not None:
            return quest.reward_amount, currency_id
        return quest.reward_gold, currency_id

    def _quest_reward_exp(self, quest: Quest) -> int:
        branch = self._quest_flag_branch(quest)
        if branch is not None and branch.reward_exp is not None:
            return branch.reward_exp
        return quest.reward_exp

    def _quest_reward_item(self, quest: Quest) -> str | None:
        branch = self._quest_flag_branch(quest)
        if branch is not None and branch.reward_item is not None:
            return branch.reward_item or None
        return quest.reward_item

    def _quest_reward_recipe(self, quest: Quest) -> str | None:
        branch = self._quest_flag_branch(quest)
        if branch is not None and branch.reward_recipe is not None:
            return branch.reward_recipe or None
        return quest.reward_recipe

    def _complete_ending_quest(
        self,
        quest: Quest,
        choice: QuestEndingChoice | None = None,
    ) -> list[str]:
        if quest.ending_choices and choice is None:
            self.progress.pending_ending_quest_id = quest.quest_id
            return self._ending_choice_lines(quest)

        ending_text = self._ending_text_for_quest(quest, choice)
        self.progress.pending_ending_quest_id = None
        lines: list[str] = []
        if ending_text and ending_text != self._quest_completion_text(quest):
            lines.append(ending_text)
        lines.append("Game over.")
        self.game_over = True
        self.await_close_on_game_over = True
        lines.extend(self._game_over_stats())
        self.save()
        return lines

    def _ending_choice_lines(self, quest: Quest) -> list[str]:
        lines = [f"Choose your ending for {quest.name}:"]
        for choice in self._available_ending_choices(quest):
            lines.append(f"  {choice.choice_id}. {choice.label}")
        lines.append("Use 'choose ending <number>' to decide.")
        return lines

    def _available_ending_choices(self, quest: Quest) -> list[QuestEndingChoice]:
        return [
            choice
            for choice in quest.ending_choices
            if all(self._has_story_flag(flag) for flag in choice.required_flags)
        ]

    def _choose_ending(self, query: str) -> list[str]:
        if not self.progress.pending_ending_quest_id:
            return ["There is no ending choice pending."]
        quest = self.world.quests[self.progress.pending_ending_quest_id]
        choice = self._match_ending_choice(quest, query)
        if choice is None:
            return ["No ending choice matches that option.", *self._ending_choice_lines(quest)]
        return self._complete_ending_quest(quest, choice)

    def _match_ending_choice(self, quest: Quest, query: str) -> QuestEndingChoice | None:
        normalized_query = self._normalize(query.replace("option", ""))
        if not normalized_query:
            return None
        for choice in self._available_ending_choices(quest):
            if normalized_query in {
                self._normalize(choice.choice_id),
                self._normalize(choice.label),
            }:
                return choice
        return None

    def _ending_text_for_quest(
        self,
        quest: Quest,
        choice: QuestEndingChoice | None = None,
    ) -> str:
        if choice is not None:
            if choice.ending_type == "default":
                return quest.ending_text or quest.completion_text or choice.text
            if choice.ending_type == "faction":
                return self._faction_ending_text_for_quest(quest) or quest.ending_text or choice.text
            return choice.text or quest.ending_text or quest.completion_text
        return self._faction_ending_text_for_quest(quest) or quest.ending_text or quest.completion_text or "Your story in this world is complete."

    def _faction_ending_text_for_quest(self, quest: Quest) -> str:
        if (
            self.progress.faction_id
            and self.progress.faction_id in quest.ending_text_by_faction
        ):
            return quest.ending_text_by_faction[self.progress.faction_id]
        return ""
