from __future__ import annotations


class EngineEnvironmentMixin:
    def _interact_with_room_object(self, query: str) -> list[str]:
        if not query:
            return ["Interact with what?"]
        if self._has_active_threats():
            return ["You cannot interact with the environment while threats are active in the room."]

        interaction_id = self._match_room_interaction(query)
        if interaction_id is None:
            return ["There is nothing like that here to interact with."]
        return self._resolve_room_interaction(interaction_id)

    def _interact_with_room_object_using_item(self, item_id: str, interaction_id: str) -> list[str]:
        if self._has_active_threats():
            return ["You cannot interact with the environment while threats are active in the room."]

        interaction = self._current_room().interactions[interaction_id]
        if interaction.required_item != item_id:
            item_name = self.world.items[item_id].name
            return [f"{item_name} does not seem useful for {interaction.name}."]
        return self._resolve_room_interaction(interaction_id, used_item_id=item_id)

    def _resolve_room_interaction(
        self,
        interaction_id: str,
        used_item_id: str | None = None,
    ) -> list[str]:
        room = self._current_room()
        interaction = room.interactions[interaction_id]
        already_done = bool(interaction.set_flags) and all(
            self._has_story_flag(flag) for flag in interaction.set_flags
        )
        if already_done and not interaction.repeatable:
            return [
                interaction.completed_text
                or f"You have already done what you can with {interaction.name}."
            ]

        required_item_name = ""
        if interaction.required_item:
            required_item_name = self.world.items[interaction.required_item].name
            if self.progress.inventory.get(interaction.required_item, 0) <= 0:
                return [
                    interaction.missing_item_text
                    or f"You need {required_item_name} to interact with {interaction.name}."
                ]
            if self._charged_item_is_depleted(interaction.required_item):
                return [f"{required_item_name} has no charge left."]

        lines = [
            interaction.interact_text
            or interaction.description
            or f"You interact with {interaction.name}."
        ]
        if interaction.required_item and interaction.consume_required_item:
            self.progress.remove_item(interaction.required_item)
            lines.append(f"You use {required_item_name}.")
        elif used_item_id and interaction.required_item == used_item_id:
            lines.append(f"You use {required_item_name}.")
        if interaction.required_item and not interaction.consume_required_item:
            charge_lines = self._spend_item_charge(interaction.required_item)
            if charge_lines:
                if not used_item_id:
                    lines.append(f"You use {required_item_name}.")
                lines.extend(charge_lines)
        added_flags = self._set_story_flags(interaction.set_flags)
        revealed_exits = [
            f"{hidden_exit.direction} -> {self.world.rooms[hidden_exit.target_room].name}"
            for hidden_exit in room.hidden_exits.values()
            if hidden_exit.required_flag in added_flags
        ]
        if revealed_exits:
            lines.append("A path is revealed: " + ", ".join(revealed_exits) + ".")
        return lines
