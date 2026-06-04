from __future__ import annotations

from ..models import Spell


class EngineLookupStateMixin:
    def _normalize(self, value: str) -> str:
        return "".join(char.lower() for char in value if char.isalnum() or char.isspace()).strip()

    def _match_from_names(self, query: str, candidates: dict[str, str]) -> str | None:
        normalized_query = self._normalize(query)
        if not normalized_query:
            return None

        exact_matches = [
            candidate_id
            for candidate_id, candidate_name in candidates.items()
            if normalized_query in {self._normalize(candidate_id), self._normalize(candidate_name)}
        ]
        if exact_matches:
            return exact_matches[0]

        partial_matches = [
            candidate_id
            for candidate_id, candidate_name in candidates.items()
            if normalized_query in self._normalize(candidate_name)
            or normalized_query in self._normalize(candidate_id)
        ]
        if partial_matches:
            return partial_matches[0]
        return None

    def _item_name(self, item_id: str) -> str:
        return self.world.items[item_id].name

    def _recipe_name(self, recipe_id: str) -> str:
        return self.world.recipes[recipe_id].name

    def _spell_name(self, spell_id: str) -> str:
        return self.world.spells[spell_id].name

    def _class_label(self, class_name: str) -> str:
        player_class = self.world.player_classes.get(class_name.lower())
        if player_class is not None:
            return player_class.name
        return class_name.replace("_", " ").title()

    def _player_class_definition(self):
        return self.world.player_classes.get(self.player.player_class.lower())

    def _player_class_name(self) -> str:
        return self._class_label(self.player.player_class)

    def _faction_name(self, faction_id: str) -> str:
        faction = self.world.factions.get(faction_id)
        if faction is not None:
            return faction.name
        return faction_id.replace("_", " ").title()

    def _spell_class_label(self, spell: Spell) -> str:
        return ", ".join(self._class_label(class_name) for class_name in spell.allowed_classes)

    def _spell_allowed_for_player(self, spell_id: str) -> bool:
        return self._spell_allowed_for_class(spell_id, self.player.player_class)

    def _spell_allowed_for_class(self, spell_id: str, class_id: str) -> bool:
        spell = self.world.spells[spell_id]
        if not spell.allowed_classes or "all" in spell.allowed_classes:
            return True
        return class_id.lower() in spell.allowed_classes

    def _spell_restriction_message(self, spell: Spell, action: str) -> str:
        return f"{spell.name} can only be {action} by {self._spell_class_label(spell)} characters."
