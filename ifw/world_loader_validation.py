from __future__ import annotations

from pathlib import Path

from .models import NPC, Room, World


MAX_ENDING_CHOICES = 10
ITEM_TYPES = {
    "weapon",
    "armor",
    "accessory",
    "consumable",
    "spellbook",
    "utility",
    "misc",
    "material",
    "quest",
    "key",
}
CHARGED_ITEM_TYPES = {
    "weapon",
    "armor",
    "accessory",
    "utility",
    "misc",
    "quest",
    "key",
}


def validate_world(world: World, source: Path) -> None:
    validate_currencies(world, source)
    validate_player_classes(world, source)
    validate_factions(world, source)
    validate_start_and_end_rooms(world, source)
    validate_rooms(world, source)
    validate_jail(world, source)
    validate_items(world, source)
    validate_spells(world, source)
    validate_enemies(world, source)
    validate_monster_pools(world, source)
    validate_quests(world, source)
    validate_recipes(world, source)
    validate_starter_loadouts(world, source)
    validate_npcs(world, source)
    validate_vendors(world, source)
    validate_enemy_loot(world, source)


def validate_currencies(world: World, source: Path) -> None:
    if not world.currencies:
        raise ValueError(f"{source}: world must define at least one currency.")
    if world.default_currency_id not in world.currencies:
        raise ValueError(
            f"{source}: default currency '{world.default_currency_id}' is not defined."
        )
    for currency_id, currency in world.currencies.items():
        if not currency_id.strip():
            raise ValueError(f"{source}: currency ids must not be empty.")
        if not currency.name.strip():
            raise ValueError(f"{source}: currency '{currency_id}' must have a name.")
        if not currency.singular.strip() or not currency.plural.strip():
            raise ValueError(
                f"{source}: currency '{currency_id}' must define singular and plural names."
            )


def validate_player_classes(world: World, source: Path) -> None:
    if not world.player_classes:
        raise ValueError(f"{source}: world must define at least one player class.")
    for class_id, player_class in world.player_classes.items():
        if class_id == "all":
            raise ValueError(f"{source}: player class id 'all' is reserved.")
        if not player_class.name.strip():
            raise ValueError(f"{source}: player class '{class_id}' must have a name.")
        if player_class.max_hp < 1:
            raise ValueError(f"{source}: player class '{class_id}' must use max_hp >= 1.")
        if player_class.max_mp < 0:
            raise ValueError(f"{source}: player class '{class_id}' must use max_mp >= 0.")
        if player_class.gold < 0:
            raise ValueError(f"{source}: player class '{class_id}' must use gold >= 0.")
        if player_class.base_attack < 0:
            raise ValueError(f"{source}: player class '{class_id}' must use base_attack >= 0.")
        if player_class.base_defense < 0:
            raise ValueError(f"{source}: player class '{class_id}' must use base_defense >= 0.")
        if player_class.hp_per_level < 0:
            raise ValueError(f"{source}: player class '{class_id}' must use hp_per_level >= 0.")
        if player_class.mp_per_level < 0:
            raise ValueError(f"{source}: player class '{class_id}' must use mp_per_level >= 0.")
        if player_class.attack_per_level < 0:
            raise ValueError(
                f"{source}: player class '{class_id}' must use attack_per_level >= 0."
            )
        if player_class.defense_per_level < 0:
            raise ValueError(
                f"{source}: player class '{class_id}' must use defense_per_level >= 0."
            )
        if not 0 <= player_class.pickpocket_chance <= 100:
            raise ValueError(
                f"{source}: player class '{class_id}' pickpocket_chance must be between 0 and 100."
            )
        if not 0 <= player_class.lockpick_chance <= 100:
            raise ValueError(
                f"{source}: player class '{class_id}' lockpick_chance must be between 0 and 100."
            )
        for currency_id, amount in player_class.starting_currencies.items():
            if currency_id not in world.currencies:
                raise ValueError(
                    f"{source}: player class '{class_id}' starts with unknown currency "
                    f"'{currency_id}'."
                )
            if amount < 0:
                raise ValueError(
                    f"{source}: player class '{class_id}' starting currency "
                    f"'{currency_id}' must be >= 0."
                )


