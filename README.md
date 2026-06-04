# IFW

`IFW` is a small Python interactive-fiction RPG framework. Worlds are stored in XML, while player characters are saved separately as JSON so the same character can revisit the same world or jump into a different one later.

## Features

- Folder-based XML worlds with a required `start_room` and optional legacy `end_room`
- Interactive fiction style room navigation and text commands
- Active threats lock normal movement and item pickup until you win or retreat
- Rooms can be locked behind required items such as keys
- Rooms can optionally seal after you leave them to prevent story backtracking
- Rooms can define interactable environment objects that set story flags and reveal hidden exits
- Rooms can define maze sequences that require a predetermined set of movement commands
- Rooms can define mining-style resource drops that respawn on room entry with a 1-in-6 roll
- Safe rooms such as inns can let the player rest and restore HP and MP for 10 gold
- Separate player save files with name, world-defined class, level, HP, MP, gold, wallet currencies, and experience
- Worlds can define multiple currencies, vendors can price goods in accepted currencies, and exchange vendors can trade currency types at XML-defined rates
- Worlds define their own player classes, including starting stats and per-level growth
- Inventory, weapons, armor, up to three accessories, consumables, player storage, and a separate key ring
- Items can carry optional HP and MP enchantments that raise effective max health or magic when equipped
- Equipment can define level requirements so weapon, armor, and accessory upgrades unlock at progression milestones
- Rogue-style classes can define pickpocket and lockpick skills, with accessories that improve success chances
- Failed pickpocketing can send the player to a configured jail with bail, level-loss escape, or game-over consequences
- Spell vendors can sell spells directly, and spellbooks can teach new spells when used
- Advanced spells can be restricted to specific character classes such as mage
- Unlockable crafting recipes earned from vendors or quest rewards
- Combat with weapons, armor, offense magic, healing magic, attack buffs, defense magic, control magic, and hit/miss rolls
- Enemies can inflict poison; poison ticks for 1-3 HP at the start of player combat turns until cured by an item or spell
- Enemies scale HP, attack, and defense with player level so older rooms and late bosses stay relevant
- Enemy defeat narration can be defined in XML to add story text after combat victories
- Standard enemies can respawn on room re-entry with a 1-in-6 roll, while boss-style enemies can be marked to stay defeated and reset to full health if they defeat the player
- Rooms can draw enemies from weighted environment-specific monster pools
- Rooms can define faction-triggered enemy spawns that begin rolling after the player pledges to a matching faction
- Utility items can act as reusable tools for room events and environmental interactions
- Misc items can represent one-off story objects for world events
- Magical equipment, utility, misc, quest, and key items can have finite charges, depleted stats, and recharge consumables
- Quest givers can hand over key items when a quest is accepted
- Quests can branch completion text and rewards based on story flags
- NPC quest givers can belong to factions, with explicit warning and confirmation before a quest locks the player into that faction
- Ending quests can offer up to ten player-selected endings, including default, faction-specific, and custom outcomes
- Recruitable companion NPCs can require a personal item before joining, then fight in combat, cast starter spells, learn purchased spells, use targeted consumables, and equip player inventory weapons or armor
- NPC dialogue, vendors, quests, and rewards
- Per-world progress tracking for rooms, enemies, quests, inventory, and learned spells

## Quick Start

1. Create a virtual environment if you want one.
2. Run the sample world:

```bash
python -m ifw --world worlds/emerald_keep
```

You can also provide an existing or new character name up front:

```bash
python -m ifw --world emerald_keep --player Rowan
```

The project also includes a larger story world:

```bash
python -m ifw --world embers_hollow --player Rowan
```

And an arcane desert oasis story:

```bash
python -m ifw --world velrasha_oasis --player Rowan
```

## Commands

- `look`, `look <object>`
- `go north`, `north`, `south`, `east`, `west`, `in`, `out`, `retreat`
- `take <item>`, `take all`, `drop <item>`, `examine room`, `examine <object or item>`, `interact <object>`
- `inventory`, `key ring`, `stats`, `wallet`
- `companions`, `recruit <npc>`, `dismiss <companion>`
- `rest`
- `equip <item>`, `unequip weapon`, `unequip armor`, `unequip accessory`, `unequip <accessory>`
- `equip <item> to <companion>`, `equip <companion> with <item>`
- `use <item or spellbook>`, `use <consumable> on <companion>`, `use <utility> on <object>`, `use <recharge item> on <charged item>`
- `pickpocket <npc or vendor> for <item>`, `lockpick <object>`, `pay bail`, `escape jail`
- `talk <npc>`, `accept <npc or quest>`
- `choose ending <number>`
- `shop`, `buy <item, recipe, or spell>`, `buy <spell or spellbook> for <companion>`, `sell <item>`
- `rates`, `exchange <amount> <currency> to <currency>`
- `attack <enemy>`
- `cast <spell> on <enemy>`
- `cast <defense spell>`
- `cast <healing spell>`
- `spells`
- `craft <result>`
- `combine <item one> with <item two>`
- `recipes`
- `storage`, `store <item>`, `retrieve <item>`
- `quests`
- `save`
- `quit`

