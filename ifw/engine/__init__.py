from __future__ import annotations

import random  # Re-exported so existing tests/tools can patch ifw.engine.random.
from typing import Callable

from .companions import EngineCompanionMixin
from .bosses import EngineBossMixin
from .combat import EngineCombatMixin
from .environment import EngineEnvironmentMixin
from .items import EngineItemMixin
from .navigation import EngineNavigationMixin
from .social import EngineSocialMixin
from .state import EngineStateMixin
from .stealth import EngineStealthMixin
from .types import (
    CombatBuff,
    HIT_CHANCE_BASE,
    HIT_CHANCE_MAX,
    HIT_CHANCE_MIN,
    HIT_SCORE_STEP,
    MAX_ACCESSORIES,
    MAX_COMPANIONS,
    BOSS_ENEMY_ATTACK_PER_LEVEL,
    BOSS_ENEMY_DEFENSE_PER_LEVEL,
    BOSS_ENEMY_HP_PER_LEVEL,
    RESPAWN_ROLL_SIDES,
    REST_COST,
    STANDARD_ENEMY_ATTACK_PER_LEVEL,
    STANDARD_ENEMY_DEFENSE_PER_LEVEL,
    STANDARD_ENEMY_HP_PER_LEVEL,
)
from .views import EngineViewMixin
from ..models import Player, World

__all__ = [
    "CombatBuff",
    "GameEngine",
    "HIT_CHANCE_BASE",
    "HIT_CHANCE_MAX",
    "HIT_CHANCE_MIN",
    "HIT_SCORE_STEP",
    "MAX_ACCESSORIES",
    "MAX_COMPANIONS",
    "BOSS_ENEMY_ATTACK_PER_LEVEL",
    "BOSS_ENEMY_DEFENSE_PER_LEVEL",
    "BOSS_ENEMY_HP_PER_LEVEL",
    "RESPAWN_ROLL_SIDES",
    "REST_COST",
    "STANDARD_ENEMY_ATTACK_PER_LEVEL",
    "STANDARD_ENEMY_DEFENSE_PER_LEVEL",
    "STANDARD_ENEMY_HP_PER_LEVEL",
]


