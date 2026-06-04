from __future__ import annotations

import xml.etree.ElementTree as ET

from ..models import Quest, QuestEndingChoice, QuestFlagBranch, QuestFlagOutcome
from ..world_loader_xml import (
    _first_attr,
    _optional_text,
    _parse_bool,
    _parse_id_list,
    _parse_int,
    _required_attr,
    _required_attr_any,
)
from .common import first_child, optional_int_attr, optional_present_attr


def parse_quests(root: ET.Element) -> dict[str, Quest]:
    quests: dict[str, Quest] = {}
    for quest_element in root.findall("./quests/quest"):
        ending_text, ending_text_by_faction, ending_choices = parse_quest_endings(quest_element)
        flag_outcome = parse_quest_flag_outcome(quest_element)
        quest = Quest(
            quest_id=_required_attr(quest_element, "id"),
            name=_required_attr(quest_element, "name"),
            giver_id=_required_attr(quest_element, "giver"),
            description=_optional_text(quest_element.find("description")),
            completion_text=_optional_text(quest_element.find("completion_text")),
            offer_dialogue=_optional_text(quest_element.find("offer_dialogue")),
            active_dialogue=_optional_text(quest_element.find("active_dialogue")),
            completed_dialogue=_optional_text(quest_element.find("completed_dialogue")),
            accept_item=quest_element.get("accept_item"),
            target_enemy=quest_element.get("target_enemy"),
            required_item=quest_element.get("required_item"),
            destination_room=quest_element.get("destination_room"),
            reward_gold=_parse_int(quest_element.get("reward_gold")),
            reward_currency=_first_attr(quest_element, "reward_currency", "currency") or "gold",
            reward_amount=optional_int_attr(
                quest_element,
                "reward_amount",
                "reward_money",
                "reward_currency_amount",
                "currency_amount",
            ),
            reward_exp=_parse_int(quest_element.get("reward_exp")),
            reward_item=quest_element.get("reward_item"),
            reward_recipe=quest_element.get("reward_recipe"),
            ends_world=(
                _parse_bool(
                    _first_attr(
                        quest_element,
                        "ending",
                        "ends_world",
                        "ending_quest",
                        "final_quest",
                    ),
                    default=False,
                )
                or bool(ending_text)
                or bool(ending_text_by_faction)
                or bool(ending_choices)
            ),
            ending_text=ending_text,
            ending_text_by_faction=ending_text_by_faction,
            ending_choices=ending_choices,
            flag_outcome=flag_outcome,
        )
        quests[quest.quest_id] = quest
    return quests


def parse_quest_flag_outcome(quest_element: ET.Element) -> QuestFlagOutcome | None:
    outcome_element = first_child(
        quest_element,
        "flag_outcome",
        "flag_check",
        "flag_result",
        "story_flag_outcome",
    )
    if outcome_element is None:
        return None
    return QuestFlagOutcome(
        flag=_required_attr_any(outcome_element, "flag", "story_flag", "check_flag"),
        when_true=parse_quest_flag_branch(
            first_child(outcome_element, "true", "when_true", "set", "flag_set")
        ),
        when_false=parse_quest_flag_branch(
            first_child(outcome_element, "false", "when_false", "unset", "flag_unset")
        ),
    )


def parse_quest_flag_branch(branch_element: ET.Element | None) -> QuestFlagBranch:
    if branch_element is None:
        return QuestFlagBranch()
    return QuestFlagBranch(
        completion_text=(
            _optional_text(branch_element.find("completion_text"))
            or _first_attr(branch_element, "completion_text", "text")
            or None
        ),
        reward_gold=optional_int_attr(branch_element, "reward_gold", "gold"),
        reward_currency=_first_attr(branch_element, "reward_currency", "currency"),
        reward_amount=optional_int_attr(
            branch_element,
            "reward_amount",
            "reward_money",
            "reward_currency_amount",
            "currency_amount",
        ),
        reward_exp=optional_int_attr(branch_element, "reward_exp", "exp", "experience"),
        reward_item=optional_present_attr(branch_element, "reward_item", "item"),
        reward_recipe=optional_present_attr(branch_element, "reward_recipe", "recipe"),
    )


def parse_quest_endings(
    quest_element: ET.Element,
) -> tuple[str, dict[str, str], list[QuestEndingChoice]]:
    ending_text = (
        _optional_text(quest_element.find("ending_text"))
        or _optional_text(quest_element.find("default_ending"))
    )
    endings_element = quest_element.find("endings")
    if endings_element is not None:
        ending_text = (
            ending_text
            or _optional_text(endings_element.find("default"))
            or _optional_text(endings_element.find("default_ending"))
        )

    ending_text_by_faction: dict[str, str] = {}
    ending_elements = quest_element.findall("./ending") + quest_element.findall("./endings/ending")
    for ending_element in ending_elements:
        faction_id = _first_attr(ending_element, "faction", "faction_id")
        text = _optional_text(ending_element)
        if faction_id:
            ending_text_by_faction[faction_id] = text
        elif text and not ending_text:
            ending_text = text

    ending_choices: list[QuestEndingChoice] = []
    for index, choice_element in enumerate(quest_element.findall("./ending_choices/choice"), start=1):
        ending_choices.append(
            QuestEndingChoice(
                choice_id=choice_element.get("id", "").strip() or str(index),
                label=(
                    choice_element.get("label", "").strip()
                    or choice_element.get("name", "").strip()
                    or f"Ending {index}"
                ),
                text=parse_ending_choice_text(choice_element),
                ending_type=_normalize_ending_choice_type(
                    _first_attr(choice_element, "type", "ending", "source")
                ),
                required_flags=parse_ending_choice_required_flags(choice_element),
            )
        )
    return ending_text, ending_text_by_faction, ending_choices


def parse_ending_choice_text(choice_element: ET.Element) -> str:
    return " ".join(part.strip() for part in choice_element.itertext() if part.strip())


def parse_ending_choice_required_flags(choice_element: ET.Element) -> list[str]:
    required_flags = _parse_id_list(
        _first_attr(
            choice_element,
            "required_flags",
            "requires_flags",
            "visible_if_flags",
            "required_flag",
            "requires_flag",
            "visible_if_flag",
        )
    )
    required_flags.extend(
        _required_attr_any(flag_element, "id", "name")
        for flag_element in (
            choice_element.findall("./required_flag")
            + choice_element.findall("./required_flags/flag")
        )
    )
    return required_flags


def _normalize_ending_choice_type(value: str) -> str:
    normalized = (value or "custom").strip().lower().replace("-", "_")
    if normalized in {"default", "non_faction", "nonfaction", "neutral"}:
        return "default"
    if normalized in {"faction", "faction_specific", "pledge"}:
        return "faction"
    return "custom"
