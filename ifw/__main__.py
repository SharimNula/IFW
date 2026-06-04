from __future__ import annotations

import argparse

from .engine import GameEngine
from .models import Player, PlayerClass, World
from .persistence import (
    ensure_data_directories,
    find_world_file,
    list_world_files,
    load_player,
    save_player,
    slugify,
)
from .world_loader import load_world


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Play an XML-driven interactive fiction RPG.")
    parser.add_argument("--world", help="Path or short name of the world folder or XML file to load.")
    parser.add_argument("--player", help="Existing player name or the new player name to create.")
    return parser


def choose_world(world_arg: str | None) -> str:
    if world_arg:
        path = find_world_file(world_arg)
        if path is None:
            raise SystemExit(f"Could not find a world matching '{world_arg}'.")
        return str(path)

    worlds = list_world_files()
    if not worlds:
        raise SystemExit("No worlds were found in the worlds directory.")

    print("Available worlds:")
    for index, path in enumerate(worlds, start=1):
        print(f"  {index}. {path.stem}")

    while True:
        choice = input("Choose a world number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(worlds):
            return str(worlds[int(choice) - 1])
        print("Please enter one of the listed numbers.")


def choose_player(player_arg: str | None, world: World) -> Player:
    if player_arg:
        existing = load_player(player_arg)
        if existing is not None:
            warn_if_player_class_missing(existing, world)
            return existing
        return create_player(player_arg, world)

    name = input("Enter your character name: ").strip()
    while not name:
        name = input("Enter your character name: ").strip()

    existing = load_player(name)
    if existing is not None:
        warn_if_player_class_missing(existing, world)
        return existing
    return create_player(name, world)


def warn_if_player_class_missing(player: Player, world: World) -> None:
    if player.player_class.lower() in world.player_classes:
        return
    print(
        f"Warning: {player.name}'s saved class '{player.player_class}' is not defined "
        f"in {world.name}. Class-specific world content may be unavailable."
    )


def _class_choice_key(value: str) -> str:
    return slugify(value).replace("-", "_")


def _class_choice_matches(choice: str, class_id: str, player_class: PlayerClass) -> bool:
    choice_key = _class_choice_key(choice)
    return choice_key in {class_id, _class_choice_key(player_class.name)}


def create_player(name: str, world: World) -> Player:
    print(f"Choose a class for {world.name}:")
    class_ids = list(world.player_classes)
    for index, class_id in enumerate(class_ids, start=1):
        player_class = world.player_classes[class_id]
        currencies = player_class.starting_currencies or {"gold": player_class.gold}
        currency_summary = ", ".join(
            f"{amount} {world.currencies.get(currency_id, world.currencies['gold']).plural}"
            for currency_id, amount in currencies.items()
            if amount
        ) or "no money"
        summary = (
            f"HP {player_class.max_hp}, MP {player_class.max_mp}, "
            f"Attack {player_class.base_attack}, Defense {player_class.base_defense}, "
            f"Currency {currency_summary}"
        )
        print(f"  {index}. {player_class.name} ({class_id}) - {summary}")
        if player_class.description:
            print(f"     {player_class.description}")

    while True:
        choice = input("Class: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(class_ids):
            class_name = class_ids[int(choice) - 1]
            break
        matching_class = next(
            (
                class_id
                for class_id in class_ids
                if _class_choice_matches(choice, class_id, world.player_classes[class_id])
            ),
            None,
        )
        if matching_class:
            class_name = matching_class
            break
        print("Please choose one of the listed classes.")

    template = world.player_classes[class_name]
    wallet = dict(template.starting_currencies or {"gold": template.gold})
    starting_gold = wallet.get("gold", template.gold)
    player = Player(
        name=name,
        player_class=class_name,
        level=1,
        experience=0,
        gold=starting_gold,
        max_hp=template.max_hp,
        hp=template.max_hp,
        max_mp=template.max_mp,
        mp=template.max_mp,
        base_attack=template.base_attack,
        base_defense=template.base_defense,
        wallet=wallet,
    )
    save_player(player)
    return player


def main() -> None:
    ensure_data_directories()
    parser = build_parser()
    args = parser.parse_args()

    world_path = choose_world(args.world)
    world = load_world(world_path)
    player = choose_player(args.player, world)

    engine = GameEngine(world=world, player=player, save_callback=save_player)
    engine.run()


if __name__ == "__main__":
    main()
