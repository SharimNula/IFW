from __future__ import annotations

from .types import REST_COST


class EngineNavigationMixin:
    def _rest(self) -> list[str]:
        if self._has_active_threats():
            return ["You cannot rest while threats are active in the room."]
        if not self._current_room().can_rest:
            return ["You cannot rest here."]
        player_max_hp = self._player_max_hp()
        player_max_mp = self._player_max_mp()
        if (
            self.player.hp == player_max_hp
            and self.player.mp == player_max_mp
            and self._companions_at_full_resources()
        ):
            return ["You are already at full health and magic."]
        if self._currency_amount("gold") < REST_COST:
            return [f"You need {self._format_currency(REST_COST, 'gold')} to rest here."]

        restored_hp = player_max_hp - self.player.hp
        restored_mp = player_max_mp - self.player.mp
        companion_restored_hp, companion_restored_mp = self._restore_companions()
        self._spend_currency("gold", REST_COST)
        self.player.hp = player_max_hp
        self.player.mp = player_max_mp
        self.buffs.clear()

        lines = [
            f"You pay {self._format_currency(REST_COST, 'gold')} and rest. HP +{restored_hp}, MP +{restored_mp}.",
            "Your strength and magic are fully restored.",
        ]
        if companion_restored_hp or companion_restored_mp:
            lines.append(
                f"Your companions recover HP +{companion_restored_hp}, MP +{companion_restored_mp}."
            )
        return lines

    def _move(self, direction: str) -> list[str]:
        if self._has_active_threats():
            return ["You cannot move while threats are active in the room. Fight or use 'retreat'."]
        room = self._current_room()
        available_exits = self._available_exits(room)
        if room.maze_sequence and direction not in available_exits:
            return self._move_through_maze(direction)
        target = available_exits.get(direction)
        if not target:
            return ["You cannot go that way."]
        target_room = self.world.rooms[target]
        blocked_message = self._entry_block_message(target)
        if blocked_message:
            return [blocked_message]

        current_room = self.progress.current_room
        seal_lines = self._seal_room_on_departure(current_room, target)
        if room.maze_sequence:
            self.progress.maze_progress[room.room_id] = 0
        self.progress.previous_room = current_room
        self.progress.current_room = target
        respawned_enemies = self._respawn_enemies_for_room(target)
        spawned_mining_items = self._respawn_mining_items_for_room(target)
        lines: list[str] = []
        if target_room.required_item:
            required_item_name = self.world.items[target_room.required_item].name
            lines.append(f"You use {required_item_name} to enter {target_room.name}.")
        lines.extend(seal_lines)
        if respawned_enemies:
            lines.append("As you return, danger stirs again: " + ", ".join(respawned_enemies) + ".")
        if spawned_mining_items:
            lines.append(self._mining_spawn_message(target, spawned_mining_items))
        lines.extend([f"You travel {direction}.", *self.describe_current_room()])
        lines.extend(self._check_quest_completion())
        lines.extend(self._complete_end_room_if_needed(target))
        return lines

    def _move_through_maze(self, direction: str) -> list[str]:
        room = self._current_room()
        current_step = self.progress.maze_progress.get(room.room_id, 0) % len(room.maze_sequence)
        expected_direction = room.maze_sequence[current_step]

        if direction != expected_direction:
            self.progress.maze_progress[room.room_id] = 0
            return [
                room.maze_failure_message
                or f"The paths of {room.name} fold back on themselves. The pattern resets."
            ]

        next_step = current_step + 1
        if next_step < len(room.maze_sequence):
            self.progress.maze_progress[room.room_id] = next_step
            return [
                room.maze_progress_message
                or f"You follow the maze pattern deeper ({next_step}/{len(room.maze_sequence)})."
            ]

        self.progress.maze_progress[room.room_id] = 0
        target = room.maze_success_room
        if target is None:
            return ["This maze has no clear exit."]
        blocked_message = self._entry_block_message(target)
        if blocked_message:
            return [blocked_message]

        current_room = self.progress.current_room
        seal_lines = self._seal_room_on_departure(current_room, target)
        self.progress.previous_room = current_room
        self.progress.current_room = target
        target_room = self.world.rooms[target]
        respawned_enemies = self._respawn_enemies_for_room(target)
        spawned_mining_items = self._respawn_mining_items_for_room(target)

        lines = [
            room.maze_success_message
            or f"You complete the pattern and find your way through {room.name}."
        ]
        if target_room.required_item:
            required_item_name = self.world.items[target_room.required_item].name
            lines.append(f"You use {required_item_name} to enter {target_room.name}.")
        lines.extend(seal_lines)
        if respawned_enemies:
            lines.append("As you return, danger stirs again: " + ", ".join(respawned_enemies) + ".")
        if spawned_mining_items:
            lines.append(self._mining_spawn_message(target, spawned_mining_items))
        lines.extend([*self.describe_current_room()])
        lines.extend(self._check_quest_completion())
        lines.extend(self._complete_end_room_if_needed(target))
        return lines

    def _complete_end_room_if_needed(self, room_id: str) -> list[str]:
        if self.world.end_room is None or room_id != self.world.end_room:
            return []
        self.game_over = True
        self.await_close_on_game_over = True
        self.save()
        return [
            f"You have reached the end room, {self.world.rooms[room_id].name}. This world is complete.",
            "Game over.",
            *self._game_over_stats(),
        ]

    def _retreat(self) -> list[str]:
        if not self._has_active_threats():
            return ["There is no active threat here to retreat from."]
        target = self.progress.previous_room
        if target is None or target == self.progress.current_room or target not in self.world.rooms:
            return ["You have nowhere safe to retreat to."]
        blocked_message = self._entry_block_message(target)
        if blocked_message:
            return [blocked_message]

        current_room = self.progress.current_room
        seal_lines = self._seal_room_on_departure(current_room, target)
        self.progress.current_room = target
        self.progress.previous_room = current_room
        respawned_enemies = self._respawn_enemies_for_room(target)
        spawned_mining_items = self._respawn_mining_items_for_room(target)
        lines: list[str] = []
        lines.extend(seal_lines)
        if respawned_enemies:
            lines.append("As you return, danger stirs again: " + ", ".join(respawned_enemies) + ".")
        if spawned_mining_items:
            lines.append(self._mining_spawn_message(target, spawned_mining_items))
        lines.extend(
            [
                f"You retreat to {self.world.rooms[target].name}.",
                *self.describe_current_room(),
            ]
        )
        return lines