## Project Layout

- [ifw/__main__.py](/C:/Code%20Projects/IFW/ifw/__main__.py) starts the CLI.
- [ifw/engine](/C:/Code%20Projects/IFW/ifw/engine) contains the game loop, command system, and engine mixins.
- [ifw/world_loader.py](/C:/Code%20Projects/IFW/ifw/world_loader.py) parses and validates XML worlds.
- [ifw/persistence.py](/C:/Code%20Projects/IFW/ifw/persistence.py) stores player saves in `players/`.
- [worlds/emerald_keep](/C:/Code%20Projects/IFW/worlds/emerald_keep) is a complete sample world.
- [worlds/embers_hollow](/C:/Code%20Projects/IFW/worlds/embers_hollow) is a larger story world set in Ember's Hollow.
- [worlds/velrasha_oasis](/C:/Code%20Projects/IFW/worlds/velrasha_oasis) is an arcane desert oasis story set around Vel'rasha's unstable Starwell.

## XML Notes

Worlds are now organized as folders. Each world folder contains a `world.xml` metadata file plus focused section files for the larger XML elements. The loader still accepts legacy single-file worlds, but the folder layout is the preferred format for rewrites and additions.

```text
worlds/emerald_keep/
  world.xml
  items.xml
  spells.xml
  enemies.xml
  npcs.xml
  vendors.xml
  quests.xml
  rooms.xml
```

The folder sections combine into the same structure as the legacy single-file format:

- `<world id="" name="" start_room="">`, with optional `end_room=""` for legacy room-based endings
- `world.xml` also contains `<currencies>`, `<player_classes>`, `<factions>`, `<starter_loadouts>`, and `<starter_spells>` when the world uses them
- `<items>`, `<spells>`
- `items.xml` can include a nested `<crafting>` block with recipe definitions
- `<npcs>`, `<vendors>`, `<quests>`, `<enemies>`
- `enemies.xml` can include a nested `<monster_pools>` block with weighted `<enemy_ref id="" weight="">` entries
- `<rooms>` with exits plus hidden exits, interactions, item, enemy, NPC, vendor, and optional lock references

Currencies are defined in `world.xml`. If a world omits `<currencies>`, `gold` is created automatically for backward compatibility. Vendors can list accepted currencies with `currencies="gold,emerald_mark"`, and individual stock, recipe, or spell entries can override their price currency with `currency="emerald_mark"`. Exchange vendors use `exchange="true"` with `<exchange_rates>` and can be used with `rates` or `exchange <amount> <currency> to <currency>`.

```xml
<currencies default="gold">
  <currency id="gold" name="Gold" singular="gold" plural="gold" />
  <currency id="emerald_mark" name="Emerald Mark" singular="emerald mark" plural="emerald marks" />
</currencies>

<vendor id="exchange_clerk" name="Exchange Clerk" currencies="gold,emerald_mark" exchange="true">
  <exchange_rates>
    <rate from="gold" to="emerald_mark" from_amount="5" to_amount="1" />
    <rate from="emerald_mark" to="gold" from_amount="1" to_amount="4" />
  </exchange_rates>
</vendor>
```

Quests support an optional `accept_item="item_id"` attribute when the quest giver should hand over an item as soon as the quest is accepted.

Quests can define `<offer_dialogue>`, `<active_dialogue>`, and `<completed_dialogue>` so each quest in an NPC chain can have its own talk text.

Fetch quests that use `required_item="item_id"` without a `destination_room` complete only after the player returns to the quest giver's room or talks to that quest giver. Destination quests still complete at their destination room.

Quests can branch their completion text and rewards based on a story flag. Add `<flag_outcome flag="flag_id">` with optional `<true>` and `<false>` branches. Branches can override `reward_gold`, `reward_currency`, `reward_amount`, `reward_exp`, `reward_item`, `reward_recipe`, and `<completion_text>`; any omitted reward falls back to the quest's normal reward. Use `reward_currency="currency_id"` plus `reward_amount=""` when a quest should pay a non-gold currency.

