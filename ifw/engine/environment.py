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

    def _answer_room_password(self, query: str) -> list[str]:
        if not query:
            return ["Answer with what?"]
        if self._has_active_threats():
            return ["You cannot interact with the environment while threats are active in the room."]

        interaction_id, answer = self._parse_password_answer(query)
        if interaction_id is None:
            return ["There is nothing here that asks for that password."]
        if not answer:
            return [
                "Use 'answer <object> with <password>' or "
                "'answer <password>' when only one password object is here."
            ]
        return self._resolve_password_interaction(interaction_id, answer)

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
        already_done = self._room_interaction_already_done(interaction)
        if already_done and not interaction.repeatable:
            return [
                interaction.completed_text
                or f"You have already done what you can with {interaction.name}."
            ]
        if interaction.password:
            return [
                f"{interaction.name} asks for a password. "
                "Use 'answer <password>' or 'answer <object> with <password>'."
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
        lines.extend(self._apply_room_interaction_flags(room, interaction))
        return lines

    def _resolve_password_interaction(self, interaction_id: str, answer: str) -> list[str]:
        room = self._current_room()
        interaction = room.interactions[interaction_id]
        if not interaction.password:
            return [f"{interaction.name} does not ask for a password."]
        if self._room_interaction_already_done(interaction) and not interaction.repeatable:
            return [
                interaction.completed_text
                or f"You have already done what you can with {interaction.name}."
            ]
        if self._normalize(answer) != self._normalize(interaction.password):
            return [
                interaction.password_failed_text
                or f"{interaction.name} does not respond to that password."
            ]

        lines = [
            interaction.password_text
            or interaction.interact_text
            or f"You speak the password to {interaction.name}."
        ]
        lines.extend(self._apply_room_interaction_flags(room, interaction))
        return lines

    def _parse_password_answer(self, query: str) -> tuple[str | None, str]:
        lower_query = query.lower()
        for delimiter in (" with ", " as "):
            if delimiter not in lower_query:
                continue
            split_at = lower_query.index(delimiter)
            interaction_query = query[:split_at].strip()
            answer = query[split_at + len(delimiter):].strip()
            return self._match_password_interaction(interaction_query), answer

        password_interactions = self._visible_password_interactions()
        if len(password_interactions) == 1:
            return next(iter(password_interactions)), query.strip()
        return self._match_password_interaction(query), ""

    def _visible_password_interactions(self) -> dict[str, object]:
        return {
            interaction_id: interaction
            for interaction_id, interaction in self._visible_room_interactions().items()
            if interaction.password
        }

    def _match_password_interaction(self, query: str) -> str | None:
        return self._match_from_names(
            query,
            {
                interaction_id: interaction.name
                for interaction_id, interaction in self._visible_password_interactions().items()
            },
        )

    def _room_interaction_already_done(self, interaction) -> bool:
        return bool(interaction.set_flags) and all(
            self._has_story_flag(flag) for flag in interaction.set_flags
        )

    def _apply_room_interaction_flags(self, room, interaction) -> list[str]:
        added_flags = self._set_story_flags(interaction.set_flags)
        revealed_exits = [
            f"{hidden_exit.direction} -> {self.world.rooms[hidden_exit.target_room].name}"
            for hidden_exit in room.hidden_exits.values()
            if hidden_exit.required_flag in added_flags
        ]
        lines: list[str] = []
        if revealed_exits:
            lines.append("A path is revealed: " + ", ".join(revealed_exits) + ".")
        return lines