def validate_factions(world: World, source: Path) -> None:
    for faction_id, faction in world.factions.items():
        if not faction_id.strip():
            raise ValueError(f"{source}: faction ids must not be empty.")
        if not faction.name.strip():
            raise ValueError(f"{source}: faction '{faction_id}' must have a name.")


def validate_start_and_end_rooms(world: World, source: Path) -> None:
    if world.start_room not in world.rooms:
        raise ValueError(f"{source}: start_room '{world.start_room}' does not exist.")
    if world.end_room is None:
        return
    if world.start_room == world.end_room:
        raise ValueError(f"{source}: start_room and end_room must be different.")
    if world.end_room not in world.rooms:
        raise ValueError(f"{source}: end_room '{world.end_room}' does not exist.")


def validate_jail(world: World, source: Path) -> None:
    if world.jail_room is not None and world.jail_room not in world.rooms:
        raise ValueError(f"{source}: jail room '{world.jail_room}' does not exist.")
    if world.jail_fee < 0:
        raise ValueError(f"{source}: jail fee must be >= 0.")
    if world.jail_currency not in world.currencies:
        raise ValueError(
            f"{source}: jail currency '{world.jail_currency}' is not defined."
        )
    if world_has_pickpocket_targets(world) and world.jail_room is None:
        raise ValueError(f"{source}: pickpocket targets require a jail room.")


def world_has_pickpocket_targets(world: World) -> bool:
    return any(npc.pickpocket_targets for npc in world.npcs.values()) or any(
        vendor.pickpocket_targets for vendor in world.vendors.values()
    )


def validate_rooms(world: World, source: Path) -> None:
    for room in world.rooms.values():
        validate_room_exits(world, room, source)
        validate_room_interactions(world, room, source)
        validate_room_items(world, room, source)
        validate_room_enemies(world, room, source)
        validate_room_people(world, room, source)
        validate_room_locking(world, room, source)
        validate_room_maze(world, room, source)


def validate_room_exits(world: World, room: Room, source: Path) -> None:
    for target_room in room.exits.values():
        if target_room not in world.rooms:
            raise ValueError(f"{source}: room '{room.room_id}' exits to unknown room '{target_room}'.")
    overlapping_hidden_exits = sorted(set(room.exits) & set(room.hidden_exits))
    if overlapping_hidden_exits:
        raise ValueError(
            f"{source}: room '{room.room_id}' cannot use a visible and hidden exit "
            "with the same direction: "
            + ", ".join(overlapping_hidden_exits)
        )
    for hidden_exit in room.hidden_exits.values():
        if hidden_exit.target_room not in world.rooms:
            raise ValueError(
                f"{source}: room '{room.room_id}' hidden exit '{hidden_exit.direction}' "
                f"targets unknown room '{hidden_exit.target_room}'."
            )
        if not hidden_exit.required_flag.strip():
            raise ValueError(
                f"{source}: room '{room.room_id}' hidden exit '{hidden_exit.direction}' "
                "requires a non-empty flag."
            )


