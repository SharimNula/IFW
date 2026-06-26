from __future__ import annotations

import random

from ..models import BossEncounter, BossEncounterChoice, EnemyState


BOSS_CHOICE_NUMBERS = {
    "fight": 1,
    "bypass": 2,
    "control": 3,
    "delay": 4,
}


class EngineBossMixin:
    def _boss_encounter_key(self, state: EnemyState) -> str:
        return f"{self.progress.current_room}:{state.enemy_id}"

    def _pending_boss_encounter(
        self,
    ) -> tuple[EnemyState, BossEncounter] | None:
        for state in self._room_enemies():
            enemy = self.world.enemies[state.enemy_id]
            if enemy.boss_encounter is None:
                continue
            if self._boss_encounter_key(state) in self.progress.started_boss_encounters:
                continue
            return state, enemy.boss_encounter
        return None

    def _boss_encounter_lines(self) -> list[str]:
        pending = self._pending_boss_encounter()
        if pending is None:
            return []
        state, encounter = pending
        enemy = self.world.enemies[state.enemy_id]
        lines = [f"Boss confrontation: {enemy.name}", encounter.intro, "Options:"]
        for choice in sorted(
            encounter.choices,
            key=lambda candidate: BOSS_CHOICE_NUMBERS[candidate.choice_type],
        ):
            number = BOSS_CHOICE_NUMBERS[choice.choice_type]
            status = self._boss_choice_status(choice)
            suffix = f" [{status}]" if status else ""
            lines.append(f"  {number}. {choice.label}{suffix}")
        lines.append("Choose with 'boss <number or option>'. You may also retreat.")
        return lines

    def _boss_choice_status(self, choice: BossEncounterChoice) -> str:
        if choice.choice_type == "bypass":
            if all(self._has_story_flag(flag) for flag in choice.required_flags):
                return "available"
            return "locked: story requirements not met"
        if choice.choice_type == "control":
            assert choice.required_item is not None
            item = self.world.items[choice.required_item]
            if self.progress.inventory.get(choice.required_item, 0) > 0:
                return f"available: {item.name}"
            return f"requires {item.name}"
        if choice.choice_type == "delay":
            return f"{choice.success_chance}% success"
        return "standard combat"

    def _choose_boss_option(self, query: str) -> list[str]:
        pending = self._pending_boss_encounter()
        if pending is None:
            return ["There is no unresolved boss confrontation here."]
        state, encounter = pending
        choice_type = self._match_boss_choice(query, encounter.choices)
        if choice_type is None:
            return [
                "Choose fight, bypass, control, delay, or option 1-4.",
                *self._boss_encounter_lines(),
            ]
        choice = next(
            (candidate for candidate in encounter.choices if candidate.choice_type == choice_type),
            None,
        )
        if choice is None:
            return [
                f"The {choice_type} option is not available for this boss.",
                *self._boss_encounter_lines(),
            ]
        if choice.choice_type == "fight":
            return self._begin_boss_fight(state, choice)
        if choice.choice_type == "bypass":
            return self._bypass_boss(state, choice)
        if choice.choice_type == "control":
            return self._control_boss(state, choice)
        return self._delay_boss(state, choice)

    def _match_boss_choice(
        self,
        query: str,
        choices: list[BossEncounterChoice],
    ) -> str | None:
        normalized = self._normalize(query)
        if normalized.startswith("option "):
            normalized = normalized[7:].strip()
        number_choices = {
            str(number): choice_type
            for choice_type, number in BOSS_CHOICE_NUMBERS.items()
        }
        if normalized in number_choices:
            return number_choices[normalized]
        return self._match_from_names(
            normalized,
            {choice.choice_type: choice.label for choice in choices},
        )

    def _begin_boss_fight(
        self,
        state: EnemyState,
        choice: BossEncounterChoice,
    ) -> list[str]:
        self._mark_boss_encounter_started(state)
        self._track_boss_fight_resolution_flag(state, choice)
        enemy = self.world.enemies[state.enemy_id]
        return [
            choice.text or f"You stand your ground against {enemy.name}.",
            "Standard combat begins.",
        ]

    def _bypass_boss(
        self,
        state: EnemyState,
        choice: BossEncounterChoice,
    ) -> list[str]:
        missing_flags = [
            flag for flag in choice.required_flags if not self._has_story_flag(flag)
        ]
        if missing_flags:
            return [
                "You have not met the story requirements for that approach.",
                *self._boss_encounter_lines(),
            ]
        enemy = self.world.enemies[state.enemy_id]
        lines = [
            choice.text
            or f"What you have learned gives {enemy.name} reason to withdraw."
        ]
        lines.extend(self._resolve_boss_without_combat(state, choice))
        return lines

    def _control_boss(
        self,
        state: EnemyState,
        choice: BossEncounterChoice,
    ) -> list[str]:
        assert choice.required_item is not None
        item = self.world.items[choice.required_item]
        if self.progress.inventory.get(choice.required_item, 0) <= 0:
            return [
                f"You need {item.name} to control this boss.",
                *self._boss_encounter_lines(),
            ]
        if choice.consume_item:
            self.progress.remove_item(choice.required_item)
        enemy = self.world.enemies[state.enemy_id]
        lines = [choice.text or f"{item.name} bends {enemy.name} to your command."]
        if choice.consume_item:
            lines.append(f"{item.name} is consumed.")
        lines.extend(self._resolve_boss_without_combat(state, choice))
        return lines

    def _delay_boss(
        self,
        state: EnemyState,
        choice: BossEncounterChoice,
    ) -> list[str]:
        self._mark_boss_encounter_started(state)
        enemy = self.world.enemies[state.enemy_id]
        if random.randint(1, 100) > choice.success_chance:
            return [
                choice.failure_text or f"Your attempt to delay {enemy.name} fails.",
                "Standard combat begins.",
            ]

        lines = [
            choice.success_text
            or f"You delay {enemy.name}, but the danger is not ended."
        ]
        lines.extend(self._resolve_boss_without_combat(state, choice))
        return lines

    def _resolve_boss_without_combat(
        self,
        state: EnemyState,
        choice: BossEncounterChoice,
    ) -> list[str]:
        self._mark_boss_encounter_started(state)
        self._apply_boss_choice_flag(choice)
        self._remove_resolved_boss(state)
        enemy = self.world.enemies[state.enemy_id]
        lines = self._award_enemy_loot(enemy, guaranteed=True)
        lines.extend(self._check_quest_completion())
        lines.extend(self._next_boss_encounter_lines())
        return lines

    def _track_boss_fight_resolution_flag(
        self,
        state: EnemyState,
        choice: BossEncounterChoice,
    ) -> None:
        encounter_key = self._boss_encounter_key(state)
        if choice.set_flag:
            self.progress.boss_resolution_flags[encounter_key] = choice.set_flag
        else:
            self.progress.boss_resolution_flags.pop(encounter_key, None)

    def _apply_boss_choice_flag(self, choice: BossEncounterChoice) -> None:
        if choice.set_flag:
            self._set_story_flags([choice.set_flag])

    def _apply_defeated_boss_resolution_flag(self, state: EnemyState) -> None:
        encounter_key = self._boss_encounter_key(state)
        flag = self.progress.boss_resolution_flags.pop(encounter_key, None)
        if flag:
            self._set_story_flags([flag])

    def _remove_resolved_boss(self, state: EnemyState) -> None:
        enemy = self.world.enemies[state.enemy_id]
        self.progress.boss_resolution_flags.pop(self._boss_encounter_key(state), None)
        self._room_enemies().remove(state)
        if enemy.enemy_id not in self.progress.defeated_enemies:
            self.progress.defeated_enemies.append(enemy.enemy_id)

    def _mark_boss_encounter_started(self, state: EnemyState) -> None:
        encounter_key = self._boss_encounter_key(state)
        if encounter_key not in self.progress.started_boss_encounters:
            self.progress.started_boss_encounters.append(encounter_key)

    def _next_boss_encounter_lines(self) -> list[str]:
        if self.game_over:
            return []
        return self._boss_encounter_lines()

    def _boss_confrontation_allows_command(self, verb: str, remainder: str) -> bool:
        if verb in {
            "look",
            "l",
            "examine",
            "inspect",
            "x",
            "inventory",
            "inv",
            "i",
            "keyring",
            "keys",
            "stats",
            "status",
            "wallet",
            "money",
            "currencies",
            "companions",
            "party",
            "quests",
            "spells",
            "recipes",
            "equip",
            "unequip",
            "retreat",
            "flee",
            "save",
            "quit",
            "exit",
            "help",
        }:
            return True
        return verb == "key" and remainder.lower() == "ring"