class GameEngine(
    EngineStateMixin,
    EngineBossMixin,
    EngineCompanionMixin,
    EngineViewMixin,
    EngineNavigationMixin,
    EngineEnvironmentMixin,
    EngineItemMixin,
    EngineSocialMixin,
    EngineStealthMixin,
    EngineCombatMixin,
):
    def __init__(self, world: World, player: Player, save_callback: Callable[[Player], object]) -> None:
        self.world = world
        self.player = player
        self.save_callback = save_callback
        self.game_over = False
        self.await_close_on_game_over = False
        self.buffs: list[CombatBuff] = []
        self.player_attack_block_turns = 0
        self._ensure_player_wallet()
        self.progress, self._welcome_lines = self._prepare_world_progress()
        self._sync_resources_to_effective_max()

    def opening_lines(self) -> list[str]:
        return [
            f"Welcome, {self.player.name} the {self._player_class_name()}.",
            f"World: {self.world.name}",
            *self._welcome_lines,
            *self.describe_current_room(),
        ]

    def run(self) -> None:
        for line in self.opening_lines():
            print(line)

        while not self.game_over:
            try:
                command = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                self.save()
                print("\nProgress saved.")
                return

            if not command:
                continue

            for line in self.handle_command(command):
                print(line)

            if not self.game_over:
                self.save()

        if self.await_close_on_game_over:
            self._wait_for_close()

    def handle_command(self, command: str) -> list[str]:
        verb, _, remainder = command.strip().partition(" ")
        verb = verb.lower()
        remainder = remainder.strip()

        try:
            if verb in {"boss", "confront", "confrontation"}:
                return self._choose_boss_option(remainder)
            if verb in {"choose", "select"} and remainder.lower().startswith("boss "):
                return self._choose_boss_option(remainder[5:].strip())
            if (
                self._pending_boss_encounter() is not None
                and not self._boss_confrontation_allows_command(verb, remainder)
            ):
                return [
                    "The boss confrontation must be resolved before you act.",
                    *self._boss_encounter_lines(),
                ]
            if verb in {"north", "south", "east", "west", "up", "down", "in", "out"}:
                return self._move(verb)
            if verb in {"n", "s", "e", "w", "u", "d"}:
                mapping = {"n": "north", "s": "south", "e": "east", "w": "west", "u": "up", "d": "down"}
                return self._move(mapping[verb])
            if verb in {"go", "move"}:
                return self._move(remainder.lower())
            if verb in {"retreat", "flee"}:
                return self._retreat()
            if verb in {"look", "l"}:
                return self._look(remainder)
            if verb in {"examine", "inspect", "x"}:
                return self._examine(remainder)
            if verb in {"interact", "activate", "search"}:
                return self._interact_with_room_object(remainder)
            if verb in {"answer", "password", "passcode", "say"}:
                return self._answer_room_password(remainder)
            if verb == "pickpocket":
                return self._pickpocket(remainder)
            if verb == "lockpick":
                return self._lockpick(remainder)
            if verb == "bail" or (verb == "pay" and remainder.lower() in {"bail", "fine"}):
                return self._pay_bail()
            if verb == "escape" and remainder.lower() in {"jail", "cell"}:
                return self._escape_jail()
            if verb in {"inventory", "inv", "i"}:
                return self._show_inventory()
            if verb in {"keyring", "keys"} or (verb == "key" and remainder.lower() == "ring"):
                return self._show_key_ring()
            if verb == "storage":
                return self._show_storage()
            if verb == "store":
                return self._store_item(remainder)
            if verb in {"retrieve", "withdraw"}:
                return self._retrieve_item(remainder)
            if verb in {"stats", "status"}:
                return self._show_stats()
            if verb in {"wallet", "money", "currencies"}:
                return self._show_wallet()
            if verb in {"companions", "party"}:
                return self._show_companions()
            if verb == "recruit":
                return self._recruit_companion(remainder)
            if verb == "dismiss":
                return self._dismiss_companion(remainder)
            if verb == "rest":
                return self._rest()
            if verb == "quests":
                return self._show_quests()
            if verb in {"ending", "end"}:
                return self._choose_ending(remainder)
            if verb in {"choose", "select"} and remainder.lower().startswith("ending "):
                return self._choose_ending(remainder[7:].strip())
            if verb == "spells":
                return self._show_spells()
            if verb == "recipes":
                return self._show_recipes()
            if verb == "take":
                return self._take_item(remainder)
            if verb == "drop":
                return self._drop_item(remainder)
            if verb == "equip":
                return self._equip_item(remainder)
            if verb == "unequip":
                return self._unequip_item(remainder)
            if verb == "use":
                if (
                    self._match_from_names(remainder, self._visible_item_pool()) is None
                    and self._match_room_interaction(remainder) is not None
                ):
                    return self._interact_with_room_object(remainder)
                return self._use_item(remainder)
            if verb == "talk":
                return self._talk_to(remainder)
            if verb == "accept":
                return self._accept_quest(remainder)
            if verb == "shop":
                return self._show_shop()
            if verb == "buy":
                return self._buy_item(remainder)
            if verb == "sell":
                return self._sell_item(remainder)
            if verb == "exchange":
                return self._exchange_currency(remainder)
            if verb == "rates":
                return self._show_exchange_rates()
            if verb == "craft":
                return self._craft_item(remainder)
            if verb == "combine":
                return self._combine_items(remainder)
            if verb == "attack":
                return self._attack_enemy(remainder)
            if verb == "cast":
                return self._cast_spell(remainder)
            if verb == "save":
                self.save()
                return ["Progress saved."]
            if verb in {"quit", "exit"}:
                self.save()
                self.game_over = True
                return ["Progress saved. Farewell, adventurer."]
            if verb == "help":
                return self._help_lines()
            return ["Unknown command. Type 'help' to see the command list."]
        except ValueError as exc:
            return [str(exc)]

    def save(self) -> None:
        self.save_callback(self.player)

    def _wait_for_close(self) -> None:
        try:
            import msvcrt

            print("\nPress any key to close...", end="", flush=True)
            msvcrt.getwch()
            print()
        except ImportError:
            input("\nPress Enter to close...")