```xml
<flag_outcome flag="ore_cipher_decoded">
  <true reward_gold="35" reward_exp="70" reward_recipe="wild_mage_robe_pattern">
    <completion_text>Nox compares the ore to the focused lens-script and finds a stronger pattern.</completion_text>
  </true>
  <false reward_gold="25" reward_exp="55">
    <completion_text>Nox reads the ore by candlelight and pays for the sample.</completion_text>
  </false>
</flag_outcome>
```

```xml
<quest id="hold_the_road" name="Hold the Road" reward_currency="emerald_mark" reward_amount="5">
  <flag_outcome flag="watch_signal_lit">
    <true reward_amount="7" reward_exp="70" />
    <false reward_amount="5" reward_exp="55" />
  </flag_outcome>
</quest>
```

Magical items can use `magical="true"` for the default three charges, or define `charges="5"` / `max_charges="5"`. Equipment can define depleted stats such as `depleted_defense_bonus`; when charged armor reaches 0 charges after its wearer takes hits, those depleted stats are used until the item is recharged. Charged utility, misc, quest, and key items spend one charge when they successfully power a room interaction. Recharging consumables use an effect flag and are targeted with `use <recharge item> on <charged item>`.

```xml
<item id="wild_mage_robe" name="Wild Mage Robe" type="armor"
      defense_bonus="2" mp_bonus="6" magical="true"
      depleted_defense_bonus="1" depleted_mp_bonus="2" />

<item id="mana_crystal" name="Mana Crystal" type="consumable">
  <effect recharge_charges="true" />
</item>
```

Enemies can inflict poison on hit with `poison_chance="35"` and optional `<poison_text>`. Poisoned players take 1-3 HP at the start of player combat turns until cured. Consumables cure poison with `<effect cure_poison="true" />`; spells can cure poison with `cure_poison="true"` on a healing or cure school.

```xml
<enemy id="forest_snake" name="Forest Snake" level="1" hp="14" attack="5" defense="1" exp_reward="30" gold_reward="9" poison_chance="35">
  <poison_text>The snake's bite leaves poison racing hot under your skin.</poison_text>
</enemy>

<item id="antidote" name="Antidote" type="consumable">
  <effect cure_poison="true" />
</item>

<spell id="purify_blood" name="Purify Blood" school="cure" mp_cost="4" cure_poison="true" />
```

Quests can end the story with `ending="true"`. Use `<ending_text>` for the default ending, then add optional faction-specific `<ending faction="faction_id">` branches. If the player has avoided factions, or their faction has no branch, the default ending is used. Worlds no longer need an `end_room` when an ending quest wraps the story.

Ending quests can also define up to ten `<ending_choices>`. A `default` choice always plays `<ending_text>`, a `faction` choice plays the player's current faction ending when one exists, and custom choices use their own text. When an ending quest with choices completes, the game waits for `choose ending <number>` before showing game over.

```xml
<quest id="seal_the_realm" name="Seal the Realm" giver="elder_rowan" ending="true">
  <description>Return to Elder Rowan once the final threat is defeated.</description>
  <completion_text>The final seal settles into place.</completion_text>
  <ending_text>You leave as a free wanderer, remembered by no banner and every road.</ending_text>
  <ending faction="town_watch">The Town Watch raises your name above the north gate.</ending>
  <ending faction="moon_archive">The Moon Archive records your victory in silver ink.</ending>
  <ending_choices>
    <choice id="1" label="Leave as a free wanderer" ending="default" />
    <choice id="2" label="Let your faction tell the story" ending="faction" />
    <choice id="3" label="Answer the whisper">Something unseen waits beyond the door.</choice>
    <choice id="4" label="Return home">You go home and live a peaceful life.</choice>
  </ending_choices>
</quest>
```

NPCs can grant a single quest with `quest_id="quest_id"` or an ordered chain with `<quests><quest_ref id="quest_id" /></quests>`. Quest chains offer only the first incomplete quest, so later quests stay locked until earlier quests are completed.

NPCs without quests can include a `<dialogue_lines>` block with exactly three `<line>` entries. Each `talk <npc>` command shows the next line and loops back to the first line after the third.

NPCs can be flagged as recruitable companions with `companion="true"` and `companion_class="class_id"`. The companion class must match one of the world's `<player_classes>`. Add `recruit_item="item_id"` when the player must give a story item before recruitment succeeds; by default the item is consumed, or set `consume_recruit_item="false"` to only require showing it. Recruited companions use that class's starter loadout and starter spells, scale with the player's level, can learn valid purchased spells with `buy <spell or spellbook> for <companion>`, can receive consumables with `use <consumable> on <companion>`, and return to their original room when dismissed. The player can travel with up to two companions.

