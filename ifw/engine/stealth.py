from __future__ import annotations

from dataclasses import dataclass
import random

from ..models import PickpocketTarget, RoomInteraction, Vendor


MAX_SKILL_CHANCE = 95
MIN_SKILL_CHANCE = 5
LOCKPICK_BREAK_FAILURES = 3


@dataclass(frozen=True, slots=True)
class StealthActor:
    name: str
    target_id: str
    base_chance: int
    is_companion: bool = False


class EngineStealthMixin:
    def _pickpocket(self, query: str) -> list[str]:
        if not query:
            return ["Pickpocket whom?"]
        if self._has_active_threats():
            return ["You cannot pickpocket while threats are active in the room."]
        actor = self._pickpocket_actor()
        if actor is None:
            return ["Your class has no pickpocket training."]

        holder_query, item_query = self._split_pickpocket_query(query)
        holder = self._match_pickpocket_holder(holder_query)
        if holder is None:
            return ["No one by that name is here to pickpocket."]
        holder_type, holder_id, holder_name, targets = holder
        available_targets = [
            target for target in targets
            if not self._pickpocket_target_was_taken(holder_type, holder_id, target.item_id)
        ]
        if not available_targets:
            return [f"{holder_name} has nothing left worth stealing."]

        target = self._match_pickpocket_target(item_query, available_targets)
        if target is None:
            if item_query:
                return [f"{holder_name} does not appear to have that item."]
            if len(available_targets) == 1:
                target = available_targets[0]
            else:
                item_names = ", ".join(
                    self.world.items[target.item_id].name for target in available_targets
                )
                return [f"Pickpocket which item from {holder_name}? Available targets: {item_names}."]

        item = self.world.items[target.item_id]
        chance = self._pickpocket_success_chance(target, actor)
        if random.randint(1, 100) <= chance:
            self.progress.add_item(target.item_id)
            self.progress.pickpocketed_targets.append(
                self._pickpocket_target_key(holder_type, holder_id, target.item_id)
            )
            lines = [self._pickpocket_success_line(actor, target, item.name, holder_name)]
            self._tick_buffs(lines, tick_on="stealth_action", target_id=actor.target_id)
            return lines

        lines = [self._pickpocket_failure_line(actor, target, item.name, holder_name)]
        self._tick_buffs(lines, tick_on="stealth_action", target_id=actor.target_id)
        lines.extend(self._handle_arrest())
        return lines

    def _split_pickpocket_query(self, query: str) -> tuple[str, str]:
        lower_query = query.lower()
        if " from " in lower_query:
            split_at = lower_query.index(" from ")
            return query[split_at + 6:].strip(), query[:split_at].strip()
        if " for " in lower_query:
            split_at = lower_query.index(" for ")
            return query[:split_at].strip(), query[split_at + 5:].strip()
        return query.strip(), ""

    def _match_pickpocket_holder(
        self, query: str
    ) -> tuple[str, str, str, list[PickpocketTarget]] | None:
        room = self._current_room()
        candidates: dict[str, str] = {}
        for npc_id in self._room_npc_ids(room):
            candidates[f"npc:{npc_id}"] = self.world.npcs[npc_id].name
        for vendor_id in room.vendor_ids:
            candidates[f"vendor:{vendor_id}"] = self.world.vendors[vendor_id].name

        holder_key = self._match_from_names(query, candidates)
        if holder_key is None:
            return None
        holder_type, holder_id = holder_key.split(":", 1)
        if holder_type == "npc":
            npc = self.world.npcs[holder_id]
            return holder_type, holder_id, npc.name, npc.pickpocket_targets
        vendor = self.world.vendors[holder_id]
        return holder_type, holder_id, vendor.name, vendor.pickpocket_targets

    def _match_pickpocket_target(
        self, query: str, targets: list[PickpocketTarget]
    ) -> PickpocketTarget | None:
        if not query:
            return None
        target_id = self._match_from_names(
            query,
            {target.item_id: self.world.items[target.item_id].name for target in targets},
        )
        if target_id is None:
            return None
        return next(target for target in targets if target.item_id == target_id)

    def _pickpocket_target_key(self, holder_type: str, holder_id: str, item_id: str) -> str:
        return f"{holder_type}:{holder_id}:{item_id}"

    def _pickpocket_target_was_taken(
        self, holder_type: str, holder_id: str, item_id: str
    ) -> bool:
        return self._pickpocket_target_key(holder_type, holder_id, item_id) in (
            self.progress.pickpocketed_targets
        )

    def _pickpocket_success_chance(
        self, target: PickpocketTarget, actor: StealthActor | None = None
    ) -> int:
        actor = actor or self._player_stealth_actor("pickpocket")
        chance = (
            actor.base_chance
            + self._stealth_actor_pickpocket_bonus(actor)
            + self._buffed_pickpocket_bonus(actor.target_id)
            - target.difficulty
        )
        return max(MIN_SKILL_CHANCE, min(MAX_SKILL_CHANCE, chance))

    def _lockpick(self, query: str) -> list[str]:
        if not query:
            return ["Lockpick what?"]
        if self._has_active_threats():
            return ["You cannot pick locks while threats are active in the room."]
        actor = self._lockpick_actor()
        if actor is None:
            return ["Your class has no lockpick training."]

        interaction_id = self._match_room_interaction(query)
        if interaction_id is None:
            return ["There is nothing like that here to lockpick."]
        interaction = self._current_room().interactions[interaction_id]
        if not interaction.lockpickable:
            return [f"{interaction.name} cannot be lockpicked."]

        already_done = bool(interaction.set_flags) and all(
            self._has_story_flag(flag) for flag in interaction.set_flags
        )
        if already_done and not interaction.repeatable:
            return [
                interaction.completed_text
                or f"You have already opened {interaction.name}."
            ]

        lockpick_item = self.world.items[interaction.lockpick_item]
        if self.progress.inventory.get(interaction.lockpick_item, 0) <= 0:
            return [
                interaction.lockpick_missing_item_text
                or f"You need {lockpick_item.name} to pick that lock."
            ]

        chance = self._lockpick_success_chance(interaction, actor)
        if random.randint(1, 100) <= chance:
            self._reset_lockpick_failures(interaction_id)
            lines = [self._lockpick_success_line(actor, interaction)]
            lines.append(f"You use {lockpick_item.name}.")
            lines.extend(self._apply_interaction_flags(interaction))
            self._tick_buffs(lines, tick_on="stealth_action", target_id=actor.target_id)
            return lines

        lines = self._handle_lockpick_failure(interaction_id, interaction, actor)
        self._tick_buffs(lines, tick_on="stealth_action", target_id=actor.target_id)
        return lines

    def _lockpick_success_chance(
        self, interaction: RoomInteraction, actor: StealthActor | None = None
    ) -> int:
        actor = actor or self._player_stealth_actor("lockpick")
        chance = (
            actor.base_chance
            + self._stealth_actor_lockpick_bonus(actor)
            + self._buffed_lockpick_bonus(actor.target_id)
            - interaction.lockpick_difficulty
        )
        return max(MIN_SKILL_CHANCE, min(MAX_SKILL_CHANCE, chance))

    def _handle_lockpick_failure(
        self,
        interaction_id: str,
        interaction: RoomInteraction,
        actor: StealthActor | None = None,
    ) -> list[str]:
        lockpick_item = self.world.items[interaction.lockpick_item]
        failure_key = self._lockpick_failure_key(interaction_id)
        failures = self.progress.lockpick_failures.get(failure_key, 0) + 1
        actor = actor or self._player_stealth_actor("lockpick")
        lines = [self._lockpick_failure_line(actor, interaction)]
        if failures >= LOCKPICK_BREAK_FAILURES:
            self.progress.lockpick_failures.pop(failure_key, None)
            self.progress.remove_item(interaction.lockpick_item)
            lines.append(f"{lockpick_item.name} break and will need to be replaced.")
            return lines

        self.progress.lockpick_failures[failure_key] = failures
        lines.append(f"Lockpick failures: {failures}/{LOCKPICK_BREAK_FAILURES}.")
        return lines

    def _lockpick_failure_key(self, interaction_id: str) -> str:
        return f"{self.progress.current_room}:{interaction_id}"

    def _reset_lockpick_failures(self, interaction_id: str) -> None:
        self.progress.lockpick_failures.pop(self._lockpick_failure_key(interaction_id), None)

    def _apply_interaction_flags(self, interaction: RoomInteraction) -> list[str]:
        room = self._current_room()
        added_flags = self._set_story_flags(interaction.set_flags)
        revealed_exits = [
            f"{hidden_exit.direction} -> {self.world.rooms[hidden_exit.target_room].name}"
            for hidden_exit in room.hidden_exits.values()
            if hidden_exit.required_flag in added_flags
        ]
        if not revealed_exits:
            return []
        return ["A path is revealed: " + ", ".join(revealed_exits) + "."]

    def _player_pickpocket_base_chance(self) -> int:
        player_class = self._player_class_definition()
        return 0 if player_class is None else player_class.pickpocket_chance

    def _player_lockpick_base_chance(self) -> int:
        player_class = self._player_class_definition()
        return 0 if player_class is None else player_class.lockpick_chance

    def _pickpocket_actor(self) -> StealthActor | None:
        return self._stealth_actor("pickpocket")

    def _lockpick_actor(self) -> StealthActor | None:
        return self._stealth_actor("lockpick")

    def _stealth_actor(self, skill: str) -> StealthActor | None:
        player_actor = self._player_stealth_actor(skill)
        if player_actor.base_chance > 0:
            return player_actor
        return self._companion_stealth_actor(skill)

    def _player_stealth_actor(self, skill: str) -> StealthActor:
        player_class = self._player_class_definition()
        base_chance = 0 if player_class is None else getattr(player_class, f"{skill}_chance")
        return StealthActor("You", "player", base_chance)

    def _companion_stealth_actor(self, skill: str) -> StealthActor | None:
        for companion in self.progress.companions:
            if companion.current_hp <= 0:
                continue
            player_class = self.world.player_classes.get(companion.class_id)
            if player_class is None:
                continue
            base_chance = getattr(player_class, f"{skill}_chance")
            if base_chance > 0:
                return StealthActor(
                    self._companion_name(companion),
                    companion.npc_id,
                    base_chance,
                    is_companion=True,
                )
        return None

    def _stealth_actor_pickpocket_bonus(self, actor: StealthActor) -> int:
        if actor.is_companion:
            return 0
        return self._equipped_pickpocket_bonus()

    def _stealth_actor_lockpick_bonus(self, actor: StealthActor) -> int:
        if actor.is_companion:
            return 0
        return self._equipped_lockpick_bonus()

    def _pickpocket_success_line(
        self,
        actor: StealthActor,
        target: PickpocketTarget,
        item_name: str,
        holder_name: str,
    ) -> str:
        if actor.is_companion:
            return f"{actor.name} lifts {item_name} from {holder_name} and slips it into your pack."
        return target.success_text or f"You lift {item_name} from {holder_name} without being noticed."

    def _pickpocket_failure_line(
        self,
        actor: StealthActor,
        target: PickpocketTarget,
        item_name: str,
        holder_name: str,
    ) -> str:
        if actor.is_companion:
            return (
                f"{holder_name} catches {actor.name} reaching for {item_name}. "
                "You take the blame before the Watch can ask whose idea it was."
            )
        return target.failure_text or f"{holder_name} catches your hand before you can take {item_name}."

    def _lockpick_success_line(self, actor: StealthActor, interaction: RoomInteraction) -> str:
        if actor.is_companion:
            return f"{actor.name} picks the lock on {interaction.name} for you."
        return interaction.lockpick_text or f"You pick the lock on {interaction.name}."

    def _lockpick_failure_line(
        self,
        actor: StealthActor | None,
        interaction: RoomInteraction,
    ) -> str:
        if actor is not None and actor.is_companion:
            return f"{actor.name} cannot get the lock on {interaction.name} to turn."
        return interaction.lockpick_failed_text or f"The lock on {interaction.name} refuses to turn."

    def _handle_arrest(self) -> list[str]:
        if self.world.jail_room is None:
            return self._jail_game_over(
                "With no jail configured for this world, the arrest ends your story."
            )

        jail = self.world.rooms[self.world.jail_room]
        self.progress.current_room = jail.room_id
        self.progress.previous_room = None
        lines = [f"You are arrested and taken to {jail.name}."]
        bail = self._format_currency(self.world.jail_fee, self.world.jail_currency)
        if self._currency_amount(self.world.jail_currency) >= self.world.jail_fee:
            lines.append(f"Pay {bail} with 'pay bail' to leave.")
            lines.extend(self.describe_current_room())
            return lines

        if self.player.level > 1:
            lines.append(
                f"You cannot afford the {bail} bail. "
                "Use 'escape jail' to lose a level and slip out."
            )
            lines.extend(self.describe_current_room())
            return lines

        return [
            *lines,
            *self._jail_game_over(
                f"You cannot afford the {bail} bail, and you have no level to spare."
            ),
        ]

    def _pay_bail(self) -> list[str]:
        if not self._player_is_in_jail():
            return ["You are not in jail."]
        if self._spend_currency(self.world.jail_currency, self.world.jail_fee):
            bail = self._format_currency(self.world.jail_fee, self.world.jail_currency)
            return [
                f"You pay {bail} and are released.",
                *self._release_from_jail(),
            ]
        bail = self._format_currency(self.world.jail_fee, self.world.jail_currency)
        if self.player.level > 1:
            return [
                f"You do not have enough to pay the {bail} bail.",
                "Use 'escape jail' to lose a level and slip out.",
            ]
        return self._jail_game_over(
            f"You cannot afford the {bail} bail, and you have no level to spare."
        )

    def _escape_jail(self) -> list[str]:
        if not self._player_is_in_jail():
            return ["You are not in jail."]
        if self._currency_amount(self.world.jail_currency) >= self.world.jail_fee:
            return ["You can still pay bail with 'pay bail'."]
        if self.player.level <= 1:
            bail = self._format_currency(self.world.jail_fee, self.world.jail_currency)
            return self._jail_game_over(
                f"You cannot afford the {bail} bail, and you have no level to spare."
            )
        old_level = self.player.level
        self._lose_player_level()
        return [
            f"You surrender a level of hard-won experience and escape jail.",
            f"Level reduced: {old_level} -> {self.player.level}.",
            *self._release_from_jail(),
        ]

    def _player_is_in_jail(self) -> bool:
        return self.world.jail_room is not None and self.progress.current_room == self.world.jail_room

    def _release_from_jail(self) -> list[str]:
        self.progress.current_room = self.world.start_room
        self.progress.previous_room = None
        return [f"You return to {self.world.rooms[self.world.start_room].name}.", *self.describe_current_room()]

    def _lose_player_level(self) -> None:
        player_class = self._player_class_definition()
        hp_per_level = player_class.hp_per_level if player_class else 8
        mp_per_level = player_class.mp_per_level if player_class else 4
        attack_per_level = player_class.attack_per_level if player_class else 2
        defense_per_level = player_class.defense_per_level if player_class else 1

        self.player.level = max(1, self.player.level - 1)
        self.player.max_hp = max(1, self.player.max_hp - hp_per_level)
        self.player.max_mp = max(0, self.player.max_mp - mp_per_level)
        self.player.base_attack = max(0, self.player.base_attack - attack_per_level)
        self.player.base_defense = max(0, self.player.base_defense - defense_per_level)
        self.player.experience = min(
            self.player.experience,
            max(0, self.player.experience_to_next_level() - 1),
        )
        self._sync_resources_to_effective_max()
        if hasattr(self, "_sync_all_companion_resources"):
            self._sync_all_companion_resources()

    def _jail_game_over(self, reason: str) -> list[str]:
        self.game_over = True
        self.await_close_on_game_over = True
        self.save()
        return [reason, "Game over.", *self._game_over_stats()]
