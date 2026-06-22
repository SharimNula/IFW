# Interactive Fiction World Engine (IFW)

IFW is a Python interactive-fiction RPG engine driven by XML world data. Worlds define their own classes, rooms, items, enemies, quests, companions, vendors, currencies, and endings. Player characters are saved separately as JSON, allowing one character to keep independent progress across multiple worlds.

The included **Emerald Keep** campaign is both a playable six-zone adventure and the canonical example for world authors.

## Quick Start

IFW requires Python 3.11 or newer and has no runtime dependencies.

Run Emerald Keep:

```powershell
python -m ifw --world emerald_keep
```

Load or create a named character:

```powershell
python -m ifw --world emerald_keep --player Rowan
```

Run without arguments to choose a world and character interactively:

```powershell
python -m ifw
```

Optional editable installation:

```powershell
python -m pip install -e .
ifw --world emerald_keep --player Rowan
```

Characters are saved in `players/<character-name>.json`. A save contains the character's shared stats and a separate progress journal for each world.

## Playing

IFW uses text commands. Type `help` in-game for the current command list.

| Area | Commands |
| --- | --- |
| Explore | `look`, `examine room`, `go <direction>`, `north`, `south`, `east`, `west`, `in`, `out`, `retreat` |
| Environment | `examine <object>`, `interact <object>`, `answer <object> with <password>` |
| Items | `take <item>`, `take all`, `drop <item>`, `inventory`, `key ring`, `examine <item>` |
| Equipment | `equip <item>`, `unequip weapon`, `unequip armor`, `unequip accessory` |
| Combat | `attack <enemy>`, `cast <spell> [on <enemy>]`, `use <consumable>` |
| Character | `stats`, `wallet`, `spells`, `recipes`, `quests`, `rest` |
| NPCs | `talk <npc>`, `accept <npc or quest>`, `pickpocket <npc or vendor> for <item>` |
| Companions | `companions`, `recruit <npc>`, `talk <companion>`, `dismiss <companion>` |
| Companion gear | `equip <item> to <companion>`, `use <consumable> on <companion>` |
| Shops | `shop`, `examine <vendor spell>`, `buy <item, recipe, or spell>`, `sell <item>` |
| Currency | `rates`, `exchange <amount> <currency> to <currency>` |
| Crafting | `craft <item>`, `combine <item> with <item>` |
| Storage | `storage`, `store <item>`, `retrieve <item>` |
| Stealth | `lockpick <object>`, `pay bail`, `escape jail` |
| Ending | `choose ending <number>` |
| Session | `save`, `quit` |

Active threats prevent normal movement, item pickup, and environment interaction. Defeat the threat or use `retreat` to return to the previous room.

Examining shop equipment compares weapons and armor against the player's currently equipped item. Examining vendor spells shows their school, description, MP cost, power, and class restrictions.

## Included Campaign

[Emerald Keep](worlds/emerald_keep) is a large campaign built around a central town and five increasingly dangerous adventure zones:

1. Emerald Keep and its surrounding roads
2. The Thornwild
3. Emberdeep
4. Vel'rasha Oasis
5. The Moonfall Archive
6. The Starless Citadel

The main story requires four guarded relics to open the final zone. The campaign demonstrates the complete engine feature set, including factions, quest chains, companions, stealth, environmental puzzles, crafting, multiple currencies, weighted monster pools, charged magical items, optional secrets, and choice-driven endings.

## Project Structure

```text
ifw/
  __main__.py                 CLI entry point
  engine/                     Commands, combat, navigation, and game state
  world_sections/             XML section parsers
  world_loader.py             World loading and section merging
  world_loader_validation.py  Cross-reference and content validation
  persistence.py              Character JSON saves
worlds/
  emerald_keep/               Complete sample campaign
players/                      Generated character saves
tests/
  test_game.py                Engine and campaign regression tests
```

Run the test suite:

```powershell
python -B -m unittest
```

## World Format

Folder-based worlds are the preferred format. The loader also accepts legacy single-file XML worlds.

```text
worlds/my_world/
  world.xml
  items.xml
  spells.xml
  enemies.xml
  npcs.xml
  vendors.xml
  quests.xml
  rooms.xml
```

Only `world.xml` is required as a file, but every valid world must define at least one player class and the declared start room. Optional section files must use the matching root element shown above. The loader merges all present sections and validates references before play begins.