def validate_room_interactions(world: World, room: Room, source: Path) -> None:
    for interaction in room.interactions.values():
        if not interaction.name.strip():
            raise ValueError(
                f"{source}: room '{room.room_id}' interaction "
                f"'{interaction.interaction_id}' must have a name."
            )
        if interaction.required_flag is not None and not interaction.required_flag.strip():
            raise ValueError(
                f"{source}: room '{room.room_id}' interaction "
                f"'{interaction.interaction_id}' uses an empty required flag."
            )
        if interaction.required_item and interaction.required_item not in world.items:
            raise ValueError(
                f"{source}: room '{room.room_id}' interaction "
                f"'{interaction.interaction_id}' requires unknown item "
                f"'{interaction.required_item}'."
            )
        for flag in interaction.set_flags:
            if not flag.strip():
                raise ValueError(
                    f"{source}: room '{room.room_id}' interaction "
                    f"'{interaction.interaction_id}' sets an empty flag."
                )
        if interaction.lockpickable:
            if interaction.lockpick_difficulty < 0:
                raise ValueError(
                    f"{source}: room '{room.room_id}' interaction "
                    f"'{interaction.interaction_id}' lockpick difficulty must be >= 0."
                )
            if interaction.lockpick_item not in world.items:
                raise ValueError(
                    f"{source}: room '{room.room_id}' interaction "
                    f"'{interaction.interaction_id}' requires unknown lockpick item "
                    f"'{interaction.lockpick_item}'."
                )
            if world.items[interaction.lockpick_item].item_type != "utility":
                raise ValueError(
                    f"{source}: room '{room.room_id}' interaction "
                    f"'{interaction.interaction_id}' lockpick item must be a utility item."
                )


def validate_room_items(world: World, room: Room, source: Path) -> None:
    for item_id in room.item_ids:
        if item_id not in world.items:
            raise ValueError(f"{source}: room '{room.room_id}' uses unknown item '{item_id}'.")
    for mining_drop in room.mining_drops:
        if mining_drop.item_id not in world.items:
            raise ValueError(
                f"{source}: room '{room.room_id}' mines unknown item "
                f"'{mining_drop.item_id}'."
            )
        if mining_drop.min_quantity < 1:
            raise ValueError(
                f"{source}: room '{room.room_id}' mining drop "
                f"'{mining_drop.item_id}' must use min >= 1."
            )
        if mining_drop.max_quantity < mining_drop.min_quantity:
            raise ValueError(
                f"{source}: room '{room.room_id}' mining drop "
                f"'{mining_drop.item_id}' must use max >= min."
            )


def validate_room_enemies(world: World, room: Room, source: Path) -> None:
    for enemy_id in room.enemy_ids:
        if enemy_id not in world.enemies:
            raise ValueError(f"{source}: room '{room.room_id}' uses unknown enemy '{enemy_id}'.")
    for faction_spawn in room.faction_enemy_spawns:
        if faction_spawn.faction_id not in world.factions:
            raise ValueError(
                f"{source}: room '{room.room_id}' faction spawn uses unknown faction "
                f"'{faction_spawn.faction_id}'."
            )
        if faction_spawn.enemy_id not in world.enemies:
            raise ValueError(
                f"{source}: room '{room.room_id}' faction spawn uses unknown enemy "
                f"'{faction_spawn.enemy_id}'."
            )
        if faction_spawn.count < 1:
            raise ValueError(
                f"{source}: room '{room.room_id}' faction spawn for enemy "
                f"'{faction_spawn.enemy_id}' must use count >= 1."
            )
    if room.monster_pool_id:
        if room.enemy_ids:
            raise ValueError(
                f"{source}: room '{room.room_id}' cannot define both static enemies "
                "and a monster_pool."
            )
        if room.monster_pool_id not in world.monster_pools:
            raise ValueError(
                f"{source}: room '{room.room_id}' uses unknown monster pool "
                f"'{room.monster_pool_id}'."
            )
        if room.monster_count < 1:
            raise ValueError(
                f"{source}: room '{room.room_id}' must use monster_count >= 1 "
                "when monster_pool is set."
            )


def validate_room_people(world: World, room: Room, source: Path) -> None:
    for npc_id in room.npc_ids:
        if npc_id not in world.npcs:
            raise ValueError(f"{source}: room '{room.room_id}' uses unknown NPC '{npc_id}'.")
    for vendor_id in room.vendor_ids:
        if vendor_id not in world.vendors:
            raise ValueError(f"{source}: room '{room.room_id}' uses unknown vendor '{vendor_id}'.")


