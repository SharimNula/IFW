from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from ..models import FactionEnemySpawn, HiddenExit, MiningDrop, Room, RoomInteraction
from ..world_loader_xml import (
    _first_attr,
    _optional_text,
    _parse_bool,
    _parse_id_list,
    _parse_int,
    _required_attr,
    _required_attr_any,
)


def parse_rooms(root: ET.Element, source: Path) -> dict[str, Room]:
    rooms: dict[str, Room] = {}
    for room_element in root.findall("./rooms/room"):
        room = parse_room(room_element, source)
        rooms[room.room_id] = room
    return rooms


def parse_room(room_element: ET.Element, source: Path) -> Room:
    room_id = _required_attr(room_element, "id")
    exits, hidden_exits = parse_room_exits(room_element)
    mining_drops, mining_message = parse_mining(room_element, room_id, source)
    maze = parse_maze(room_element)
    return Room(
        room_id=room_id,
        name=_required_attr(room_element, "name"),
        description=_optional_text(room_element.find("description")),
        exits=exits,
        hidden_exits=hidden_exits,
        interactions=parse_room_interactions(room_element),
        companion_dialogue=parse_companion_dialogue(room_element),
        item_ids=[
            _required_attr(item_ref, "id") for item_ref in room_element.findall("./items/item_ref")
        ],
        enemy_ids=[
            _required_attr(enemy_ref, "id")
            for enemy_ref in room_element.findall("./enemies/enemy_ref")
        ],
        faction_enemy_spawns=parse_faction_enemy_spawns(room_element),
        monster_pool_id=room_element.get("monster_pool"),
        monster_count=_parse_int(
            room_element.get("monster_count"),
            default=1 if room_element.get("monster_pool") else 0,
        ),
        npc_ids=[
            _required_attr(npc_ref, "id") for npc_ref in room_element.findall("./npcs/npc_ref")
        ],
        vendor_ids=[
            _required_attr(vendor_ref, "id")
            for vendor_ref in room_element.findall("./vendors/vendor_ref")
        ],
        has_storage=_parse_bool(room_element.get("storage"), default=False),
        can_rest=_parse_bool(room_element.get("rest"), default=False),
        locks_on_exit=_parse_bool(room_element.get("locks_on_exit"), default=False),
        required_item=room_element.get("required_item"),
        locked_message=_optional_text(room_element.find("locked_message")),
        sealed_message=_optional_text(room_element.find("sealed_message")),
        maze_sequence=maze["maze_sequence"],
        maze_success_room=maze["maze_success_room"],
        maze_progress_message=maze["maze_progress_message"],
        maze_failure_message=maze["maze_failure_message"],
        maze_success_message=maze["maze_success_message"],
        mining_drops=mining_drops,
        mining_message=mining_message,
    )


def parse_companion_dialogue(room_element: ET.Element) -> list[str]:
    dialogue_elements = (
        room_element.findall("./companion_dialogue/line")
        + room_element.findall("./companion_dialogue/dialogue")
        + room_element.findall("./companion_dialogues/dialogue")
    )
    dialogue = [
        text
        for dialogue_element in dialogue_elements
        if (text := _optional_text(dialogue_element))
    ]
    if dialogue:
        return dialogue

    room_name = _required_attr(room_element, "name")
    return [
        f"{room_name} feels like the sort of place that rewards a careful second look.",
        f"Keep an eye on the edges of {room_name}; secrets rarely wait in the middle.",
    ]


def parse_room_exits(room_element: ET.Element) -> tuple[dict[str, str], dict[str, HiddenExit]]:
    exits: dict[str, str] = {}
    hidden_exits: dict[str, HiddenExit] = {}
    for exit_element in room_element.findall("./exits/exit"):
        direction = _required_attr(exit_element, "direction").lower()
        target_room = _required_attr(exit_element, "to")
        required_flag = _first_attr(
            exit_element,
            "required_flag",
            "requires_flag",
            "revealed_by_flag",
            "hidden_until_flag",
            "flag",
        )
        if required_flag:
            hidden_exits[direction] = HiddenExit(
                direction=direction,
                target_room=target_room,
                required_flag=required_flag,
            )
        else:
            exits[direction] = target_room
    for exit_element in room_element.findall("./hidden_exits/exit"):
        direction = _required_attr(exit_element, "direction").lower()
        hidden_exits[direction] = HiddenExit(
            direction=direction,
            target_room=_required_attr(exit_element, "to"),
            required_flag=_required_attr_any(
                exit_element,
                "required_flag",
                "requires_flag",
                "revealed_by_flag",
                "hidden_until_flag",
                "flag",
            ),
        )
    return exits, hidden_exits


def parse_room_interactions(room_element: ET.Element) -> dict[str, RoomInteraction]:
    interactions: dict[str, RoomInteraction] = {}
    for interaction_element in (
        room_element.findall("./interactions/object")
        + room_element.findall("./interactions/interaction")
        + room_element.findall("./objects/object")
    ):
        interaction = parse_room_interaction(interaction_element)
        interactions[interaction.interaction_id] = interaction
    return interactions


