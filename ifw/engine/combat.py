from __future__ import annotations

import random

from ..models import EnemyState


class EngineCombatMixin:
    def _resolve_enemy_state(self, query: str) -> EnemyState:
        enemy_id = self._match_from_names(
            query, {state.enemy_id: self.world.enemies[state.enemy_id].name for state in self._room_enemies()}
        )
        if enemy_id is None:
            raise ValueError("That enemy is not here.")
        for state in self._room_enemies():
            if state.enemy_id == enemy_id:
                return state
        raise ValueError("That enemy is not here.")

    def _attack_enemy(self, query: str) -> list[str]:
        if not query:
            return ["Attack whom?"]
        state = self._resolve_enemy_state(query)
        lines, defeated_by_poison = self._start_player_combat_turn()
        if defeated_by_poison:
            return lines
        if self._player_attack_is_blocked():
            lines.extend(self._blocked_player_attack_turn())
            return lines
        enemy = self.world.enemies[state.enemy_id]
        enemy_defense = self._enemy_defense_score(enemy)
        if not self._hit_lands(
            self._player_attack_score(), enemy_defense + self._enemy_level_score(enemy)
        ):
            lines.append(f"Your attack misses {enemy.name}.")
            self._tick_buffs(lines, tick_on="player_attack", target_id="player")
            if self._room_enemies() and not self.game_over:
                lines.extend(self._companion_turn())
            if self._room_enemies() and not self.game_over:
                lines.extend(self._enemy_turn())
            return lines
        damage = max(1, self._player_attack_score() + random.randint(-2, 2) - enemy_defense)
        state.current_hp -= damage
        lines.append(f"You attack {enemy.name} for {damage} damage.")
        if state.current_hp <= 0:
            lines.extend(self._defeat_enemy(state))
        else:
            lines.append(f"{enemy.name} has {state.current_hp} HP left.")
        self._tick_buffs(lines, tick_on="player_attack", target_id="player")
        if self._room_enemies() and not self.game_over:
            lines.extend(self._companion_turn())
        if self._room_enemies() and not self.game_over:
            lines.extend(self._enemy_turn())
        return lines

    def _cast_spell(self, query: str) -> list[str]:
        if not query:
            return ["Cast what?"]
        spell_query = query
        target_query = ""
        if " on " in query.lower():
            spell_query, target_query = query.split(" on ", 1)
        spell_id = self._match_from_names(
            spell_query.strip(),
            {spell_id: self.world.spells[spell_id].name for spell_id in self.progress.learned_spells},
        )
        if spell_id is None:
            return ["You do not know that spell in this world."]
        spell = self.world.spells[spell_id]
        if not self._spell_allowed_for_player(spell_id):
            return [self._spell_restriction_message(spell, "cast")]
        if self.player.mp < spell.mp_cost:
            return ["You do not have enough MP."]

        supported_schools = {
            "offense",
            "defense",
            "attack",
            "attack_boost",
            "healing",
            "heal",
            "stealth",
            "control",
            "disable",
            "attack_block",
        }
        if spell.school not in supported_schools and not spell.cure_poison:
            return ["That spell school is not supported."]

        target_state: EnemyState | None = None
        if spell.school == "offense":
            if target_query.strip():
                target_state = self._resolve_enemy_state(target_query.strip())
            else:
                enemies = self._room_enemies()
                if len(enemies) != 1:
                    return ["Name a target with: cast <spell> on <enemy>."]
                target_state = enemies[0]
        elif spell.school in {"control", "disable", "attack_block"}:
            target_state = self._control_spell_target(target_query)
        elif spell.school in {"healing", "heal"} or spell.cure_poison:
            target = self._normalize(target_query)
            if target and target not in {"me", "self"}:
                return ["Healing spells can only target yourself."]
        elif spell.school == "stealth":
            if target_query.strip():
                return ["Stealth spells do not need a target."]

        lines, defeated_by_poison = self._start_player_combat_turn(skip_poison=spell.cure_poison)
        if defeated_by_poison:
            return lines
        if spell.school in {"offense", "control", "disable", "attack_block"} and self._player_attack_is_blocked():
            lines.extend(self._blocked_player_attack_turn())
            return lines

        if spell.school == "offense":
            assert target_state is not None
            self.player.mp -= spell.mp_cost
            enemy = self.world.enemies[target_state.enemy_id]
            spell_attack_score = spell.power + (self.player.level * 2)
            enemy_defense = self._enemy_defense_score(enemy)
            if not self._hit_lands(
                spell_attack_score, enemy_defense + self._enemy_level_score(enemy)
            ):
                lines.append(f"{spell.name} misses {enemy.name}.")
            else:
                damage = max(
                    1,
                    spell.power + (self.player.level * 2) + random.randint(0, 3)
                    - enemy_defense // 2,
                )
                target_state.current_hp -= damage
                lines.append(f"You cast {spell.name} on {enemy.name} for {damage} damage.")
                if target_state.current_hp <= 0:
                    lines.extend(self._defeat_enemy(target_state))
                else:
                    lines.append(f"{enemy.name} has {target_state.current_hp} HP left.")
        elif spell.school == "defense":
            self.player.mp -= spell.mp_cost
            lines.append(
                self._apply_combat_buff(
                    spell,
                    tick_on="enemy_turn",
                    cast_message=f"You cast {spell.name} and raise your defenses.",
                )
            )
        elif spell.school in {"attack", "attack_boost"}:
            self.player.mp -= spell.mp_cost
            lines.append(
                self._apply_combat_buff(
                    spell,
                    tick_on="player_attack",
                    cast_message=f"You cast {spell.name} and sharpen your attacks.",
                )
            )
        elif spell.school in {"healing", "heal"} or spell.cure_poison:
            target = self._normalize(target_query)
            if target and target not in {"me", "self"}:
                return ["Healing spells can only target yourself."]
            missing_hp = self._player_max_hp() - self.player.hp
            if missing_hp <= 0 and not (spell.cure_poison and self.progress.player_poisoned):
                if spell.cure_poison:
                    return ["You are not poisoned."]
                return ["You are already at full health."]
            self.player.mp -= spell.mp_cost
            restored_hp = min(spell.power, missing_hp)
            if restored_hp:
                self.player.hp += restored_hp
                lines.append(f"You cast {spell.name} and restore {restored_hp} HP.")
            if spell.cure_poison and self.progress.player_poisoned:
                self.progress.player_poisoned = False
                lines.append(f"You cast {spell.name} and purge the poison.")
        elif spell.school == "stealth":
            self.player.mp -= spell.mp_cost
            lines.append(self._apply_stealth_buff(spell))
        elif spell.school in {"control", "disable", "attack_block"}:
            assert target_state is not None
            self.player.mp -= spell.mp_cost
            enemy = self.world.enemies[target_state.enemy_id]
            spell_attack_score = max(1, spell.power) + (self.player.level * 2)
            enemy_defense = self._enemy_defense_score(enemy)
            if not self._hit_lands(
                spell_attack_score, enemy_defense + self._enemy_level_score(enemy)
            ):
                lines.append(f"{spell.name} misses {enemy.name}.")
            else:
                target_state.skip_turns = max(target_state.skip_turns, spell.skip_turns)
                if spell.skip_turns == 1:
                    lines.append(
                        f"You cast {spell.name} on {enemy.name}. "
                        f"{enemy.name} will miss its next attack."
                    )
                else:
                    lines.append(
                        f"You cast {spell.name} on {enemy.name}. "
                        f"{enemy.name} will miss its next {spell.skip_turns} attacks."
                    )
        else:
            return ["That spell school is not supported."]

        if self._room_enemies() and not self.game_over:
            lines.extend(self._companion_turn())
        if self._room_enemies() and not self.game_over:
            lines.extend(self._enemy_turn())
        return lines

    def _control_spell_target(self, target_query: str) -> EnemyState:
        if target_query.strip():
            return self._resolve_enemy_state(target_query.strip())
        enemies = self._room_enemies()
        if len(enemies) != 1:
            raise ValueError("Name a target with: cast <spell> on <enemy>.")
        return enemies[0]

    def _defeat_enemy(self, state: EnemyState) -> list[str]:
        enemy = self.world.enemies[state.enemy_id]
        self._room_enemies().remove(state)
        if enemy.enemy_id not in self.progress.defeated_enemies:
            self.progress.defeated_enemies.append(enemy.enemy_id)

        lines = [f"{enemy.name} falls in battle."]
        if enemy.defeat_text:
            lines.append(enemy.defeat_text)
        if enemy.boss_encounter is not None:
            self._apply_defeated_boss_resolution_flag(state)
        self._add_currency("gold", enemy.gold_reward)
        lines.append(f"You gain {self._format_currency(enemy.gold_reward, 'gold')}.")
        lines.append(f"You gain {enemy.exp_reward} experience.")
        lines.extend(self._gain_player_experience(enemy.exp_reward))

        lines.extend(self._award_enemy_loot(enemy, guaranteed=enemy.boss_encounter is not None))

        lines.extend(self._check_quest_completion())
        return lines

    def _award_enemy_loot(self, enemy, guaranteed: bool = False) -> list[str]:
        lines: list[str] = []
        for drop in enemy.loot:
            if guaranteed or random.random() <= drop.chance:
                self.progress.add_item(drop.item_id)
                lines.append(f"Loot found: {self.world.items[drop.item_id].name}.")
        return lines

    def _enemy_turn(self) -> list[str]:
        lines = ["Enemies retaliate:"]
        for state in list(self._room_enemies()):
            enemy = self.world.enemies[state.enemy_id]
            if state.skip_turns > 0:
                state.skip_turns -= 1
                lines.append(f"  {enemy.name} is dazzled and cannot attack.")
                continue
            target_companion = self._enemy_target_companion()
            target_name = "you" if target_companion is None else self._companion_name(target_companion)
            defender_score = (
                self._player_defense_score()
                if target_companion is None
                else self._companion_defense_score(target_companion)
            )
            enemy_attack = self._enemy_attack_score(enemy)
            if not self._hit_lands(
                enemy_attack + self._enemy_level_score(enemy), defender_score
            ):
                lines.append(f"  {enemy.name} misses {target_name}.")
                continue
            damage = max(1, enemy_attack + random.randint(-1, 2) - defender_score)
            if target_companion is None:
                previous_max_hp = self._player_max_hp()
                previous_max_mp = self._player_max_mp()
                self.player.hp -= damage
                lines.append(f"  {enemy.name} hits you for {damage} damage.")
                lines.extend(self._spend_equipped_armor_charge())
                self._sync_resources_to_effective_max(previous_max_hp, previous_max_mp)
                if self.player.hp > 0:
                    self._try_enemy_prevent_player_attack(enemy, lines)
                    self._try_enemy_poison_player(enemy, lines)
            else:
                previous_max_hp = self._companion_max_hp(target_companion)
                previous_max_mp = self._companion_max_mp(target_companion)
                target_companion.current_hp -= damage
                lines.append(f"  {enemy.name} hits {target_name} for {damage} damage.")
                lines.extend(self._spend_companion_armor_charge(target_companion))
                self._sync_companion_resources(
                    target_companion,
                    previous_max_hp,
                    previous_max_mp,
                )
                if target_companion.current_hp <= 0:
                    target_companion.current_hp = 0
                    lines.append(f"  {target_name} falls back and can no longer fight.")
            if self.player.hp <= 0:
                break

        self._tick_buffs(lines, tick_on="enemy_turn")

        if self.player.hp <= 0:
            lines.extend(self._handle_player_defeat())
        return lines

    def _start_player_combat_turn(self, skip_poison: bool = False) -> tuple[list[str], bool]:
        if skip_poison or not self.progress.player_poisoned or not self._has_active_threats():
            return [], False
        damage = random.randint(1, 3)
        self.player.hp -= damage
        lines = [f"Poison burns through you for {damage} damage."]
        if self.player.hp <= 0:
            lines.extend(self._handle_player_defeat())
            return lines, True
        return lines, False

    def _spend_equipped_armor_charge(self) -> list[str]:
        if not self.progress.armor_id:
            return []
        return self._spend_item_charge(self.progress.armor_id)

    def _spend_companion_armor_charge(self, companion) -> list[str]:
        if not companion.armor_id:
            return []
        return self._spend_item_charge(companion.armor_id)

    def _try_enemy_prevent_player_attack(self, enemy, lines: list[str]) -> None:
        if enemy.prevent_attack_chance <= 0:
            return
        if random.randint(1, 100) > enemy.prevent_attack_chance:
            return
        self.player_attack_block_turns = max(
            self.player_attack_block_turns,
            enemy.prevent_attack_turns,
        )
        if enemy.prevent_attack_text:
            lines.append(f"  {enemy.prevent_attack_text}")
        else:
            lines.append(f"  {enemy.name} disrupts your focus. Your next attack will fail.")

    def _try_enemy_poison_player(self, enemy, lines: list[str]) -> None:
        if enemy.poison_chance <= 0 or self.progress.player_poisoned:
            return
        if random.randint(1, 100) > enemy.poison_chance:
            return
        self.progress.player_poisoned = True
        if enemy.poison_text:
            lines.append(f"  {enemy.poison_text}")
        else:
            lines.append(f"  {enemy.name}'s venom poisons you.")

    def _player_attack_is_blocked(self) -> bool:
        return self.player_attack_block_turns > 0

    def _blocked_player_attack_turn(self) -> list[str]:
        self.player_attack_block_turns = max(0, self.player_attack_block_turns - 1)
        lines = ["You are disoriented and cannot attack this turn."]
        if self._room_enemies() and not self.game_over:
            lines.extend(self._companion_turn())
        if self._room_enemies() and not self.game_over:
            lines.extend(self._enemy_turn())
        return lines

    def _enemy_target_companion(self):
        companions = self._living_companions()
        if not companions:
            return None
        target_index = random.randint(0, len(companions))
        if target_index == 0:
            return None
        return companions[target_index - 1]

    def _tick_buffs(self, lines: list[str], tick_on: str, target_id: str | None = None) -> None:
        expired: list[str] = []
        for buff in list(self.buffs):
            if buff.tick_on != tick_on:
                continue
            if target_id is not None and buff.target_id != target_id:
                continue
            buff.remaining_turns -= 1
            if buff.remaining_turns <= 0:
                expired.append(buff.name)
                self.buffs.remove(buff)
        if expired:
            lines.append("Magic fades: " + ", ".join(expired))

    def _handle_player_defeat(self) -> list[str]:
        boss_reset_lines = self._reset_boss_enemies_after_player_defeat()
        current_gold = self._currency_amount("gold")
        gold_loss = min(current_gold, max(5, current_gold // 5))
        self._spend_currency("gold", gold_loss)
        self.progress.current_room = self.world.start_room
        self.progress.previous_room = None
        self.progress.player_poisoned = False
        self.buffs.clear()
        self.player_attack_block_turns = 0
        self.player.hp = self._player_max_hp()
        self.player.mp = self._player_max_mp()
        self._restore_companions()
        return [
            "You are overwhelmed and collapse.",
            *boss_reset_lines,
            f"You lose {self._format_currency(gold_loss, 'gold')} while recovering.",
            f"You awaken back in {self.world.rooms[self.world.start_room].name}.",
            *self.describe_current_room(),
        ]

    def _reset_boss_enemies_after_player_defeat(self) -> list[str]:
        lines: list[str] = []
        for state in self._room_enemies():
            enemy = self.world.enemies[state.enemy_id]
            if enemy.respawns:
                continue
            state.max_hp = self._enemy_max_hp(enemy)
            state.current_hp = state.max_hp
            state.scaled_level = self.player.level
            lines.append(f"{enemy.name} regains full strength as you fall.")
        return lines