def validate_room_locking(world: World, room: Room, source: Path) -> None:
    if room.required_item and room.required_item not in world.items:
        raise ValueError(
            f"{source}: room '{room.room_id}' requires unknown item '{room.required_item}'."
        )


def validate_room_maze(world: World, room: Room, source: Path) -> None:
    if room.maze_sequence:
        if room.maze_success_room not in world.rooms:
            raise ValueError(
                f"{source}: room '{room.room_id}' maze exits to unknown room "
                f"'{room.maze_success_room}'."
            )
        overlapping_directions = sorted(set(room.maze_sequence) & set(room.exits))
        if overlapping_directions:
            raise ValueError(
                f"{source}: room '{room.room_id}' maze directions cannot also be normal exits: "
                + ", ".join(overlapping_directions)
            )
    elif room.maze_success_room:
        raise ValueError(
            f"{source}: room '{room.room_id}' defines a maze success room without maze steps."
        )


def validate_items(world: World, source: Path) -> None:
    for item in world.items.values():
        if item.item_type not in ITEM_TYPES:
            raise ValueError(
                f"{source}: item '{item.item_id}' uses unknown item type '{item.item_type}'."
            )
        if item.required_level < 1:
            raise ValueError(
                f"{source}: item '{item.item_id}' required_level must be at least 1."
            )
        if item.required_level > 1 and item.item_type not in {"weapon", "armor", "accessory"}:
            raise ValueError(
                f"{source}: item '{item.item_id}' uses required_level but is not equipment."
            )
        if item.teaches_spell and item.teaches_spell not in world.spells:
            raise ValueError(
                f"{source}: item '{item.item_id}' teaches unknown spell '{item.teaches_spell}'."
            )
        if item.pickpocket_bonus < 0 or item.lockpick_bonus < 0:
            raise ValueError(
                f"{source}: item '{item.item_id}' stealth bonuses must be >= 0."
            )
        if (item.pickpocket_bonus or item.lockpick_bonus) and item.item_type != "accessory":
            raise ValueError(
                f"{source}: item '{item.item_id}' uses stealth bonuses but is not an accessory."
            )
        if item.max_charges < 0:
            raise ValueError(f"{source}: item '{item.item_id}' max charges must be >= 0.")
        if item.max_charges and item.item_type not in CHARGED_ITEM_TYPES:
            raise ValueError(
                f"{source}: item '{item.item_id}' uses charges but is not chargeable."
            )
        depleted_values = (
            item.depleted_attack_bonus,
            item.depleted_defense_bonus,
            item.depleted_hp_bonus,
            item.depleted_mp_bonus,
        )
        if any(value is not None for value in depleted_values) and item.max_charges <= 0:
            raise ValueError(
                f"{source}: item '{item.item_id}' defines depleted stats without charges."
            )
        if item.effect:
            if item.effect.recharge_charges and item.item_type != "consumable":
                raise ValueError(
                    f"{source}: item '{item.item_id}' recharges charges but is not consumable."
                )
            if item.effect.cure_poison and item.item_type != "consumable":
                raise ValueError(
                    f"{source}: item '{item.item_id}' cures poison but is not consumable."
                )
            has_temporary_bonus = bool(item.effect.attack_bonus or item.effect.defense_bonus)
            if has_temporary_bonus and item.effect.duration < 1:
                raise ValueError(
                    f"{source}: item '{item.item_id}' temporary stat effects require duration >= 1."
                )