def parse_room_interaction(interaction_element: ET.Element) -> RoomInteraction:
    interaction_id = _required_attr(interaction_element, "id")
    required_item, missing_item_text, consume_required_item = parse_interaction_item_requirement(
        interaction_element
    )
    set_flags = _parse_id_list(
        _first_attr(
            interaction_element,
            "set_flag",
            "sets_flag",
            "set_flags",
            "reveals_flag",
            "reveal_flag",
        )
    )
    set_flags.extend(
        _required_attr_any(flag_element, "id", "name")
        for flag_element in interaction_element.findall("./set_flag")
    )
    return RoomInteraction(
        interaction_id=interaction_id,
        name=interaction_element.get("name", "").strip()
        or interaction_id.replace("_", " ").title(),
        description=_optional_text(interaction_element.find("description")),
        interact_text=(
            _optional_text(interaction_element.find("interact_text"))
            or _optional_text(interaction_element.find("success_text"))
        ),
        completed_text=_optional_text(interaction_element.find("completed_text")),
        password=_first_attr(
            interaction_element,
            "password",
            "answer",
            "passcode",
        )
        or "",
        password_text=(
            _optional_text(interaction_element.find("password_text"))
            or _optional_text(interaction_element.find("password_success_text"))
        ),
        password_failed_text=(
            _optional_text(interaction_element.find("password_failed_text"))
            or _optional_text(interaction_element.find("password_failure_text"))
        ),
        required_flag=_first_attr(
            interaction_element,
            "required_flag",
            "requires_flag",
            "visible_if_flag",
        ),
        required_item=required_item,
        missing_item_text=missing_item_text,
        consume_required_item=consume_required_item,
        set_flags=set_flags,
        repeatable=_parse_bool(interaction_element.get("repeatable"), default=False),
        lockpickable=_parse_bool(
            _first_attr(
                interaction_element,
                "lockpick",
                "lockpickable",
                "can_lockpick",
            ),
            default=False,
        ),
        lockpick_difficulty=_parse_int(
            _first_attr(interaction_element, "lockpick_difficulty", "lockpick_dc", "lock_dc")
        ),
        lockpick_item=_first_attr(
            interaction_element,
            "lockpick_item",
            "lockpick_required_item",
        ) or "lockpicks",
        lockpick_text=(
            _optional_text(interaction_element.find("lockpick_text"))
            or _optional_text(interaction_element.find("lockpick_success_text"))
        ),
        lockpick_failed_text=(
            _optional_text(interaction_element.find("lockpick_failed_text"))
            or _optional_text(interaction_element.find("lockpick_failure_text"))
        ),
        lockpick_missing_item_text=_optional_text(
            interaction_element.find("lockpick_missing_item_text")
        ),
    )


def parse_interaction_item_requirement(
    interaction_element: ET.Element,
) -> tuple[str | None, str, bool]:
    required_item_element = interaction_element.find("required_item")
    required_item = _first_attr(
        interaction_element,
        "required_item",
        "requires_item",
        "item",
    )
    consume_required_item = _parse_bool(
        _first_attr(
            interaction_element,
            "consume_item",
            "consume_required_item",
        ),
        default=False,
    )
    missing_item_text = _optional_text(interaction_element.find("missing_item_text"))
    if required_item_element is not None:
        required_item = _required_attr(required_item_element, "id")
        consume_required_item = _parse_bool(
            _first_attr(
                required_item_element,
                "consume",
                "consume_item",
                "consume_required_item",
            ),
            default=consume_required_item,
        )
        missing_item_text = (
            _optional_text(required_item_element.find("missing_text"))
            or _optional_text(required_item_element.find("missing_item_text"))
            or missing_item_text
        )
    return required_item, missing_item_text, consume_required_item


def parse_maze(room_element: ET.Element) -> dict[str, object]:
    maze_element = room_element.find("maze")
    if maze_element is None:
        return {
            "maze_sequence": [],
            "maze_success_room": None,
            "maze_progress_message": "",
            "maze_failure_message": "",
            "maze_success_message": "",
        }

    sequence_attr = maze_element.get("sequence", "")
    if sequence_attr:
        maze_sequence = [
            direction.strip().lower()
            for direction in sequence_attr.split(",")
            if direction.strip()
        ]
    else:
        maze_sequence = [
            _required_attr(step_element, "direction").lower()
            for step_element in maze_element.findall("./step")
        ]

    return {
        "maze_sequence": maze_sequence,
        "maze_success_room": _required_attr(maze_element, "success_room"),
        "maze_progress_message": _optional_text(maze_element.find("progress_message")),
        "maze_failure_message": _optional_text(maze_element.find("failure_message")),
        "maze_success_message": _optional_text(maze_element.find("success_message")),
    }


def parse_mining(
    room_element: ET.Element, room_id: str, source: Path
) -> tuple[list[MiningDrop], str]:
    mining_element = room_element.find("mining")
    if mining_element is None:
        return [], ""

    mining_message = (
        mining_element.get("message", "").strip()
        or _optional_text(mining_element.find("message"))
    )
    mining_drops = [
        MiningDrop(
            item_id=_required_attr(mining_item, "id"),
            min_quantity=_parse_int(
                mining_item.get("min") or mining_item.get("min_quantity"),
                default=1,
            ),
            max_quantity=_parse_int(
                mining_item.get("max") or mining_item.get("max_quantity"),
                default=3,
            ),
        )
        for mining_item in mining_element.findall("./item_ref")
    ]
    if not mining_drops:
        raise ValueError(f"{source}: room '{room_id}' mining block has no item references.")
    return mining_drops, mining_message


def parse_faction_enemy_spawns(room_element: ET.Element) -> list[FactionEnemySpawn]:
    faction_enemy_spawns: list[FactionEnemySpawn] = []
    for faction_enemy_element in (
        room_element.findall("./faction_enemies/enemy_ref")
        + room_element.findall("./faction_spawns/enemy_ref")
    ):
        faction_enemy_spawns.append(
            FactionEnemySpawn(
                faction_id=_required_attr_any(
                    faction_enemy_element,
                    "faction",
                    "faction_id",
                    "player_faction",
                ),
                enemy_id=_required_attr(faction_enemy_element, "id"),
                count=_parse_int(
                    faction_enemy_element.get("count")
                    or faction_enemy_element.get("max_count"),
                    default=1,
                ),
            )
        )
    return faction_enemy_spawns
