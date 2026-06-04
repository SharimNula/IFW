from __future__ import annotations

from dataclasses import dataclass

MAX_ACCESSORIES = 3
MAX_COMPANIONS = 2
REST_COST = 10
RESPAWN_ROLL_SIDES = 6
HIT_CHANCE_BASE = 70
HIT_CHANCE_MIN = 35
HIT_CHANCE_MAX = 95
HIT_SCORE_STEP = 5
STANDARD_ENEMY_HP_PER_LEVEL = 8
STANDARD_ENEMY_ATTACK_PER_LEVEL = 2
STANDARD_ENEMY_DEFENSE_PER_LEVEL = 1
BOSS_ENEMY_HP_PER_LEVEL = 22
BOSS_ENEMY_ATTACK_PER_LEVEL = 3
BOSS_ENEMY_DEFENSE_PER_LEVEL = 2


@dataclass(slots=True)
class CombatBuff:
    spell_id: str
    name: str
    attack_bonus: int = 0
    armor_bonus: int = 0
    pickpocket_bonus: int = 0
    lockpick_bonus: int = 0
    remaining_turns: int = 0
    tick_on: str = ""
    target_id: str = "player"