def validate_spells(world: World, source: Path) -> None:
    for spell in world.spells.values():
        for class_name in spell.allowed_classes:
            if class_name != "all" and class_name not in world.player_classes:
                raise ValueError(
                    f"{source}: spell '{spell.spell_id}' allows unknown player class "
                    f"'{class_name}'."
                )
        if spell.skip_turns < 0:
            raise ValueError(f"{source}: spell '{spell.spell_id}' uses skip_turns below 0.")
        if spell.pickpocket_bonus < 0 or spell.lockpick_bonus < 0:
            raise ValueError(
                f"{source}: spell '{spell.spell_id}' uses stealth skill bonuses below 0."
            )
        if spell.school == "stealth" and not (spell.pickpocket_bonus or spell.lockpick_bonus):
            raise ValueError(
                f"{source}: stealth spell '{spell.spell_id}' must boost pickpocket or lockpick."
            )
        if (spell.pickpocket_bonus or spell.lockpick_bonus) and spell.school != "stealth":
            raise ValueError(
                f"{source}: spell '{spell.spell_id}' must use the stealth school for stealth skill bonuses."
            )
        if (spell.pickpocket_bonus or spell.lockpick_bonus) and spell.duration < 1:
            raise ValueError(
                f"{source}: stealth spell '{spell.spell_id}' must use duration >= 1."
            )
        if spell.school in {"control", "disable", "attack_block"} and spell.skip_turns < 1:
            raise ValueError(
                f"{source}: control spell '{spell.spell_id}' must use skip_turns >= 1."
            )
        if spell.cure_poison and spell.school not in {
            "cure",
            "cleanse",
            "cleansing",
            "healing",
            "heal",
            "poison_cure",
            "cure_poison",
        }:
            raise ValueError(
                f"{source}: poison cure spell '{spell.spell_id}' must use a healing or cure school."
            )


def validate_enemies(world: World, source: Path) -> None:
    for enemy in world.enemies.values():
        if not 0 <= enemy.prevent_attack_chance <= 100:
            raise ValueError(
                f"{source}: enemy '{enemy.enemy_id}' prevent_attack_chance must be between 0 and 100."
            )
        if enemy.prevent_attack_chance and enemy.prevent_attack_turns < 1:
            raise ValueError(
                f"{source}: enemy '{enemy.enemy_id}' prevent_attack_turns must be at least 1."
            )
        if not 0 <= enemy.poison_chance <= 100:
            raise ValueError(
                f"{source}: enemy '{enemy.enemy_id}' poison_chance must be between 0 and 100."
            )


def validate_monster_pools(world: World, source: Path) -> None:
    for pool in world.monster_pools.values():
        if not pool.entries:
            raise ValueError(f"{source}: monster pool '{pool.pool_id}' has no enemy references.")
        for entry in pool.entries:
            if entry.enemy_id not in world.enemies:
                raise ValueError(
                    f"{source}: monster pool '{pool.pool_id}' uses unknown enemy "
                    f"'{entry.enemy_id}'."
                )
            if entry.weight < 1:
                raise ValueError(
                    f"{source}: monster pool '{pool.pool_id}' uses invalid weight "
                    f"{entry.weight} for enemy '{entry.enemy_id}'."
                )