```xml
<npc id="trailhand_pip" name="Trailhand Pip" companion="true" companion_class="rogue" recruit_item="pip_lucky_button">
  <dialogue>Pip leans beside the common-room stairs, already mapping exits and shadows.</dialogue>
  <recruit_missing_item_text>Pip will not leave without his lucky button.</recruit_missing_item_text>
</npc>
```

Worlds can define factions with `<factions><faction id="" name="">`. An NPC can use `faction="faction_id"` to mark quests from that NPC as faction quests. The first accepted quest from a faction NPC requires confirmation with `accept <npc or quest> confirm`; accepting it pledges the player to that faction and blocks quests from NPCs in other factions. Talking to a faction quest giver shows a faction warning before commitment.

Rooms can define faction-triggered enemies with `<faction_spawns>`. These enemies are not part of the room's initial enemy list; after the player pledges to the matching faction, the room rolls the same 1-in-6 respawn chance on entry. Use `count` to allow more than one copy.

```xml
<faction_spawns>
  <enemy_ref faction="town_watch" id="bandit_scout" count="1" />
</faction_spawns>
```

Worlds define playable roles with `<player_classes>`. Each `<class>` needs a stable `id` used by role-dependent systems, a display `name`, starting stats, starting gold, and optional per-level growth values. Extra starting currencies can be added inside `<starting_currencies>`. Starter loadouts, starter spells, and spell class restrictions are validated against these class ids, so custom narrative classes can drive world-specific mechanics.

```xml
<player_classes>
  <class id="warrior" name="Hearthguard" max_hp="42" max_mp="12" gold="35" base_attack="7" base_defense="4" hp_per_level="8" mp_per_level="4" attack_per_level="2" defense_per_level="1">
    <description>A shield-bearing defender trained to fight through smoke and panic.</description>
  </class>
  <class id="rogue" name="Sootrunner" max_hp="34" max_mp="18" gold="32" base_attack="6" base_defense="3" pickpocket_chance="65" lockpick_chance="60" />
</player_classes>
```

Pickpocket targets can be added to NPCs or vendors. The player targets a specific item, and failure sends them to the world's configured jail. If they cannot pay bail, they may use `escape jail` to lose a level; if they cannot pay and are level 1, the game ends. Lockpickable room interactions require a utility item such as `lockpicks`; after three failed attempts against the same lock, one set of lockpicks breaks. Accessories can improve these odds with `pickpocket_bonus` and `lockpick_bonus`.

```xml
<jail room="town_jail" fee="15" currency="gold" />

<vendor id="exchange_clerk" name="Exchange Clerk">
  <pickpocket>
    <item_ref id="exchange_vault_key" difficulty="10" />
  </pickpocket>
</vendor>

<object id="exchange_vault_door" name="Exchange Vault Door"
        required_item="exchange_vault_key"
        lockpick="true" lockpick_difficulty="15"
        lockpick_item="lockpicks"
        set_flag="exchange_vault_opened" />

<item id="nimble_fingers_ring" name="Nimble Fingers Ring" type="accessory"
      pickpocket_bonus="10" lockpick_bonus="10" />
```

Rooms can define environment interactions and hidden exits driven by persistent story flags. Interactions appear as notable objects in room descriptions, can be examined, and can be activated with `interact <object>` or `use <object>` when no matching inventory item exists. Hidden exits are not displayed or usable until their required flag has been set.

Interactions can require an inventory item with `required_item="item_id"`. Add `consume_item="true"` when the item should be removed after a successful interaction, and use `<missing_item_text>` for the blocked message shown when the player does not have the item. Utility tools can target these interactions directly with `use <utility> on <object>`.

```xml
<hidden_exits>
  <exit direction="west" to="mage_tower" required_flag="town_mural_opened" />
</hidden_exits>
<interactions>
  <object id="weathered_mural" name="Weathered Mural" set_flag="town_mural_opened">
    <description>A mural shows scholars walking through an impossible doorway.</description>
    <interact_text>You press the moon sigil, and a hidden stair opens west.</interact_text>
    <completed_text>The hidden stair is already open.</completed_text>
  </object>
  <object id="hearth_ward" name="Hearth Ward" required_item="healing_tonic" consume_item="true" set_flag="hearth_ward_kindled">
    <description>A brass ward bowl rests beside the hearth.</description>
    <missing_item_text>The ward bowl needs a Healing Tonic before its runes will wake.</missing_item_text>
    <interact_text>You pour in a Healing Tonic, and amber runes flare softly.</interact_text>
  </object>
</interactions>
```