### Section Responsibilities

| File | Defines |
| --- | --- |
| `world.xml` | World metadata, classes, currencies, factions, jail, starter loadouts, and starter spells |
| `items.xml` | Equipment, consumables, keys, tools, story items, spellbooks, materials, and crafting recipes |
| `spells.xml` | Offensive, defensive, healing, control, attack-buff, cure, and stealth spells |
| `enemies.xml` | Enemies, loot, poison/control effects, boss behavior, and weighted monster pools |
| `npcs.xml` | Quest givers, rotating-dialogue NPCs, faction membership, pickpocket targets, and companions |
| `vendors.xml` | Item, recipe, and spell stock, accepted currencies, exchange rates, and pickpocket targets |
| `quests.xml` | Quest objectives, rewards, flag branches, faction consequences, quest dialogue, and endings |
| `rooms.xml` | Navigation, encounters, NPC/vendor placement, items, interactions, puzzles, and companion dialogue |

### Minimal World

`world.xml`:

```xml
<world id="small_world" name="Small World" start_room="crossroads">
  <description>A compact example world.</description>
  <player_classes>
    <class id="wanderer" name="Wanderer"
           max_hp="30" max_mp="10" gold="20"
           base_attack="5" base_defense="3" />
  </player_classes>
</world>
```

`rooms.xml`:

```xml
<rooms>
  <room id="crossroads" name="Crossroads">
    <description>Four roads meet beneath an old lantern.</description>
    <exits>
      <exit direction="north" to="hilltop" />
    </exits>
  </room>

  <room id="hilltop" name="Hilltop">
    <description>The road ends beneath an open sky.</description>
    <exits>
      <exit direction="south" to="crossroads" />
    </exits>
  </room>
</rooms>
```

## Core Authoring Concepts

### Rooms and Story Flags

Rooms support normal and hidden exits, required entry items, weighted encounters, faction encounters, storage, paid rest, mining drops, compact movement mazes, and optional one-way sealing.

Environment interactions can require items, spend magical charges, accept passwords, set persistent flags, and reveal hidden exits:

```xml
<room id="grotto" name="Crystal Grotto">
  <description>Green crystals hum behind a sealed wall.</description>

  <hidden_exits>
    <exit direction="in" to="secret_cache" required_flag="cache_opened" />
  </hidden_exits>

  <interactions>
    <object id="cipher_door" name="Cipher Door"
            password="SNAKE" set_flag="cache_opened">
      <description>Five blank crystal scales surround a narrow seam.</description>
      <password_text>The scales turn, revealing a hidden passage.</password_text>
      <password_failed_text>The scales reset without opening.</password_failed_text>
    </object>
  </interactions>
</room>
```

Hidden paths are neither displayed nor usable until their required flag is set.

### Companion Dialogue

Rooms may define two companion observations:

```xml
<companion_dialogue>
  <line>The road is too quiet. Keep your weapon close.</line>
  <line>Someone passed through recently, and they were moving quickly.</line>
</companion_dialogue>
```

With two companions, each companion speaks one line. With one companion, that companion speaks both. If the block is omitted, the loader generates two room-specific fallback observations.

### Items and Equipment

Supported item types are:

```text
weapon, armor, accessory, consumable, spellbook,
utility, misc, material, quest, key
```

- Weapons, armor, and accessories can require a player level.
- Players may equip one weapon, one armor item, and up to three accessories.
- Key items appear on the key ring rather than in standard inventory.
- Utility and misc items can power room interactions.
- Spellbooks teach unique spells when used.
- Recipes are unlocked through vendors or quest rewards.
- Equipment can modify attack, defense, HP, and MP.
- Consumables can restore resources, cure poison, recharge magic, or grant temporary buffs.

Magical items use `magical="true"` for three default charges or `charges="N"` for a custom amount. Charged armor loses uses when hit; charged tools lose uses when they successfully power an interaction. Depleted equipment can define reduced stats until recharged.

### Combat and Progression

- Player level requirements control equipment progression.
- Experience required for the next level increases by 50 points per level.
- Attacks and offensive spells use hit/miss rolls.
- Enemies scale with player level.
- Respawning enemies use a 1-in-6 room re-entry roll.
- Non-respawning enemies are treated as bosses, receive stronger scaling, and heal fully if they defeat the player.
- Configured bosses pause on first encounter for fight, story-flag bypass, quest-item control, or risky delay choices.
- Enemies can poison players or prevent their next offensive action.
- Rooms can select one or more enemies from weighted environment pools.