def validate_quests(world: World, source: Path) -> None:
    for quest in world.quests.values():
        if quest.giver_id not in world.npcs:
            raise ValueError(f"{source}: quest '{quest.quest_id}' uses unknown giver '{quest.giver_id}'.")
        if quest.accept_item and quest.accept_item not in world.items:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' uses unknown acceptance item '{quest.accept_item}'."
            )
        if quest.target_enemy and quest.target_enemy not in world.enemies:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' uses unknown enemy '{quest.target_enemy}'."
            )
        if quest.required_item and quest.required_item not in world.items:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' uses unknown item '{quest.required_item}'."
            )
        if quest.destination_room and quest.destination_room not in world.rooms:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' uses unknown room '{quest.destination_room}'."
            )
        if quest.reward_item and quest.reward_item not in world.items:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' uses unknown reward item '{quest.reward_item}'."
            )
        if quest.reward_recipe and quest.reward_recipe not in world.recipes:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' uses unknown reward recipe '{quest.reward_recipe}'."
            )
        if quest.reward_gold < 0:
            raise ValueError(f"{source}: quest '{quest.quest_id}' uses negative gold.")
        if quest.reward_currency not in world.currencies:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' uses unknown reward currency "
                f"'{quest.reward_currency}'."
            )
        if quest.reward_amount is not None and quest.reward_amount < 0:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' uses negative currency reward."
            )
        validate_quest_flag_outcome(world, quest, source)
        if quest.ends_world and not (quest.ending_text or quest.completion_text):
            raise ValueError(
                f"{source}: ending quest '{quest.quest_id}' must define default ending text."
            )
        if len(quest.ending_choices) > MAX_ENDING_CHOICES:
            raise ValueError(
                f"{source}: ending quest '{quest.quest_id}' defines more than "
                f"{MAX_ENDING_CHOICES} ending choices."
            )
        seen_choice_ids: set[str] = set()
        for choice in quest.ending_choices:
            if not choice.choice_id.strip():
                raise ValueError(
                    f"{source}: ending quest '{quest.quest_id}' has an ending choice with an empty id."
                )
            if choice.choice_id in seen_choice_ids:
                raise ValueError(
                    f"{source}: ending quest '{quest.quest_id}' repeats ending choice "
                    f"'{choice.choice_id}'."
                )
            seen_choice_ids.add(choice.choice_id)
            if not choice.label.strip():
                raise ValueError(
                    f"{source}: ending quest '{quest.quest_id}' ending choice "
                    f"'{choice.choice_id}' must have a label."
                )
            if choice.ending_type not in {"custom", "default", "faction"}:
                raise ValueError(
                    f"{source}: ending quest '{quest.quest_id}' ending choice "
                    f"'{choice.choice_id}' uses unknown ending type '{choice.ending_type}'."
                )
            if choice.ending_type == "custom" and not choice.text.strip():
                raise ValueError(
                    f"{source}: ending quest '{quest.quest_id}' custom ending choice "
                    f"'{choice.choice_id}' must define ending text."
                )
            for required_flag in choice.required_flags:
                if not required_flag.strip():
                    raise ValueError(
                        f"{source}: ending quest '{quest.quest_id}' ending choice "
                        f"'{choice.choice_id}' requires an empty flag."
                    )
        for faction_id, ending_text in quest.ending_text_by_faction.items():
            if faction_id not in world.factions:
                raise ValueError(
                    f"{source}: quest '{quest.quest_id}' ending uses unknown faction "
                    f"'{faction_id}'."
                )
            if not ending_text.strip():
                raise ValueError(
                    f"{source}: quest '{quest.quest_id}' ending for faction "
                    f"'{faction_id}' must not be empty."
                )


def validate_quest_flag_outcome(world: World, quest, source: Path) -> None:
    if quest.flag_outcome is None:
        return
    if not quest.flag_outcome.flag.strip():
        raise ValueError(f"{source}: quest '{quest.quest_id}' uses an empty outcome flag.")
    for label, branch in (
        ("true", quest.flag_outcome.when_true),
        ("false", quest.flag_outcome.when_false),
    ):
        if branch.reward_gold is not None and branch.reward_gold < 0:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' {label} flag outcome uses negative gold."
            )
        if branch.reward_currency is not None and branch.reward_currency not in world.currencies:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' {label} flag outcome uses unknown reward "
                f"currency '{branch.reward_currency}'."
            )
        if branch.reward_amount is not None and branch.reward_amount < 0:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' {label} flag outcome uses negative "
                "currency reward."
            )
        if branch.reward_exp is not None and branch.reward_exp < 0:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' {label} flag outcome uses negative experience."
            )
        if branch.reward_item is not None and branch.reward_item and branch.reward_item not in world.items:
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' {label} flag outcome uses unknown reward item "
                f"'{branch.reward_item}'."
            )
        if (
            branch.reward_recipe is not None
            and branch.reward_recipe
            and branch.reward_recipe not in world.recipes
        ):
            raise ValueError(
                f"{source}: quest '{quest.quest_id}' {label} flag outcome uses unknown reward recipe "
                f"'{branch.reward_recipe}'."
            )