Items support an optional `teaches_spell="spell_id"` attribute so spellbooks can teach a spell when used.

Items with `type="key"` are stored with the player for lock checks, but they are hidden from the standard inventory and displayed with the `key ring`, `keyring`, or `keys` command.

Items with `type="utility"` represent reusable tools for room events, such as pry bars, lenses, ropes, or other adventuring gear. Utility items appear in standard inventory and can be used with `use <utility> on <object>` when a room interaction requires that item. Leave `consume_item` unset or false for reusable tools.

Items with `type="misc"` represent story objects that do not fit equipment, consumable, key, quest, material, spellbook, or utility categories. They appear in standard inventory and can be used for one-off room events with `use <misc item> on <object>`, commonly with `consume_item="true"` when the story object should be handed over or placed permanently.

Items also support optional `hp_bonus` and `mp_bonus` attributes for equipment enchantments that raise effective max HP or MP while the item is equipped.

Weapons, armor, and accessories can include `required_level="N"` to prevent equipping them until the player reaches that level. The loader also accepts `level_required` and `level_requirement` as aliases, and validates that level requirements are only used on equipment.

Consumable `<effect>` blocks can restore resources with `hp_restore` and `mp_restore`, or apply temporary potion buffs with `attack_bonus`, `defense_bonus`, and `duration`. Attack potion duration ticks down when the player attacks; defense potion duration ticks down on enemy turns.

Spells support optional `attack_bonus`, `armor_bonus`, and `duration` attributes for temporary combat buffs. Use `school="attack"` for attack-boosting spells and `school="defense"` for defensive wards. Use `school="healing"` with `power` to restore HP up to the player's current maximum. Use `school="control"` with `skip_turns="1"` for spells like Flash that make the target enemy miss its next attack.

Spells also support an optional `classes="mage"` attribute. Leave it blank or omit it for spells available to every class; use comma-separated class ids such as `classes="mage,rogue"` for class-specific magic.

Enemies can include an optional `<defeat_text>` block to add narrative completion text after that enemy is defeated.

Enemies support an optional `respawns="false"` attribute for boss-style encounters that should stay defeated once cleared.

Enemies can prevent the player's next offensive action with `prevent_attack_chance="25"` and `prevent_attack_turns="1"`. Add `<prevent_attack_text>` to customize the combat message.

Enemy HP, attack, and defense scale upward when the player outlevels the enemy's XML `level`. Standard respawning enemies receive steady scaling, while `respawns="false"` enemies are treated as boss encounters and receive a stronger boost. Existing saved enemy states are normalized when the room is revisited, so bosses created earlier in a world journal still scale to the player's current level.

If the player falls while fighting a `respawns="false"` enemy, that enemy's current HP resets to its scaled maximum before the player wakes at the start room.

Rooms can include `monster_pool="pool_id"` and `monster_count="1"` attributes to roll enemies from an environment pool when the world journal is first created, then use that same pool for possible respawns.

Rooms can include a `<mining>` block to expose resource items on entry. Each entry rolls with the same 1-in-6 respawn rate as standard enemies when no configured mining resource is currently lying in that room. On a successful roll, each `<item_ref>` spawns a random quantity from `min` to `max`, defaulting to 1-3.

```xml
<mining>
  <message>The coal seam cracks open under old pressure.</message>
  <item_ref id="ember_shard" min="1" max="3" />
</mining>
```

Rooms can include a `<maze success_room="room_id">` block to turn movement commands into a compact puzzle path. Define the required moves with either `sequence="north,east,north"` or `<step direction="north" />` entries, plus optional `<progress_message>`, `<failure_message>`, and `<success_message>` text. Normal exits still work, but maze directions cannot overlap normal exit directions.

Rooms support an optional `locks_on_exit="true"` attribute plus an optional `<sealed_message>` block when they should let the player enter once, then close behind them after they leave for a new forward room. Stepping back to the room you just came from does not seal them.

Vendors can include a `<spells>` section with `<spell_ref id="" price="">` entries to sell spells directly. Target a recruited companion with `buy <spell> for <companion>` to teach that companion instead of the player; spellbook items that define `teaches_spell` can also be purchased for companions.

The loader validates room references, quest references, starter loadouts, loot, recipe unlock references, the required start room, and the optional end room before the game starts.
