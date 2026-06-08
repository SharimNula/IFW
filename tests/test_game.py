from __future__ import annotations

from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from ifw.__main__ import create_player
from ifw.engine import GameEngine
from ifw.models import (
    CompanionState,
    EnemyState,
    FactionEnemySpawn,
    HiddenExit,
    MiningDrop,
    NPC,
    Player,
    RoomInteraction,
    QuestEndingChoice,
    QuestFlagBranch,
    QuestFlagOutcome,
    WorldProgress,
)
from ifw.persistence import find_world_file, list_world_files, load_player, save_player
from ifw.world_loader import _validate_world, load_world
from ifw.world_loader_sections import parse_quests, parse_world


ROOT = Path(__file__).resolve().parents[1]
WORLD_PATH = ROOT / "worlds" / "emerald_keep"


class GameProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.world = load_world(WORLD_PATH)
        self.player = Player(
            name="TestHero",
            player_class="warrior",
            level=1,
            experience=0,
            gold=35,
            max_hp=42,
            hp=42,
            max_mp=12,
            mp=12,
            base_attack=7,
            base_defense=4,
        )

    def _place_forest_wolf(self, engine: GameEngine) -> EnemyState:
        state = EnemyState(enemy_id="forest_wolf", current_hp=16)
        engine.progress.current_room = "forest_path"
        engine.progress.room_enemies["forest_path"] = [state]
        return state

    def _engine(self) -> GameEngine:
        return GameEngine(self.world, self.player, save_callback=lambda _player: None)

    def _ready_seal_the_heart(self, faction_id: str | None = None) -> GameEngine:
        engine = self._engine()
        engine.progress.active_quests.append("seal_the_heart")
        engine.progress.current_room = "heart_sanctum"
        engine.progress.room_enemies["heart_sanctum"] = []
        engine.progress.add_item("heart_lantern")
        engine.progress.faction_id = faction_id
        return engine

    def _ready_final_ending(self, faction_id: str | None = None) -> GameEngine:
        engine = self._engine()
        engine.progress.active_quests.append("end_the_concord_wyrm")
        engine.progress.current_room = "concord_throne"
        engine.progress.room_enemies["concord_throne"] = []
        engine.progress.defeated_enemies.append("concord_wyrm")
        engine.progress.faction_id = faction_id
        return engine

    def _add_rogue_companion(self, engine: GameEngine) -> CompanionState:
        companion = engine._create_companion_state("trailhand_pip", "lantern_inn")
        engine.progress.companions.append(companion)
        return companion

    def _assert_world_validation_error(self, mutate_world, expected_message: str) -> None:
        world = load_world(WORLD_PATH)
        mutate_world(world)
        with self.assertRaisesRegex(ValueError, expected_message):
            _validate_world(world, WORLD_PATH)

    def test_world_loader_reads_sample_world_feature_hooks(self) -> None:
        self.assertEqual(self.world.start_room, "town_square")
        self.assertIsNone(self.world.end_room)
        self.assertIn(self.world.start_room, self.world.rooms)
        self.assertFalse(self.world.quests["seal_the_heart"].ends_world)
        self.assertEqual(self.world.quests["seal_the_heart"].ending_text_by_faction, {})
        self.assertEqual(self.world.quests["seal_the_heart"].ending_choices, [])
        self.assertTrue(self.world.quests["end_the_concord_wyrm"].ends_world)
        self.assertEqual(len(self.world.quests["end_the_concord_wyrm"].ending_choices), 5)
        self.assertEqual(self.world.quests["end_the_concord_wyrm"].ending_choices[0].ending_type, "default")
        self.assertEqual(self.world.quests["end_the_concord_wyrm"].ending_choices[1].ending_type, "faction")
        self.assertEqual(
            self.world.rooms["crystal_grotto"].mining_drops[0].item_id,
            "glimmer_ore",
        )
        self.assertEqual(
            self.world.rooms["crystal_grotto"].hidden_exits["in"].target_room,
            "arcane_thief_cache",
        )
        self.assertEqual(
            self.world.rooms["crystal_grotto"].interactions["serpent_cipher_door"].password,
            "SNAKE",
        )
        self.assertTrue(
            all(len(room.companion_dialogue) == 2 for room in self.world.rooms.values())
        )
        self.assertEqual(
            self.world.rooms["town_square"].companion_dialogue,
            [
                "Every road meets here. If Emerald Keep has a heartbeat, this square is where it stumbles loudest.",
                "The banners look cheerful, but everyone keeps glancing toward the roads. Something has the whole town listening.",
            ],
        )
        self.assertIn("serpentstep_jacket", self.world.rooms["arcane_thief_cache"].item_ids)
        self.assertEqual(self.world.items["serpentstep_jacket"].item_type, "armor")
        self.assertEqual(self.world.items["serpentstep_jacket"].required_level, 6)
        self.assertEqual(self.world.items["serpentstep_jacket"].max_charges, 3)
        self.assertEqual(
            self.world.rooms["thorn_maze"].maze_sequence,
            ["north", "east", "north"],
        )
        self.assertIn("ruins_patrols", self.world.monster_pools)
        self.assertEqual(self.world.rooms["ruins"].monster_pool_id, "ruins_patrols")
        self.assertEqual(
            [entry.enemy_id for entry in self.world.monster_pools["ruins_patrols"].entries],
            ["bandit_scout", "bandit_raider", "bandit_lookout"],
        )
        self.assertTrue(all(len(pool.entries) == 3 for pool in self.world.monster_pools.values()))
        self.assertEqual(self.world.rooms["forest_path"].monster_pool_id, "forest_threats")
        self.assertEqual(self.world.rooms["forest_path"].monster_count, 1)
        self.assertEqual(self.world.rooms["forest_path"].enemy_ids, [])
        self.assertEqual(self.world.rooms["forest_path"].faction_enemy_spawns[0].faction_id, "town_watch")
        self.assertEqual(self.world.rooms["forest_path"].faction_enemy_spawns[0].enemy_id, "bandit_scout")
        self.assertEqual(self.world.default_currency_id, "gold")
        self.assertEqual(self.world.currencies["emerald_mark"].plural, "emerald marks")
        self.assertEqual(self.world.rooms["town_square"].exits["east"], "market_street")
        self.assertEqual(self.world.rooms["market_street"].exits["east"], "smithy")
        self.assertEqual(
            self.world.rooms["market_street"].exits["south"],
            "currency_exchange_office",
        )
        self.assertEqual(
            self.world.rooms["currency_exchange_office"].vendor_ids,
            ["exchange_clerk_marlow"],
        )
        exchange_door = self.world.rooms["currency_exchange_office"].interactions["exchange_vault_door"]
        self.assertTrue(exchange_door.lockpickable)
        self.assertEqual(exchange_door.lockpick_difficulty, 15)
        self.assertEqual(exchange_door.lockpick_item, "lockpicks")
        self.assertEqual(self.world.rooms["currency_exchange_office"].hidden_exits["east"].target_room, "exchange_vault")
        self.assertEqual(self.world.jail_room, "town_jail")
        self.assertEqual(self.world.jail_fee, 15)
        self.assertEqual(
            self.world.vendors["smith_orin"].accepted_currencies,
            ["gold", "emerald_mark"],
        )
        self.assertEqual(
            self.world.vendors["smith_orin"].stock_currencies["silver_ring"],
            "emerald_mark",
        )
        self.assertEqual(
            self.world.vendors["exchange_clerk_marlow"].exchange_rates[0].from_amount,
            5,
        )
        self.assertEqual(
            self.world.vendors["exchange_clerk_marlow"].pickpocket_targets[0].item_id,
            "exchange_vault_key",
        )
        self.assertEqual(self.world.items["nimble_fingers_ring"].pickpocket_bonus, 10)
        self.assertEqual(self.world.items["nimble_fingers_ring"].lockpick_bonus, 10)
        self.assertEqual(self.world.rooms["town_square"].hidden_exits["west"].required_flag, "town_mural_opened")
        self.assertIn("weathered_mural", self.world.rooms["town_square"].interactions)
        hearth_ward = self.world.rooms["lantern_inn"].interactions["hearth_ward"]
        self.assertEqual(hearth_ward.required_item, "healing_tonic")
        self.assertTrue(hearth_ward.consume_required_item)
        self.assertEqual(self.world.items["iron_pry_bar"].item_type, "utility")
        self.assertEqual(
            self.world.rooms["smithy"].interactions["jammed_grate"].required_item,
            "iron_pry_bar",
        )
        self.assertEqual(self.world.items["watch_token"].item_type, "utility")
        self.assertEqual(
            self.world.rooms["guard_post"].interactions["signal_lantern"].required_item,
            "watch_token",
        )
        self.assertEqual(self.world.items["archive_cipher"].item_type, "utility")
        self.assertEqual(self.world.items["archive_cipher"].max_charges, 3)
        self.assertEqual(
            self.world.rooms["crystal_grotto"].interactions["whispering_vein"].required_item,
            "archive_cipher",
        )
        self.assertTrue(self.world.items["mana_crystal"].effect.recharge_charges)
        self.assertEqual(self.world.items["wild_mage_robe"].max_charges, 3)
        self.assertEqual(self.world.items["wild_mage_robe"].depleted_defense_bonus, 1)
        self.assertEqual(self.world.items["wild_mage_robe"].depleted_mp_bonus, 2)
        self.assertEqual(self.world.items["faded_keepsake"].item_type, "misc")
        self.assertEqual(
            self.world.rooms["elder_house"].interactions["memory_shelf"].required_item,
            "faded_keepsake",
        )
        self.assertEqual(self.world.spells["frost_lance"].allowed_classes, ["mage"])
        self.assertEqual(self.world.spells["ember_bolt"].allowed_classes, [])
        self.assertEqual(self.world.spells["minor_mend"].school, "healing")
        self.assertTrue(self.world.spells["purify_blood"].cure_poison)
        self.assertEqual(self.world.spells["flash"].skip_turns, 1)
        self.assertEqual(self.world.spells["shadow_palm"].allowed_classes, ["rogue"])
        self.assertEqual(self.world.spells["shadow_palm"].pickpocket_bonus, 20)
        self.assertEqual(self.world.spells["lock_whisper"].allowed_classes, ["rogue"])
        self.assertEqual(self.world.spells["lock_whisper"].lockpick_bonus, 20)
        self.assertIn("shadow_palm", self.world.vendors["spellweaver_iris"].spell_stock)
        self.assertIn("lock_whisper", self.world.vendors["spellweaver_iris"].spell_stock)
        self.assertEqual(self.world.enemies["bandit_lookout"].prevent_attack_chance, 25)
        self.assertEqual(self.world.enemies["forest_bear"].poison_chance, 0)
        self.assertEqual(self.world.enemies["forest_snake"].poison_chance, 35)
        self.assertIn("poison racing", self.world.enemies["forest_snake"].poison_text)
        ore_outcome = self.world.quests["read_the_ore"].flag_outcome
        self.assertIsNotNone(ore_outcome)
        assert ore_outcome is not None
        self.assertEqual(ore_outcome.flag, "ore_cipher_decoded")
        self.assertEqual(ore_outcome.when_true.reward_gold, 35)
        self.assertEqual(ore_outcome.when_true.reward_recipe, "wild_mage_robe_pattern")
        road_outcome = self.world.quests["hold_the_road"].flag_outcome
        self.assertIsNotNone(road_outcome)
        assert road_outcome is not None
        self.assertEqual(road_outcome.flag, "watch_signal_lit")
        self.assertEqual(self.world.quests["hold_the_road"].reward_currency, "emerald_mark")
        self.assertEqual(self.world.quests["hold_the_road"].reward_amount, 5)
        self.assertEqual(road_outcome.when_true.reward_amount, 7)
        self.assertEqual(road_outcome.when_true.reward_exp, 70)
        self.assertEqual(self.world.player_classes["warrior"].name, "Warrior")
        self.assertEqual(self.world.player_classes["warrior"].max_hp, 42)
        self.assertEqual(self.world.player_classes["mage"].max_mp, 26)
        self.assertEqual(self.world.player_classes["rogue"].base_attack, 6)
        self.assertEqual(self.world.player_classes["rogue"].pickpocket_chance, 65)
        self.assertEqual(self.world.player_classes["rogue"].lockpick_chance, 60)
        self.assertEqual(self.world.factions["town_watch"].name, "Town Watch")
        self.assertEqual(self.world.npcs["well_keeper_mara"].faction_id, "town_watch")
        self.assertEqual(self.world.rooms["town_square"].exits["south"], "title_street")
        self.assertEqual(self.world.rooms["title_street"].exits["south"], "elder_house")
        self.assertEqual(self.world.rooms["title_street"].exits["east"], "new_moon_temple")
        self.assertNotIn("relic_seer_maelis", self.world.rooms["town_square"].npc_ids)
        self.assertIn("relic_seer_maelis", self.world.rooms["new_moon_temple"].npc_ids)
        healing_tonic_effect = self.world.items["healing_tonic"].effect
        assert healing_tonic_effect is not None
        self.assertLess(self.world.spells["minor_mend"].power, healing_tonic_effect.hp_restore)
        fury_draught_effect = self.world.items["fury_draught"].effect
        assert fury_draught_effect is not None
        self.assertEqual(fury_draught_effect.attack_bonus, 3)
        self.assertEqual(fury_draught_effect.duration, 2)
        antidote_effect = self.world.items["antidote"].effect
        assert antidote_effect is not None
        self.assertTrue(antidote_effect.cure_poison)
        self.assertEqual(self.world.spells["battle_focus"].allowed_classes, ["warrior"])
        self.assertEqual(self.world.spells["battle_focus"].attack_bonus, 4)
        self.assertEqual(self.world.items["iron_spear"].required_level, 2)
        self.assertEqual(self.world.items["guardian_band"].required_level, 3)
        self.assertEqual(len(self.world.npcs["well_keeper_mara"].dialogue_lines), 3)
        self.assertTrue(self.world.npcs["squire_tovin"].can_recruit)
        self.assertEqual(self.world.npcs["squire_tovin"].companion_class, "warrior")
        self.assertEqual(self.world.items["pip_lucky_button"].item_type, "misc")
        self.assertEqual(self.world.npcs["trailhand_pip"].recruit_required_item, "pip_lucky_button")
        self.assertTrue(self.world.npcs["trailhand_pip"].consume_recruit_item)
        self.assertIn("lucky button", self.world.npcs["trailhand_pip"].recruit_missing_item_text)
        self.assertEqual(self.world.npcs["elder_rowan"].quest_ids, ["cull_the_wolf"])
        self.assertEqual(self.world.npcs["elder_rowan"].active_dialogue, "")
        self.assertEqual(
            self.world.quests["cull_the_wolf"].active_dialogue,
            "Keep your footing on the forest path. That wolf knows the road better than any of us.",
        )
        self.assertEqual(
            self.world.quests["recover_the_sigil"].completed_dialogue,
            "The patterns are clearer now that the sigil has been recovered. You have preserved more than a relic.",
        )
        self.assertEqual(self.world.recipes["wild_mage_robe_pattern"].ingredients.count("wolf_pelt"), 2)
        self.assertEqual(self.world.recipes["wild_mage_robe_pattern"].ingredients.count("bear_pelt"), 1)

    def test_emerald_keep_expanded_item_pool_stays_integrated_and_unique(self) -> None:
        expected_types = {
            "accessory",
            "armor",
            "consumable",
            "key",
            "material",
            "misc",
            "quest",
            "spellbook",
            "utility",
            "weapon",
        }
        item_types = {item.item_type for item in self.world.items.values()}
        self.assertEqual(item_types, expected_types)
        self.assertGreaterEqual(len(self.world.items), 100)
        for item_type in expected_types:
            with self.subTest(item_type=item_type):
                self.assertGreater(
                    sum(1 for item in self.world.items.values() if item.item_type == item_type),
                    0,
                )

        vendor_spell_ids = {
            spell_id
            for vendor in self.world.vendors.values()
            for spell_id in vendor.spell_stock
        }
        spellbook_spell_ids = {
            item.teaches_spell
            for item in self.world.items.values()
            if item.item_type == "spellbook" and item.teaches_spell
        }
        self.assertTrue(spellbook_spell_ids.isdisjoint(vendor_spell_ids))
        self.assertTrue(
            {
                "root_mend",
                "storm_chain",
                "quietus_glimmer",
                "starless_aegis",
            }.issubset(spellbook_spell_ids)
        )

        vendor_item_ids = {
            item_id
            for vendor in self.world.vendors.values()
            for item_id in vendor.stock
        }
        recipe_result_ids = {recipe.result_item for recipe in self.world.recipes.values()}
        self.assertTrue(recipe_result_ids.isdisjoint(vendor_item_ids))
        self.assertTrue(
            {
                "thornweave_cloak",
                "glass_sabre",
                "moonfall_scepter",
                "wyrmfang_lance",
                "wyrmhide_wardcoat",
                "concord_seal_band",
            }.issubset(recipe_result_ids)
        )

        self.assertIn("field_trowel", self.world.vendors["smith_orin"].stock)
        self.assertIn("root_mender_primer", self.world.vendors["spellweaver_iris"].stock)
        self.assertIn("glass_sabre_pattern", self.world.vendors["ember_quartermaster"].recipe_stock)
        self.assertIn("moonfall_scepter_pattern", self.world.vendors["archive_scribe_orrin"].recipe_stock)
        self.assertEqual(
            self.world.quests["shatter_void_shards"].reward_recipe,
            "wyrmhide_wardcoat_pattern",
        )
        self.assertIn("quietus_glimmer_notes", self.world.rooms["mirage_cache"].item_ids)
        self.assertEqual(self.world.rooms["lunar_stacks"].required_item, "warded_stacks_key")
        self.assertIn(
            "wyrm_scale",
            [drop.item_id for drop in self.world.enemies["abyss_serpent"].loot],
        )

    def test_emerald_keep_spell_schools_have_five_spells_each(self) -> None:
        school_counts: dict[str, int] = {}
        for spell in self.world.spells.values():
            school_counts[spell.school] = school_counts.get(spell.school, 0) + 1

        self.assertEqual(
            school_counts,
            {
                "attack": 5,
                "control": 5,
                "cure": 5,
                "defense": 5,
                "healing": 5,
                "offense": 5,
                "stealth": 5,
            },
        )
        self.assertIn("steady_pulse", self.world.vendors["spellweaver_iris"].spell_stock)
        self.assertIn("colossus_rhythm", self.world.vendors["ember_quartermaster"].spell_stock)
        self.assertIn("hourglass_stutter", self.world.vendors["oasis_trader_namira"].spell_stock)
        self.assertIn("gravity_lull", self.world.vendors["archive_scribe_orrin"].spell_stock)
        self.assertIn("final_oath", self.world.vendors["citadel_wayfarer"].spell_stock)

    def test_emerald_keep_room_event_flags_unlock_followup_content(self) -> None:
        set_flags: set[str] = set()
        required_flags: set[str] = set()
        for room in self.world.rooms.values():
            for hidden_exit in room.hidden_exits.values():
                required_flags.add(hidden_exit.required_flag)
            for interaction in room.interactions.values():
                set_flags.update(interaction.set_flags)
                if interaction.required_flag:
                    required_flags.add(interaction.required_flag)
        for quest in self.world.quests.values():
            if quest.flag_outcome:
                required_flags.add(quest.flag_outcome.flag)
            for choice in quest.ending_choices:
                required_flags.update(choice.required_flags)

        self.assertEqual(set_flags - required_flags, set())
        event_choice = next(
            choice
            for choice in self.world.quests["end_the_concord_wyrm"].ending_choices
            if choice.choice_id == "5"
        )
        self.assertEqual(set(event_choice.required_flags), set_flags)
        self.assertEqual(
            self.world.rooms["elder_house"].hidden_exits["down"].required_flag,
            "elder_memory_honored",
        )
        self.assertEqual(
            self.world.rooms["lantern_inn"].hidden_exits["down"].target_room,
            "hearth_supply_cache",
        )
        self.assertEqual(
            self.world.rooms["smithy"].hidden_exits["in"].required_flag,
            "cellar_door_opened",
        )
        self.assertEqual(
            self.world.rooms["smithy"].hidden_exits["down"].required_flag,
            "smithy_grate_opened",
        )
        self.assertNotIn("down", self.world.rooms["ember_crosscut"].exits)
        self.assertEqual(
            self.world.rooms["ember_crosscut"].hidden_exits["down"].required_flag,
            "ember_pumps_repaired",
        )
        self.assertEqual(
            self.world.rooms["ember_lift"].hidden_exits["in"].required_flag,
            "miner_roll_honored",
        )
        self.assertEqual(
            self.world.rooms["moon_index"].interactions["fracture_measure"].required_flag,
            "moon_index_focused",
        )
        self.assertEqual(
            self.world.rooms["relic_gate"].hidden_exits["north"].required_flag,
            "moonfall_seal_woken",
        )
        self.assertEqual(
            self.world.rooms["starless_keep"].hidden_exits["north"].required_flag,
            "silent_fault_tuned",
        )

    def test_final_event_completion_ending_is_hidden_until_all_event_flags_are_set(self) -> None:
        engine = self._engine()
        quest = self.world.quests["end_the_concord_wyrm"]
        event_choice = next(choice for choice in quest.ending_choices if choice.choice_id == "5")
        engine.progress.pending_ending_quest_id = quest.quest_id

        hidden_lines = engine._ending_choice_lines(quest)
        invalid_lines = engine.handle_command("choose ending 5")

        set_flags = {
            flag
            for room in self.world.rooms.values()
            for interaction in room.interactions.values()
            for flag in interaction.set_flags
        }
        self.assertEqual(set(event_choice.required_flags), set_flags)
        self.assertNotIn("  5. Seal every hidden mercy", hidden_lines)
        self.assertIn("No ending choice matches that option.", invalid_lines)
        self.assertNotIn("  5. Seal every hidden mercy", invalid_lines)

        engine.progress.story_flags.extend(event_choice.required_flags)
        visible_lines = engine._ending_choice_lines(quest)
        ending_lines = engine.handle_command("choose ending 5")

        self.assertIn("  5. Seal every hidden mercy", visible_lines)
        self.assertTrue(any("left no quiet kindness unfinished" in line for line in ending_lines))
        self.assertIn("Game over.", ending_lines)
        self.assertTrue(engine.game_over)

    def test_miner_tally_stone_can_honor_miners_roll_and_unlock_cache(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "ember_lift"
        engine.progress.add_item("miner_tally_stone")

        lines = engine.handle_command("use miner tally stone on miners roll")
        move_lines = engine.handle_command("in")

        self.assertIn(
            "You hang the Miner Tally Stone beneath the matching shift mark. The old board settles with a soft click, and a supply niche opens beside the lift.",
            lines,
        )
        self.assertIn("You use Miner Tally Stone.", lines)
        self.assertIn("A path is revealed: in -> Miners' Supply Cache.", lines)
        self.assertIn("miner_roll_honored", engine.progress.story_flags)
        self.assertNotIn("miner_tally_stone", engine.progress.inventory)
        self.assertIn("You travel in.", move_lines)
        self.assertEqual(engine.progress.current_room, "miners_supply_cache")

    def test_world_loader_reads_ending_quest_branches(self) -> None:
        root = ET.fromstring(
            """
            <world>
              <quests>
                <quest id="seal_story" name="Seal the Story" giver="elder_rowan" ending="true">
                  <description>End the tale.</description>
                  <completion_text>The last page turns.</completion_text>
                  <ending_text>The keep remembers a wanderer who chose no banner.</ending_text>
                  <ending faction="town_watch">The Town Watch raises your name over every gate.</ending>
                  <ending faction="moon_archive">The Moon Archive writes your victory in silver ink.</ending>
                </quest>
              </quests>
            </world>
            """
        )

        quest = parse_quests(root)["seal_story"]

        self.assertTrue(quest.ends_world)
        self.assertEqual(
            quest.ending_text,
            "The keep remembers a wanderer who chose no banner.",
        )
        self.assertEqual(
            quest.ending_text_by_faction["town_watch"],
            "The Town Watch raises your name over every gate.",
        )
        self.assertEqual(
            quest.ending_text_by_faction["moon_archive"],
            "The Moon Archive writes your victory in silver ink.",
        )

    def test_all_world_files_load(self) -> None:
        world_paths = list_world_files(ROOT / "worlds")
        world_ids = {load_world(path).world_id for path in world_paths}

        self.assertEqual(world_ids, {"emerald_keep"})

    def test_split_world_folder_can_load_from_folder_or_metadata_file(self) -> None:
        folder_world = load_world(WORLD_PATH)
        metadata_world = load_world(WORLD_PATH / "world.xml")

        self.assertEqual(folder_world.world_id, "emerald_keep")
        self.assertEqual(metadata_world.world_id, "emerald_keep")
        self.assertIn("town_square", metadata_world.rooms)

    def test_world_lookup_finds_split_world_by_short_name(self) -> None:
        path = find_world_file("emerald_keep", ROOT / "worlds")

        self.assertEqual(path, WORLD_PATH)

    def test_world_loader_allows_world_without_end_room(self) -> None:
        root = ET.fromstring(
            """
            <world id="quest_ended_world" name="Quest Ended World" start_room="start">
              <player_classes>
                <class id="wanderer" name="Wanderer" max_hp="10" max_mp="0" gold="0" base_attack="1" base_defense="0" />
              </player_classes>
              <rooms>
                <room id="start" name="Start">
                  <description>A simple place where the story can end by quest.</description>
                </room>
              </rooms>
            </world>
            """
        )
        source = Path("inline_world.xml")

        world = parse_world(root, source)
        _validate_world(world, source)

        self.assertEqual(world.start_room, "start")
        self.assertIsNone(world.end_room)

    def test_world_loader_reads_mining_room_drops(self) -> None:
        world = load_world(WORLD_PATH)
        ember_seam = world.rooms["ember_seam"]

        self.assertIn("ember-bright ore", ember_seam.mining_message)
        self.assertEqual(len(ember_seam.mining_drops), 2)
        self.assertEqual(ember_seam.mining_drops[0].item_id, "ember_ore")
        self.assertEqual(ember_seam.mining_drops[0].min_quantity, 1)
        self.assertEqual(ember_seam.mining_drops[0].max_quantity, 3)
        self.assertEqual(ember_seam.mining_drops[1].item_id, "emberglass_ingot")
        self.assertEqual(ember_seam.mining_drops[1].min_quantity, 1)
        self.assertEqual(ember_seam.mining_drops[1].max_quantity, 1)

    def test_emerald_keep_large_campaign_uses_six_zone_progression_hooks(self) -> None:
        world = load_world(WORLD_PATH)

        self.assertGreaterEqual(len(world.rooms), 50)
        self.assertIn("thorn_crown_relic", world.items)
        self.assertIn("emberheart_relic", world.items)
        self.assertIn("mirage_orb_relic", world.items)
        self.assertIn("moonfall_relic", world.items)
        self.assertEqual(world.quests["claim_thorn_relic"].target_enemy, "thorn_matriarch")
        self.assertEqual(world.quests["claim_ember_relic"].target_enemy, "ember_colossus")
        self.assertEqual(world.quests["claim_mirage_relic"].target_enemy, "oasis_sphinx")
        self.assertEqual(world.quests["claim_moonfall_relic"].target_enemy, "moonfall_warden")
        self.assertFalse(world.enemies["thorn_matriarch"].respawns)
        self.assertFalse(world.enemies["ember_colossus"].respawns)
        self.assertFalse(world.enemies["oasis_sphinx"].respawns)
        self.assertFalse(world.enemies["moonfall_warden"].respawns)
        self.assertEqual(world.rooms["relic_gate"].hidden_exits["east"].target_room, "starless_approach")
        self.assertEqual(
            world.rooms["relic_gate"].hidden_exits["east"].required_flag,
            "final_gate_opened",
        )
        self.assertFalse(world.rooms["moon_threshold"].locks_on_exit)
        self.assertEqual(world.rooms["starless_approach"].locks_on_exit, True)
        self.assertEqual(world.rooms["eldergrove"].monster_pool_id, "thornwild_threats")
        self.assertEqual(world.rooms["ember_crosscut"].monster_pool_id, "emberdeep_threats")
        self.assertEqual(world.rooms["moonlit_spring"].monster_pool_id, "oasis_threats")
        self.assertEqual(world.rooms["scriptorium"].monster_pool_id, "moonfall_threats")
        self.assertEqual(world.rooms["void_bastion"].monster_pool_id, "citadel_threats")
        self.assertEqual(len(world.npcs["ranger_ileth"].quest_ids), 3)
        self.assertEqual(len(world.npcs["foreman_borin"].quest_ids), 3)
        self.assertEqual(len(world.npcs["astronomer_sahir"].quest_ids), 3)
        self.assertEqual(len(world.npcs["curator_vesper"].quest_ids), 3)
        self.assertEqual(len(world.npcs["scout_naeve"].quest_ids), 3)
        self.assertTrue(world.quests["end_the_concord_wyrm"].ends_world)

    def test_emerald_keep_relic_gate_uses_all_four_relics_to_open_final_zone(self) -> None:
        world = load_world(WORLD_PATH)
        player = Player(
            name="RelicTester",
            player_class="warrior",
            level=1,
            experience=0,
            gold=35,
            max_hp=42,
            hp=42,
            max_mp=12,
            mp=12,
            base_attack=7,
            base_defense=4,
        )
        engine = GameEngine(world, player, save_callback=lambda player: None)
        engine.progress.current_room = "relic_gate"
        for relic_id in (
            "thorn_crown_relic",
            "emberheart_relic",
            "mirage_orb_relic",
            "moonfall_relic",
        ):
            engine.progress.add_item(relic_id)

        thorn_lines = engine.handle_command("interact thorn seal")
        ember_lines = engine.handle_command("interact ember seal")
        mirage_lines = engine.handle_command("interact mirage seal")
        moon_lines = engine.handle_command("interact moonfall seal")
        move_lines = engine.handle_command("east")

        self.assertIn("thorn_seal_woken", engine.progress.story_flags)
        self.assertIn("ember_seal_woken", engine.progress.story_flags)
        self.assertIn("mirage_seal_woken", engine.progress.story_flags)
        self.assertIn("final_gate_opened", engine.progress.story_flags)
        self.assertIn("Green briars bloom", " ".join(thorn_lines))
        self.assertIn("Heat races through the gate", " ".join(ember_lines))
        self.assertIn("Every false road", " ".join(mirage_lines))
        self.assertIn("Starless Gate opens east", " ".join(moon_lines))
        self.assertEqual(engine.progress.current_room, "starless_approach")
        self.assertIn("You travel east.", move_lines)

    def test_player_can_return_through_moon_threshold_to_accept_ending_quest(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "starless_approach"
        engine.progress.previous_room = "relic_gate"
        engine.progress.completed_quests.extend(
            [
                "claim_thorn_relic",
                "claim_ember_relic",
                "claim_mirage_relic",
                "claim_moonfall_relic",
                "open_starless_gate",
            ]
        )
        engine.progress.add_item("vault_key")
        engine.progress.room_enemies["vault"] = []
        engine.progress.room_enemies["ruins"] = []
        engine.progress.room_enemies["forest_path"] = []

        with patch("ifw.engine.random.randint", return_value=2):
            for direction in (
                "west",
                "west",
                "west",
                "west",
                "west",
                "south",
                "south",
                "south",
                "south",
                "east",
            ):
                move_lines = engine.handle_command(direction)
                self.assertIn(f"You travel {direction}.", move_lines)

        talk_lines = engine.handle_command("talk relic-seer maelis")

        self.assertEqual(engine.progress.current_room, "new_moon_temple")
        self.assertNotIn("moon_threshold", engine.progress.sealed_rooms)
        self.assertNotIn("starless_approach", engine.progress.sealed_rooms)
        self.assertIn(
            "Quest available: End the Concord Wyrm. Use 'accept Relic-Seer Maelis'.",
            talk_lines,
        )

    def test_emerald_keep_velrasha_zone_uses_maze_and_locked_boss_court(self) -> None:
        world = load_world(WORLD_PATH)
        player = Player(
            name="DuneTester",
            player_class="warrior",
            level=1,
            experience=0,
            gold=35,
            max_hp=42,
            hp=42,
            max_mp=12,
            mp=12,
            base_attack=7,
            base_defense=4,
        )
        engine = GameEngine(world, player, save_callback=lambda player: None)
        engine.progress.current_room = "oasis_camp"

        warning_lines = engine.handle_command("accept astronomer sahir")
        lines = engine.handle_command("accept astronomer sahir confirm")

        self.assertEqual(world.rooms["mirage_maze"].maze_success_room, "mirage_cache")
        self.assertEqual(
            world.rooms["mirage_maze"].maze_sequence,
            ["east", "north", "east", "south"],
        )
        self.assertEqual(world.rooms["sphinx_court"].required_item, "desert_compass")
        self.assertEqual(world.rooms["moonlit_spring"].monster_pool_id, "oasis_threats")
        self.assertEqual(world.quests["recover_astrolabe"].required_item, "broken_astrolabe")
        self.assertEqual(world.quests["recover_astrolabe"].reward_item, "desert_compass")
        self.assertIn("Faction warning:", warning_lines[0])
        self.assertIn("Quest accepted: Recover the Broken Astrolabe", lines)

    def test_emerald_keep_velrasha_maze_path_reaches_hidden_cache(self) -> None:
        world = load_world(WORLD_PATH)
        player = Player(
            name="DuneTester",
            player_class="warrior",
            level=1,
            experience=0,
            gold=35,
            max_hp=42,
            hp=42,
            max_mp=12,
            mp=12,
            base_attack=7,
            base_defense=4,
        )
        engine = GameEngine(world, player, save_callback=lambda player: None)
        engine.progress.current_room = "mirage_maze"

        wrong_step_lines = engine.handle_command("south")
        self.assertIn(
            "The desert laughs in heat-haze and returns you to the first false dune.",
            wrong_step_lines,
        )
        self.assertEqual(engine.progress.maze_progress["mirage_maze"], 0)

        first_step_lines = engine.handle_command("east")
        self.assertIn(
            "The mirage thins as you hold to the remembered star path.",
            first_step_lines,
        )

        second_step_lines = engine.handle_command("north")
        self.assertIn(
            "The mirage thins as you hold to the remembered star path.",
            second_step_lines,
        )

        third_step_lines = engine.handle_command("east")
        self.assertIn(
            "The mirage thins as you hold to the remembered star path.",
            third_step_lines,
        )

        final_step_lines = engine.handle_command("south")
        self.assertIn(
            "The false horizon splits, revealing a hidden cache beneath a white stone arch.",
            final_step_lines,
        )
        self.assertEqual(engine.progress.current_room, "mirage_cache")

    def test_world_loader_rejects_invalid_room_and_interaction_content(self) -> None:
        cases = [
            (
                "mixed static enemies and monster pool",
                "cannot define both static enemies and a monster_pool",
                lambda world: world.rooms["forest_path"].enemy_ids.append("forest_wolf"),
            ),
            (
                "maze direction overlaps normal exit",
                "maze directions cannot also be normal exits",
                lambda world: world.rooms["mirage_maze"].exits.__setitem__("east", "oasis_camp"),
            ),
            (
                "unknown faction spawn faction",
                "faction spawn uses unknown faction",
                lambda world: world.rooms["town_square"].faction_enemy_spawns.append(
                    FactionEnemySpawn("missing_order", "bandit_scout")
                ),
            ),
            (
                "unknown faction spawn enemy",
                "faction spawn uses unknown enemy",
                lambda world: world.rooms["town_square"].faction_enemy_spawns.append(
                    FactionEnemySpawn("town_watch", "missing_enemy")
                ),
            ),
            (
                "invalid faction spawn count",
                "must use count >= 1",
                lambda world: world.rooms["town_square"].faction_enemy_spawns.append(
                    FactionEnemySpawn("town_watch", "bandit_scout", count=0)
                ),
            ),
            (
                "hidden exit targets unknown room",
                "hidden exit 'down' targets unknown room",
                lambda world: world.rooms["town_square"].hidden_exits.__setitem__(
                    "down",
                    HiddenExit("down", "forgotten_cellar", "cellar_opened"),
                ),
            ),
            (
                "visible and hidden exit direction overlap",
                "visible and hidden exit",
                lambda world: world.rooms["town_square"].exits.__setitem__("west", "smithy"),
            ),
            (
                "interaction empty set flag",
                "sets an empty flag",
                lambda world: world.rooms["town_square"].interactions.__setitem__(
                    "broken_switch",
                    RoomInteraction("broken_switch", "Broken Switch", set_flags=[""]),
                ),
            ),
            (
                "interaction unknown required item",
                "requires unknown item 'missing_key'",
                lambda world: world.rooms["town_square"].interactions.__setitem__(
                    "sealed_font",
                    RoomInteraction("sealed_font", "Sealed Font", required_item="missing_key"),
                ),
            ),
            (
                "unknown lockpick item",
                "requires unknown lockpick item",
                lambda world: setattr(
                    world.rooms["currency_exchange_office"].interactions["exchange_vault_door"],
                    "lockpick_item",
                    "missing_picks",
                ),
            ),
            (
                "password text without password",
                "defines password text without a password",
                lambda world: setattr(
                    world.rooms["town_square"].interactions["weathered_mural"],
                    "password_text",
                    "The wall answers.",
                ),
            ),
            (
                "room has only one companion dialogue line",
                "must define exactly two companion dialogue lines",
                lambda world: world.rooms["town_square"].companion_dialogue.pop(),
            ),
        ]

        for name, expected_message, mutate_world in cases:
            with self.subTest(name):
                self._assert_world_validation_error(mutate_world, expected_message)

    def test_world_loader_rejects_invalid_actor_and_class_content(self) -> None:
        cases = [
            (
                "bad cycling npc dialogue count",
                "must define exactly three dialogue lines",
                lambda world: world.npcs["well_keeper_mara"].dialogue_lines.pop(),
            ),
            (
                "missing player classes",
                "must define at least one player class",
                lambda world: world.player_classes.clear(),
            ),
            (
                "unknown starter loadout class",
                "starter loadout uses unknown player class",
                lambda world: world.starter_items.__setitem__("chronomancer", []),
            ),
            (
                "unknown spell class restriction",
                "allows unknown player class",
                lambda world: setattr(world.spells["frost_lance"], "allowed_classes", ["chronomancer"]),
            ),
            (
                "unknown npc faction",
                "uses unknown faction",
                lambda world: setattr(world.npcs["elder_rowan"], "faction_id", "missing_order"),
            ),
            (
                "companion without class",
                "must define a companion_class",
                lambda world: (
                    setattr(world.npcs["elder_rowan"], "can_recruit", True),
                    setattr(world.npcs["elder_rowan"], "companion_class", None),
                ),
            ),
            (
                "unknown companion class",
                "uses unknown player class",
                lambda world: (
                    setattr(world.npcs["elder_rowan"], "can_recruit", True),
                    setattr(world.npcs["elder_rowan"], "companion_class", "chronomancer"),
                ),
            ),
            (
                "unknown companion recruit item",
                "requires unknown recruit item",
                lambda world: setattr(
                    world.npcs["trailhand_pip"],
                    "recruit_required_item",
                    "missing_keepsake",
                ),
            ),
            (
                "invalid stealth skill chance",
                "pickpocket_chance must be between 0 and 100",
                lambda world: setattr(world.player_classes["rogue"], "pickpocket_chance", 101),
            ),
        ]

        for name, expected_message, mutate_world in cases:
            with self.subTest(name):
                self._assert_world_validation_error(mutate_world, expected_message)

    def test_world_loader_rejects_invalid_item_content(self) -> None:
        def remove_temporary_effect_duration(world) -> None:
            effect = world.items["fury_draught"].effect
            assert effect is not None
            effect.duration = 0

        cases = [
            (
                "temporary stat consumable without duration",
                "temporary stat effects require duration",
                remove_temporary_effect_duration,
            ),
            (
                "charged consumable",
                "uses charges but is not chargeable",
                lambda world: setattr(world.items["healing_tonic"], "max_charges", 3),
            ),
            (
                "depleted stats without charges",
                "defines depleted stats without charges",
                lambda world: setattr(world.items["chainmail"], "depleted_defense_bonus", 2),
            ),
            (
                "non-consumable recharge item",
                "recharges charges but is not consumable",
                lambda world: setattr(world.items["mana_crystal"], "item_type", "utility"),
            ),
            (
                "non-consumable poison cure",
                "cures poison but is not consumable",
                lambda world: setattr(world.items["antidote"], "item_type", "utility"),
            ),
            (
                "level requirement on non-equipment",
                "uses required_level but is not equipment",
                lambda world: setattr(world.items["healing_tonic"], "required_level", 2),
            ),
            (
                "unknown item type",
                "uses unknown item type",
                lambda world: setattr(world.items["healing_tonic"], "item_type", "gadget"),
            ),
            (
                "invalid level requirement",
                "required_level must be at least 1",
                lambda world: setattr(world.items["iron_spear"], "required_level", 0),
            ),
            (
                "stealth bonus on non-accessory",
                "uses stealth bonuses but is not an accessory",
                lambda world: setattr(world.items["iron_pry_bar"], "lockpick_bonus", 5),
            ),
        ]

        for name, expected_message, mutate_world in cases:
            with self.subTest(name):
                self._assert_world_validation_error(mutate_world, expected_message)

    def test_world_loader_rejects_invalid_enemy_spell_and_pickpocket_content(self) -> None:
        cases = [
            (
                "invalid enemy poison chance",
                "poison_chance must be between 0 and 100",
                lambda world: setattr(world.enemies["forest_snake"], "poison_chance", 101),
            ),
            (
                "poison cure spell with attack school",
                "must use a healing or cure school",
                lambda world: setattr(world.spells["ember_bolt"], "cure_poison", True),
            ),
            (
                "unknown pickpocket item",
                "has unknown pickpocket item",
                lambda world: setattr(
                    world.vendors["exchange_clerk_marlow"].pickpocket_targets[0],
                    "item_id",
                    "missing_key",
                ),
            ),
        ]

        for name, expected_message, mutate_world in cases:
            with self.subTest(name):
                self._assert_world_validation_error(mutate_world, expected_message)

    def test_world_loader_accepts_up_to_ten_ending_choices(self) -> None:
        world = load_world(WORLD_PATH)
        quest = world.quests["cull_the_wolf"]
        quest.ends_world = True
        quest.ending_text = "The keep remembers a wanderer who chose no banner."
        quest.ending_choices = [
            QuestEndingChoice(str(index), f"Choice {index}", f"Ending {index}")
            for index in range(1, 11)
        ]

        _validate_world(world, WORLD_PATH)

    def test_world_loader_rejects_invalid_quest_endings_and_rewards(self) -> None:
        def configure_ending_quest(world):
            quest = world.quests["cull_the_wolf"]
            quest.ends_world = True
            quest.ending_text = "The keep remembers a wanderer who chose no banner."
            return quest

        cases = [
            (
                "unknown ending faction",
                "ending uses unknown faction",
                lambda world: configure_ending_quest(world).ending_text_by_faction.__setitem__(
                    "missing_order",
                    "The missing order claims the ending.",
                ),
            ),
            (
                "too many ending choices",
                "more than 10 ending choices",
                lambda world: setattr(
                    configure_ending_quest(world),
                    "ending_choices",
                    [
                        QuestEndingChoice(str(index), f"Choice {index}", f"Ending {index}")
                        for index in range(1, 12)
                    ],
                ),
            ),
            (
                "custom ending choice without text",
                "must define ending text",
                lambda world: setattr(
                    configure_ending_quest(world),
                    "ending_choices",
                    [QuestEndingChoice("1", "Empty Ending")],
                ),
            ),
            (
                "flag outcome unknown reward item",
                "true flag outcome uses unknown reward item",
                lambda world: setattr(
                    world.quests["cull_the_wolf"],
                    "flag_outcome",
                    QuestFlagOutcome(
                        "town_mural_opened",
                        when_true=QuestFlagBranch(reward_item="missing_item"),
                    ),
                ),
            ),
            (
                "flag outcome unknown reward recipe",
                "false flag outcome uses unknown reward recipe",
                lambda world: setattr(
                    world.quests["cull_the_wolf"],
                    "flag_outcome",
                    QuestFlagOutcome(
                        "town_mural_opened",
                        when_false=QuestFlagBranch(reward_recipe="missing_recipe"),
                    ),
                ),
            ),
            (
                "unknown quest reward currency",
                "uses unknown reward currency",
                lambda world: setattr(world.quests["cull_the_wolf"], "reward_currency", "moon_pebbles"),
            ),
            (
                "unknown flag reward currency",
                "true flag outcome uses unknown reward currency",
                lambda world: setattr(
                    world.quests["cull_the_wolf"],
                    "flag_outcome",
                    QuestFlagOutcome(
                        "town_mural_opened",
                        when_true=QuestFlagBranch(reward_currency="moon_pebbles", reward_amount=2),
                    ),
                ),
            ),
        ]

        for name, expected_message, mutate_world in cases:
            with self.subTest(name):
                self._assert_world_validation_error(mutate_world, expected_message)

    def test_create_player_uses_world_defined_class_template(self) -> None:
        world = load_world(WORLD_PATH)

        with (
            patch("builtins.input", return_value="Warrior"),
            patch("builtins.print"),
            patch("ifw.__main__.save_player"),
        ):
            player = create_player("KeepNewcomer", world)

        self.assertEqual(player.player_class, "warrior")
        self.assertEqual(player.max_hp, 42)
        self.assertEqual(player.max_mp, 12)
        self.assertEqual(player.gold, 35)

    def test_new_world_progress_gets_starter_gear_and_spells(self) -> None:
        engine = self._engine()
        inventory_lines = engine.handle_command("inventory")

        self.assertEqual(engine.progress.weapon_id, "rusty_sword")
        self.assertEqual(engine.progress.armor_id, "padded_armor")
        self.assertIn("ember_bolt", engine.progress.learned_spells)
        self.assertIn("arcane_ward", engine.progress.learned_spells)
        self.assertIn("minor_mend", engine.progress.learned_spells)
        self.assertIn("  [Armor] Padded Armor x1", inventory_lines)
        self.assertIn("  [Weapon] Rusty Sword x1", inventory_lines)

    def test_inventory_sorts_items_by_type_before_name(self) -> None:
        engine = self._engine()
        engine.progress.add_item("healing_tonic")
        engine.progress.add_item("wolf_pelt")
        engine.progress.add_item("vault_key")
        engine.progress.add_item("silver_ring")
        engine.progress.add_item("iron_pry_bar")
        engine.progress.add_item("faded_keepsake")

        lines = engine.handle_command("inventory")

        self.assertLess(lines.index("  [Weapon] Rusty Sword x1"), lines.index("  [Armor] Padded Armor x1"))
        self.assertLess(lines.index("  [Armor] Padded Armor x1"), lines.index("  [Accessory] Silver Ring x1"))
        self.assertLess(lines.index("  [Accessory] Silver Ring x1"), lines.index("  [Consumable] Healing Tonic x1"))
        self.assertLess(lines.index("  [Consumable] Healing Tonic x1"), lines.index("  [Utility] Iron Pry Bar x1"))
        self.assertLess(lines.index("  [Utility] Iron Pry Bar x1"), lines.index("  [Misc] Faded Keepsake x1"))
        self.assertLess(lines.index("  [Misc] Faded Keepsake x1"), lines.index("  [Material] Wolf Pelt x1"))
        self.assertFalse(any("Vault Key" in line for line in lines))

    def test_key_ring_shows_collected_keys(self) -> None:
        engine = self._engine()
        engine.progress.add_item("vault_key")

        inventory_lines = engine.handle_command("inventory")
        key_ring_lines = engine.handle_command("key ring")

        self.assertFalse(any("Vault Key" in line for line in inventory_lines))
        self.assertIn("Key ring:", key_ring_lines)
        self.assertIn("  Vault Key x1", key_ring_lines)

    def test_key_ring_reports_when_no_keys_are_collected(self) -> None:
        engine = self._engine()

        lines = engine.handle_command("keyring")

        self.assertEqual(lines, ["Key ring:", "  No keys collected."])

    def test_crafting_recipe_consumes_parts_and_creates_result(self) -> None:
        engine = self._engine()
        engine.progress.add_item("iron_blade")
        engine.progress.add_item("oak_haft")
        engine.progress.unlocked_recipes.append("iron_spear_pattern")

        lines = engine.handle_command("combine iron blade with oak haft")

        self.assertIn("You craft Iron Spear.", lines)
        self.assertEqual(engine.progress.inventory.get("iron_blade", 0), 0)
        self.assertEqual(engine.progress.inventory.get("oak_haft", 0), 0)
        self.assertEqual(engine.progress.inventory.get("iron_spear", 0), 1)

    def test_equipment_level_requirement_blocks_early_equips(self) -> None:
        engine = self._engine()
        engine.progress.add_item("iron_spear")

        early_lines = engine.handle_command("equip iron spear")
        self.assertIn("Iron Spear requires level 2. You are level 1.", early_lines)
        self.assertEqual(engine.progress.weapon_id, "rusty_sword")

        self.player.level = 2
        ready_lines = engine.handle_command("equip iron spear")

        self.assertIn("You equip Iron Spear as your weapon.", ready_lines)
        self.assertEqual(engine.progress.weapon_id, "iron_spear")

    def test_existing_save_unequips_items_above_player_level(self) -> None:
        self.player.world_states[self.world.world_id] = WorldProgress(
            current_room=self.world.start_room,
            inventory={"iron_spear": 1, "chainmail": 1, "guardian_band": 1},
            weapon_id="iron_spear",
            armor_id="chainmail",
            accessory_ids=["guardian_band"],
        )

        engine = self._engine()

        self.assertIsNone(engine.progress.weapon_id)
        self.assertIsNone(engine.progress.armor_id)
        self.assertEqual(engine.progress.accessory_ids, [])
        self.assertIn(
            "Unequipped items above your level: Iron Spear, Chainmail, Guardian Band.",
            engine.opening_lines(),
        )

    def test_existing_save_loads_companion_with_depleted_magical_armor(self) -> None:
        self.player.level = 6
        saved_progress = WorldProgress(
            current_room=self.world.start_room,
            companions=[
                CompanionState(
                    npc_id="squire_tovin",
                    class_id="warrior",
                    origin_room="lantern_inn",
                    current_hp=999,
                    current_mp=999,
                    weapon_id="rusty_sword",
                    armor_id="serpentstep_jacket",
                    spell_ids=["ember_bolt"],
                )
            ],
            item_charges={"serpentstep_jacket": 0},
        )
        self.player.world_states[self.world.world_id] = saved_progress

        engine = self._engine()
        companion = engine.progress.companions[0]

        self.assertIs(engine.progress, saved_progress)
        self.assertEqual(companion.armor_id, "serpentstep_jacket")
        self.assertEqual(engine._effective_item_bonus("serpentstep_jacket", "hp_bonus"), 2)
        self.assertEqual(companion.current_hp, engine._companion_max_hp(companion))
        self.assertEqual(companion.current_mp, engine._companion_max_mp(companion))

    def test_world_class_growth_controls_level_up_stats(self) -> None:
        self.player.player_class = "mage"
        self.player.experience = 90
        self.player.max_hp = 28
        self.player.hp = 28
        self.player.max_mp = 26
        self.player.mp = 26
        self.player.base_attack = 4
        self.player.base_defense = 2
        engine = self._engine()

        lines = engine._gain_player_experience(10)

        self.assertIn("You reached level 2. Your strength and reserves surge back to full.", lines)
        self.assertEqual(engine.player.max_hp, 33)
        self.assertEqual(engine.player.max_mp, 33)
        self.assertEqual(engine.player.base_attack, 5)
        self.assertEqual(engine.player.base_defense, 3)

    def test_leveling_threshold_increases_by_fifty_experience_each_level(self) -> None:
        engine = self._engine()

        first_lines = engine._gain_player_experience(100)
        almost_third_lines = engine._gain_player_experience(149)
        third_lines = engine._gain_player_experience(1)
        almost_fourth_lines = engine._gain_player_experience(199)
        fourth_lines = engine._gain_player_experience(1)

        self.assertEqual(engine.player.experience_to_next_level(), 700)
        self.assertIn("You reached level 2. Your strength and reserves surge back to full.", first_lines)
        self.assertEqual(almost_third_lines, [])
        self.assertEqual(engine.player.level, 4)
        self.assertIn("You reached level 3. Your strength and reserves surge back to full.", third_lines)
        self.assertEqual(almost_fourth_lines, [])
        self.assertIn("You reached level 4. Your strength and reserves surge back to full.", fourth_lines)

    def test_recipe_can_be_unlocked_by_vendor_purchase(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "smithy"

        lines = engine.handle_command("buy iron spear pattern")

        self.assertIn("You buy Iron Spear Pattern for 18 gold.", lines)
        self.assertIn("Recipe unlocked: Iron Spear.", lines)
        self.assertEqual(engine.player.gold, 17)
        self.assertEqual(engine.progress.unlocked_recipes, ["iron_spear_pattern"])

    def test_shop_marks_equipment_level_requirements(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "smithy"

        lines = engine.handle_command("shop")

        self.assertIn("Accepted currencies: gold, emerald marks.", lines)
        self.assertIn("  [Armor] Chainmail [requires level 2] - 55 gold", lines)
        self.assertIn("  [Accessory] Silver Ring - 5 emerald marks", lines)
        self.assertIn("  [Recipe] Iron Spear Pattern - 18 gold", lines)

    def test_shop_marks_vendor_spells_with_spell_category(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("shop")

        self.assertIn("  [Spell] Frost Lance [Mage only] - 18 gold", lines)
        self.assertIn("  [Spell] Shadow Palm [Rogue only] - 15 gold", lines)
        self.assertIn("Use 'examine <item or spell>' to inspect stock before buying.", lines)

    def test_shop_sorts_item_stock_by_type_before_name(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "smithy"

        lines = engine.handle_command("shop")

        self.assertLess(lines.index("  [Weapon] Watch Halberd [requires level 3] - 68 gold"), lines.index("  [Armor] Chainmail [requires level 2] - 55 gold"))
        self.assertLess(lines.index("  [Armor] Watch Coat [requires level 2] - 42 gold"), lines.index("  [Accessory] Nimble Fingers Ring - 6 emerald marks"))
        self.assertLess(lines.index("  [Accessory] Silver Ring - 5 emerald marks"), lines.index("  [Consumable] Antidote - 18 gold"))
        self.assertLess(lines.index("  [Consumable] Mana Tonic - 15 gold"), lines.index("  [Utility] Field Trowel - 14 gold"))
        self.assertLess(lines.index("  [Utility] Rubbing Kit - 18 gold"), lines.index("  [Material] Oak Haft - 10 gold"))

    def test_examine_vendor_spell_shows_spell_details(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "mage_tower"

        lines = engine.handle_command("examine frost lance")

        self.assertEqual(lines[0], "Frost Lance")
        self.assertIn("A mage-only spear of cold light that punches through ordinary defenses.", lines)
        self.assertIn("School: Offense", lines)
        self.assertIn("MP cost: 7", lines)
        self.assertIn("Power level: 16", lines)
        self.assertIn("Classes: Mage", lines)

    def test_exchange_vendor_trades_between_world_currencies(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"

        rate_lines = engine.handle_command("rates")
        exchange_lines = engine.handle_command("exchange 10 gold to emerald marks")
        wallet_lines = engine.handle_command("wallet")

        self.assertIn("  5 gold -> 1 emerald mark", rate_lines)
        self.assertIn("You exchange 10 gold for 2 emerald marks.", exchange_lines)
        self.assertEqual(engine.player.gold, 25)
        self.assertEqual(engine.player.wallet["emerald_mark"], 2)
        self.assertIn("  25 gold", wallet_lines)
        self.assertIn("  2 emerald marks", wallet_lines)

    def test_vendor_can_price_stock_in_alternate_currency(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"
        engine.handle_command("exchange 25 gold to emerald marks")
        engine.progress.current_room = "smithy"

        lines = engine.handle_command("buy silver ring")

        self.assertIn("You buy Silver Ring for 5 emerald marks.", lines)
        self.assertEqual(engine.player.gold, 10)
        self.assertEqual(engine.player.wallet["emerald_mark"], 0)
        self.assertEqual(engine.progress.inventory.get("silver_ring"), 1)

    def test_rogue_starts_with_lockpicks(self) -> None:
        self.player.player_class = "rogue"
        engine = self._engine()

        self.assertEqual(engine.progress.inventory.get("lockpicks"), 1)

    def test_non_rogue_cannot_use_stealth_skills(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"

        pickpocket_lines = engine.handle_command("pickpocket exchange clerk marlow for exchange vault key")
        lockpick_lines = engine.handle_command("lockpick exchange vault door")

        self.assertEqual(pickpocket_lines, ["Your class has no pickpocket training."])
        self.assertEqual(lockpick_lines, ["Your class has no lockpick training."])

    def test_non_rogue_can_pickpocket_with_rogue_companion(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"
        self._add_rogue_companion(engine)

        with patch("ifw.engine.random.randint", return_value=1):
            lines = engine.handle_command("pickpocket exchange clerk marlow for exchange vault key")

        self.assertIn(
            "Trailhand Pip lifts Exchange Vault Key from Exchange Clerk Marlow and slips it into your pack.",
            lines,
        )
        self.assertEqual(engine.progress.inventory.get("exchange_vault_key"), 1)
        self.assertIn(
            "vendor:exchange_clerk_marlow:exchange_vault_key",
            engine.progress.pickpocketed_targets,
        )

    def test_failed_companion_pickpocket_sends_player_to_jail(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"
        self._add_rogue_companion(engine)

        with patch("ifw.engine.random.randint", return_value=100):
            lines = engine.handle_command("pickpocket exchange clerk marlow for exchange vault key")

        self.assertIn(
            "Exchange Clerk Marlow catches Trailhand Pip reaching for Exchange Vault Key. "
            "You take the blame before the Watch can ask whose idea it was.",
            lines,
        )
        self.assertIn("You are arrested and taken to Town Jail.", lines)
        self.assertEqual(engine.progress.current_room, "town_jail")

    def test_companion_lockpick_still_requires_player_lockpicks(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"
        self._add_rogue_companion(engine)

        lines = engine.handle_command("lockpick exchange vault door")

        self.assertEqual(lines, ["You need Lockpicks before you can work the vault's leaf-lock."])

    def test_non_rogue_can_lockpick_with_rogue_companion(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"
        engine.progress.add_item("lockpicks")
        self._add_rogue_companion(engine)

        with patch("ifw.engine.random.randint", return_value=1):
            lines = engine.handle_command("lockpick exchange vault door")

        self.assertIn("Trailhand Pip picks the lock on Exchange Vault Door for you.", lines)
        self.assertIn("You use Lockpicks.", lines)
        self.assertIn("A path is revealed: east -> Exchange Vault.", lines)
        self.assertIn("exchange_vault_opened", engine.progress.story_flags)

    def test_rogue_can_pickpocket_specific_vendor_item(self) -> None:
        self.player.player_class = "rogue"
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"

        with patch("ifw.engine.random.randint", return_value=1):
            lines = engine.handle_command("pickpocket exchange clerk marlow for exchange vault key")

        self.assertIn(
            "You palm the Exchange Vault Key from Marlow's waist chain while he checks a ledger.",
            lines,
        )
        self.assertEqual(engine.progress.inventory.get("exchange_vault_key"), 1)
        self.assertIn(
            "vendor:exchange_clerk_marlow:exchange_vault_key",
            engine.progress.pickpocketed_targets,
        )

    def test_rogue_pickpocket_spell_temporarily_boosts_pickpocket_chance(self) -> None:
        self.player.player_class = "rogue"
        self.player.max_mp = 18
        self.player.mp = 18
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"
        engine.progress.learned_spells.append("shadow_palm")
        target = self.world.vendors["exchange_clerk_marlow"].pickpocket_targets[0]

        self.assertEqual(engine._pickpocket_success_chance(target), 55)
        cast_lines = engine.handle_command("cast shadow palm")
        stats_after_cast = engine.handle_command("stats")

        self.assertIn("You cast Shadow Palm; pickpocket chance +20% for 3 turns.", cast_lines)
        self.assertEqual(engine._pickpocket_success_chance(target), 75)
        self.assertIn("Active magic: Shadow Palm (3 turns)", stats_after_cast)
        self.assertIn("Stealth: Pickpocket 85%, Lockpick 60%", stats_after_cast)

        with patch("ifw.engine.random.randint", return_value=70):
            steal_lines = engine.handle_command("pickpocket exchange clerk marlow for exchange vault key")

        self.assertIn(
            "You palm the Exchange Vault Key from Marlow's waist chain while he checks a ledger.",
            steal_lines,
        )
        self.assertIn("Active magic: Shadow Palm (2 turns)", engine.handle_command("stats"))

    def test_failed_pickpocket_sends_player_to_jail_until_bail_is_paid(self) -> None:
        self.player.player_class = "rogue"
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"

        with patch("ifw.engine.random.randint", return_value=100):
            arrest_lines = engine.handle_command("pickpocket exchange clerk marlow for exchange vault key")
        bail_lines = engine.handle_command("pay bail")

        self.assertIn("Marlow snaps the ledger shut on your wrist and calls for the Watch.", arrest_lines)
        self.assertIn("You are arrested and taken to Town Jail.", arrest_lines)
        self.assertIn("Pay 15 gold with 'pay bail' to leave.", arrest_lines)
        self.assertEqual(engine.progress.current_room, "town_square")
        self.assertIn("You pay 15 gold and are released.", bail_lines)
        self.assertEqual(engine.player.gold, 20)

    def test_failed_pickpocket_without_bail_at_level_one_ends_game(self) -> None:
        self.player.player_class = "rogue"
        self.player.gold = 0
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"

        with patch("ifw.engine.random.randint", return_value=100):
            lines = engine.handle_command("pickpocket exchange clerk marlow for exchange vault key")

        self.assertTrue(engine.game_over)
        self.assertIn("Game over.", lines)
        self.assertIn("Final player stats:", lines)
        self.assertIn("you have no level to spare", " ".join(lines))

    def test_player_can_escape_jail_by_losing_level_when_bail_is_unavailable(self) -> None:
        self.player.player_class = "rogue"
        self.player.level = 2
        self.player.experience = 150
        self.player.gold = 0
        self.player.max_hp = 41
        self.player.hp = 41
        self.player.max_mp = 23
        self.player.mp = 23
        self.player.base_attack = 8
        self.player.base_defense = 4
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"

        with patch("ifw.engine.random.randint", return_value=100):
            arrest_lines = engine.handle_command("pickpocket exchange clerk marlow for exchange vault key")
        escape_lines = engine.handle_command("escape jail")

        self.assertTrue(
            any("Use 'escape jail' to lose a level and slip out." in line for line in arrest_lines)
        )
        self.assertIn("Level reduced: 2 -> 1.", escape_lines)
        self.assertEqual(engine.player.level, 1)
        self.assertEqual(engine.player.experience, 99)
        self.assertEqual(engine.player.max_hp, 34)
        self.assertEqual(engine.player.max_mp, 18)
        self.assertEqual(engine.progress.current_room, "town_square")

    def test_lockpick_requires_lockpicks(self) -> None:
        self.player.player_class = "rogue"
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"
        engine.progress.remove_item("lockpicks")

        lines = engine.handle_command("lockpick exchange vault door")

        self.assertEqual(lines, ["You need Lockpicks before you can work the vault's leaf-lock."])

    def test_rogue_can_lockpick_exchange_vault(self) -> None:
        self.player.player_class = "rogue"
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"

        with patch("ifw.engine.random.randint", return_value=1):
            lines = engine.handle_command("lockpick exchange vault door")
        move_lines = engine.handle_command("east")

        self.assertIn(
            "You tease the leaf-lock open with a quiet click, and the exchange vault door swings inward.",
            lines,
        )
        self.assertIn("A path is revealed: east -> Exchange Vault.", lines)
        self.assertIn("exchange_vault_opened", engine.progress.story_flags)
        self.assertEqual(engine.progress.current_room, "exchange_vault")
        self.assertIn("You travel east.", move_lines)

    def test_rogue_lockpick_spell_temporarily_boosts_lockpick_chance(self) -> None:
        self.player.player_class = "rogue"
        self.player.max_mp = 18
        self.player.mp = 18
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"
        engine.progress.learned_spells.append("lock_whisper")
        interaction = self.world.rooms["currency_exchange_office"].interactions["exchange_vault_door"]

        self.assertEqual(engine._lockpick_success_chance(interaction), 45)
        cast_lines = engine.handle_command("cast lock whisper")
        stats_after_cast = engine.handle_command("stats")

        self.assertIn("You cast Lock Whisper; lockpick chance +20% for 3 turns.", cast_lines)
        self.assertEqual(engine._lockpick_success_chance(interaction), 65)
        self.assertIn("Active magic: Lock Whisper (3 turns)", stats_after_cast)
        self.assertIn("Stealth: Pickpocket 65%, Lockpick 80%", stats_after_cast)

        with patch("ifw.engine.random.randint", return_value=60):
            lines = engine.handle_command("lockpick exchange vault door")

        self.assertIn(
            "You tease the leaf-lock open with a quiet click, and the exchange vault door swings inward.",
            lines,
        )
        self.assertIn("Active magic: Lock Whisper (2 turns)", engine.handle_command("stats"))

    def test_key_can_open_exchange_vault_without_lockpicking(self) -> None:
        self.player.player_class = "rogue"
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"

        with patch("ifw.engine.random.randint", return_value=1):
            engine.handle_command("pickpocket exchange clerk marlow for exchange vault key")
        lines = engine.handle_command("use exchange vault key on exchange vault door")

        self.assertIn(
            "The Exchange Vault Key turns with a soft click, and the vault door opens into green lamplight.",
            lines,
        )
        self.assertIn("exchange_vault_opened", engine.progress.story_flags)

    def test_three_failed_lockpicks_break_one_set_of_picks(self) -> None:
        self.player.player_class = "rogue"
        engine = self._engine()
        engine.progress.current_room = "currency_exchange_office"

        with patch("ifw.engine.random.randint", return_value=100):
            first_lines = engine.handle_command("lockpick exchange vault door")
            second_lines = engine.handle_command("lockpick exchange vault door")
            third_lines = engine.handle_command("lockpick exchange vault door")

        self.assertIn("Lockpick failures: 1/3.", first_lines)
        self.assertIn("Lockpick failures: 2/3.", second_lines)
        self.assertIn("Lockpicks break and will need to be replaced.", third_lines)
        self.assertNotIn("lockpicks", engine.progress.inventory)
        self.assertEqual(engine.progress.lockpick_failures, {})

    def test_spell_vendor_can_sell_new_spell(self) -> None:
        self.player.player_class = "mage"
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy frost lance")

        self.assertIn("You buy Frost Lance for 18 gold.", lines)
        self.assertIn("Spell learned: Frost Lance.", lines)
        self.assertEqual(engine.player.gold, 17)
        self.assertIn("frost_lance", engine.progress.learned_spells)

    def test_spell_vendor_can_sell_rogue_stealth_spell(self) -> None:
        self.player.player_class = "rogue"
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy shadow palm")

        self.assertIn("You buy Shadow Palm for 15 gold.", lines)
        self.assertIn("Spell learned: Shadow Palm.", lines)
        self.assertEqual(engine.player.gold, 20)
        self.assertIn("shadow_palm", engine.progress.learned_spells)

    def test_non_mage_cannot_buy_mage_only_spell(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy frost lance")

        self.assertIn("Frost Lance can only be learned by Mage characters.", lines)
        self.assertEqual(engine.player.gold, 35)
        self.assertNotIn("frost_lance", engine.progress.learned_spells)

    def test_warrior_can_buy_warrior_only_attack_spell(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy battle focus")

        self.assertIn("You buy Battle Focus for 16 gold.", lines)
        self.assertIn("Spell learned: Battle Focus.", lines)
        self.assertEqual(engine.player.gold, 19)
        self.assertIn("battle_focus", engine.progress.learned_spells)

    def test_non_warrior_cannot_buy_warrior_only_attack_spell(self) -> None:
        self.player.player_class = "mage"
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy battle focus")

        self.assertIn("Battle Focus can only be learned by Warrior characters.", lines)
        self.assertEqual(engine.player.gold, 35)
        self.assertNotIn("battle_focus", engine.progress.learned_spells)

    def test_spellbook_item_can_be_used_to_learn_spell(self) -> None:
        self.player.player_class = "mage"
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        buy_lines = engine.handle_command("buy sunfire codex")
        use_lines = engine.handle_command("use sunfire codex")

        self.assertIn("You buy Sunfire Codex for 22 gold.", buy_lines)
        self.assertIn("You study Sunfire Codex.", use_lines)
        self.assertIn("Spell learned: Sunfire Burst.", use_lines)
        self.assertNotIn("sunfire_codex", engine.progress.inventory)
        self.assertIn("sunfire_burst", engine.progress.learned_spells)

    def test_non_mage_cannot_buy_mage_only_spellbook(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy sunfire codex")

        self.assertIn("Sunfire Burst can only be learned by Mage characters.", lines)
        self.assertEqual(engine.player.gold, 35)
        self.assertNotIn("sunfire_codex", engine.progress.inventory)

    def test_non_mage_cannot_use_mage_only_spellbook(self) -> None:
        engine = self._engine()
        engine.progress.add_item("sunfire_codex")

        lines = engine.handle_command("use sunfire codex")

        self.assertIn("Sunfire Burst can only be learned by Mage characters.", lines)
        self.assertEqual(engine.progress.inventory.get("sunfire_codex"), 1)
        self.assertNotIn("sunfire_burst", engine.progress.learned_spells)

    def test_spell_vendor_can_sell_spell_to_companion(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit apprentice mira")
        companion = engine.progress.companions[0]
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy frost lance for apprentice mira")

        self.assertIn("You buy Frost Lance for 18 gold and teach it to Apprentice Mira.", lines)
        self.assertIn("Apprentice Mira learned Frost Lance.", lines)
        self.assertEqual(engine.player.gold, 17)
        self.assertIn("frost_lance", companion.spell_ids)
        self.assertNotIn("frost_lance", engine.progress.learned_spells)

    def test_companion_spell_purchase_uses_companion_class_restrictions(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit apprentice mira")
        companion = engine.progress.companions[0]
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy battle focus for apprentice mira")

        self.assertIn("Battle Focus can only be learned by Warrior characters.", lines)
        self.assertEqual(engine.player.gold, 35)
        self.assertNotIn("battle_focus", companion.spell_ids)

    def test_spellbook_purchase_can_teach_companion(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit apprentice mira")
        companion = engine.progress.companions[0]
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy sunfire codex for apprentice mira")

        self.assertIn("You buy Sunfire Codex for 22 gold and give it to Apprentice Mira.", lines)
        self.assertIn("Apprentice Mira learned Sunfire Burst.", lines)
        self.assertEqual(engine.player.gold, 13)
        self.assertIn("sunfire_burst", companion.spell_ids)
        self.assertNotIn("sunfire_codex", engine.progress.inventory)

    def test_companion_spell_purchase_requires_active_companion(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("buy frost lance for apprentice mira")

        self.assertEqual(lines, ["That companion is not traveling with you."])
        self.assertEqual(engine.player.gold, 35)

    def test_non_mage_cannot_cast_mage_only_spell(self) -> None:
        engine = self._engine()
        self._place_forest_wolf(engine)
        engine.progress.learned_spells.append("frost_lance")

        lines = engine.handle_command("cast frost lance on forest wolf")

        self.assertIn("Frost Lance can only be cast by Mage characters.", lines)
        self.assertEqual(engine.player.mp, 12)

    def test_warrior_attack_spell_boosts_attack_score(self) -> None:
        engine = self._engine()
        engine.progress.learned_spells.append("battle_focus")
        base_attack = engine._player_attack_score()

        cast_lines = engine.handle_command("cast battle focus")
        stats_lines = engine.handle_command("stats")

        self.assertIn("You cast Battle Focus and sharpen your attacks.", cast_lines)
        self.assertEqual(engine.player.mp, 8)
        self.assertEqual(engine._player_attack_score(), base_attack + 4)
        self.assertIn(f"Attack {base_attack + 4}  Defense {engine._player_defense_score()}", stats_lines)
        self.assertIn("Active magic: Battle Focus (3 turns)", stats_lines)

    def test_attack_buff_cast_in_combat_lasts_until_player_attacks(self) -> None:
        engine = self._engine()
        self._place_forest_wolf(engine)
        engine.progress.learned_spells.append("battle_focus")

        with patch("ifw.engine.random.randint", return_value=100):
            cast_lines = engine.handle_command("cast battle focus")
        stats_after_cast = engine.handle_command("stats")

        with patch("ifw.engine.random.randint", side_effect=[1, 0, 100]):
            attack_lines = engine.handle_command("attack forest wolf")
        stats_after_attack = engine.handle_command("stats")

        self.assertIn("You cast Battle Focus and sharpen your attacks.", cast_lines)
        self.assertIn("  Forest Wolf misses you.", cast_lines)
        self.assertIn("Active magic: Battle Focus (3 turns)", stats_after_cast)
        self.assertIn("Forest Wolf has 2 HP left.", attack_lines)
        self.assertIn("Active magic: Battle Focus (2 turns)", stats_after_attack)

    def test_non_warrior_cannot_cast_warrior_only_attack_spell(self) -> None:
        self.player.player_class = "mage"
        engine = self._engine()
        engine.progress.learned_spells.append("battle_focus")

        lines = engine.handle_command("cast battle focus")

        self.assertIn("Battle Focus can only be cast by Warrior characters.", lines)
        self.assertEqual(engine.player.mp, 12)

    def test_low_grade_healing_spell_restores_less_than_healing_tonic(self) -> None:
        engine = self._engine()
        tonic_effect = self.world.items["healing_tonic"].effect
        assert tonic_effect is not None
        engine.player.hp = 20

        lines = engine.handle_command("cast minor mend")
        spell_lines = engine.handle_command("spells")

        self.assertIn("You cast Minor Mend and restore 8 HP.", lines)
        self.assertEqual(engine.player.hp, 28)
        self.assertEqual(engine.player.mp, 9)
        self.assertLess(self.world.spells["minor_mend"].power, tonic_effect.hp_restore)
        self.assertTrue(any("Minor Mend [healing] (heals 8 HP)" in line for line in spell_lines))

    def test_healing_spell_cannot_be_wasted_at_full_health(self) -> None:
        engine = self._engine()

        lines = engine.handle_command("cast minor mend")

        self.assertIn("You are already at full health.", lines)
        self.assertEqual(engine.player.hp, 42)
        self.assertEqual(engine.player.mp, 12)

    def test_control_spell_prevents_enemy_next_attack(self) -> None:
        engine = self._engine()
        state = self._place_forest_wolf(engine)
        engine.progress.learned_spells.append("flash")

        with patch("ifw.engine.random.randint", return_value=1):
            lines = engine.handle_command("cast flash on forest wolf")

        self.assertIn("You cast Flash on Forest Wolf. Forest Wolf will miss its next attack.", lines)
        self.assertIn("  Forest Wolf is dazzled and cannot attack.", lines)
        self.assertEqual(state.skip_turns, 0)
        self.assertEqual(engine.player.hp, 42)
        self.assertEqual(engine.player.mp, 8)

    def test_control_spell_can_miss(self) -> None:
        engine = self._engine()
        state = self._place_forest_wolf(engine)
        engine.progress.learned_spells.append("flash")

        with patch("ifw.engine.random.randint", side_effect=[100, 100]):
            lines = engine.handle_command("cast flash on forest wolf")

        self.assertIn("Flash misses Forest Wolf.", lines)
        self.assertIn("  Forest Wolf misses you.", lines)
        self.assertEqual(state.skip_turns, 0)
        self.assertEqual(engine.player.mp, 8)

    def test_enemy_can_prevent_player_next_attack(self) -> None:
        engine = self._engine()
        wolf = self.world.enemies["forest_wolf"]
        wolf.prevent_attack_chance = 100
        wolf.prevent_attack_turns = 1
        wolf.prevent_attack_text = "The wolf kicks dust into your eyes. Your next attack will falter."
        state = self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", side_effect=[1, 0, 1]):
            enemy_lines = engine._enemy_turn()
        stats_lines = engine.handle_command("stats")
        with patch("ifw.engine.random.randint", return_value=100):
            attack_lines = engine.handle_command("attack forest wolf")

        self.assertIn("  The wolf kicks dust into your eyes. Your next attack will falter.", enemy_lines)
        self.assertIn("Attack disrupted: 1 turn(s)", stats_lines)
        self.assertIn("You are disoriented and cannot attack this turn.", attack_lines)
        self.assertEqual(state.current_hp, 16)
        self.assertEqual(engine.player_attack_block_turns, 0)

    def test_enemy_can_poison_player_on_hit(self) -> None:
        engine = self._engine()
        wolf = self.world.enemies["forest_wolf"]
        wolf.poison_chance = 100
        wolf.poison_text = "The wolf's fangs leave venom burning in your blood."
        self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", side_effect=[1, 0, 1]):
            enemy_lines = engine._enemy_turn()
        stats_lines = engine.handle_command("stats")

        self.assertIn("  The wolf's fangs leave venom burning in your blood.", enemy_lines)
        self.assertTrue(engine.progress.player_poisoned)
        self.assertIn("Status: Poisoned", stats_lines)

    def test_poison_ticks_at_start_of_player_combat_turn(self) -> None:
        engine = self._engine()
        engine.progress.player_poisoned = True
        state = self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", side_effect=[2, 1, 0, 100]):
            lines = engine.handle_command("attack forest wolf")

        self.assertEqual(lines[0], "Poison burns through you for 2 damage.")
        self.assertIn("Forest Wolf has 6 HP left.", lines)
        self.assertEqual(state.current_hp, 6)
        self.assertEqual(engine.player.hp, 40)
        self.assertTrue(engine.progress.player_poisoned)

    def test_antidote_cures_poison_without_poison_tick(self) -> None:
        engine = self._engine()
        engine.progress.player_poisoned = True
        engine.player.hp = 20
        engine.progress.add_item("antidote")
        self._place_forest_wolf(engine)

        lines = engine.handle_command("use antidote")

        self.assertEqual(lines, ["You use Antidote. Poison cured."])
        self.assertFalse(engine.progress.player_poisoned)
        self.assertEqual(engine.player.hp, 20)
        self.assertNotIn("antidote", engine.progress.inventory)

    def test_poison_cure_spell_clears_poison(self) -> None:
        engine = self._engine()
        engine.progress.player_poisoned = True
        engine.progress.learned_spells.append("purify_blood")

        lines = engine.handle_command("cast purify blood")

        self.assertEqual(lines, ["You cast Purify Blood and purge the poison."])
        self.assertFalse(engine.progress.player_poisoned)
        self.assertEqual(engine.player.mp, 8)

    def test_poison_tick_can_defeat_player_and_clears_on_recovery(self) -> None:
        engine = self._engine()
        engine.progress.player_poisoned = True
        engine.player.hp = 1
        self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", return_value=3):
            lines = engine.handle_command("attack forest wolf")

        self.assertIn("Poison burns through you for 3 damage.", lines)
        self.assertIn("You are overwhelmed and collapse.", lines)
        self.assertFalse(engine.progress.player_poisoned)
        self.assertEqual(engine.progress.current_room, self.world.start_room)
        self.assertEqual(engine.player.hp, engine._player_max_hp())

    def test_enemy_attack_block_prevents_offense_spell_without_costing_mp(self) -> None:
        engine = self._engine()
        state = self._place_forest_wolf(engine)
        engine.player_attack_block_turns = 1

        with patch("ifw.engine.random.randint", return_value=100):
            lines = engine.handle_command("cast ember bolt on forest wolf")

        self.assertIn("You are disoriented and cannot attack this turn.", lines)
        self.assertEqual(state.current_hp, 16)
        self.assertEqual(engine.player.mp, 12)
        self.assertEqual(engine.player_attack_block_turns, 0)

    def test_recipe_is_not_available_before_unlock(self) -> None:
        engine = self._engine()
        engine.progress.add_item("iron_blade")
        engine.progress.add_item("oak_haft")

        lines = engine.handle_command("craft iron spear pattern")

        self.assertIn("You have not unlocked any recipes yet.", lines)

    def test_crafting_recipe_honors_ingredient_quantities(self) -> None:
        engine = self._engine()
        engine.progress.unlocked_recipes.append("wild_mage_robe_pattern")
        engine.progress.add_item("wolf_pelt")
        engine.progress.add_item("bear_pelt")

        missing_lines = engine.handle_command("craft wild mage robe pattern")
        engine.progress.add_item("wolf_pelt")
        craft_lines = engine.handle_command("craft wild mage robe pattern")

        self.assertIn("You do not have the required crafting materials.", missing_lines)
        self.assertIn("You craft Wild Mage Robe.", craft_lines)
        self.assertEqual(engine.progress.inventory.get("wolf_pelt", 0), 0)
        self.assertEqual(engine.progress.inventory.get("bear_pelt", 0), 0)
        self.assertEqual(engine.progress.inventory.get("wild_mage_robe"), 1)

    def test_quest_reward_can_unlock_recipe(self) -> None:
        engine = self._engine()
        engine.progress.active_quests.append("recover_the_sigil")
        engine.progress.add_item("moon_sigil")
        engine.progress.current_room = "vault"

        early_lines = engine._check_quest_completion()
        engine.progress.current_room = "forest_path"
        engine.progress.room_enemies["forest_path"] = []
        turn_in_lines = engine.handle_command("in")

        self.assertEqual(early_lines, [])
        self.assertIn("You travel in.", turn_in_lines)
        self.assertIn("recover_the_sigil", engine.progress.completed_quests)
        self.assertNotIn("moon_sigil", engine.progress.inventory)
        self.assertIn("Quest complete: Recover the Sigil", turn_in_lines)
        self.assertIn("Reward recipe unlocked: Guardian Band Pattern", turn_in_lines)
        self.assertIn("guardian_band_pattern", engine.progress.unlocked_recipes)

    def test_quest_flag_outcome_uses_false_branch_when_flag_is_missing(self) -> None:
        engine = self._engine()
        engine.progress.active_quests.append("read_the_ore")
        engine.progress.add_item("glimmer_ore")
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine._check_quest_completion()

        self.assertIn("Quest complete: Read the Ore", lines)
        self.assertIn(
            "Nox reads the ore by candlelight, frowns, then rewards you for surviving scholarship.",
            lines,
        )
        self.assertIn("Reward: 25 gold", lines)
        self.assertIn("Reward: 55 experience", lines)
        self.assertIn("Reward item: Warding Pendant", lines)
        self.assertNotIn("Reward recipe unlocked: Wild Mage Robe Pattern", lines)
        self.assertEqual(engine.player.gold, 60)
        self.assertEqual(engine.progress.inventory.get("warding_pendant"), 1)
        self.assertNotIn("wild_mage_robe_pattern", engine.progress.unlocked_recipes)

    def test_quest_flag_outcome_uses_true_branch_rewards_when_flag_is_set(self) -> None:
        engine = self._engine()
        engine.progress.active_quests.append("read_the_ore")
        engine.progress.add_item("glimmer_ore")
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []
        engine.progress.story_flags.append("ore_cipher_decoded")

        lines = engine._check_quest_completion()

        self.assertIn("Quest complete: Read the Ore", lines)
        self.assertIn(
            "Nox compares your cipher marks to the ore and grins like a locked door just apologized.",
            lines,
        )
        self.assertIn("Reward: 35 gold", lines)
        self.assertIn("Reward: 70 experience", lines)
        self.assertIn("Reward item: Warding Pendant", lines)
        self.assertIn("Reward recipe unlocked: Wild Mage Robe Pattern", lines)
        self.assertEqual(engine.player.gold, 70)
        self.assertEqual(engine.progress.inventory.get("warding_pendant"), 1)
        self.assertIn("wild_mage_robe_pattern", engine.progress.unlocked_recipes)

    def test_watch_token_signal_improves_hold_the_road_reward(self) -> None:
        engine = self._engine()
        engine.progress.active_quests.append("hold_the_road")
        engine.progress.defeated_enemies.append("bandit_scout")
        engine.progress.current_room = "guard_post"
        engine.progress.story_flags.append("watch_signal_lit")

        lines = engine._check_quest_completion()

        self.assertIn("Quest complete: Hold the Road", lines)
        self.assertIn(
            "Sera reads the lit road map, smiles once, and names you the reason the north road stayed open.",
            lines,
        )
        self.assertIn("Reward: 7 emerald marks", lines)
        self.assertIn("Reward: 70 experience", lines)
        self.assertIn("Reward item: Hunter Band", lines)
        self.assertEqual(engine.player.gold, 35)
        self.assertEqual(engine.player.wallet["emerald_mark"], 7)
        self.assertEqual(engine.progress.inventory.get("hunter_band"), 1)

    def test_hold_the_road_uses_default_reward_without_signal(self) -> None:
        engine = self._engine()
        engine.progress.active_quests.append("hold_the_road")
        engine.progress.defeated_enemies.append("bandit_scout")
        engine.progress.current_room = "guard_post"

        lines = engine._check_quest_completion()

        self.assertIn("Quest complete: Hold the Road", lines)
        self.assertIn("Sera knots a green cord around your token and names you road-friend.", lines)
        self.assertIn("Reward: 5 emerald marks", lines)
        self.assertIn("Reward: 55 experience", lines)
        self.assertIn("Reward item: Hunter Band", lines)
        self.assertEqual(engine.player.gold, 35)
        self.assertEqual(engine.player.wallet["emerald_mark"], 5)
        self.assertEqual(engine.progress.inventory.get("hunter_band"), 1)

    def test_talking_to_fetch_quest_giver_turns_in_item(self) -> None:
        engine = self._engine()
        engine.progress.active_quests.append("recover_the_sigil")
        engine.progress.add_item("moon_sigil")
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("talk archivist lyra")

        self.assertIn(
            "Archivist Lyra: The sigil should be in the vault. Watch the old wards there; they were made to keep intruders out.",
            lines,
        )
        self.assertIn("Quest complete: Recover the Sigil", lines)
        self.assertNotIn("moon_sigil", engine.progress.inventory)

    def test_accepting_lyra_quest_grants_vault_key(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("accept archivist lyra")

        self.assertIn("Quest accepted: Recover the Sigil", lines)
        self.assertIn("Archivist Lyra gives you Vault Key.", lines)
        self.assertEqual(engine.progress.inventory.get("vault_key"), 1)

    def test_cannot_move_while_threat_is_active(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "forest_path"
        engine.progress.previous_room = "town_square"

        lines = engine.handle_command("go north")

        self.assertIn("You cannot move while threats are active in the room. Fight or use 'retreat'.", lines)
        self.assertEqual(engine.progress.current_room, "forest_path")

    def test_standard_enemy_can_respawn_when_reentering_room(self) -> None:
        engine = self._engine()
        engine.progress.room_enemies["forest_path"] = []

        with patch("ifw.engine.random.randint", return_value=1):
            lines = engine.handle_command("north")

        self.assertIn("As you return, danger stirs again: Forest Wolf.", lines)
        self.assertIn("Threats: Forest Wolf (16 HP)", lines)
        self.assertEqual(engine.progress.current_room, "forest_path")
        self.assertEqual(
            [state.enemy_id for state in engine.progress.room_enemies["forest_path"]],
            ["forest_wolf"],
        )

    def test_room_uses_environment_monster_pool_for_initial_enemy(self) -> None:
        with patch("ifw.engine.random.randint", return_value=1):
            engine = self._engine()

        self.assertEqual(
            [state.enemy_id for state in engine.progress.room_enemies["forest_path"]],
            ["forest_wolf"],
        )
        self.assertEqual(
            [state.enemy_id for state in engine.progress.room_enemies["ruins"]],
            ["bandit_scout"],
        )

    def test_weighted_monster_pool_can_select_forest_snake(self) -> None:
        with patch("ifw.engine.random.randint", return_value=5):
            engine = self._engine()

        self.assertEqual(
            [state.enemy_id for state in engine.progress.room_enemies["forest_path"]],
            ["forest_snake"],
        )

    def test_weighted_monster_pool_can_select_rare_forest_bear(self) -> None:
        with patch("ifw.engine.random.randint", return_value=7):
            engine = self._engine()

        self.assertEqual(
            [state.enemy_id for state in engine.progress.room_enemies["forest_path"]],
            ["forest_bear"],
        )

    def test_standard_enemy_stats_scale_with_player_level(self) -> None:
        self.player.level = 10
        engine = self._engine()
        wolf = self.world.enemies["forest_wolf"]
        state = engine._spawn_enemy_state("forest_wolf")

        self.assertEqual(engine._enemy_max_hp(wolf), 88)
        self.assertEqual(engine._enemy_attack_score(wolf), 24)
        self.assertEqual(engine._enemy_defense_score(wolf), 10)
        self.assertEqual(state.current_hp, 88)
        self.assertEqual(state.max_hp, 88)
        self.assertEqual(state.scaled_level, 10)

    def test_non_respawn_enemy_receives_boss_scaling_boost(self) -> None:
        self.player.level = 10
        engine = self._engine()
        sentinel = self.world.enemies["arcane_sentinel"]
        scout = self.world.enemies["bandit_scout"]

        self.assertFalse(sentinel.respawns)
        self.assertTrue(scout.respawns)
        self.assertEqual(engine._enemy_max_hp(sentinel), 240)
        self.assertEqual(engine._enemy_attack_score(sentinel), 62)
        self.assertEqual(engine._enemy_defense_score(sentinel), 22)
        self.assertGreater(engine._enemy_max_hp(sentinel), engine._enemy_max_hp(scout))

    def test_boss_enemy_resets_to_full_health_when_player_falls(self) -> None:
        self.player.level = 10
        engine = self._engine()
        sentinel = self.world.enemies["arcane_sentinel"]
        state = EnemyState("arcane_sentinel", current_hp=7)
        engine.progress.current_room = "vault"
        engine.progress.room_enemies["vault"] = [state]
        engine.player.hp = 1

        with patch("ifw.engine.random.randint", side_effect=[1, 2]):
            lines = engine._enemy_turn()

        self.assertIn("Arcane Sentinel regains full strength as you fall.", lines)
        self.assertEqual(state.current_hp, engine._enemy_max_hp(sentinel))
        self.assertEqual(state.max_hp, engine._enemy_max_hp(sentinel))
        self.assertEqual(state.scaled_level, self.player.level)
        self.assertEqual(engine.progress.current_room, self.world.start_room)

    def test_standard_enemy_does_not_reset_to_full_health_when_player_falls(self) -> None:
        engine = self._engine()
        state = self._place_forest_wolf(engine)
        state.current_hp = 4
        engine.player.hp = 1

        with patch("ifw.engine.random.randint", side_effect=[1, 2]):
            lines = engine._enemy_turn()

        self.assertNotIn("Forest Wolf regains full strength as you fall.", lines)
        self.assertEqual(state.current_hp, 4)
        self.assertEqual(engine.progress.current_room, self.world.start_room)

    def test_existing_enemy_state_scales_when_room_is_viewed(self) -> None:
        self.player.level = 10
        engine = self._engine()
        engine.progress.current_room = "forest_path"
        engine.progress.room_enemies["forest_path"] = [EnemyState("forest_wolf", 16)]

        lines = engine.describe_current_room()
        state = engine.progress.room_enemies["forest_path"][0]

        self.assertEqual(state.current_hp, 88)
        self.assertEqual(state.max_hp, 88)
        self.assertEqual(state.scaled_level, 10)
        self.assertIn("Threats: Forest Wolf (88 HP)", lines)

    def test_environment_pool_enemy_can_respawn_on_reentry(self) -> None:
        engine = self._engine()
        engine.progress.room_enemies["ruins"] = []

        with patch("ifw.engine.random.randint", side_effect=[1, 1]):
            respawned = engine._respawn_enemies_for_room("ruins")

        self.assertEqual(respawned, ["Bandit Scout"])
        self.assertEqual(
            [state.enemy_id for state in engine.progress.room_enemies["ruins"]],
            ["bandit_scout"],
        )

    def test_monster_pool_respawn_rerolls_weighted_selection(self) -> None:
        engine = self._engine()
        engine.progress.room_enemies["forest_path"] = []

        with patch("ifw.engine.random.randint", side_effect=[1, 7]):
            respawned = engine._respawn_enemies_for_room("forest_path")

        self.assertEqual(respawned, ["Forest Bear"])
        self.assertEqual(
            [state.enemy_id for state in engine.progress.room_enemies["forest_path"]],
            ["forest_bear"],
        )

    def test_faction_enemy_can_spawn_after_player_pledges_to_matching_faction(self) -> None:
        engine = self._engine()
        engine.progress.faction_id = "town_watch"
        engine.progress.room_enemies["forest_path"] = []

        with patch("ifw.engine.random.randint", side_effect=[4, 1]):
            lines = engine.handle_command("north")

        self.assertIn("As you return, danger stirs again: Bandit Scout.", lines)
        self.assertEqual(
            [state.enemy_id for state in engine.progress.room_enemies["forest_path"]],
            ["bandit_scout"],
        )

    def test_faction_enemy_does_not_spawn_without_matching_faction(self) -> None:
        engine = self._engine()
        engine.progress.room_enemies["forest_path"] = []

        with patch("ifw.engine.random.randint", side_effect=[4]):
            spawned = engine._respawn_enemies_for_room("forest_path")

        self.assertEqual(spawned, [])
        self.assertEqual(engine.progress.room_enemies["forest_path"], [])

    def test_standard_enemy_stays_gone_when_respawn_roll_fails(self) -> None:
        engine = self._engine()
        engine.progress.room_enemies["forest_path"] = []

        with patch("ifw.engine.random.randint", return_value=4):
            lines = engine.handle_command("north")

        self.assertEqual(engine.progress.current_room, "forest_path")
        self.assertEqual(engine.progress.room_enemies["forest_path"], [])
        self.assertTrue(all(not line.startswith("Threats:") for line in lines))

    def test_mining_room_can_respawn_resource_items(self) -> None:
        engine = self._engine()
        self.world.rooms["forest_path"].mining_drops = [MiningDrop("wolf_pelt", 1, 3)]
        engine.progress.room_items["forest_path"] = []

        with patch("ifw.engine.random.randint", side_effect=[1, 3]):
            spawned = engine._respawn_mining_items_for_room("forest_path")

        self.assertEqual(spawned, ["Wolf Pelt x3"])
        self.assertEqual(engine.progress.room_items["forest_path"], ["wolf_pelt"] * 3)

    def test_mining_room_stays_empty_when_respawn_roll_fails(self) -> None:
        engine = self._engine()
        self.world.rooms["forest_path"].mining_drops = [MiningDrop("wolf_pelt", 1, 3)]
        engine.progress.room_items["forest_path"] = []

        with patch("ifw.engine.random.randint", return_value=4):
            spawned = engine._respawn_mining_items_for_room("forest_path")

        self.assertEqual(spawned, [])
        self.assertEqual(engine.progress.room_items["forest_path"], [])

    def test_mining_room_does_not_stack_while_resource_items_remain(self) -> None:
        engine = self._engine()
        self.world.rooms["forest_path"].mining_drops = [MiningDrop("wolf_pelt", 1, 3)]
        engine.progress.room_items["forest_path"] = ["wolf_pelt"]

        with patch("ifw.engine.random.randint", return_value=1):
            spawned = engine._respawn_mining_items_for_room("forest_path")

        self.assertEqual(spawned, [])
        self.assertEqual(engine.progress.room_items["forest_path"], ["wolf_pelt"])

    def test_boss_enemy_does_not_respawn_on_reentry(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "ruins"
        engine.progress.room_enemies["ruins"] = []
        engine.progress.room_enemies["vault"] = []
        engine.progress.add_item("vault_key")

        with patch("ifw.engine.random.randint", return_value=1):
            lines = engine.handle_command("north")

        self.assertIn("You use Vault Key to enter Ancient Vault.", lines)
        self.assertEqual(engine.progress.current_room, "vault")
        self.assertEqual(engine.progress.room_enemies["vault"], [])
        self.assertTrue(all("Arcane Sentinel" not in line for line in lines if line.startswith("Threats:")))

    def test_in_command_enters_building_room(self) -> None:
        engine = self._engine()

        lines = engine.handle_command("in")

        self.assertIn("You travel in.", lines)
        self.assertEqual(engine.progress.current_room, "lantern_inn")

    def test_out_command_exits_building_room(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.progress.room_enemies["lantern_inn"] = []

        lines = engine.handle_command("out")

        self.assertIn("You travel out.", lines)
        self.assertEqual(engine.progress.current_room, "town_square")

    def test_hidden_exit_stays_hidden_until_environment_flag_is_set(self) -> None:
        engine = self._engine()

        look_lines = engine.handle_command("look")
        blocked_lines = engine.handle_command("west")

        self.assertTrue(all("west -> Mage Tower" not in line for line in look_lines))
        self.assertIn("You cannot go that way.", blocked_lines)

        interact_lines = engine.handle_command("interact weathered mural")
        revealed_lines = engine.handle_command("look")
        move_lines = engine.handle_command("west")

        self.assertIn(
            "You press the moon sigil in the mural. Stone grinds beneath the square, and a hidden stair opens to the west.",
            interact_lines,
        )
        self.assertIn("A path is revealed: west -> Mage Tower.", interact_lines)
        self.assertIn("town_mural_opened", engine.progress.story_flags)
        self.assertIn(
            "Exits: in -> Lantern Inn, up -> Guard Post, north -> Forest Path, east -> Market Street, south -> Title Street, west -> Mage Tower",
            revealed_lines,
        )
        self.assertIn("You travel west.", move_lines)
        self.assertEqual(engine.progress.current_room, "mage_tower")

    def test_examine_room_and_environment_object(self) -> None:
        engine = self._engine()

        room_lines = engine.handle_command("examine room")
        object_lines = engine.handle_command("examine weathered mural")

        self.assertIn("Notable objects: Weathered Mural.", room_lines)
        self.assertIn("Weathered Mural", object_lines)
        self.assertIn(
            "A weathered mural shows moonlit scholars walking through a door that is not painted on the wall.",
            object_lines,
        )

    def test_use_can_interact_with_environment_object(self) -> None:
        engine = self._engine()

        lines = engine.handle_command("use weathered mural")

        self.assertIn("town_mural_opened", engine.progress.story_flags)
        self.assertIn("A path is revealed: west -> Mage Tower.", lines)

    def test_environment_interaction_cannot_happen_with_active_threats(self) -> None:
        engine = self._engine()
        engine.progress.room_enemies["town_square"] = [EnemyState("bandit_scout", 12)]

        lines = engine.handle_command("interact weathered mural")

        self.assertIn("You cannot interact with the environment while threats are active in the room.", lines)
        self.assertNotIn("town_mural_opened", engine.progress.story_flags)

    def test_environment_interaction_requires_inventory_item(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"

        lines = engine.handle_command("interact hearth ward")

        self.assertIn(
            "The ward bowl is dry. It needs a Healing Tonic before its runes will wake.",
            lines,
        )
        self.assertNotIn("hearth_ward_kindled", engine.progress.story_flags)

    def test_environment_interaction_consumes_required_item_on_success(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.progress.add_item("healing_tonic")

        lines = engine.handle_command("interact hearth ward")

        self.assertIn(
            "You pour a Healing Tonic into the ward bowl. Amber runes flare softly around the inn.",
            lines,
        )
        self.assertIn("You use Healing Tonic.", lines)
        self.assertIn("hearth_ward_kindled", engine.progress.story_flags)
        self.assertNotIn("healing_tonic", engine.progress.inventory)

    def test_utility_item_can_be_used_on_room_event_without_consuming_it(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "smithy"
        engine.progress.add_item("iron_pry_bar")

        lines = engine.handle_command("use iron pry bar on jammed grate")

        self.assertTrue(any("You lever the grate open" in line for line in lines))
        self.assertIn("You use Iron Pry Bar.", lines)
        self.assertIn("smithy_grate_opened", engine.progress.story_flags)
        self.assertEqual(engine.progress.inventory.get("iron_pry_bar"), 1)

    def test_archive_cipher_decodes_crystal_grotto_ore_for_quest_outcome(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "crystal_grotto"
        engine.progress.add_item("archive_cipher")

        lines = engine.handle_command("use archive cipher on whispering vein")

        self.assertIn(
            "You hold the Archive Cipher against the vein. Moon-script aligns with the ore's flicker, and the whispers settle into a usable pattern.",
            lines,
        )
        self.assertIn("You use Archive Cipher.", lines)
        self.assertIn("Archive Cipher has 2/3 charges left.", lines)
        self.assertIn("ore_cipher_decoded", engine.progress.story_flags)
        self.assertEqual(engine.progress.inventory.get("archive_cipher"), 1)
        self.assertEqual(engine.progress.item_charges["archive_cipher"], 2)

    def test_password_interaction_reveals_arcane_thief_cache(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "crystal_grotto"
        engine.progress.story_flags.extend(
            [
                "cipher_letter_s_found",
                "cipher_letter_n_found",
                "cipher_letter_a_found",
                "cipher_letter_k_found",
                "cipher_letter_e_found",
            ]
        )

        interact_lines = engine.handle_command("interact serpent cipher door")
        wrong_lines = engine.handle_command("answer serpent cipher door with ember")
        self.assertNotIn("arcane_thief_cache_opened", engine.progress.story_flags)
        right_lines = engine.handle_command("answer serpent cipher door with snake")
        move_lines = engine.handle_command("in")

        self.assertIn(
            "Serpent Cipher Door asks for a password. Use 'answer <password>' or 'answer <object> with <password>'.",
            interact_lines,
        )
        self.assertIn(
            "The crystal scales click once, unimpressed, and settle back into blank silence.",
            wrong_lines,
        )
        self.assertIn(
            "You speak SNAKE. The five scales turn one by one, and a green-lit passage curls open into the stone.",
            right_lines,
        )
        self.assertIn("A path is revealed: in -> Arcane Thief's Cache.", right_lines)
        self.assertIn("arcane_thief_cache_opened", engine.progress.story_flags)
        self.assertEqual(engine.progress.current_room, "arcane_thief_cache")
        self.assertIn("Arcane Thief's Cache", move_lines)

    def test_archive_cipher_scavenger_hunt_requires_recharge_to_finish_password(self) -> None:
        engine = self._engine()
        engine.progress.add_item("archive_cipher")

        clue_steps = [
            ("elder_memory_cache", "elder cipher scale", "cipher_letter_s_found", "first recovered letter is S"),
            ("hearth_supply_cache", "hearth cipher scale", "cipher_letter_n_found", "second recovered letter is N"),
            ("smithy_cellar_cache", "smithy cipher scale", "cipher_letter_a_found", "third recovered letter is A"),
        ]
        for room_id, object_name, flag, text in clue_steps:
            engine.progress.current_room = room_id
            lines = engine.handle_command(f"use archive cipher on {object_name}")
            self.assertTrue(any(text in line for line in lines))
            self.assertIn(flag, engine.progress.story_flags)

        self.assertEqual(engine.progress.item_charges["archive_cipher"], 0)
        engine.progress.current_room = "archive_supply_room"
        blocked_lines = engine.handle_command("use archive cipher on archive supply cipher scale")
        self.assertEqual(blocked_lines, ["Archive Cipher has no charge left."])
        self.assertNotIn("cipher_letter_k_found", engine.progress.story_flags)

        engine.progress.add_item("mana_crystal")
        recharge_lines = engine.handle_command("use mana crystal on archive cipher")
        self.assertEqual(
            recharge_lines,
            [
                "You use Mana Crystal on Archive Cipher.",
                "Archive Cipher is fully recharged.",
            ],
        )

        final_steps = [
            ("archive_supply_room", "archive supply cipher scale", "cipher_letter_k_found", "fourth recovered letter is K"),
            ("thorn_seed_cache", "thorn cipher scale", "cipher_letter_e_found", "fifth recovered letter is E"),
        ]
        for room_id, object_name, flag, text in final_steps:
            engine.progress.current_room = room_id
            lines = engine.handle_command(f"use archive cipher on {object_name}")
            self.assertTrue(any(text in line for line in lines))
            self.assertIn(flag, engine.progress.story_flags)

        engine.progress.current_room = "crystal_grotto"
        password_lines = engine.handle_command("password snake")
        self.assertIn("arcane_thief_cache_opened", engine.progress.story_flags)
        self.assertIn("A path is revealed: in -> Arcane Thief's Cache.", password_lines)
        self.assertEqual(engine.progress.item_charges["archive_cipher"], 1)

    def test_depleted_charged_utility_item_cannot_be_used(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "crystal_grotto"
        engine.progress.add_item("archive_cipher")
        engine.progress.item_charges["archive_cipher"] = 0

        lines = engine.handle_command("use archive cipher on whispering vein")

        self.assertEqual(lines, ["Archive Cipher has no charge left."])
        self.assertNotIn("ore_cipher_decoded", engine.progress.story_flags)

    def test_recharge_consumable_restores_charged_item_uses(self) -> None:
        engine = self._engine()
        engine.progress.add_item("archive_cipher")
        engine.progress.add_item("mana_crystal")
        engine.progress.item_charges["archive_cipher"] = 0

        lines = engine.handle_command("use mana crystal on archive cipher")

        self.assertEqual(
            lines,
            [
                "You use Mana Crystal on Archive Cipher.",
                "Archive Cipher is fully recharged.",
            ],
        )
        self.assertEqual(engine.progress.item_charges["archive_cipher"], 3)
        self.assertNotIn("mana_crystal", engine.progress.inventory)

    def test_recharge_consumable_must_target_charged_item(self) -> None:
        engine = self._engine()
        engine.progress.add_item("mana_crystal")
        engine.progress.add_item("healing_tonic")

        lines = engine.handle_command("use mana crystal on healing tonic")

        self.assertEqual(lines, ["Healing Tonic does not hold magical charges."])
        self.assertEqual(engine.progress.inventory.get("mana_crystal"), 1)

    def test_misc_item_can_be_used_as_one_off_story_event_item(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "elder_house"
        engine.progress.add_item("faded_keepsake")

        lines = engine.handle_command("use faded keepsake on memory shelf")

        self.assertIn(
            "You place the Faded Keepsake on the shelf. The room seems to exhale, and the old house feels less alone.",
            lines,
        )
        self.assertIn("You use Faded Keepsake.", lines)
        self.assertIn("elder_memory_honored", engine.progress.story_flags)
        self.assertNotIn("faded_keepsake", engine.progress.inventory)

    def test_watch_token_lights_guard_post_signal_for_quest_outcome(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "guard_post"
        engine.progress.add_item("watch_token")

        lines = engine.handle_command("use watch token on signal lantern")

        self.assertIn(
            "You press the Watch Token to the lantern's crest. Green light spills over the north road map, marking bandit trails in sharp lines.",
            lines,
        )
        self.assertIn("You use Watch Token.", lines)
        self.assertIn("watch_signal_lit", engine.progress.story_flags)
        self.assertEqual(engine.progress.inventory.get("watch_token"), 1)

    def test_room_event_rejects_wrong_utility_item(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.progress.add_item("iron_pry_bar")

        lines = engine.handle_command("use iron pry bar on hearth ward")

        self.assertEqual(lines, ["Iron Pry Bar does not seem useful for Hearth Ward."])
        self.assertNotIn("hearth_ward_kindled", engine.progress.story_flags)

    def test_targeted_required_consumable_can_still_be_used_on_room_event(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.progress.add_item("healing_tonic")

        lines = engine.handle_command("use healing tonic on hearth ward")

        self.assertIn("You use Healing Tonic.", lines)
        self.assertIn("hearth_ward_kindled", engine.progress.story_flags)
        self.assertNotIn("healing_tonic", engine.progress.inventory)

    def test_completed_environment_interaction_does_not_require_item_again(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.progress.story_flags.append("hearth_ward_kindled")

        lines = engine.handle_command("interact hearth ward")

        self.assertIn("The hearth ward already glows with tonic-warmed light.", lines)

    def test_examine_environment_object_shows_required_item(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"

        lines = engine.handle_command("examine hearth ward")

        self.assertIn("Requires item: Healing Tonic (consumed)", lines)

    def test_rest_restores_hp_and_mp_in_rest_room(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.player.hp = 15
        engine.player.mp = 3

        lines = engine.handle_command("rest")

        self.assertIn("You pay 10 gold and rest. HP +27, MP +9.", lines)
        self.assertEqual(engine.player.hp, engine.player.max_hp)
        self.assertEqual(engine.player.mp, engine.player.max_mp)
        self.assertEqual(engine.player.gold, 25)

    def test_rest_fails_outside_rest_room(self) -> None:
        engine = self._engine()

        lines = engine.handle_command("rest")

        self.assertIn("You cannot rest here.", lines)

    def test_rest_fails_when_already_at_full_health_and_magic(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"

        lines = engine.handle_command("rest")

        self.assertIn("You are already at full health and magic.", lines)
        self.assertEqual(engine.player.gold, 35)

    def test_rest_fails_without_enough_gold(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.player.gold = 5
        engine.player.hp = 10
        engine.player.mp = 1

        lines = engine.handle_command("rest")

        self.assertIn("You need 10 gold to rest here.", lines)
        self.assertEqual(engine.player.gold, 5)
        self.assertEqual(engine.player.hp, 10)
        self.assertEqual(engine.player.mp, 1)

    def test_locked_room_blocks_entry_without_required_item(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "ruins"
        engine.progress.room_enemies["ruins"] = []

        lines = engine.handle_command("go north")

        self.assertIn("The vault door is locked tight. You need the Vault Key to enter.", lines)
        self.assertEqual(engine.progress.current_room, "ruins")

    def test_locked_room_allows_entry_with_required_item(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "ruins"
        engine.progress.room_enemies["ruins"] = []
        engine.progress.add_item("vault_key")

        lines = engine.handle_command("go north")

        self.assertIn("You use Vault Key to enter Ancient Vault.", lines)
        self.assertEqual(engine.progress.current_room, "vault")

    def test_room_can_lock_after_you_leave_and_block_backtracking(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "relic_gate"
        engine.progress.story_flags.append("final_gate_opened")

        enter_approach = engine.handle_command("go east")
        self.assertIn("You travel east.", enter_approach)
        self.assertEqual(engine.progress.current_room, "starless_approach")
        self.assertEqual(engine.progress.previous_room, "relic_gate")
        self.assertEqual(engine.progress.sealed_rooms, [])

        leave_approach = engine.handle_command("go east")
        self.assertIn("With a final echo, Starless Approach seals behind you.", leave_approach)
        self.assertEqual(engine.progress.current_room, "citadel_forward_camp")
        self.assertEqual(engine.progress.previous_room, "starless_approach")
        self.assertEqual(engine.progress.sealed_rooms, ["starless_approach"])

        blocked_return = engine.handle_command("go west")
        self.assertIn(
            "The Concord Gate seals behind you. The citadel will not let the story retreat unchanged.",
            blocked_return,
        )
        self.assertEqual(engine.progress.current_room, "citadel_forward_camp")

    def test_backtracking_from_story_room_does_not_soft_lock_progress(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "relic_gate"
        engine.progress.story_flags.append("final_gate_opened")

        enter_approach = engine.handle_command("go east")
        self.assertIn("You travel east.", enter_approach)
        self.assertEqual(engine.progress.current_room, "starless_approach")
        self.assertEqual(engine.progress.previous_room, "relic_gate")
        self.assertEqual(engine.progress.sealed_rooms, [])

        step_back = engine.handle_command("go west")
        self.assertIn("You travel west.", step_back)
        self.assertEqual(engine.progress.current_room, "relic_gate")
        self.assertEqual(engine.progress.previous_room, "starless_approach")
        self.assertEqual(engine.progress.sealed_rooms, [])

        reenter_approach = engine.handle_command("go east")
        self.assertIn("You travel east.", reenter_approach)
        self.assertEqual(engine.progress.current_room, "starless_approach")
        self.assertEqual(engine.progress.previous_room, "relic_gate")
        self.assertEqual(engine.progress.sealed_rooms, [])

        move_forward = engine.handle_command("go east")
        self.assertIn("With a final echo, Starless Approach seals behind you.", move_forward)
        self.assertEqual(engine.progress.current_room, "citadel_forward_camp")
        self.assertEqual(engine.progress.previous_room, "starless_approach")
        self.assertEqual(engine.progress.sealed_rooms, ["starless_approach"])

    def test_retreat_cannot_bypass_a_sealed_story_room(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "citadel_forward_camp"
        engine.progress.previous_room = "starless_approach"
        engine.progress.sealed_rooms.append("starless_approach")
        engine.progress.room_enemies["citadel_forward_camp"] = [
            EnemyState(enemy_id="bandit_scout", current_hp=12)
        ]

        lines = engine.handle_command("retreat")

        self.assertIn(
            "The Concord Gate seals behind you. The citadel will not let the story retreat unchanged.",
            lines,
        )
        self.assertEqual(engine.progress.current_room, "citadel_forward_camp")

    def test_cannot_take_item_while_threat_is_active(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "forest_path"
        engine.progress.previous_room = "town_square"

        lines = engine.handle_command("take mana tonic")

        self.assertIn("You cannot grab items while threats are active in the room.", lines)
        self.assertEqual(engine.progress.inventory.get("mana_tonic", 0), 0)

    def test_take_all_collects_every_item_in_room(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        lines = engine.handle_command("take all")

        self.assertIn("You take everything: Healing Tonic, Warding Pendant.", lines)
        self.assertEqual(engine.progress.inventory.get("healing_tonic"), 1)
        self.assertEqual(engine.progress.inventory.get("warding_pendant"), 1)
        self.assertEqual(engine.progress.room_items["mage_tower"], [])

    def test_accessory_equips_and_changes_player_stats(self) -> None:
        engine = self._engine()
        engine.progress.add_item("silver_ring")
        engine.progress.add_item("warding_pendant")

        equip_ring = engine.handle_command("equip silver ring")
        equip_pendant = engine.handle_command("equip warding pendant")

        self.assertIn("You equip Silver Ring as an accessory (1/3).", equip_ring)
        self.assertIn("You equip Warding Pendant as an accessory (2/3).", equip_pendant)
        self.assertEqual(engine.progress.accessory_ids, ["silver_ring", "warding_pendant"])
        self.assertEqual(engine._player_attack_score(), 12)
        self.assertEqual(engine._player_defense_score(), 8)

    def test_cannot_equip_more_than_three_accessories(self) -> None:
        self.player.level = 2
        engine = self._engine()
        for item_id in ["silver_ring", "warding_pendant", "hunter_band"]:
            engine.progress.add_item(item_id)
            engine.handle_command(f"equip {engine.world.items[item_id].name}")
        engine.progress.add_item("silver_ring")

        lines = engine.handle_command("equip silver ring")

        self.assertIn("You can equip at most 3 accessories.", lines)
        self.assertEqual(len(engine.progress.accessory_ids), 3)

    def test_enchanted_items_raise_effective_hp_and_mp_caps(self) -> None:
        self.player.level = 2
        engine = self._engine()
        engine.progress.add_item("chainmail")
        engine.progress.add_item("warding_pendant")

        engine.handle_command("equip chainmail")
        engine.handle_command("equip warding pendant")
        lines = engine.handle_command("stats")

        self.assertEqual(engine._player_max_hp(), 48)
        self.assertEqual(engine._player_max_mp(), 16)
        self.assertEqual(engine.player.hp, 48)
        self.assertEqual(engine.player.mp, 16)
        self.assertIn("HP 48/48  MP 16/16  Gold 35", lines)

    def test_unequipping_enchanted_items_clamps_bonus_resources(self) -> None:
        self.player.level = 2
        engine = self._engine()
        engine.progress.add_item("chainmail")
        engine.progress.add_item("warding_pendant")

        engine.handle_command("equip chainmail")
        engine.handle_command("equip warding pendant")
        engine.handle_command("unequip armor")
        engine.handle_command("unequip warding pendant")

        self.assertEqual(engine._player_max_hp(), 42)
        self.assertEqual(engine._player_max_mp(), 12)
        self.assertEqual(engine.player.hp, 42)
        self.assertEqual(engine.player.mp, 12)

    def test_charged_armor_loses_charges_on_hits_and_uses_depleted_stats(self) -> None:
        engine = self._engine()
        engine.progress.add_item("wild_mage_robe")
        engine.handle_command("equip wild mage robe")
        self.assertEqual(engine._player_defense_score(), 6)
        self.assertEqual(engine._player_max_mp(), 18)

        self._place_forest_wolf(engine)
        with patch("ifw.engine.random.randint", side_effect=[1, 0, 1, 0, 1, 0]):
            first_hit = engine._enemy_turn()
            second_hit = engine._enemy_turn()
            third_hit = engine._enemy_turn()

        self.assertIn("Wild Mage Robe has 2/3 charges left.", first_hit)
        self.assertIn("Wild Mage Robe has 1/3 charges left.", second_hit)
        self.assertIn("Wild Mage Robe's magic fades; it needs recharging.", third_hit)
        self.assertEqual(engine.progress.item_charges["wild_mage_robe"], 0)
        self.assertEqual(engine._player_defense_score(), 5)
        self.assertEqual(engine._player_max_mp(), 14)
        self.assertEqual(engine.player.mp, 14)

    def test_mana_crystal_restores_depleted_armor_stats(self) -> None:
        engine = self._engine()
        engine.progress.add_item("wild_mage_robe")
        engine.progress.add_item("mana_crystal")
        engine.handle_command("equip wild mage robe")
        engine.progress.item_charges["wild_mage_robe"] = 0
        engine._sync_resources_to_effective_max()

        lines = engine.handle_command("use mana crystal on wild mage robe")

        self.assertIn("Wild Mage Robe is fully recharged.", lines)
        self.assertEqual(engine.progress.item_charges["wild_mage_robe"], 3)
        self.assertEqual(engine._player_defense_score(), 6)
        self.assertEqual(engine._player_max_mp(), 18)

    def test_examine_item_shows_description_and_effects(self) -> None:
        engine = self._engine()
        engine.progress.add_item("healing_tonic")

        lines = engine.handle_command("examine healing tonic")

        self.assertIn("Healing Tonic", lines)
        self.assertIn("Type: Consumable", lines)
        self.assertIn("Restores HP: 18", lines)

    def test_examine_weapon_compares_to_equipped_weapon(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "smithy"

        better_lines = engine.handle_command("examine watch halberd")
        engine.progress.add_item("iron_dagger")
        worse_lines = engine.handle_command("examine iron dagger")

        self.assertIn("Comparison to equipped Rusty Sword:", better_lines)
        self.assertIn("  Attack: +7 vs +3 (+4)", better_lines)
        self.assertIn("Overall comparison: Better.", better_lines)
        self.assertIn("  Attack: +2 vs +3 (-1)", worse_lines)
        self.assertIn("Overall comparison: Worse.", worse_lines)

    def test_examine_armor_compares_to_equipped_armor(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "smithy"

        lines = engine.handle_command("examine chainmail")

        self.assertIn("Comparison to equipped Padded Armor:", lines)
        self.assertIn("  Defense: +4 vs +2 (+2)", lines)
        self.assertIn("  HP: +6 vs +0 (+6)", lines)
        self.assertIn("Overall comparison: Better.", lines)

    def test_examine_item_shows_hp_and_mp_enchantments(self) -> None:
        engine = self._engine()
        engine.progress.add_item("guardian_band")

        lines = engine.handle_command("examine guardian band")

        self.assertIn("HP bonus: +3", lines)
        self.assertIn("MP bonus: +3", lines)
        self.assertIn("Requires level: 3", lines)

    def test_examine_item_shows_temporary_potion_effects(self) -> None:
        engine = self._engine()
        engine.progress.add_item("fury_draught")

        lines = engine.handle_command("examine fury draught")

        self.assertIn("Fury Draught", lines)
        self.assertIn("Temporary attack bonus: +3", lines)
        self.assertIn("Duration: 2 turns", lines)

    def test_examine_and_spell_list_show_poison_cures(self) -> None:
        engine = self._engine()
        engine.progress.add_item("antidote")
        engine.progress.learned_spells.append("purify_blood")

        item_lines = engine.handle_command("examine antidote")
        spell_lines = engine.handle_command("spells")

        self.assertIn("Use: cures poison", item_lines)
        self.assertTrue(any("Purify Blood [cure] (cures poison)" in line for line in spell_lines))

    def test_examine_item_shows_charges_and_recharge_effects(self) -> None:
        engine = self._engine()
        engine.progress.add_item("wild_mage_robe")
        engine.progress.add_item("mana_crystal")
        engine.progress.item_charges["wild_mage_robe"] = 1

        robe_lines = engine.handle_command("examine wild mage robe")
        crystal_lines = engine.handle_command("examine mana crystal")

        self.assertIn("Charges: 1/3", robe_lines)
        self.assertIn("When depleted: defense +1, MP +2", robe_lines)
        self.assertIn("Use: recharges a charged magical item", crystal_lines)

    def test_examine_utility_item_shows_room_event_use(self) -> None:
        engine = self._engine()
        engine.progress.add_item("iron_pry_bar")

        lines = engine.handle_command("examine iron pry bar")

        self.assertIn("Iron Pry Bar", lines)
        self.assertIn("Type: Utility", lines)
        self.assertIn("Use: room events and environmental interactions", lines)

    def test_examine_misc_item_shows_story_event_use(self) -> None:
        engine = self._engine()
        engine.progress.add_item("faded_keepsake")

        lines = engine.handle_command("examine faded keepsake")

        self.assertIn("Faded Keepsake", lines)
        self.assertIn("Type: Misc", lines)
        self.assertIn("Use: story events and one-off room interactions", lines)

    def test_attack_potion_boosts_attack_until_player_attacks(self) -> None:
        engine = self._engine()
        engine.progress.add_item("fury_draught")
        base_attack = engine._player_attack_score()

        use_lines = engine.handle_command("use fury draught")
        stats_after_use = engine.handle_command("stats")
        self._place_forest_wolf(engine)
        with patch("ifw.engine.random.randint", side_effect=[1, 0, 100]):
            attack_lines = engine.handle_command("attack forest wolf")
        stats_after_attack = engine.handle_command("stats")

        self.assertIn("You use Fury Draught. Attack +3 for 2 attacks", use_lines)
        self.assertNotIn("fury_draught", engine.progress.inventory)
        self.assertEqual(engine._player_attack_score(), base_attack + 3)
        self.assertIn("Active magic: Fury Draught (2 turns)", stats_after_use)
        self.assertIn("Forest Wolf has 3 HP left.", attack_lines)
        self.assertIn("Active magic: Fury Draught (1 turns)", stats_after_attack)

    def test_defense_potion_boosts_defense_until_enemy_turns(self) -> None:
        engine = self._engine()
        engine.progress.add_item("guard_tonic")
        base_defense = engine._player_defense_score()

        use_lines = engine.handle_command("use guard tonic")
        self._place_forest_wolf(engine)
        with patch("ifw.engine.random.randint", return_value=100):
            enemy_lines = engine._enemy_turn()
        stats_after_enemy_turn = engine.handle_command("stats")

        self.assertIn("You use Guard Tonic. Defense +3 for 2 enemy turns", use_lines)
        self.assertNotIn("guard_tonic", engine.progress.inventory)
        self.assertEqual(engine._player_defense_score(), base_defense + 3)
        self.assertIn("  Forest Wolf misses you.", enemy_lines)
        self.assertIn("Active magic: Guard Tonic (1 turns)", stats_after_enemy_turn)

    def test_defeating_enemy_shows_narrative_completion_text(self) -> None:
        engine = self._engine()
        state = self._place_forest_wolf(engine)

        with patch("ifw.engine.random.random", return_value=0.0):
            lines = engine._defeat_enemy(state)

        self.assertIn("Forest Wolf falls in battle.", lines)
        self.assertIn(
            "The wolf gives one last ragged snarl before the forest path falls quiet again and the trees stop shivering around you.",
            lines,
        )

    def test_player_attack_can_miss_and_enemy_can_miss_back(self) -> None:
        engine = self._engine()
        state = self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", side_effect=[100, 100, 100]):
            lines = engine.handle_command("attack forest wolf")

        self.assertIn("Your attack misses Forest Wolf.", lines)
        self.assertIn("  Forest Wolf misses you.", lines)
        self.assertEqual(state.current_hp, 16)
        self.assertEqual(engine.player.hp, 42)

    def test_offense_magic_can_miss_but_still_costs_mp(self) -> None:
        engine = self._engine()
        state = self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", side_effect=[100, 100, 100]):
            lines = engine.handle_command("cast ember bolt on forest wolf")

        self.assertIn("Ember Bolt misses Forest Wolf.", lines)
        self.assertEqual(state.current_hp, 16)
        self.assertEqual(engine.player.mp, 7)

    def test_enemy_attack_can_miss(self) -> None:
        engine = self._engine()
        self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", return_value=100):
            lines = engine._enemy_turn()

        self.assertIn("  Forest Wolf misses you.", lines)
        self.assertEqual(engine.player.hp, 42)

    def test_rest_uses_enchanted_hp_and_mp_caps(self) -> None:
        self.player.level = 2
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.progress.add_item("chainmail")
        engine.progress.add_item("warding_pendant")
        engine.handle_command("equip chainmail")
        engine.handle_command("equip warding pendant")
        engine.player.hp = 20
        engine.player.mp = 5

        lines = engine.handle_command("rest")

        self.assertIn("You pay 10 gold and rest. HP +28, MP +11.", lines)
        self.assertEqual(engine.player.hp, 48)
        self.assertEqual(engine.player.mp, 16)
        self.assertEqual(engine.player.gold, 25)

    def test_retreat_moves_player_back_to_previous_room(self) -> None:
        engine = self._engine()

        engine.handle_command("go north")
        lines = engine.handle_command("retreat")

        self.assertIn("You retreat to Town Square.", lines)
        self.assertEqual(engine.progress.current_room, "town_square")
        self.assertEqual(engine.progress.previous_room, "forest_path")

    def test_quest_giver_uses_active_dialogue_after_accepting_quest(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "elder_house"

        engine.handle_command("accept elder rowan")
        lines = engine.handle_command("talk elder rowan")

        self.assertIn(
            "Elder Rowan: Keep your footing on the forest path. That wolf knows the road better than any of us.",
            lines,
        )
        self.assertIn("You are already working on: Cull the Wolf.", lines)

    def test_quest_giver_uses_completed_dialogue_after_finishing_quest(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "elder_house"
        engine.progress.completed_quests.append("cull_the_wolf")

        lines = engine.handle_command("talk elder rowan")

        self.assertIn(
            "Elder Rowan: You have my thanks. The road north sounds like a road again, not a hunting ground.",
            lines,
        )

    def test_npc_quest_chain_requires_previous_quest_completion(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "elder_house"
        elder = engine.world.npcs["elder_rowan"]
        elder.quest_ids = ["cull_the_wolf", "recover_the_sigil"]
        elder.quest_id = "cull_the_wolf"
        engine.world.quests["recover_the_sigil"].giver_id = "elder_rowan"

        initial_talk = engine.handle_command("talk elder rowan")
        locked_accept = engine.handle_command("accept recover the sigil")
        first_accept = engine.handle_command("accept elder rowan")
        engine.progress.defeated_enemies.append("forest_wolf")
        first_complete = engine._check_quest_completion()
        next_talk = engine.handle_command("talk elder rowan")
        second_accept = engine.handle_command("accept elder rowan")

        self.assertIn(
            "Elder Rowan: The road north is no place for travelers until that wolf is dealt with.",
            initial_talk,
        )
        self.assertIn("Quest available: Cull the Wolf. Use 'accept Elder Rowan'.", initial_talk)
        self.assertIn(
            "Complete Cull the Wolf before Recover the Sigil is available.",
            locked_accept,
        )
        self.assertIn("Quest accepted: Cull the Wolf", first_accept)
        self.assertIn("Quest complete: Cull the Wolf", first_complete)
        self.assertIn(
            "Elder Rowan: The sanctum key is somewhere beyond the ruins. Bring me the sigil if you find it.",
            next_talk,
        )
        self.assertIn(
            "Quest available: Recover the Sigil. Use 'accept Elder Rowan'.",
            next_talk,
        )
        self.assertIn("Quest accepted: Recover the Sigil", second_accept)
        self.assertIn("Elder Rowan gives you Vault Key.", second_accept)
        self.assertIn("recover_the_sigil", engine.progress.active_quests)

    def test_multi_quest_npc_mentions_more_quests_before_chain_end(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "ember_lift"

        first_talk = engine.handle_command("talk foreman borin")
        engine.progress.completed_quests.append("repair_ember_pumps")
        middle_talk = engine.handle_command("talk foreman borin")
        engine.progress.completed_quests.append("mine_ember_ore")
        final_talk = engine.handle_command("talk foreman borin")

        self.assertIn(
            "This NPC has more quests available after you complete Repair the Ember Pumps.",
            first_talk,
        )
        self.assertIn(
            "This NPC has more quests available after you complete Mine Ember Ore.",
            middle_talk,
        )
        self.assertNotIn(
            "This NPC has more quests available after you complete Break the Ash Hound.",
            final_talk,
        )

    def test_multi_quest_npc_mentions_next_quest_after_turn_in(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "ember_lift"
        engine.progress.active_quests.append("repair_ember_pumps")
        engine.progress.add_item("ember_pump_gear")

        lines = engine.handle_command("talk foreman borin")

        self.assertIn("Quest complete: Repair the Ember Pumps", lines)
        self.assertIn(
            "This NPC has more quests available: Mine Ember Ore is now available.",
            lines,
        )

    def test_faction_quest_warns_before_acceptance(self) -> None:
        self.world.npcs["elder_rowan"].faction_id = "town_watch"
        engine = self._engine()
        engine.progress.current_room = "elder_house"

        talk_lines = engine.handle_command("talk elder rowan")
        accept_lines = engine.handle_command("accept elder rowan")

        self.assertIn(
            "Faction warning: Accepting Cull the Wolf will pledge you to Town Watch and block quests from other factions.",
            talk_lines,
        )
        self.assertIn(
            "Faction warning: Accepting Cull the Wolf will pledge you to Town Watch and block quests from other factions.",
            accept_lines,
        )
        self.assertIn("Use 'accept elder rowan confirm' to make this commitment.", accept_lines)
        self.assertNotIn("cull_the_wolf", engine.progress.active_quests)
        self.assertIsNone(engine.progress.faction_id)

    def test_confirmed_faction_quest_locks_player_to_faction(self) -> None:
        self.world.npcs["elder_rowan"].faction_id = "town_watch"
        engine = self._engine()
        engine.progress.current_room = "elder_house"

        lines = engine.handle_command("accept elder rowan confirm")

        self.assertIn("Quest accepted: Cull the Wolf", lines)
        self.assertIn("Faction pledged: Town Watch.", lines)
        self.assertEqual(engine.progress.faction_id, "town_watch")
        self.assertIn("cull_the_wolf", engine.progress.active_quests)
        self.assertIn("Faction: Town Watch", engine.handle_command("stats"))
        self.assertIn("Faction pledge: Town Watch", engine.handle_command("quests"))

    def test_faction_lock_blocks_other_faction_quests(self) -> None:
        self.world.npcs["elder_rowan"].faction_id = "town_watch"
        self.world.npcs["archivist_lyra"].faction_id = "moon_archive"
        engine = self._engine()
        engine.progress.current_room = "elder_house"
        engine.handle_command("accept elder rowan confirm")
        engine.progress.current_room = "mage_tower"
        engine.progress.room_enemies["mage_tower"] = []

        talk_lines = engine.handle_command("talk archivist lyra")
        accept_lines = engine.handle_command("accept archivist lyra confirm")

        self.assertIn(
            "You are pledged to Town Watch and cannot accept quests for Moon Archive.",
            talk_lines,
        )
        self.assertIn(
            "You are pledged to Town Watch and cannot accept quests for Moon Archive.",
            accept_lines,
        )
        self.assertNotIn("recover_the_sigil", engine.progress.active_quests)

    def test_active_faction_quest_completion_locks_legacy_save(self) -> None:
        self.world.npcs["elder_rowan"].faction_id = "town_watch"
        engine = self._engine()
        engine.progress.active_quests.append("cull_the_wolf")
        engine.progress.defeated_enemies.append("forest_wolf")

        lines = engine._check_quest_completion()

        self.assertIn("Faction pledged: Town Watch.", lines)
        self.assertEqual(engine.progress.faction_id, "town_watch")

    def test_ending_quest_uses_default_text_without_faction(self) -> None:
        quest = self.world.quests["cull_the_wolf"]
        quest.ends_world = True
        quest.ending_text = "The keep remembers a wanderer who chose no banner."
        quest.ending_text_by_faction["town_watch"] = "The Town Watch raises your name over every gate."
        engine = self._engine()
        engine.progress.active_quests.append("cull_the_wolf")
        engine.progress.defeated_enemies.append("forest_wolf")

        lines = engine._check_quest_completion()

        self.assertIn("Quest complete: Cull the Wolf", lines)
        self.assertIn("The keep remembers a wanderer who chose no banner.", lines)
        self.assertNotIn("The Town Watch raises your name over every gate.", lines)
        self.assertIn("Game over.", lines)
        self.assertIn("Final player stats:", lines)
        self.assertTrue(engine.game_over)
        self.assertTrue(engine.await_close_on_game_over)

    def test_ending_quest_uses_faction_specific_text(self) -> None:
        quest = self.world.quests["cull_the_wolf"]
        quest.ends_world = True
        quest.ending_text = "The keep remembers a wanderer who chose no banner."
        quest.ending_text_by_faction["town_watch"] = "The Town Watch raises your name over every gate."
        engine = self._engine()
        engine.progress.faction_id = "town_watch"
        engine.progress.active_quests.append("cull_the_wolf")
        engine.progress.defeated_enemies.append("forest_wolf")

        lines = engine._check_quest_completion()

        self.assertIn("The Town Watch raises your name over every gate.", lines)
        self.assertNotIn("The keep remembers a wanderer who chose no banner.", lines)
        self.assertIn("Game over.", lines)
        self.assertTrue(engine.game_over)

    def test_seal_the_heart_is_standard_story_quest(self) -> None:
        engine = self._ready_seal_the_heart()

        lines = engine._check_quest_completion()

        self.assertIn("Quest complete: Seal the Heart", lines)
        self.assertIn("The Heart Lantern rises from your hands and opens like a small green sun.", lines)
        self.assertNotIn("Game over.", lines)
        self.assertIsNone(engine.progress.pending_ending_quest_id)
        self.assertIn("seal_the_heart", engine.progress.completed_quests)
        self.assertFalse(engine.game_over)

    def test_ending_quest_with_choices_waits_for_player_selection(self) -> None:
        engine = self._ready_final_ending()

        lines = engine._check_quest_completion()

        self.assertIn("Quest complete: End the Concord Wyrm", lines)
        self.assertIn("Choose your ending for End the Concord Wyrm:", lines)
        self.assertIn("  1. Let the keep govern itself", lines)
        self.assertIn("  4. Return to a quiet village", lines)
        self.assertNotIn("  5. Seal every hidden mercy", lines)
        self.assertEqual(engine.progress.pending_ending_quest_id, "end_the_concord_wyrm")
        self.assertIn("end_the_concord_wyrm", engine.progress.completed_quests)
        self.assertFalse(engine.game_over)

    def test_ending_choice_one_uses_default_non_faction_ending(self) -> None:
        engine = self._ready_final_ending(faction_id="town_watch")
        engine._check_quest_completion()

        lines = engine.handle_command("choose ending 1")

        self.assertTrue(any(
            "Emerald Keep survives as a free city of lanterns, archives, roads, and ordinary brave people."
            in line
            for line in lines
        ))
        self.assertNotIn("The Town Watch raises green lanterns across every road.", lines)
        self.assertIn("Game over.", lines)
        self.assertIsNone(engine.progress.pending_ending_quest_id)
        self.assertTrue(engine.game_over)

    def test_ending_choice_two_uses_faction_ending(self) -> None:
        engine = self._ready_final_ending(faction_id="town_watch")
        engine._check_quest_completion()

        lines = engine.handle_command("choose ending 2")

        self.assertIn(
            "The Town Watch raises green lanterns across every road. Emerald Keep becomes a shield-city, practical and stubborn, with your deeds carved above the north gate.",
            lines,
        )
        self.assertIn("Game over.", lines)
        self.assertTrue(engine.game_over)

    def test_ending_choice_three_uses_bad_ending(self) -> None:
        engine = self._ready_final_ending()
        engine._check_quest_completion()

        lines = engine.handle_command("choose ending 3")

        self.assertTrue(any(
            "You gather the four relics and leave before dawn." in line
            for line in lines
        ))
        self.assertIn("Game over.", lines)
        self.assertTrue(engine.game_over)

    def test_ending_choice_four_uses_good_village_life_ending(self) -> None:
        engine = self._ready_final_ending()
        engine._check_quest_completion()

        lines = engine.handle_command("choose ending 4")

        self.assertTrue(any(
            "You refuse every title and walk home by lanternlight." in line
            for line in lines
        ))
        self.assertIn("Game over.", lines)
        self.assertTrue(engine.game_over)

    def test_ending_choice_ten_is_allowed_when_defined(self) -> None:
        engine = self._ready_final_ending()
        quest = self.world.quests["end_the_concord_wyrm"]
        quest.ending_choices = [
            QuestEndingChoice(str(index), f"Choice {index}", f"Ending {index}")
            for index in range(1, 11)
        ]
        engine._check_quest_completion()

        lines = engine.handle_command("choose ending 10")

        self.assertIn("Ending 10", lines)
        self.assertIn("Game over.", lines)
        self.assertTrue(engine.game_over)

    def test_invalid_ending_choice_repeats_available_options(self) -> None:
        engine = self._ready_final_ending()
        engine._check_quest_completion()

        lines = engine.handle_command("choose ending 9")

        self.assertIn("No ending choice matches that option.", lines)
        self.assertIn("Choose your ending for End the Concord Wyrm:", lines)
        self.assertFalse(engine.game_over)

    def test_non_quest_npc_cycles_three_dialogue_lines(self) -> None:
        engine = self._engine()

        first = engine.handle_command("talk mara")
        second = engine.handle_command("talk mara")
        third = engine.handle_command("talk mara")
        fourth = engine.handle_command("talk mara")

        self.assertIn(
            "Well Keeper Mara: The well has moods. Today it sounds like rain remembered from very far away.",
            first,
        )
        self.assertIn(
            "Well Keeper Mara: If you travel north, mind the quiet patches. Forests only go silent when they are listening.",
            second,
        )
        self.assertIn(
            "Well Keeper Mara: I keep three buckets ready: one for thirst, one for fire, and one for strange heroes.",
            third,
        )
        self.assertEqual(first, fourth)
        self.assertEqual(engine.progress.npc_dialogue_indices["well_keeper_mara"], 1)

    def test_single_companion_gets_both_room_dialogue_lines(self) -> None:
        engine = self._engine()
        companion = engine._create_companion_state("squire_tovin", "lantern_inn")
        engine.progress.companions.append(companion)

        lines = engine.handle_command("talk squire tovin")

        self.assertEqual(
            lines,
            [
                "Squire Tovin: Every road meets here. If Emerald Keep has a heartbeat, this square is where it stumbles loudest.",
                "Squire Tovin: The banners look cheerful, but everyone keeps glancing toward the roads. Something has the whole town listening.",
            ],
        )

    def test_two_companions_split_room_dialogue_slots(self) -> None:
        engine = self._engine()
        tovin = engine._create_companion_state("squire_tovin", "lantern_inn")
        mira = engine._create_companion_state("apprentice_mira", "lantern_inn")
        engine.progress.companions.extend([tovin, mira])

        tovin_lines = engine.handle_command("talk squire tovin")
        mira_lines = engine.handle_command("talk apprentice mira")

        self.assertEqual(
            tovin_lines,
            [
                "Squire Tovin: Every road meets here. If Emerald Keep has a heartbeat, this square is where it stumbles loudest."
            ],
        )
        self.assertEqual(
            mira_lines,
            [
                "Apprentice Mira: The banners look cheerful, but everyone keeps glancing toward the roads. Something has the whole town listening."
            ],
        )

    def test_recruiting_companion_uses_class_starter_setup(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"

        lines = engine.handle_command("recruit squire tovin")

        self.assertIn("Squire Tovin joins your party as a Warrior.", lines)
        self.assertEqual(len(engine.progress.companions), 1)
        companion = engine.progress.companions[0]
        self.assertEqual(companion.npc_id, "squire_tovin")
        self.assertEqual(companion.class_id, "warrior")
        self.assertEqual(companion.origin_room, "lantern_inn")
        self.assertEqual(companion.weapon_id, "rusty_sword")
        self.assertEqual(companion.armor_id, "padded_armor")
        self.assertIn("ember_bolt", companion.spell_ids)
        room_lines = engine.describe_current_room()
        people_lines = [line for line in room_lines if line.startswith("People here:")]
        self.assertFalse(any("Squire Tovin" in line for line in people_lines))
        self.assertIn("Companions: Squire Tovin", room_lines)

    def test_recruiting_companion_requires_story_item(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"

        lines = engine.handle_command("recruit trailhand pip")

        self.assertEqual(
            lines,
            [
                "Pip pats every pocket, then tries not to look worried. He will not leave the inn without his lucky button."
            ],
        )
        self.assertEqual(engine.progress.companions, [])

    def test_recruiting_companion_consumes_required_story_item(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.progress.add_item("pip_lucky_button")

        lines = engine.handle_command("recruit trailhand pip")

        self.assertIn("You give Pip's Lucky Button to Trailhand Pip.", lines)
        self.assertIn("Trailhand Pip joins your party as a Rogue.", lines)
        self.assertNotIn("pip_lucky_button", engine.progress.inventory)
        self.assertEqual(engine.progress.companions[0].npc_id, "trailhand_pip")

    def test_companion_limit_is_two(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"

        first = engine.handle_command("recruit squire tovin")
        second = engine.handle_command("recruit apprentice mira")
        third = engine.handle_command("recruit trailhand pip")

        self.assertIn("Squire Tovin joins your party as a Warrior.", first)
        self.assertIn("Apprentice Mira joins your party as a Mage.", second)
        self.assertEqual(third, ["You can travel with at most 2 companions."])
        self.assertEqual(len(engine.progress.companions), 2)

    def test_dismissed_companion_returns_to_origin_room(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit squire tovin")
        engine.progress.current_room = "forest_path"
        engine.progress.room_enemies["forest_path"] = []

        lines = engine.handle_command("dismiss squire tovin")

        self.assertEqual(lines, ["Squire Tovin leaves your party and returns to Lantern Inn."])
        self.assertEqual(engine.progress.companions, [])
        engine.progress.current_room = "lantern_inn"
        self.assertTrue(any("Squire Tovin" in line for line in engine.describe_current_room()))

    def test_player_can_equip_companion_from_inventory(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit squire tovin")
        engine.progress.add_item("iron_dagger")

        lines = engine.handle_command("equip iron dagger to squire tovin")

        self.assertEqual(lines, ["Squire Tovin equips Iron Dagger as weapon."])
        self.assertEqual(engine.progress.companions[0].weapon_id, "iron_dagger")

    def test_companion_casts_offense_spell_in_combat(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit squire tovin")
        state = self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", side_effect=[1, 0]):
            lines = engine._companion_turn()

        self.assertIn("Companions act:", lines)
        self.assertIn("  Squire Tovin casts Ember Bolt on Forest Wolf for 13 damage.", lines)
        self.assertEqual(state.current_hp, 3)
        self.assertEqual(engine.progress.companions[0].current_mp, 7)

    def test_companion_attacks_when_out_of_spell_power(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit squire tovin")
        companion = engine.progress.companions[0]
        companion.current_mp = 0
        state = self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", side_effect=[1, 0]):
            lines = engine._companion_turn()

        self.assertIn("  Squire Tovin attacks Forest Wolf for 10 damage.", lines)
        self.assertEqual(state.current_hp, 6)

    def test_enemies_can_target_companions(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit squire tovin")
        companion = engine.progress.companions[0]
        self._place_forest_wolf(engine)

        with patch("ifw.engine.random.randint", side_effect=[1, 1, 0]):
            lines = engine._enemy_turn()

        self.assertIn("  Forest Wolf hits Squire Tovin for 1 damage.", lines)
        self.assertEqual(companion.current_hp, 41)
        self.assertEqual(engine.player.hp, 42)

    def test_rest_restores_companions(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit squire tovin")
        companion = engine.progress.companions[0]
        companion.current_hp = 20
        companion.current_mp = 3

        lines = engine.handle_command("rest")

        self.assertIn("Your companions recover HP +22, MP +9.", lines)
        self.assertEqual(companion.current_hp, 42)
        self.assertEqual(companion.current_mp, 12)
        self.assertEqual(engine.player.gold, 25)

    def test_player_can_use_healing_consumable_on_companion(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit squire tovin")
        companion = engine.progress.companions[0]
        companion.current_hp = 30
        engine.progress.add_item("healing_tonic")

        lines = engine.handle_command("use healing tonic on squire tovin")

        self.assertIn("You use Healing Tonic on Squire Tovin. Squire Tovin HP +12", lines)
        self.assertEqual(companion.current_hp, 42)
        self.assertNotIn("healing_tonic", engine.progress.inventory)

    def test_player_can_use_mana_consumable_on_companion(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit apprentice mira")
        companion = engine.progress.companions[0]
        companion.current_mp = engine._companion_max_mp(companion) - 6
        engine.progress.add_item("mana_tonic")

        lines = engine.handle_command("use mana tonic for apprentice mira")

        self.assertIn("You use Mana Tonic on Apprentice Mira. Apprentice Mira MP +6", lines)
        self.assertEqual(companion.current_mp, engine._companion_max_mp(companion))
        self.assertNotIn("mana_tonic", engine.progress.inventory)

    def test_player_can_use_attack_potion_on_companion(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "lantern_inn"
        engine.handle_command("recruit squire tovin")
        companion = engine.progress.companions[0]
        companion.current_mp = 0
        engine.progress.add_item("fury_draught")
        base_attack = engine._companion_attack_score(companion)

        use_lines = engine.handle_command("use fury draught on squire tovin")
        stats_after_use = engine.handle_command("stats")
        state = self._place_forest_wolf(engine)
        with patch("ifw.engine.random.randint", side_effect=[1, 0]):
            attack_lines = engine._companion_turn()
        stats_after_attack = engine.handle_command("stats")

        self.assertIn("You use Fury Draught on Squire Tovin. Attack +3 for 2 attacks", use_lines)
        self.assertEqual(engine._companion_attack_score(companion), base_attack + 3)
        self.assertIn("Active magic: Squire Tovin: Fury Draught (2 turns)", stats_after_use)
        self.assertIn("  Squire Tovin attacks Forest Wolf for 13 damage.", attack_lines)
        self.assertEqual(state.current_hp, 3)
        self.assertIn("Active magic: Squire Tovin: Fury Draught (1 turns)", stats_after_attack)
        self.assertNotIn("fury_draught", engine.progress.inventory)

    def test_entering_end_room_marks_game_over(self) -> None:
        self.world.end_room = "heart_sanctum"
        engine = self._engine()
        engine.progress.current_room = "sanctum"
        engine.progress.room_enemies["sanctum"] = []

        lines = engine.handle_command("go east")

        self.assertTrue(engine.game_over)
        self.assertTrue(engine.await_close_on_game_over)
        self.assertIn("Game over.", lines)
        self.assertIn("Final player stats:", lines)
        self.assertIn("TestHero the Warrior", lines)

    def test_player_save_round_trip_keeps_world_progress_separate(self) -> None:
        engine = self._engine()
        engine.progress.current_room = "forest_path"
        engine.progress.previous_room = "town_square"
        engine.progress.sealed_rooms.append("starless_approach")
        engine.progress.story_flags.append("town_mural_opened")
        engine.progress.faction_id = "town_watch"
        engine.progress.pending_ending_quest_id = "end_the_concord_wyrm"
        engine.progress.item_charges["archive_cipher"] = 1
        engine.progress.player_poisoned = True
        engine.progress.pickpocketed_targets.append("vendor:exchange_clerk_marlow:exchange_vault_key")
        engine.progress.lockpick_failures["currency_exchange_office:exchange_vault_door"] = 2
        engine.player.wallet["emerald_mark"] = 3
        engine.progress.add_item("wolf_pelt")
        engine.progress.add_item("silver_ring")
        engine.handle_command("equip silver ring")
        engine.progress.unlocked_recipes.append("iron_spear_pattern")
        engine.progress.npc_dialogue_indices["well_keeper_mara"] = 2
        engine.progress.companions.append(
            CompanionState(
                npc_id="squire_tovin",
                class_id="warrior",
                origin_room="town_square",
                current_hp=30,
                current_mp=6,
                weapon_id="rusty_sword",
                armor_id="padded_armor",
                spell_ids=["ember_bolt"],
            )
        )

        save_root = ROOT / "tests" / "_tmp_saves"
        save_root.mkdir(parents=True, exist_ok=True)
        save_player(self.player, save_root)
        loaded = load_player("TestHero", save_root)

        self.assertIsNotNone(loaded)
        assert loaded is not None
        progress = loaded.world_states["emerald_keep"]
        self.assertEqual(loaded.wallet["emerald_mark"], 3)
        self.assertEqual(progress.current_room, "forest_path")
        self.assertEqual(progress.previous_room, "town_square")
        self.assertEqual(progress.sealed_rooms, ["starless_approach"])
        self.assertEqual(progress.story_flags, ["town_mural_opened"])
        self.assertEqual(progress.faction_id, "town_watch")
        self.assertEqual(progress.pending_ending_quest_id, "end_the_concord_wyrm")
        self.assertEqual(progress.item_charges["archive_cipher"], 1)
        self.assertTrue(progress.player_poisoned)
        self.assertEqual(
            progress.pickpocketed_targets,
            ["vendor:exchange_clerk_marlow:exchange_vault_key"],
        )
        self.assertEqual(progress.lockpick_failures["currency_exchange_office:exchange_vault_door"], 2)
        self.assertEqual(progress.accessory_ids, ["silver_ring"])
        self.assertEqual(progress.unlocked_recipes, ["iron_spear_pattern"])
        self.assertEqual(progress.inventory.get("wolf_pelt"), 1)
        self.assertEqual(progress.npc_dialogue_indices["well_keeper_mara"], 2)
        self.assertEqual(progress.companions[0].npc_id, "squire_tovin")
        self.assertEqual(progress.companions[0].current_hp, 30)
        self.assertEqual(progress.companions[0].spell_ids, ["ember_bolt"])



if __name__ == "__main__":
    unittest.main()