def validate_recipes(world: World, source: Path) -> None:
    for recipe in world.recipes.values():
        if recipe.result_item not in world.items:
            raise ValueError(f"{source}: recipe result '{recipe.result_item}' is not defined as an item.")
        for ingredient in recipe.ingredients:
            if ingredient not in world.items:
                raise ValueError(
                    f"{source}: recipe ingredient '{ingredient}' is not defined as an item."
                )


def validate_starter_loadouts(world: World, source: Path) -> None:
    for class_name, item_ids in world.starter_items.items():
        if class_name != "all" and class_name not in world.player_classes:
            raise ValueError(
                f"{source}: starter loadout uses unknown player class '{class_name}'."
            )
        for item_id in item_ids:
            if item_id not in world.items:
                raise ValueError(
                    f"{source}: starter loadout for '{class_name}' uses unknown item '{item_id}'."
                )

    for class_name, spell_ids in world.starter_spells.items():
        if class_name != "all" and class_name not in world.player_classes:
            raise ValueError(
                f"{source}: starter spells use unknown player class '{class_name}'."
            )
        for spell_id in spell_ids:
            if spell_id not in world.spells:
                raise ValueError(
                    f"{source}: starter spells for '{class_name}' use unknown spell '{spell_id}'."
                )


def validate_npcs(world: World, source: Path) -> None:
    for npc in world.npcs.values():
        validate_npc(world, npc, source)


def validate_npc(world: World, npc: NPC, source: Path) -> None:
    if npc.faction_id and npc.faction_id not in world.factions:
        raise ValueError(
            f"{source}: NPC '{npc.npc_id}' uses unknown faction '{npc.faction_id}'."
        )
    if npc.can_recruit:
        if not npc.companion_class:
            raise ValueError(
                f"{source}: companion NPC '{npc.npc_id}' must define a companion_class."
            )
        if npc.companion_class not in world.player_classes:
            raise ValueError(
                f"{source}: companion NPC '{npc.npc_id}' uses unknown player class "
                f"'{npc.companion_class}'."
            )
    if npc.recruit_required_item:
        if not npc.can_recruit:
            raise ValueError(
                f"{source}: NPC '{npc.npc_id}' uses a recruit item but is not recruitable."
            )
        if npc.recruit_required_item not in world.items:
            raise ValueError(
                f"{source}: companion NPC '{npc.npc_id}' requires unknown recruit item "
                f"'{npc.recruit_required_item}'."
            )
    if len(set(npc.quest_ids)) != len(npc.quest_ids):
        raise ValueError(f"{source}: NPC '{npc.npc_id}' repeats a quest in its quest chain.")
    for quest_id in npc.quest_ids:
        if quest_id not in world.quests:
            raise ValueError(f"{source}: NPC '{npc.npc_id}' uses unknown quest '{quest_id}'.")
        if world.quests[quest_id].giver_id != npc.npc_id:
            raise ValueError(
                f"{source}: NPC '{npc.npc_id}' lists quest '{quest_id}', "
                f"but that quest uses giver '{world.quests[quest_id].giver_id}'."
            )
    if npc.dialogue_lines:
        if npc.quest_ids:
            raise ValueError(
                f"{source}: NPC '{npc.npc_id}' cannot use dialogue_lines with quest_id."
            )
        if len(npc.dialogue_lines) != 3:
            raise ValueError(
                f"{source}: NPC '{npc.npc_id}' must define exactly three dialogue lines."
            )
    validate_pickpocket_targets(world, source, "NPC", npc.npc_id, npc.pickpocket_targets)


