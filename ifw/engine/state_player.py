from __future__ import annotations

from .types import CombatBuff
from ..models import Recipe, Spell, Vendor


class EnginePlayerStateMixin:
    def _ensure_player_wallet(self) -> None:
        if not self.player.wallet:
            self.player.wallet = {"gold": self.player.gold}
        for currency_id in self.world.currencies:
            self.player.wallet.setdefault(currency_id, 0)
        self.player.wallet["gold"] = self.player.gold

    def _currency_amount(self, currency_id: str) -> int:
        self._ensure_player_wallet()
        if currency_id == "gold":
            self.player.wallet["gold"] = self.player.gold
            return self.player.gold
        return self.player.wallet.get(currency_id, 0)

    def _add_currency(self, currency_id: str, amount: int) -> None:
        if amount == 0:
            return
        self._ensure_player_wallet()
        if currency_id == "gold":
            self.player.gold = max(0, self.player.gold + amount)
            self.player.wallet["gold"] = self.player.gold
            return
        self.player.wallet[currency_id] = max(0, self.player.wallet.get(currency_id, 0) + amount)

    def _spend_currency(self, currency_id: str, amount: int) -> bool:
        if amount < 0:
            raise ValueError("Currency costs must not be negative.")
        if self._currency_amount(currency_id) < amount:
            return False
        self._add_currency(currency_id, -amount)
        return True

    def _currency_label(self, currency_id: str, amount: int = 2) -> str:
        currency = self.world.currencies.get(currency_id)
        if currency is None:
            return currency_id.replace("_", " ")
        return currency.singular if amount == 1 else currency.plural

    def _format_currency(self, amount: int, currency_id: str) -> str:
        return f"{amount} {self._currency_label(currency_id, amount)}"

    def _wallet_entries(self) -> list[tuple[str, int]]:
        self._ensure_player_wallet()
        currency_ids = list(self.world.currencies)
        for currency_id in self.player.wallet:
            if currency_id not in currency_ids:
                currency_ids.append(currency_id)
        return [
            (currency_id, self._currency_amount(currency_id))
            for currency_id in currency_ids
            if self._currency_amount(currency_id) > 0 or currency_id == "gold"
        ]

    def _vendor_accepted_currencies(self, vendor: Vendor) -> list[str]:
        return vendor.accepted_currencies or [self.world.default_currency_id]

    def _vendor_default_currency(self, vendor: Vendor) -> str:
        return self._vendor_accepted_currencies(vendor)[0]

    def _vendor_sale_currency(self, vendor: Vendor, sale_type: str, sale_id: str) -> str:
        if sale_type == "item":
            return vendor.stock_currencies.get(sale_id) or self._vendor_default_currency(vendor)
        if sale_type == "recipe":
            return vendor.recipe_currencies.get(sale_id) or self._vendor_default_currency(vendor)
        if sale_type == "spell":
            return vendor.spell_currencies.get(sale_id) or self._vendor_default_currency(vendor)
        raise ValueError(f"Unknown vendor sale type '{sale_type}'.")

    def _not_enough_currency_message(self, currency_id: str) -> str:
        return f"You do not have enough {self._currency_label(currency_id)}."

    def _item_max_charges(self, item_id: str) -> int:
        return max(0, self.world.items[item_id].max_charges)

    def _item_charges(self, item_id: str) -> int:
        max_charges = self._item_max_charges(item_id)
        if max_charges <= 0:
            return 0
        return max(0, min(max_charges, self.progress.item_charges.get(item_id, max_charges)))

    def _set_item_charges(self, item_id: str, charges: int) -> None:
        max_charges = self._item_max_charges(item_id)
        if max_charges <= 0:
            return
        self.progress.item_charges[item_id] = max(0, min(max_charges, charges))

    def _charged_item_is_depleted(self, item_id: str) -> bool:
        return self._item_max_charges(item_id) > 0 and self._item_charges(item_id) <= 0

    def _item_charge_display(self, item_id: str) -> str:
        max_charges = self._item_max_charges(item_id)
        if max_charges <= 0:
            return ""
        return f" ({self._item_charges(item_id)}/{max_charges} charges)"

    def _effective_item_bonus(self, item_id: str, bonus_name: str) -> int:
        item = self.world.items[item_id]
        if self._charged_item_is_depleted(item_id):
            depleted_bonus = getattr(item, f"depleted_{bonus_name}")
            if depleted_bonus is not None:
                return depleted_bonus
        return getattr(item, bonus_name)

    def _spend_item_charge(self, item_id: str) -> list[str]:
        max_charges = self._item_max_charges(item_id)
        if max_charges <= 0:
            return []
        remaining = self._item_charges(item_id)
        if remaining <= 0:
            return [f"{self.world.items[item_id].name} has no charge left."]
        self._set_item_charges(item_id, remaining - 1)
        if remaining - 1 <= 0:
            return [f"{self.world.items[item_id].name}'s magic fades; it needs recharging."]
        return [
            f"{self.world.items[item_id].name} has "
            f"{remaining - 1}/{max_charges} charges left."
        ]

    def _recharge_item(self, item_id: str) -> None:
        self._set_item_charges(item_id, self._item_max_charges(item_id))

    def _equipped_weapon_bonus(self) -> int:
        if self.progress.weapon_id:
            return self._effective_item_bonus(self.progress.weapon_id, "attack_bonus")
        return 0

    def _equipped_armor_bonus(self) -> int:
        if self.progress.armor_id:
            return self._effective_item_bonus(self.progress.armor_id, "defense_bonus")
        return 0

    def _equipped_accessory_attack_bonus(self) -> int:
        return sum(
            self._effective_item_bonus(item_id, "attack_bonus")
            for item_id in self.progress.accessory_ids
        )

    def _equipped_accessory_defense_bonus(self) -> int:
        return sum(
            self._effective_item_bonus(item_id, "defense_bonus")
            for item_id in self.progress.accessory_ids
        )

    def _equipped_pickpocket_bonus(self) -> int:
        return sum(
            self.world.items[item_id].pickpocket_bonus
            for item_id in self.progress.accessory_ids
        )

    def _equipped_lockpick_bonus(self) -> int:
        return sum(
            self.world.items[item_id].lockpick_bonus
            for item_id in self.progress.accessory_ids
        )

    def _equipped_accessory_names(self) -> list[str]:
        return [self.world.items[item_id].name for item_id in self.progress.accessory_ids]

    def _equipped_hp_bonus(self) -> int:
        total = 0
        if self.progress.weapon_id:
            total += self._effective_item_bonus(self.progress.weapon_id, "hp_bonus")
        if self.progress.armor_id:
            total += self._effective_item_bonus(self.progress.armor_id, "hp_bonus")
        total += sum(
            self._effective_item_bonus(item_id, "hp_bonus")
            for item_id in self.progress.accessory_ids
        )
        return total

    def _equipped_mp_bonus(self) -> int:
        total = 0
        if self.progress.weapon_id:
            total += self._effective_item_bonus(self.progress.weapon_id, "mp_bonus")
        if self.progress.armor_id:
            total += self._effective_item_bonus(self.progress.armor_id, "mp_bonus")
        total += sum(
            self._effective_item_bonus(item_id, "mp_bonus")
            for item_id in self.progress.accessory_ids
        )
        return total

    def _player_max_hp(self) -> int:
        return self.player.max_hp + self._equipped_hp_bonus()

    def _player_max_mp(self) -> int:
        return self.player.max_mp + self._equipped_mp_bonus()

    def _sync_resources_to_effective_max(
        self, previous_max_hp: int | None = None, previous_max_mp: int | None = None
    ) -> None:
        current_max_hp = self._player_max_hp()
        current_max_mp = self._player_max_mp()

        if previous_max_hp is None:
            self.player.hp = current_max_hp if self.player.hp <= 0 else min(self.player.hp, current_max_hp)
        else:
            if self.player.hp >= previous_max_hp:
                self.player.hp = current_max_hp
            else:
                self.player.hp = max(0, min(self.player.hp, current_max_hp))

        if previous_max_mp is None:
            self.player.mp = max(0, min(self.player.mp, current_max_mp))
        else:
            if self.player.mp >= previous_max_mp:
                self.player.mp = current_max_mp
            else:
                self.player.mp = max(0, min(self.player.mp, current_max_mp))

    def _known_recipes(self) -> list[Recipe]:
        return [
            self.world.recipes[recipe_id]
            for recipe_id in self.progress.unlocked_recipes
            if recipe_id in self.world.recipes
        ]

    def _unlock_recipe(self, recipe_id: str) -> bool:
        if recipe_id not in self.world.recipes:
            raise ValueError(f"Unknown recipe '{recipe_id}'.")
        if recipe_id in self.progress.unlocked_recipes:
            return False
        self.progress.unlocked_recipes.append(recipe_id)
        return True

    def _learn_spell(self, spell_id: str) -> bool:
        if spell_id not in self.world.spells:
            raise ValueError(f"Unknown spell '{spell_id}'.")
        if not self._spell_allowed_for_player(spell_id):
            raise ValueError(self._spell_restriction_message(self.world.spells[spell_id], "learned"))
        if spell_id in self.progress.learned_spells:
            return False
        self.progress.learned_spells.append(spell_id)
        return True

    def _gain_player_experience(self, amount: int) -> list[str]:
        player_class = self._player_class_definition()
        if player_class is None:
            messages = self.player.gain_experience(amount)
        else:
            messages = self.player.gain_experience(
                amount,
                hp_per_level=player_class.hp_per_level,
                mp_per_level=player_class.mp_per_level,
                attack_per_level=player_class.attack_per_level,
                defense_per_level=player_class.defense_per_level,
            )
        if messages:
            self.player.hp = self._player_max_hp()
            self.player.mp = self._player_max_mp()
            if hasattr(self, "_sync_all_companion_resources"):
                self._sync_all_companion_resources()
        else:
            self._sync_resources_to_effective_max()
        return messages

    def _buffed_defense_bonus(self, target_id: str = "player") -> int:
        return sum(buff.armor_bonus for buff in self.buffs if buff.target_id == target_id)

    def _buffed_attack_bonus(self, target_id: str = "player") -> int:
        return sum(buff.attack_bonus for buff in self.buffs if buff.target_id == target_id)

    def _buffed_pickpocket_bonus(self, target_id: str = "player") -> int:
        return sum(buff.pickpocket_bonus for buff in self.buffs if buff.target_id == target_id)

    def _buffed_lockpick_bonus(self, target_id: str = "player") -> int:
        return sum(buff.lockpick_bonus for buff in self.buffs if buff.target_id == target_id)

    def _apply_named_combat_buff(
        self,
        buff_id: str,
        name: str,
        attack_bonus: int,
        armor_bonus: int,
        duration: int,
        tick_on: str,
        apply_message: str,
        target_id: str = "player",
        pickpocket_bonus: int = 0,
        lockpick_bonus: int = 0,
    ) -> str:
        existing = next(
            (buff for buff in self.buffs if buff.spell_id == buff_id and buff.target_id == target_id),
            None,
        )
        if existing:
            existing.remaining_turns = duration
            existing.attack_bonus = attack_bonus
            existing.armor_bonus = armor_bonus
            existing.pickpocket_bonus = pickpocket_bonus
            existing.lockpick_bonus = lockpick_bonus
            existing.tick_on = tick_on
            return f"You refresh {name}."
        self.buffs.append(
            CombatBuff(
                spell_id=buff_id,
                name=name,
                attack_bonus=attack_bonus,
                armor_bonus=armor_bonus,
                pickpocket_bonus=pickpocket_bonus,
                lockpick_bonus=lockpick_bonus,
                remaining_turns=duration,
                tick_on=tick_on,
                target_id=target_id,
            )
        )
        return apply_message

    def _apply_combat_buff(self, spell: Spell, tick_on: str, cast_message: str) -> str:
        return self._apply_named_combat_buff(
            buff_id=spell.spell_id,
            name=spell.name,
            attack_bonus=spell.attack_bonus,
            armor_bonus=spell.armor_bonus,
            duration=spell.duration,
            tick_on=tick_on,
            apply_message=cast_message,
        )

    def _apply_stealth_buff(self, spell: Spell) -> str:
        effects: list[str] = []
        if spell.pickpocket_bonus:
            effects.append(f"pickpocket chance +{spell.pickpocket_bonus}%")
        if spell.lockpick_bonus:
            effects.append(f"lockpick chance +{spell.lockpick_bonus}%")
        effect_text = " and ".join(effects) if effects else "subtle work"
        return self._apply_named_combat_buff(
            buff_id=spell.spell_id,
            name=spell.name,
            attack_bonus=0,
            armor_bonus=0,
            pickpocket_bonus=spell.pickpocket_bonus,
            lockpick_bonus=spell.lockpick_bonus,
            duration=spell.duration,
            tick_on="stealth_action",
            apply_message=f"You cast {spell.name}; {effect_text} for {spell.duration} turns.",
        )

    def _player_attack_score(self) -> int:
        return (
            self.player.base_attack
            + self._equipped_weapon_bonus()
            + self._equipped_accessory_attack_bonus()
            + self._buffed_attack_bonus()
            + self.player.level
        )

    def _player_defense_score(self) -> int:
        return (
            self.player.base_defense
            + self._equipped_armor_bonus()
            + self._equipped_accessory_defense_bonus()
            + self._buffed_defense_bonus()
            + self.player.level // 2
        )