Boss confrontations are defined on a non-respawning enemy. Fight is always option 1;
the other fixed options appear when their XML blocks are present:

```xml
<enemy id="thorn_matriarch" name="Thorn Matriarch"
       level="6" hp="72" attack="20" defense="8"
       exp_reward="180" gold_reward="50" respawns="false">
  <boss_encounter>
    <intro>The guardian pauses long enough for you to choose an approach.</intro>
    <fight label="Stand and fight">You draw your weapon.</fight>
    <bypass label="Invoke the restored oath"
            required_flags="oath_read,shrine_restored">
      The guardian accepts the repaired covenant and withdraws.
    </bypass>
    <control label="Raise the binding relic"
             required_item="binding_relic" consume_item="true">
      The relic bends the guardian to your command.
    </control>
    <delay label="Collapse the pursuit route"
           chance="50" set_flag="guardian_delayed">
      <success_text>You escape with the guardian's loot, but not its forgiveness.</success_text>
      <failure_text>The trap fails. Standard combat begins.</failure_text>
    </delay>
  </boss_encounter>
</enemy>
```

Use `boss <1-4>` or `boss fight|bypass|control|delay`. Bypass and control
remove the boss without combat rewards. Successful delay guarantees the boss's
configured item drops, grants no boss gold or experience, and sets its story
flag; a failed delay enters standard combat. Resolved alternatives satisfy
quests that target that enemy.

A delay flag can trigger a one-time future challenge when the player enters a
later room:

```xml
<flag_enemies>
  <enemy_ref id="thorn_debt_stalker"
             required_flag="guardian_delayed" count="1" />
</flag_enemies>
```

Flag-triggered enemies must use `respawns="false"`. Once defeated, they do not
appear again.

### NPCs, Companions, and Stealth

NPCs may offer a single quest, an ordered quest chain, or three cycling idle dialogue lines.

Recruitable companions:

- Use a world-defined player class
- Receive that class's starter equipment and spells
- Scale with the player
- Attack and cast spells in combat
- Can equip player-owned weapons and armor
- Can learn purchased spells and receive consumables
- Can require a story item before recruitment
- Return to their original room when dismissed

The party limit is two companions.

Rogue-capable characters and rogue companions can pickpocket specific NPC/vendor items and lockpick configured room objects. Failed pickpocketing sends the player to the world's jail. Three failed attempts against the same lock break one set of lockpicks.

### Quests, Factions, and Endings

Quests can:

- Target an enemy, required item, or destination room
- Give an item when accepted
- Reward currencies, experience, items, or recipes
- Use unique offer, active, and completed dialogue
- Branch completion text and rewards based on a story flag
- Belong to an ordered NPC quest chain
- Commit the player to a faction after explicit confirmation

Fetch quests complete when the player returns to the quest giver. Faction commitment blocks quests from competing factions and can trigger faction-specific enemies.

Ending quests replace the old requirement for an end room. They can provide default text, faction-specific text, and up to ten player-selected endings. Ending choices may be hidden behind required story flags.

### Vendors and Currencies

Worlds may define multiple currencies. Vendors choose accepted currencies and may price individual items, recipes, or spells in different currencies. Exchange vendors define explicit conversion rates.

Vendors can sell:

- Items and spellbooks
- Unlockable crafting recipes
- Directly learned spells
- Spells or spellbooks for recruited companions

## Validation and Reference

World loading fails early when content contains invalid references or incompatible settings, including unknown rooms, items, spells, enemies, quests, factions, currencies, recipes, or class IDs.

For complete, working XML examples, use the Emerald Keep files:

- [World metadata and classes](worlds/emerald_keep/world.xml)
- [Items and recipes](worlds/emerald_keep/items.xml)
- [Spells](worlds/emerald_keep/spells.xml)
- [Enemies and monster pools](worlds/emerald_keep/enemies.xml)
- [NPCs and companions](worlds/emerald_keep/npcs.xml)
- [Vendors and currencies](worlds/emerald_keep/vendors.xml)
- [Quests and endings](worlds/emerald_keep/quests.xml)
- [Rooms and interactions](worlds/emerald_keep/rooms.xml)