def validate_pickpocket_targets(
    world: World,
    source: Path,
    holder_type: str,
    holder_id: str,
    targets,
) -> None:
    seen_items: set[str] = set()
    for target in targets:
        if target.item_id not in world.items:
            raise ValueError(
                f"{source}: {holder_type} '{holder_id}' has unknown pickpocket item "
                f"'{target.item_id}'."
            )
        if target.item_id in seen_items:
            raise ValueError(
                f"{source}: {holder_type} '{holder_id}' repeats pickpocket item "
                f"'{target.item_id}'."
            )
        seen_items.add(target.item_id)
        if target.difficulty < 0:
            raise ValueError(
                f"{source}: {holder_type} '{holder_id}' pickpocket item "
                f"'{target.item_id}' difficulty must be >= 0."
            )


def validate_vendors(world: World, source: Path) -> None:
    for vendor in world.vendors.values():
        accepted_currencies = vendor.accepted_currencies or [world.default_currency_id]
        for currency_id in accepted_currencies:
            if currency_id not in world.currencies:
                raise ValueError(
                    f"{source}: vendor '{vendor.vendor_id}' accepts unknown currency "
                    f"'{currency_id}'."
                )
        for item_id in vendor.stock:
            if item_id not in world.items:
                raise ValueError(
                    f"{source}: vendor '{vendor.vendor_id}' sells unknown item '{item_id}'."
                )
            validate_vendor_price_currency(
                world,
                source,
                vendor.vendor_id,
                item_id,
                vendor.stock_currencies.get(item_id),
                accepted_currencies,
            )
        for recipe_id in vendor.recipe_stock:
            if recipe_id not in world.recipes:
                raise ValueError(
                    f"{source}: vendor '{vendor.vendor_id}' sells unknown recipe '{recipe_id}'."
                )
            validate_vendor_price_currency(
                world,
                source,
                vendor.vendor_id,
                recipe_id,
                vendor.recipe_currencies.get(recipe_id),
                accepted_currencies,
            )
        for spell_id in vendor.spell_stock:
            if spell_id not in world.spells:
                raise ValueError(
                    f"{source}: vendor '{vendor.vendor_id}' sells unknown spell '{spell_id}'."
                )
            validate_vendor_price_currency(
                world,
                source,
                vendor.vendor_id,
                spell_id,
                vendor.spell_currencies.get(spell_id),
                accepted_currencies,
            )
        if vendor.is_exchange and not vendor.exchange_rates:
            raise ValueError(
                f"{source}: exchange vendor '{vendor.vendor_id}' must define exchange rates."
            )
        for rate in vendor.exchange_rates:
            if rate.from_currency not in world.currencies:
                raise ValueError(
                    f"{source}: vendor '{vendor.vendor_id}' exchanges unknown currency "
                    f"'{rate.from_currency}'."
                )
            if rate.to_currency not in world.currencies:
                raise ValueError(
                    f"{source}: vendor '{vendor.vendor_id}' exchanges unknown currency "
                    f"'{rate.to_currency}'."
                )
            if rate.from_amount < 1 or rate.to_amount < 1:
                raise ValueError(
                    f"{source}: vendor '{vendor.vendor_id}' exchange rates must use "
                    "positive amounts."
                )
        validate_pickpocket_targets(
            world,
            source,
            "vendor",
            vendor.vendor_id,
            vendor.pickpocket_targets,
        )


def validate_vendor_price_currency(
    world: World,
    source: Path,
    vendor_id: str,
    sale_id: str,
    currency_id: str | None,
    accepted_currencies: list[str],
) -> None:
    if not currency_id:
        return
    if currency_id not in world.currencies:
        raise ValueError(
            f"{source}: vendor '{vendor_id}' prices '{sale_id}' in unknown currency "
            f"'{currency_id}'."
        )
    if currency_id not in accepted_currencies:
        raise ValueError(
            f"{source}: vendor '{vendor_id}' prices '{sale_id}' in '{currency_id}' "
            "but does not accept that currency."
        )


def validate_enemy_loot(world: World, source: Path) -> None:
    for enemy in world.enemies.values():
        for drop in enemy.loot:
            if drop.item_id not in world.items:
                raise ValueError(
                    f"{source}: enemy '{enemy.enemy_id}' drops unknown item '{drop.item_id}'."
                )
