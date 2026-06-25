# Aurelian Marches Path Map

Generated from `worlds/aurelian_marches/rooms.xml`. This map lists authored room movement, including normal exits, hidden exits, conditional flags, locked destination rooms, maze rooms, storage, and rest rooms.

## Legend

- `north/east/south/west/up/down/in/out` are movement commands.
- `hidden` exits are not shown by the engine until their required flag is set.
- `target requires item` means the destination room has a room-level key/item requirement.
- `maze` notes show the required movement sequence and success room for maze-style rooms.
- Cross-zone exits are shown with the target zone in parentheses.

## World Summary

- Rooms: `473`
- Normal exits: `1059`
- Hidden exits: `15`
- Zones: `10`

| Zone | Rooms | Normal Exits | Hidden Exits | Special Rooms |
|---|---:|---:|---:|---|
| Hearthwatch Crossing `hearthwatch_crossing` | 25 | 76 | 1 | storage |
| Greenbarrow Fields `greenbarrow_fields` | 38 | 100 | 0 | maze, storage |
| Whispering Briar `whispering_briar` | 30 | 74 | 0 | storage |
| Dawnhammer Hills `dawnhammer_hills` | 49 | 120 | 0 | storage |
| Sunken Crown Marsh `sunken_crown_marsh` | 44 | 92 | 4 | locked |
| Glasswind Expanse `glasswind_expanse` | 49 | 101 | 2 | - |
| Duskfall Coast `duskfall_coast` | 68 | 144 | 0 | locked, maze |
| Thundervale Peaks `thundervale_peaks` | 58 | 127 | 0 | storage |
| Umbralwyrm Depths `umbralwyrm_depths` | 67 | 139 | 1 | locked |
| Astral Crown Citadel `astral_crown_citadel` | 45 | 86 | 7 | sealing, storage, rest |

## Special Movement Index

### Hidden Exits

| From | Direction | To | Zone | Condition |
|---|---|---|---|---|
| Warehouse District: Ferry Landing `ferry_landing` | south | Tidebound Ferry: Hearthwatch Crossing Run `dc_hearthwatch_ferry_crossing` | Duskfall Coast | hidden; requires flag `dc_ferry_ticket_checked`; target requires item `dc_ferry_ticket` |
| Cistern Works: Upper Pump House `sc_keep_cistern_works` | down | Upper Drain Spillway `sc_vault_upper_drain` | Sunken Crown Marsh | hidden; requires flag `sc_upper_vault_drained` |
| Sunken Vaults: Floodline Anteroom `sc_vault_anteroom` | east | Drained Armory `sc_vault_dry_armory` | Sunken Crown Marsh | hidden; requires flag `sc_upper_vault_drained` |
| Knee-Deep Gallery `sc_vault_knee_deep_gallery` | east | Pumped-Out Prison Cells `sc_vault_flooded_cells` | Sunken Crown Marsh | hidden; requires flag `sc_upper_vault_drained` |
| Crown Mosaic Hall `sc_vault_crown_mosaic_hall` | down | Pumped-Out Sunken Treasury `sc_vault_sunken_treasury` | Sunken Crown Marsh | hidden; requires flag `sc_lower_vault_drained` |
| Buried Titan Highway: Invisible Barrier Basin `gw_highway_barrier_basin` | in | Invisible Dungeon: Absent Threshold `gw_invisible_threshold` | Glasswind Expanse | hidden; requires flag `gw_invisible_barrier_dropped` |
| Ember Mirage Tower: Scriptorium `gw_ember_tower_scriptorium` | in | Ember Mirage Tower: Hidden Spell Cache `gw_ember_spell_cache` | Glasswind Expanse | hidden; requires flag `gw_ember_spell_cache_opened` |
| The Last Breath Before Stars `um_last_breath_before_stars` | north | Citadel Threshold of Falling Seals `ac_threshold_falling_seals` | Astral Crown Citadel | hidden; requires flag `astral_crown_gate_opened` |
| Seal Gate of Survival `ac_seal_gate_survival` | north | The Concordance Halls `ac_concordance_halls` | Astral Crown Citadel | hidden; requires flag `ac_survival_gate_opened` |
| Seal Gate of Survival `ac_seal_gate_survival` | east | Survival Seal Cache `ac_survival_cache` | Astral Crown Citadel | hidden; requires flag `ac_survival_gate_opened` |
| Seal Gate of Memory `ac_seal_gate_memory` | north | Starless Reliquary Entry `ac_starless_reliquary_entry` | Astral Crown Citadel | hidden; requires flag `ac_memory_gate_opened` |
| Seal Gate of Memory `ac_seal_gate_memory` | east | Memory Seal Cache `ac_memory_cache` | Astral Crown Citadel | hidden; requires flag `ac_memory_gate_opened` |
| Seal Gate of Direction `ac_seal_gate_direction` | north | The Lich’s Processional `ac_lich_processional` | Astral Crown Citadel | hidden; requires flag `ac_direction_gate_opened` |
| Seal Gate of Direction `ac_seal_gate_direction` | west | Reliquary of Wrong Horizons `ac_reliquary_wrong_horizons` | Astral Crown Citadel | hidden; requires flag `ac_direction_gate_opened` |
| Black-Star Door `ac_black_star_door` | north | Throne Antechamber `ac_throne_antechamber` | Astral Crown Citadel | hidden; requires flag `ac_black_star_door_opened` |

### Conditional Normal Exits

| From | Direction | To | Zone | Condition |
|---|---|---|---|---|
| Stormlift Base `tv_stormlift_base` | up | Upper Stormlift Landing `tv_upper_stormlift_landing` | Thundervale Peaks | requires flag `tv_stormlift_awakened` |

### Locked Destination Rooms

| Room | Zone | Required Item |
|---|---|---|
| Hawga Daar Heartwalk `hawga_daar_heartwalk` | Sunken Crown Marsh | `hawga_daar_oath_scale` |
| Tidebound Ferry: Hearthwatch Crossing Run `dc_hearthwatch_ferry_crossing` | Duskfall Coast | `dc_ferry_ticket` |
| The Blackfall Descent `um_blackfall_descent` | Umbralwyrm Depths | `thundervale_peaks_relic` |
| Glowcap Commons Entry `um_glowcap_commons_entrance` | Umbralwyrm Depths | `um_glowcap_safe_lantern` |
| Sun-Mote Outer Cache `um_sunmote_outer_cache` | Umbralwyrm Depths | `um_wyrmglass_lens` |
| Ossuary Sun-Mote Chamber `um_sunmote_chamber` | Umbralwyrm Depths | `um_wyrmglass_lens` |

### Maze Rooms

| Room | Zone | Sequence | Success Room |
|---|---|---|---|
| Dire Burrows: Grave-Loam Maze `dire_burrows_grave_loam_maze` | Greenbarrow Fields | `east,north,west,north` | Dire Burrows: First Seed Cache `dire_burrows_seed_cache` |
| The Buried Labyrinth: Saltblind Maze `dc_saltblind_maze` | Duskfall Coast | `north,west,north,east,south` | Threshold of the Worthy Tide `dc_labyrinth_worthy_threshold` |

### Cross-Zone Connections

| From | Direction | To | Zone | Condition |
|---|---|---|---|---|
| Warehouse District: Ferry Landing `ferry_landing` | north | Greenbarrow Road: Applebough Mile `greenbarrow_road` | Greenbarrow Fields | - |
| Greenbarrow Road: Applebough Mile `greenbarrow_road` | south | Warehouse District: Ferry Landing `ferry_landing` | Hearthwatch Crossing | - |
| North Stile Beyond the Barrows `greenbarrow_north_stile` | north | Root-Toll Hollow `whispering_briar_crossroads` | Whispering Briar | - |
| Root-Toll Hollow `whispering_briar_crossroads` | south | North Stile Beyond the Barrows `greenbarrow_north_stile` | Greenbarrow Fields | - |
| Grotto: Pool of All Stolen Names `wb_oracle_boss_chamber` | north | Dawnhammer Roadhead `dawnhammer_hills_crossroads` | Dawnhammer Hills | - |
| Dawnhammer Roadhead `dawnhammer_hills_crossroads` | south | Grotto: Pool of All Stolen Names `wb_oracle_boss_chamber` | Whispering Briar | - |
| The Quiet Tunnels: Blackvein Command Vault `dawnhammer_hills_boss_chamber` | north | Sunken Crown Marsh: Blackwater Approach `sunken_crown_marsh_crossroads` | Sunken Crown Marsh | - |
| Sunken Crown Marsh: Blackwater Approach `sunken_crown_marsh_crossroads` | south | The Quiet Tunnels: Blackvein Command Vault `dawnhammer_hills_boss_chamber` | Dawnhammer Hills | - |
| The Sunken Vaults: Drowned Oathhall `sunken_crown_marsh_boss_chamber` | north | Buried Titan Highway: Marshward Gate `glasswind_expanse_crossroads` | Glasswind Expanse | - |
| Buried Titan Highway: Marshward Gate `glasswind_expanse_crossroads` | south | The Sunken Vaults: Drowned Oathhall `sunken_crown_marsh_boss_chamber` | Sunken Crown Marsh | - |
| Buried Titan Highway: Eastern Arch of Blue Veils `gw_highway_eastern_arch` | north | Duskfall Coast: Saltflat Border Road `dc_saltflat_border_road` | Duskfall Coast | - |
| Invisible Dungeon: Glass Wyrm’s Crucible `glasswind_expanse_boss_chamber` | north | Duskfall Coast: Saltflat Border Road `dc_saltflat_border_road` | Duskfall Coast | - |
| Duskfall Coast: Saltflat Border Road `dc_saltflat_border_road` | south | Buried Titan Highway: Eastern Arch of Blue Veils `gw_highway_eastern_arch` | Glasswind Expanse | - |
| Tidebound Ferry: Hearthwatch Crossing Run `dc_hearthwatch_ferry_crossing` | north | Warehouse District: Ferry Landing `ferry_landing` | Hearthwatch Crossing | - |
| Duskfall North Cliff Road `dc_north_cliff_road` | north | Stormbreak Foothills `thundervale_peaks_crossroads` | Thundervale Peaks | - |
| Stormbreak Foothills `thundervale_peaks_crossroads` | south | Duskfall North Cliff Road `dc_north_cliff_road` | Duskfall Coast | - |
| Thunderheart Aegis Chamber `tv_thunderheart_aegis_chamber` | north | The Blackfall Descent `um_blackfall_descent` | Umbralwyrm Depths | target requires item `thundervale_peaks_relic` |
| The Blackfall Descent `um_blackfall_descent` | south | Thunderheart Aegis Chamber `tv_thunderheart_aegis_chamber` | Thundervale Peaks | - |
| Citadel Threshold of Falling Seals `ac_threshold_falling_seals` | south | The Last Breath Before Stars `um_last_breath_before_stars` | Umbralwyrm Depths | - |
| Warehouse District: Ferry Landing `ferry_landing` | south | Tidebound Ferry: Hearthwatch Crossing Run `dc_hearthwatch_ferry_crossing` | Duskfall Coast | hidden; requires flag `dc_ferry_ticket_checked`; target requires item `dc_ferry_ticket` |
| The Last Breath Before Stars `um_last_breath_before_stars` | north | Citadel Threshold of Falling Seals `ac_threshold_falling_seals` | Astral Crown Citadel | hidden; requires flag `astral_crown_gate_opened` |

## Hearthwatch Crossing

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| Hearthwatch Keep Courtyard `hearthwatch_square` | 1 | central_keep | **north** -> Noble District: Aurelian Terrace `hearthwatch_noble_terrace`<br>**east** -> Market District: Lantern Arcade `market_arcade`<br>**west** -> Warehouse District: River Gate `river_gate`<br>**south** -> Residential District: Hearth Commons `hearthwatch_residential_common`<br>**up** -> Arcane District: Concordium Lanternhouse `concordium_lanternhouse`<br>**out** -> Temple District: Row of Six Lamps `temple_row`<br>**in** -> Keep Council Hall `keep_council_hall`<br>**down** -> Hearthwatch Keep Lockup `hearthwatch_lockup` | - | - |
| Keep Council Hall `keep_council_hall` | 1 | central_keep | **out** -> Hearthwatch Keep Courtyard `hearthwatch_square`<br>**east** -> Keep Muster Yard `keep_muster_yard`<br>**south** -> Noble District: Council Garden `council_garden` | - | - |
| Keep Muster Yard `keep_muster_yard` | 1 | central_keep | **west** -> Keep Council Hall `keep_council_hall`<br>**out** -> Hearthwatch Keep Courtyard `hearthwatch_square`<br>**down** -> Residential District: Hearth Commons `hearthwatch_residential_common` | - | storage |
| Hearthwatch Keep Lockup `hearthwatch_lockup` | 1 | central_keep | **up** -> Hearthwatch Keep Courtyard `hearthwatch_square`<br>**west** -> Warehouse District: Customs Vault `customs_vault` | - | - |
| Residential District: Hearth Commons `hearthwatch_residential_common` | 1 | residential | **north** -> Hearthwatch Keep Courtyard `hearthwatch_square`<br>**east** -> Residential District: Bellfounder Lane `bellfounder_lane`<br>**west** -> Temple District: Mercy Cloister `mercy_cloister`<br>**up** -> Keep Muster Yard `keep_muster_yard`<br>**in** -> Bronze Bell Inn `bronze_bell_inn` | - | - |
| Residential District: Bellfounder Lane `bellfounder_lane` | 1 | residential | **west** -> Residential District: Hearth Commons `hearthwatch_residential_common`<br>**north** -> Market District: Lantern Arcade `market_arcade` | - | - |
| Bronze Bell Inn `bronze_bell_inn` | 1 | residential | **out** -> Residential District: Hearth Commons `hearthwatch_residential_common`<br>**up** -> Bronze Bell Guest Rooms `inn_rooms`<br>**east** -> Market District: Lantern Arcade `market_arcade` | - | - |
| Bronze Bell Guest Rooms `inn_rooms` | 1 | residential | **down** -> Bronze Bell Inn `bronze_bell_inn` | - | - |
| Noble District: Aurelian Terrace `hearthwatch_noble_terrace` | 1 | noble | **south** -> Hearthwatch Keep Courtyard `hearthwatch_square`<br>**east** -> Noble District: Council Garden `council_garden`<br>**west** -> Market District: Guildhall of Measures `guildhall_of_measures`<br>**in** -> Noble District: Auric House Parlor `auric_house_parlor` | - | - |
| Noble District: Auric House Parlor `auric_house_parlor` | 1 | noble | **out** -> Noble District: Aurelian Terrace `hearthwatch_noble_terrace` | - | - |
| Noble District: Council Garden `council_garden` | 1 | noble | **west** -> Noble District: Aurelian Terrace `hearthwatch_noble_terrace`<br>**north** -> Keep Council Hall `keep_council_hall`<br>**east** -> Arcane District: Concordium Lanternhouse `concordium_lanternhouse` | - | - |
| Market District: Lantern Arcade `market_arcade` | 1 | market | **west** -> Hearthwatch Keep Courtyard `hearthwatch_square`<br>**south** -> Residential District: Bellfounder Lane `bellfounder_lane`<br>**north** -> Market District: Guildhall of Measures `guildhall_of_measures`<br>**east** -> Market District: Adventurers Exchange `adventurers_exchange`<br>**in** -> Bronze Bell Inn `bronze_bell_inn` | - | - |
| Market District: Guildhall of Measures `guildhall_of_measures` | 1 | market | **south** -> Market District: Lantern Arcade `market_arcade`<br>**east** -> Noble District: Aurelian Terrace `hearthwatch_noble_terrace`<br>**west** -> Warehouse District: River Gate `river_gate` | - | - |
| Market District: Adventurers Exchange `adventurers_exchange` | 1 | market | **west** -> Market District: Lantern Arcade `market_arcade`<br>**north** -> Arcane District: Spellwright Lane `spellwright_lane` | - | storage |
| Warehouse District: River Gate `river_gate` | 1 | warehouse | **east** -> Hearthwatch Keep Courtyard `hearthwatch_square`<br>**west** -> Warehouse District: Lantern Quay `warehouse_quay`<br>**north** -> Market District: Guildhall of Measures `guildhall_of_measures`<br>**down** -> Warehouse District: Customs Vault `customs_vault` | - | - |
| Warehouse District: Lantern Quay `warehouse_quay` | 1 | warehouse | **east** -> Warehouse District: River Gate `river_gate`<br>**west** -> Warehouse District: Ferry Landing `ferry_landing`<br>**in** -> Warehouse District: Customs Vault `customs_vault` | - | - |
| Warehouse District: Customs Vault `customs_vault` | 1 | warehouse | **up** -> Warehouse District: River Gate `river_gate`<br>**out** -> Warehouse District: Lantern Quay `warehouse_quay`<br>**east** -> Hearthwatch Keep Lockup `hearthwatch_lockup` | - | - |
| Warehouse District: Ferry Landing `ferry_landing` | 1 | warehouse | **east** -> Warehouse District: Lantern Quay `warehouse_quay`<br>**north** -> Greenbarrow Road: Applebough Mile `greenbarrow_road` (Greenbarrow Fields) | **south** -> Tidebound Ferry: Hearthwatch Crossing Run `dc_hearthwatch_ferry_crossing` (Duskfall Coast) [flag `dc_ferry_ticket_checked`, hidden] | - |
| Temple District: Row of Six Lamps `temple_row` | 1 | temple | **in** -> Hearthwatch Keep Courtyard `hearthwatch_square`<br>**south** -> Temple District: Mercy Cloister `mercy_cloister`<br>**east** -> Temple District: Oath Brazier Sanctum `oath_brazier_sanctum`<br>**north** -> Arcane District: Concordium Lanternhouse `concordium_lanternhouse` | - | - |
| Temple District: Mercy Cloister `mercy_cloister` | 1 | temple | **north** -> Temple District: Row of Six Lamps `temple_row`<br>**east** -> Residential District: Hearth Commons `hearthwatch_residential_common` | - | - |
| Temple District: Oath Brazier Sanctum `oath_brazier_sanctum` | 1 | temple | **west** -> Temple District: Row of Six Lamps `temple_row`<br>**north** -> Arcane District: Starfall Observatory `starfall_observatory` | - | - |
| Arcane District: Concordium Lanternhouse `concordium_lanternhouse` | 1 | arcane | **out** -> Hearthwatch Keep Courtyard `hearthwatch_square`<br>**south** -> Temple District: Row of Six Lamps `temple_row`<br>**west** -> Noble District: Council Garden `council_garden`<br>**east** -> Arcane District: Spellwright Lane `spellwright_lane`<br>**up** -> Arcane District: Starfall Observatory `starfall_observatory`<br>**down** -> Arcane District: Subterranean Glyph Archive `glyph_archive` | - | - |
| Arcane District: Spellwright Lane `spellwright_lane` | 1 | arcane | **west** -> Arcane District: Concordium Lanternhouse `concordium_lanternhouse`<br>**south** -> Market District: Adventurers Exchange `adventurers_exchange` | - | - |
| Arcane District: Subterranean Glyph Archive `glyph_archive` | 1 | arcane | **up** -> Arcane District: Concordium Lanternhouse `concordium_lanternhouse` | - | - |
| Arcane District: Starfall Observatory `starfall_observatory` | 1 | arcane | **down** -> Arcane District: Concordium Lanternhouse `concordium_lanternhouse`<br>**south** -> Temple District: Oath Brazier Sanctum `oath_brazier_sanctum` | - | - |

## Greenbarrow Fields

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| Greenbarrow Road: Applebough Mile `greenbarrow_road` | 2-5 | - | **south** -> Warehouse District: Ferry Landing `ferry_landing` (Hearthwatch Crossing)<br>**north** -> Applewallow South Stile `applewallow_south_stile`<br>**east** -> Roadside Lantern Furrow `greenbarrow_roadside_lanterns`<br>**west** -> Wayside Shrine of the Full Bowl `greenbarrow_wayside_shrine` | - | - |
| Roadside Lantern Furrow `greenbarrow_roadside_lanterns` | 2-5 | - | **west** -> Greenbarrow Road: Applebough Mile `greenbarrow_road`<br>**north** -> Scarecrow Furrows `greenbarrow_scarecrow_furrows` | - | - |
| Wayside Shrine of the Full Bowl `greenbarrow_wayside_shrine` | 2-5 | - | **east** -> Greenbarrow Road: Applebough Mile `greenbarrow_road`<br>**north** -> Clover-Barrow Rise `greenbarrow_south_barrows` | - | - |
| Applewallow South Stile `applewallow_south_stile` | 2-5 | - | **south** -> Greenbarrow Road: Applebough Mile `greenbarrow_road`<br>**north** -> Applewallow Village Green `greenbarrow_fields_settlement`<br>**east** -> Cloverdown Sheepfolds `greenbarrow_sheepfolds`<br>**west** -> Applebough Orchards `greenbarrow_apple_orchards` | - | - |
| Applewallow Village Green `greenbarrow_fields_settlement` | 2-5 | - | **south** -> Applewallow South Stile `applewallow_south_stile`<br>**north** -> Applewallow Moot Hall `applewallow_moot_hall`<br>**east** -> Cider Market and Tinker Stalls `applewallow_cider_market`<br>**west** -> Applewallow Common Kitchen `applewallow_common_kitchen`<br>**in** -> Burrowhome Lanes `applewallow_burrowhomes`<br>**out** -> Freehold Grain Co-op `applewallow_grain_coop`<br>**up** -> Harvest Chapel of Yondalla’s Table `applewallow_harvest_chapel`<br>**down** -> Freehold Militia Post `barrow_freehold_militia_post` | - | storage |
| Applewallow Common Kitchen `applewallow_common_kitchen` | 2-5 | - | **east** -> Applewallow Village Green `greenbarrow_fields_settlement`<br>**west** -> Common Root Cellars `applewallow_root_cellars` | - | - |
| Common Root Cellars `applewallow_root_cellars` | 2-5 | - | **east** -> Applewallow Common Kitchen `applewallow_common_kitchen`<br>**down** -> Dire Burrows: Stolen Root Cellar `dire_burrows_root_cellar` | - | - |
| Cider Market and Tinker Stalls `applewallow_cider_market` | 2-5 | - | **west** -> Applewallow Village Green `greenbarrow_fields_settlement`<br>**east** -> Honeybell Bee-Yards `applewallow_bee_yards`<br>**north** -> Miller Stream and Waterwheel `applewallow_miller_stream` | - | - |
| Honeybell Bee-Yards `applewallow_bee_yards` | 2-5 | - | **west** -> Cider Market and Tinker Stalls `applewallow_cider_market`<br>**north** -> Applebough Orchards `greenbarrow_apple_orchards` | - | - |
| Harvest Chapel of Yondalla’s Table `applewallow_harvest_chapel` | 2-5 | - | **down** -> Applewallow Village Green `greenbarrow_fields_settlement`<br>**north** -> Clover-Barrow Rise `greenbarrow_south_barrows` | - | - |
| Burrowhome Lanes `applewallow_burrowhomes` | 2-5 | - | **out** -> Applewallow Village Green `greenbarrow_fields_settlement`<br>**down** -> Common Root Cellars `applewallow_root_cellars` | - | - |
| Freehold Grain Co-op `applewallow_grain_coop` | 2-5 | - | **in** -> Applewallow Village Green `greenbarrow_fields_settlement`<br>**north** -> Miller Stream and Waterwheel `applewallow_miller_stream` | - | - |
| Applewallow Moot Hall `applewallow_moot_hall` | 2-5 | - | **south** -> Applewallow Village Green `greenbarrow_fields_settlement`<br>**north** -> Applebough Orchards `greenbarrow_apple_orchards`<br>**up** -> Moot Hall Loft `moot_hall_loft` | - | - |
| Moot Hall Loft `moot_hall_loft` | 2-5 | - | **down** -> Applewallow Moot Hall `applewallow_moot_hall` | - | - |
| Freehold Militia Post `barrow_freehold_militia_post` | 2-5 | - | **up** -> Applewallow Village Green `greenbarrow_fields_settlement`<br>**east** -> Cloverdown Sheepfolds `greenbarrow_sheepfolds` | - | - |
| Applebough Orchards `greenbarrow_apple_orchards` | 2-5 | - | **south** -> Applewallow Moot Hall `applewallow_moot_hall`<br>**east** -> Honeybell Bee-Yards `applewallow_bee_yards`<br>**west** -> Applewallow South Stile `applewallow_south_stile`<br>**north** -> Miller Stream and Waterwheel `applewallow_miller_stream` | - | - |
| Cloverdown Sheepfolds `greenbarrow_sheepfolds` | 2-5 | - | **west** -> Freehold Militia Post `barrow_freehold_militia_post`<br>**south** -> Applewallow South Stile `applewallow_south_stile`<br>**north** -> North Furrows and Badger Runs `greenbarrow_fields_wilds` | - | - |
| Miller Stream and Waterwheel `applewallow_miller_stream` | 2-5 | - | **south** -> Applebough Orchards `greenbarrow_apple_orchards`<br>**west** -> Freehold Grain Co-op `applewallow_grain_coop`<br>**east** -> Cider Market and Tinker Stalls `applewallow_cider_market`<br>**north** -> North Furrows and Badger Runs `greenbarrow_fields_wilds` | - | - |
| Clover-Barrow Rise `greenbarrow_south_barrows` | 2-5 | - | **south** -> Harvest Chapel of Yondalla’s Table `applewallow_harvest_chapel`<br>**east** -> Scarecrow Furrows `greenbarrow_scarecrow_furrows`<br>**west** -> Wayside Shrine of the Full Bowl `greenbarrow_wayside_shrine`<br>**down** -> Ancestor Crypt of Shared Loaves `greenbarrow_barrows_crypt` | - | - |
| Ancestor Crypt of Shared Loaves `greenbarrow_barrows_crypt` | 2-5 | - | **up** -> Clover-Barrow Rise `greenbarrow_south_barrows` | - | - |
| Scarecrow Furrows `greenbarrow_scarecrow_furrows` | 2-5 | - | **west** -> Clover-Barrow Rise `greenbarrow_south_barrows`<br>**south** -> Roadside Lantern Furrow `greenbarrow_roadside_lanterns`<br>**north** -> North Furrows and Badger Runs `greenbarrow_fields_wilds` | - | - |
| North Furrows and Badger Runs `greenbarrow_fields_wilds` | 2-5 | - | **south** -> Miller Stream and Waterwheel `applewallow_miller_stream`<br>**east** -> Scarecrow Furrows `greenbarrow_scarecrow_furrows`<br>**west** -> Cloverdown Sheepfolds `greenbarrow_sheepfolds`<br>**north** -> Old Willow Crossing `greenbarrow_old_willow_crossing` | - | - |
| Old Willow Crossing `greenbarrow_old_willow_crossing` | 2-5 | - | **south** -> North Furrows and Badger Runs `greenbarrow_fields_wilds`<br>**north** -> The Dire Burrows Mouth `greenbarrow_fields_dungeon_gate`<br>**east** -> Tenant Copse `tenant_copse`<br>**west** -> Elder Barrow Marker `elder_barrow_marker` | - | - |
| Tenant Copse `tenant_copse` | 2-5 | - | **west** -> Old Willow Crossing `greenbarrow_old_willow_crossing` | - | - |
| Elder Barrow Marker `elder_barrow_marker` | 2-5 | - | **east** -> Old Willow Crossing `greenbarrow_old_willow_crossing` | - | - |
| The Dire Burrows Mouth `greenbarrow_fields_dungeon_gate` | 2-5 | - | **south** -> Old Willow Crossing `greenbarrow_old_willow_crossing`<br>**in** -> Dire Burrows: Lantern Ledge `greenbarrow_fields_dungeon_depths` | - | - |
| Dire Burrows: Lantern Ledge `greenbarrow_fields_dungeon_depths` | 2-5 | - | **out** -> The Dire Burrows Mouth `greenbarrow_fields_dungeon_gate`<br>**north** -> Dire Burrows: Three-Tine Fork `dire_burrows_fork`<br>**east** -> Dire Burrows: Mushroom Run `dire_burrows_mushroom_run`<br>**down** -> Dire Burrows: Chittering Nest `dire_burrows_chittering_nest` | - | - |
| Dire Burrows: Mushroom Run `dire_burrows_mushroom_run` | 2-5 | - | **west** -> Dire Burrows: Lantern Ledge `greenbarrow_fields_dungeon_depths`<br>**north** -> Dire Burrows: Stolen Root Cellar `dire_burrows_root_cellar` | - | - |
| Dire Burrows: Chittering Nest `dire_burrows_chittering_nest` | 2-5 | - | **up** -> Dire Burrows: Lantern Ledge `greenbarrow_fields_dungeon_depths`<br>**north** -> Dire Burrows: Bone Pantry `dire_burrows_bone_pantry` | - | - |
| Dire Burrows: Three-Tine Fork `dire_burrows_fork` | 2-5 | - | **south** -> Dire Burrows: Lantern Ledge `greenbarrow_fields_dungeon_depths`<br>**east** -> Dire Burrows: Stolen Root Cellar `dire_burrows_root_cellar`<br>**west** -> Dire Burrows: Bone Pantry `dire_burrows_bone_pantry`<br>**north** -> Dire Burrows: Grave-Loam Maze `dire_burrows_grave_loam_maze` | - | - |
| Dire Burrows: Stolen Root Cellar `dire_burrows_root_cellar` | 2-5 | - | **west** -> Dire Burrows: Three-Tine Fork `dire_burrows_fork`<br>**south** -> Dire Burrows: Mushroom Run `dire_burrows_mushroom_run` | - | - |
| Dire Burrows: Bone Pantry `dire_burrows_bone_pantry` | 2-5 | - | **east** -> Dire Burrows: Three-Tine Fork `dire_burrows_fork`<br>**south** -> Dire Burrows: Chittering Nest `dire_burrows_chittering_nest`<br>**north** -> Dire Burrows: Grave-Loam Maze `dire_burrows_grave_loam_maze` | - | - |
| Dire Burrows: Grave-Loam Maze `dire_burrows_grave_loam_maze` | 2-5 | - | **south** -> Dire Burrows: Bone Pantry `dire_burrows_bone_pantry` | - | maze `east,north,west,north` -> `dire_burrows_seed_cache` |
| Dire Burrows: First Seed Cache `dire_burrows_seed_cache` | 2-5 | - | **west** -> Dire Burrows: Grave-Loam Maze `dire_burrows_grave_loam_maze`<br>**north** -> Dire Burrows: Fallow Shrine `dire_burrows_fallow_shrine` | - | - |
| Dire Burrows: Fallow Shrine `dire_burrows_fallow_shrine` | 2-5 | - | **south** -> Dire Burrows: First Seed Cache `dire_burrows_seed_cache`<br>**north** -> Dire Burrows: Starved Hall `dire_burrows_starved_hall` | - | - |
| Dire Burrows: Starved Hall `dire_burrows_starved_hall` | 2-5 | - | **south** -> Dire Burrows: Fallow Shrine `dire_burrows_fallow_shrine`<br>**north** -> The Dire Burrows: Hoard-Throne of the Unsharing Maw `greenbarrow_fields_boss_chamber` | - | - |
| The Dire Burrows: Hoard-Throne of the Unsharing Maw `greenbarrow_fields_boss_chamber` | 2-5 | - | **south** -> Dire Burrows: Starved Hall `dire_burrows_starved_hall`<br>**north** -> North Stile Beyond the Barrows `greenbarrow_north_stile` | - | - |
| North Stile Beyond the Barrows `greenbarrow_north_stile` | 2-5 | - | **south** -> The Dire Burrows: Hoard-Throne of the Unsharing Maw `greenbarrow_fields_boss_chamber`<br>**north** -> Root-Toll Hollow `whispering_briar_crossroads` (Whispering Briar) | - | - |

## Whispering Briar

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| Root-Toll Hollow `whispering_briar_crossroads` | 5-9 | - | **south** -> North Stile Beyond the Barrows `greenbarrow_north_stile` (Greenbarrow Fields)<br>**north** -> Moonmote Causeway `wb_moonmote_causeway`<br>**east** -> Glimmerhazel Path `wb_glimmerhazel_path` | - | - |
| Glimmerhazel Path `wb_glimmerhazel_path` | 5-9 | - | **west** -> Root-Toll Hollow `whispering_briar_crossroads`<br>**north** -> Vowtree Grove `wb_vowtree_grove`<br>**east** -> Briar Mere `wb_briar_mere` | - | - |
| Moonmote Causeway `wb_moonmote_causeway` | 5-9 | - | **south** -> Root-Toll Hollow `whispering_briar_crossroads`<br>**north** -> Onfadell Living Gate `wb_living_gate`<br>**east** -> Briar Mere `wb_briar_mere` | - | - |
| Briar Mere `wb_briar_mere` | 5-9 | - | **west** -> Glimmerhazel Path `wb_glimmerhazel_path`<br>**north** -> Name-Taken Ford `wb_name_taken_ford`<br>**south** -> Moonmote Causeway `wb_moonmote_causeway` | - | - |
| Vowtree Grove `wb_vowtree_grove` | 5-9 | - | **south** -> Glimmerhazel Path `wb_glimmerhazel_path`<br>**north** -> Seat of the Thorn Court `wb_onfadell_thorn_court`<br>**east** -> Name-Taken Ford `wb_name_taken_ford` | - | - |
| Name-Taken Ford `wb_name_taken_ford` | 5-9 | - | **west** -> Vowtree Grove `wb_vowtree_grove`<br>**south** -> Briar Mere `wb_briar_mere`<br>**north** -> Grotto of the Nameless Oracle: Briar-Mouth `wb_oracle_grotto_mouth` | - | - |
| Onfadell Living Gate `wb_living_gate` | 5-9 | - | **south** -> Moonmote Causeway `wb_moonmote_causeway`<br>**north** -> Onfadell Outer Ring `wb_onfadell_outer_ring`<br>**east** -> Onfadell Briar Market `wb_onfadell_briar_market` | - | - |
| Onfadell Outer Ring `wb_onfadell_outer_ring` | 5-9 | - | **south** -> Onfadell Living Gate `wb_living_gate`<br>**north** -> Seat of the Thorn Court `wb_onfadell_thorn_court`<br>**east** -> Glassroot Residences `wb_onfadell_glassroot_residences`<br>**west** -> Verdant Archive `wb_onfadell_verdant_archive` | - | storage |
| Onfadell Briar Market `wb_onfadell_briar_market` | 5-9 | - | **west** -> Onfadell Living Gate `wb_living_gate`<br>**north** -> Glassroot Residences `wb_onfadell_glassroot_residences` | - | storage |
| Glassroot Residences `wb_onfadell_glassroot_residences` | 5-9 | - | **west** -> Onfadell Outer Ring `wb_onfadell_outer_ring`<br>**south** -> Onfadell Briar Market `wb_onfadell_briar_market`<br>**north** -> Seat of the Thorn Court `wb_onfadell_thorn_court` | - | - |
| Verdant Archive `wb_onfadell_verdant_archive` | 5-9 | - | **east** -> Onfadell Outer Ring `wb_onfadell_outer_ring`<br>**north** -> The Lost Orrery: Overgrown Portico `wb_lost_orrery_portico` | - | - |
| Seat of the Thorn Court `wb_onfadell_thorn_court` | 5-9 | - | **south** -> Onfadell Outer Ring `wb_onfadell_outer_ring`<br>**east** -> Glassroot Residences `wb_onfadell_glassroot_residences`<br>**west** -> Vowtree Grove `wb_vowtree_grove`<br>**north** -> Grotto of the Nameless Oracle: Briar-Mouth `wb_oracle_grotto_mouth` | - | - |
| The Lost Orrery: Overgrown Portico `wb_lost_orrery_portico` | 5-9 | - | **south** -> Verdant Archive `wb_onfadell_verdant_archive`<br>**in** -> The Lost Orrery: Axis Hall `wb_lost_orrery_axis` | - | - |
| The Lost Orrery: Axis Hall `wb_lost_orrery_axis` | 5-9 | - | **out** -> The Lost Orrery: Overgrown Portico `wb_lost_orrery_portico`<br>**north** -> The Lost Orrery: Moonstairs `wb_lost_orrery_moonstairs`<br>**east** -> The Lost Orrery: Starwell `wb_lost_orrery_starwell`<br>**down** -> The Lost Orrery: Gearvault Below `wb_lost_orrery_gearvault` | - | - |
| The Lost Orrery: Moonstairs `wb_lost_orrery_moonstairs` | 5-9 | - | **south** -> The Lost Orrery: Axis Hall `wb_lost_orrery_axis`<br>**up** -> The Lost Orrery: Broken Planetarium `wb_lost_orrery_planetarium` | - | - |
| The Lost Orrery: Starwell `wb_lost_orrery_starwell` | 5-9 | - | **west** -> The Lost Orrery: Axis Hall `wb_lost_orrery_axis` | - | - |
| The Lost Orrery: Gearvault Below `wb_lost_orrery_gearvault` | 5-9 | - | **up** -> The Lost Orrery: Axis Hall `wb_lost_orrery_axis` | - | - |
| The Lost Orrery: Broken Planetarium `wb_lost_orrery_planetarium` | 5-9 | - | **down** -> The Lost Orrery: Moonstairs `wb_lost_orrery_moonstairs` | - | - |
| Grotto of the Nameless Oracle: Briar-Mouth `wb_oracle_grotto_mouth` | 5-9 | - | **south** -> Seat of the Thorn Court `wb_onfadell_thorn_court`<br>**east** -> Name-Taken Ford `wb_name_taken_ford`<br>**in** -> Grotto: Veilpool Antechamber `wb_oracle_veilpool` | - | - |
| Grotto: Veilpool Antechamber `wb_oracle_veilpool` | 5-9 | - | **out** -> Grotto of the Nameless Oracle: Briar-Mouth `wb_oracle_grotto_mouth`<br>**north** -> Grotto: Echoing Reeds `wb_oracle_echoing_reeds`<br>**east** -> Grotto: Shelves of Unkept Memory `wb_oracle_memory_shelves` | - | - |
| Grotto: Echoing Reeds `wb_oracle_echoing_reeds` | 5-9 | - | **south** -> Grotto: Veilpool Antechamber `wb_oracle_veilpool`<br>**north** -> Grotto: Three Springs of Judgment `wb_oracle_three_springs` | - | - |
| Grotto: Shelves of Unkept Memory `wb_oracle_memory_shelves` | 5-9 | - | **west** -> Grotto: Veilpool Antechamber `wb_oracle_veilpool`<br>**north** -> Grotto: Root-Mirror Chamber `wb_oracle_root_mirror` | - | - |
| Grotto: Three Springs of Judgment `wb_oracle_three_springs` | 5-9 | - | **south** -> Grotto: Echoing Reeds `wb_oracle_echoing_reeds`<br>**west** -> Grotto: Spring of Truth `wb_oracle_spring_truth`<br>**north** -> Grotto: Spring of Grief `wb_oracle_spring_grief`<br>**east** -> Grotto: Spring of Debt `wb_oracle_spring_debt`<br>**down** -> Grotto: Unspeaking Descent `wb_oracle_unspeaking_descent` | - | - |
| Grotto: Spring of Truth `wb_oracle_spring_truth` | 5-9 | - | **east** -> Grotto: Three Springs of Judgment `wb_oracle_three_springs` | - | - |
| Grotto: Spring of Grief `wb_oracle_spring_grief` | 5-9 | - | **south** -> Grotto: Three Springs of Judgment `wb_oracle_three_springs` | - | - |
| Grotto: Spring of Debt `wb_oracle_spring_debt` | 5-9 | - | **west** -> Grotto: Three Springs of Judgment `wb_oracle_three_springs` | - | - |
| Grotto: Unspeaking Descent `wb_oracle_unspeaking_descent` | 5-9 | - | **up** -> Grotto: Three Springs of Judgment `wb_oracle_three_springs`<br>**down** -> Grotto: Root-Mirror Chamber `wb_oracle_root_mirror` | - | - |
| Grotto: Root-Mirror Chamber `wb_oracle_root_mirror` | 5-9 | - | **south** -> Grotto: Shelves of Unkept Memory `wb_oracle_memory_shelves`<br>**up** -> Grotto: Unspeaking Descent `wb_oracle_unspeaking_descent`<br>**north** -> Grotto: Chamber of the Last Name `wb_oracle_last_name_chamber` | - | - |
| Grotto: Chamber of the Last Name `wb_oracle_last_name_chamber` | 5-9 | - | **south** -> Grotto: Root-Mirror Chamber `wb_oracle_root_mirror`<br>**north** -> Grotto: Pool of All Stolen Names `wb_oracle_boss_chamber` | - | - |
| Grotto: Pool of All Stolen Names `wb_oracle_boss_chamber` | 5-9 | - | **south** -> Grotto: Chamber of the Last Name `wb_oracle_last_name_chamber`<br>**north** -> Dawnhammer Roadhead `dawnhammer_hills_crossroads` (Dawnhammer Hills) | - | - |

## Dawnhammer Hills

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| Dawnhammer Roadhead `dawnhammer_hills_crossroads` | 9-13 | - | **south** -> Grotto: Pool of All Stolen Names `wb_oracle_boss_chamber` (Whispering Briar)<br>**east** -> Sun-Iron Way: Western Cut `dh_suniron_way_west`<br>**north** -> Switchback Watch `dh_switchback_watch` | - | - |
| Switchback Watch `dh_switchback_watch` | 9-13 | - | **south** -> Dawnhammer Roadhead `dawnhammer_hills_crossroads`<br>**east** -> Red Scree Ambush Site `dh_red_scree_ambush` | - | - |
| Red Scree Ambush Site `dh_red_scree_ambush` | 9-13 | - | **west** -> Switchback Watch `dh_switchback_watch`<br>**east** -> Broken Wagon Hollow `dawnhammer_hills_wilds`<br>**in** -> Raider Hide-Scrape `dh_raider_hide_scrape` | - | - |
| Raider Hide-Scrape `dh_raider_hide_scrape` | 9-13 | - | **out** -> Red Scree Ambush Site `dh_red_scree_ambush`<br>**down** -> The Quiet Tunnels: Abandoned Mouth `dawnhammer_hills_dungeon_gate` | - | - |
| Sun-Iron Way: Western Cut `dh_suniron_way_west` | 9-13 | - | **west** -> Dawnhammer Roadhead `dawnhammer_hills_crossroads`<br>**east** -> Sun-Iron Way: Midway Stones `dh_caravan_midway`<br>**north** -> Bhon Falduhr Mine Gate `dh_bhon_falduhr_gate` | - | - |
| Bhon Falduhr Mine Gate `dh_bhon_falduhr_gate` | 9-13 | - | **south** -> Sun-Iron Way: Western Cut `dh_suniron_way_west`<br>**in** -> Bhon Falduhr Yard `dh_bhon_falduhr_yard` | - | - |
| Bhon Falduhr Yard `dh_bhon_falduhr_yard` | 9-13 | - | **out** -> Bhon Falduhr Mine Gate `dh_bhon_falduhr_gate`<br>**north** -> Bhon Falduhr Lift House `dh_bhon_falduhr_lift_house`<br>**east** -> Bhon Falduhr Assay Hall `dh_bhon_falduhr_assay_hall`<br>**west** -> Bhon Falduhr Bunkhouse `dh_bhon_falduhr_bunkhouse`<br>**south** -> Bhon Falduhr Counting Office `dh_bhon_falduhr_counting_office` | - | storage |
| Bhon Falduhr Assay Hall `dh_bhon_falduhr_assay_hall` | 9-13 | - | **west** -> Bhon Falduhr Yard `dh_bhon_falduhr_yard`<br>**down** -> Bhon Falduhr: Sun-Iron Face `dh_bhon_falduhr_suniron_face` | - | - |
| Bhon Falduhr: Sun-Iron Face `dh_bhon_falduhr_suniron_face` | 9-13 | - | **up** -> Bhon Falduhr Assay Hall `dh_bhon_falduhr_assay_hall`<br>**east** -> Bhon Falduhr: Sealed Old Gallery `dh_bhon_falduhr_old_gallery` | - | - |
| Bhon Falduhr: Sealed Old Gallery `dh_bhon_falduhr_old_gallery` | 9-13 | - | **west** -> Bhon Falduhr: Sun-Iron Face `dh_bhon_falduhr_suniron_face`<br>**down** -> Quiet Tunnels: Pump Sump `dh_qt_pump_sump` | - | - |
| Bhon Falduhr Lift House `dh_bhon_falduhr_lift_house` | 9-13 | - | **south** -> Bhon Falduhr Yard `dh_bhon_falduhr_yard`<br>**down** -> Bhon Falduhr Deep Lift `dh_bhon_falduhr_deep_lift` | - | - |
| Bhon Falduhr Deep Lift `dh_bhon_falduhr_deep_lift` | 9-13 | - | **up** -> Bhon Falduhr Lift House `dh_bhon_falduhr_lift_house`<br>**east** -> Quiet Tunnels: Foreman Station `dh_qt_foreman_station` | - | - |
| Bhon Falduhr Bunkhouse `dh_bhon_falduhr_bunkhouse` | 9-13 | - | **east** -> Bhon Falduhr Yard `dh_bhon_falduhr_yard` | - | - |
| Bhon Falduhr Counting Office `dh_bhon_falduhr_counting_office` | 9-13 | - | **north** -> Bhon Falduhr Yard `dh_bhon_falduhr_yard` | - | - |
| Sun-Iron Way: Midway Stones `dh_caravan_midway` | 9-13 | - | **west** -> Sun-Iron Way: Western Cut `dh_suniron_way_west`<br>**east** -> Sun-Iron Way: Eastern Grade `dh_suniron_way_east`<br>**south** -> Broken Wagon Hollow `dawnhammer_hills_wilds`<br>**north** -> Convoy Cookfires `dh_waystation_cookfires` | - | - |
| Convoy Cookfires `dh_waystation_cookfires` | 9-13 | - | **south** -> Sun-Iron Way: Midway Stones `dh_caravan_midway` | - | - |
| Broken Wagon Hollow `dawnhammer_hills_wilds` | 9-13 | - | **north** -> Sun-Iron Way: Midway Stones `dh_caravan_midway`<br>**west** -> Red Scree Ambush Site `dh_red_scree_ambush`<br>**in** -> The Quiet Tunnels: Abandoned Mouth `dawnhammer_hills_dungeon_gate`<br>**south** -> Abandoned Wheelwright Shack `dh_abandoned_wheelwright_shack` | - | - |
| Abandoned Wheelwright Shack `dh_abandoned_wheelwright_shack` | 9-13 | - | **north** -> Broken Wagon Hollow `dawnhammer_hills_wilds` | - | - |
| Sun-Iron Way: Eastern Grade `dh_suniron_way_east` | 9-13 | - | **west** -> Sun-Iron Way: Midway Stones `dh_caravan_midway`<br>**east** -> Vandarom West Gate `dh_vandarom_west_gate`<br>**south** -> The Quiet Tunnels: Abandoned Mouth `dawnhammer_hills_dungeon_gate` | - | - |
| Vandarom West Gate `dh_vandarom_west_gate` | 9-13 | - | **west** -> Sun-Iron Way: Eastern Grade `dh_suniron_way_east`<br>**in** -> Vandarom Guildhall `dawnhammer_hills_settlement`<br>**east** -> Vandarom Foundry Quarter `dh_vandarom_foundry_quarter` | - | - |
| Vandarom Guildhall `dawnhammer_hills_settlement` | 9-13 | - | **out** -> Vandarom West Gate `dh_vandarom_west_gate`<br>**east** -> Vandarom Foundry Quarter `dh_vandarom_foundry_quarter`<br>**north** -> Vandarom Gear Market `dh_vandarom_gear_market`<br>**south** -> Vandarom Caravan Yard `dh_vandarom_caravan_yard`<br>**up** -> Vandarom Rune Press `dh_vandarom_rune_press`<br>**west** -> The Open Anvil Taproom `dh_vandarom_taproom` | - | storage |
| Vandarom Foundry Quarter `dh_vandarom_foundry_quarter` | 9-13 | - | **west** -> Vandarom West Gate `dh_vandarom_west_gate`<br>**south** -> Vandarom Gear Market `dh_vandarom_gear_market`<br>**east** -> Vandarom Rune Press `dh_vandarom_rune_press` | - | - |
| Vandarom Gear Market `dh_vandarom_gear_market` | 9-13 | - | **south** -> Vandarom Guildhall `dawnhammer_hills_settlement`<br>**east** -> Vandarom Foundry Quarter `dh_vandarom_foundry_quarter` | - | - |
| Vandarom Caravan Yard `dh_vandarom_caravan_yard` | 9-13 | - | **north** -> Vandarom Guildhall `dawnhammer_hills_settlement`<br>**west** -> Sun-Iron Way: Eastern Grade `dh_suniron_way_east`<br>**south** -> The Quiet Tunnels: Abandoned Mouth `dawnhammer_hills_dungeon_gate` | - | - |
| Vandarom Rune Press `dh_vandarom_rune_press` | 9-13 | - | **down** -> Vandarom Guildhall `dawnhammer_hills_settlement`<br>**west** -> Vandarom Foundry Quarter `dh_vandarom_foundry_quarter` | - | - |
| The Open Anvil Taproom `dh_vandarom_taproom` | 9-13 | - | **east** -> Vandarom Guildhall `dawnhammer_hills_settlement` | - | - |
| The Quiet Tunnels: Abandoned Mouth `dawnhammer_hills_dungeon_gate` | 9-13 | - | **out** -> Broken Wagon Hollow `dawnhammer_hills_wilds`<br>**north** -> Vandarom Caravan Yard `dh_vandarom_caravan_yard`<br>**in** -> Quiet Tunnels: Foreman Station `dh_qt_foreman_station`<br>**west** -> Raider Hide-Scrape `dh_raider_hide_scrape` | - | - |
| Quiet Tunnels: Foreman Station `dh_qt_foreman_station` | 9-13 | - | **out** -> The Quiet Tunnels: Abandoned Mouth `dawnhammer_hills_dungeon_gate`<br>**north** -> Quiet Tunnels: Sunken Rail Junction `dh_qt_sunken_rail`<br>**east** -> Quiet Tunnels: Dead-End Timber Pocket `dh_qt_dead_end_timber`<br>**west** -> Quiet Tunnels: Ore Cart Spur `dh_qt_ore_cart_spur` | - | - |
| Quiet Tunnels: Dead-End Timber Pocket `dh_qt_dead_end_timber` | 9-13 | - | **west** -> Quiet Tunnels: Foreman Station `dh_qt_foreman_station` | - | - |
| Quiet Tunnels: Ore Cart Spur `dh_qt_ore_cart_spur` | 9-13 | - | **east** -> Quiet Tunnels: Foreman Station `dh_qt_foreman_station`<br>**west** -> Quiet Tunnels: False Vein Dead End `dh_qt_false_vein_dead_end`<br>**down** -> Quiet Tunnels: Pitfall Drop `dh_qt_pitfall_drop`<br>**north** -> Quiet Tunnels: Dry Powder Cache `dh_qt_powder_cache` | - | - |
| Quiet Tunnels: False Vein Dead End `dh_qt_false_vein_dead_end` | 9-13 | - | **east** -> Quiet Tunnels: Ore Cart Spur `dh_qt_ore_cart_spur` | - | - |
| Quiet Tunnels: Pitfall Drop `dh_qt_pitfall_drop` | 9-13 | - | **up** -> Quiet Tunnels: Ore Cart Spur `dh_qt_ore_cart_spur`<br>**east** -> Quiet Tunnels: Pump Sump `dh_qt_pump_sump`<br>**down** -> Quiet Tunnels: Lower Haulage `dawnhammer_hills_dungeon_depths` | - | - |
| Quiet Tunnels: Dry Powder Cache `dh_qt_powder_cache` | 9-13 | - | **south** -> Quiet Tunnels: Ore Cart Spur `dh_qt_ore_cart_spur` | - | - |
| Quiet Tunnels: Sunken Rail Junction `dh_qt_sunken_rail` | 9-13 | - | **south** -> Quiet Tunnels: Foreman Station `dh_qt_foreman_station`<br>**east** -> Quiet Tunnels: Pump Sump `dh_qt_pump_sump`<br>**north** -> Quiet Tunnels: Collapsed Barricade `dh_qt_collapsed_barricade`<br>**west** -> Quiet Tunnels: Side-Cutter Cache `dh_qt_side_cutter_cache` | - | - |
| Quiet Tunnels: Side-Cutter Cache `dh_qt_side_cutter_cache` | 9-13 | - | **east** -> Quiet Tunnels: Sunken Rail Junction `dh_qt_sunken_rail` | - | - |
| Quiet Tunnels: Pump Sump `dh_qt_pump_sump` | 9-13 | - | **west** -> Quiet Tunnels: Sunken Rail Junction `dh_qt_sunken_rail`<br>**north** -> Quiet Tunnels: Bone-Rail Tram `dh_qt_bone_rail`<br>**up** -> Bhon Falduhr: Sealed Old Gallery `dh_bhon_falduhr_old_gallery` | - | - |
| Quiet Tunnels: Collapsed Barricade `dh_qt_collapsed_barricade` | 9-13 | - | **south** -> Quiet Tunnels: Sunken Rail Junction `dh_qt_sunken_rail`<br>**east** -> Quiet Tunnels: Unfinished Chain Pens `dh_qt_enslavement_pens`<br>**north** -> Quiet Tunnels: Lower Haulage `dawnhammer_hills_dungeon_depths` | - | - |
| Quiet Tunnels: Unfinished Chain Pens `dh_qt_enslavement_pens` | 9-13 | - | **west** -> Quiet Tunnels: Collapsed Barricade `dh_qt_collapsed_barricade` | - | - |
| Quiet Tunnels: Lower Haulage `dawnhammer_hills_dungeon_depths` | 9-13 | - | **south** -> Quiet Tunnels: Collapsed Barricade `dh_qt_collapsed_barricade`<br>**west** -> Quiet Tunnels: Echo Chamber `dh_qt_echo_chamber`<br>**east** -> Quiet Tunnels: Bone-Rail Tram `dh_qt_bone_rail`<br>**north** -> Quiet Tunnels: Black Anvil Chapel `dh_qt_black_anvil_chapel`<br>**down** -> Quiet Tunnels: Lichlit Stoping `dh_qt_lichlit_stoping` | - | - |
| Quiet Tunnels: Echo Chamber `dh_qt_echo_chamber` | 9-13 | - | **east** -> Quiet Tunnels: Lower Haulage `dawnhammer_hills_dungeon_depths`<br>**north** -> Quiet Tunnels: Hidden Audit Cache `dh_qt_audit_cache`<br>**west** -> Quiet Tunnels: Blind Raise `dh_qt_blind_raise` | - | - |
| Quiet Tunnels: Hidden Audit Cache `dh_qt_audit_cache` | 9-13 | - | **south** -> Quiet Tunnels: Echo Chamber `dh_qt_echo_chamber` | - | - |
| Quiet Tunnels: Blind Raise `dh_qt_blind_raise` | 9-13 | - | **east** -> Quiet Tunnels: Echo Chamber `dh_qt_echo_chamber` | - | - |
| Quiet Tunnels: Bone-Rail Tram `dh_qt_bone_rail` | 9-13 | - | **west** -> Quiet Tunnels: Lower Haulage `dawnhammer_hills_dungeon_depths`<br>**east** -> Quiet Tunnels: Crownless Forge Plan `dh_qt_crownless_forge_plan`<br>**south** -> Quiet Tunnels: Pump Sump `dh_qt_pump_sump` | - | - |
| Quiet Tunnels: Crownless Forge Plan `dh_qt_crownless_forge_plan` | 9-13 | - | **west** -> Quiet Tunnels: Bone-Rail Tram `dh_qt_bone_rail` | - | - |
| Quiet Tunnels: Black Anvil Chapel `dh_qt_black_anvil_chapel` | 9-13 | - | **south** -> Quiet Tunnels: Lower Haulage `dawnhammer_hills_dungeon_depths`<br>**north** -> The Quiet Tunnels: Blackvein Command Vault `dawnhammer_hills_boss_chamber`<br>**east** -> Quiet Tunnels: Sun-Iron Reliquary `dh_qt_suniron_reliquary` | - | - |
| Quiet Tunnels: Sun-Iron Reliquary `dh_qt_suniron_reliquary` | 9-13 | - | **west** -> Quiet Tunnels: Black Anvil Chapel `dh_qt_black_anvil_chapel` | - | - |
| Quiet Tunnels: Lichlit Stoping `dh_qt_lichlit_stoping` | 9-13 | - | **up** -> Quiet Tunnels: Lower Haulage `dawnhammer_hills_dungeon_depths`<br>**north** -> The Quiet Tunnels: Blackvein Command Vault `dawnhammer_hills_boss_chamber`<br>**east** -> Quiet Tunnels: Collapsed Stope Dead End `dh_qt_collapsed_stope_dead_end` | - | - |
| Quiet Tunnels: Collapsed Stope Dead End `dh_qt_collapsed_stope_dead_end` | 9-13 | - | **west** -> Quiet Tunnels: Lichlit Stoping `dh_qt_lichlit_stoping` | - | - |
| The Quiet Tunnels: Blackvein Command Vault `dawnhammer_hills_boss_chamber` | 9-13 | - | **south** -> Quiet Tunnels: Black Anvil Chapel `dh_qt_black_anvil_chapel`<br>**west** -> Quiet Tunnels: Lichlit Stoping `dh_qt_lichlit_stoping`<br>**north** -> Sunken Crown Marsh: Blackwater Approach `sunken_crown_marsh_crossroads` (Sunken Crown Marsh) | - | - |

## Sunken Crown Marsh

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| Sunken Crown Marsh: Blackwater Approach `sunken_crown_marsh_crossroads` | 13-17 | - | **south** -> The Quiet Tunnels: Blackvein Command Vault `dawnhammer_hills_boss_chamber` (Dawnhammer Hills)<br>**north** -> Blackwater Causeway `sc_blackwater_causeway`<br>**east** -> Blackwater Lotus Isle `sc_bog_lotus_isle` | - | - |
| Blackwater Lotus Isle `sc_bog_lotus_isle` | 13-17 | - | **west** -> Sunken Crown Marsh: Blackwater Approach `sunken_crown_marsh_crossroads` | - | - |
| Blackwater Causeway `sc_blackwater_causeway` | 13-17 | - | **south** -> Sunken Crown Marsh: Blackwater Approach `sunken_crown_marsh_crossroads`<br>**north** -> Reed-Blind Watch `sc_reed_blind_watch`<br>**east** -> Drowned Cause-Stones `sc_drowned_cause_stones` | - | - |
| Drowned Cause-Stones `sc_drowned_cause_stones` | 13-17 | - | **west** -> Blackwater Causeway `sc_blackwater_causeway`<br>**north** -> Ghost Barge Mooring `sc_ghost_barge` | - | - |
| Ghost Barge Mooring `sc_ghost_barge` | 13-17 | - | **south** -> Drowned Cause-Stones `sc_drowned_cause_stones`<br>**in** -> Ghost Barge Hold `sc_ghost_barge_hold` | - | - |
| Ghost Barge Hold `sc_ghost_barge_hold` | 13-17 | - | **out** -> Ghost Barge Mooring `sc_ghost_barge` | - | - |
| Reed-Blind Watch `sc_reed_blind_watch` | 13-17 | - | **south** -> Blackwater Causeway `sc_blackwater_causeway`<br>**north** -> Hawga Daar Outer Palings `hawga_daar_outer_palings`<br>**west** -> Mire Hunter Camp `sc_mire_hunter_camp` | - | - |
| Mire Hunter Camp `sc_mire_hunter_camp` | 13-17 | - | **east** -> Reed-Blind Watch `sc_reed_blind_watch`<br>**north** -> Mangrove Cut `sc_mangrove_cut` | - | - |
| Mangrove Cut `sc_mangrove_cut` | 13-17 | - | **south** -> Mire Hunter Camp `sc_mire_hunter_camp`<br>**north** -> Old Keep Overlook `hawga_daar_old_keep_overlook`<br>**east** -> Trial Pool of Patient Teeth `sc_trial_pool` | - | - |
| Trial Pool of Patient Teeth `sc_trial_pool` | 13-17 | - | **west** -> Mangrove Cut `sc_mangrove_cut`<br>**south** -> Hatchling Reed-Nest `sc_hatchling_reed_nest`<br>**east** -> Blackjaw Den `sc_blackjaw_den`<br>**north** -> Hawga Daar Outer Palings `hawga_daar_outer_palings` | - | - |
| Hatchling Reed-Nest `sc_hatchling_reed_nest` | 13-17 | - | **north** -> Trial Pool of Patient Teeth `sc_trial_pool` | - | - |
| Blackjaw Den `sc_blackjaw_den` | 13-17 | - | **west** -> Trial Pool of Patient Teeth `sc_trial_pool` | - | - |
| Hawga Daar Outer Palings `hawga_daar_outer_palings` | 13-17 | - | **south** -> Reed-Blind Watch `sc_reed_blind_watch`<br>**east** -> Trial Pool of Patient Teeth `sc_trial_pool`<br>**in** -> Hawga Daar Heartwalk `hawga_daar_heartwalk` | - | - |
| Hawga Daar Heartwalk `hawga_daar_heartwalk` | 13-17 | - | **out** -> Hawga Daar Outer Palings `hawga_daar_outer_palings`<br>**north** -> Stilt-House Ring `hawga_daar_stilt_ring`<br>**south** -> Warm-Nest Broodhouse `hawga_daar_broodhouse`<br>**east** -> Sunken Plaza of the Lost King `hawga_daar_sunken_plaza`<br>**west** -> Brood-Mother’s Platform `hawga_daar_chieftain_platform` | - | requires item `hawga_daar_oath_scale` |
| Brood-Mother’s Platform `hawga_daar_chieftain_platform` | 13-17 | - | **east** -> Hawga Daar Heartwalk `hawga_daar_heartwalk` | - | - |
| Warm-Nest Broodhouse `hawga_daar_broodhouse` | 13-17 | - | **north** -> Hawga Daar Heartwalk `hawga_daar_heartwalk` | - | - |
| Stilt-House Ring `hawga_daar_stilt_ring` | 13-17 | - | **south** -> Hawga Daar Heartwalk `hawga_daar_heartwalk`<br>**east** -> Bonecarver Dock `hawga_daar_bonecarver_dock`<br>**west** -> Story Stones of Hawga Daar `hawga_daar_story_stones`<br>**north** -> Pumpwright Pier `hawga_daar_pumpwright_pier` | - | - |
| Bonecarver Dock `hawga_daar_bonecarver_dock` | 13-17 | - | **west** -> Stilt-House Ring `hawga_daar_stilt_ring` | - | - |
| Story Stones of Hawga Daar `hawga_daar_story_stones` | 13-17 | - | **east** -> Stilt-House Ring `hawga_daar_stilt_ring` | - | - |
| Pumpwright Pier `hawga_daar_pumpwright_pier` | 13-17 | - | **south** -> Stilt-House Ring `hawga_daar_stilt_ring`<br>**north** -> Old Keep Overlook `hawga_daar_old_keep_overlook` | - | - |
| Sunken Plaza of the Lost King `hawga_daar_sunken_plaza` | 13-17 | - | **west** -> Hawga Daar Heartwalk `hawga_daar_heartwalk`<br>**north** -> Ruin-Market Under Stilt Shadows `hawga_daar_ruin_market`<br>**east** -> Old Keep Overlook `hawga_daar_old_keep_overlook` | - | - |
| Ruin-Market Under Stilt Shadows `hawga_daar_ruin_market` | 13-17 | - | **south** -> Sunken Plaza of the Lost King `hawga_daar_sunken_plaza` | - | - |
| Old Keep Overlook `hawga_daar_old_keep_overlook` | 13-17 | - | **south** -> Pumpwright Pier `hawga_daar_pumpwright_pier`<br>**west** -> Sunken Plaza of the Lost King `hawga_daar_sunken_plaza`<br>**east** -> The Sunken Vaults: Drowned Sallyport `sunken_crown_marsh_dungeon_gate`<br>**north** -> Mangrove Cut `sc_mangrove_cut` | - | - |
| The Sunken Vaults: Drowned Sallyport `sunken_crown_marsh_dungeon_gate` | 13-17 | - | **west** -> Old Keep Overlook `hawga_daar_old_keep_overlook`<br>**in** -> Old Keep Courtyard `sc_keep_outer_courtyard` | - | - |
| Old Keep Courtyard `sc_keep_outer_courtyard` | 13-17 | - | **out** -> The Sunken Vaults: Drowned Sallyport `sunken_crown_marsh_dungeon_gate`<br>**north** -> Gatehouse Dead-End Cache `sc_keep_gatehouse_cache`<br>**east** -> Cracked Battlement Walk `sc_keep_cracked_battlement`<br>**west** -> Cistern Works: Upper Pump House `sc_keep_cistern_works`<br>**down** -> Sunken Vaults: Floodline Anteroom `sc_vault_anteroom` | - | - |
| Gatehouse Dead-End Cache `sc_keep_gatehouse_cache` | 13-17 | - | **south** -> Old Keep Courtyard `sc_keep_outer_courtyard` | - | - |
| Cracked Battlement Walk `sc_keep_cracked_battlement` | 13-17 | - | **west** -> Old Keep Courtyard `sc_keep_outer_courtyard` | - | - |
| Cistern Works: Upper Pump House `sc_keep_cistern_works` | 13-17 | - | **east** -> Old Keep Courtyard `sc_keep_outer_courtyard` | **down** -> Upper Drain Spillway `sc_vault_upper_drain` [flag `sc_upper_vault_drained`, hidden] | - |
| Upper Drain Spillway `sc_vault_upper_drain` | 13-17 | - | **up** -> Cistern Works: Upper Pump House `sc_keep_cistern_works`<br>**east** -> Drained Armory `sc_vault_dry_armory` | - | - |
| Sunken Vaults: Floodline Anteroom `sc_vault_anteroom` | 13-17 | - | **up** -> Old Keep Courtyard `sc_keep_outer_courtyard`<br>**west** -> Silted Records Room `sc_vault_silted_records`<br>**north** -> Knee-Deep Gallery `sc_vault_knee_deep_gallery` | **east** -> Drained Armory `sc_vault_dry_armory` [flag `sc_upper_vault_drained`, hidden] | - |
| Silted Records Room `sc_vault_silted_records` | 13-17 | - | **east** -> Sunken Vaults: Floodline Anteroom `sc_vault_anteroom` | - | - |
| Drained Armory `sc_vault_dry_armory` | 13-17 | - | **west** -> Sunken Vaults: Floodline Anteroom `sc_vault_anteroom`<br>**north** -> Upper Drain Spillway `sc_vault_upper_drain` | - | - |
| Knee-Deep Gallery `sc_vault_knee_deep_gallery` | 13-17 | - | **south** -> Sunken Vaults: Floodline Anteroom `sc_vault_anteroom`<br>**west** -> Half-Drowned Barracks `sc_vault_half_drowned_barracks`<br>**north** -> Lower Pump Chamber `sc_vault_lower_pump_chamber` | **east** -> Pumped-Out Prison Cells `sc_vault_flooded_cells` [flag `sc_upper_vault_drained`, hidden] | - |
| Half-Drowned Barracks `sc_vault_half_drowned_barracks` | 13-17 | - | **east** -> Knee-Deep Gallery `sc_vault_knee_deep_gallery`<br>**down** -> Pitfall Shaft `sc_vault_pitfall_shaft` | - | - |
| Pitfall Shaft `sc_vault_pitfall_shaft` | 13-17 | - | **up** -> Half-Drowned Barracks `sc_vault_half_drowned_barracks`<br>**down** -> Sump Dead-End Cache `sc_vault_sump_deadend` | - | - |
| Sump Dead-End Cache `sc_vault_sump_deadend` | 13-17 | - | **up** -> Pitfall Shaft `sc_vault_pitfall_shaft` | - | - |
| Pumped-Out Prison Cells `sc_vault_flooded_cells` | 13-17 | - | **west** -> Knee-Deep Gallery `sc_vault_knee_deep_gallery` | - | - |
| Lower Pump Chamber `sc_vault_lower_pump_chamber` | 13-17 | - | **south** -> Knee-Deep Gallery `sc_vault_knee_deep_gallery`<br>**north** -> Crown Mosaic Hall `sc_vault_crown_mosaic_hall` | - | - |
| Crown Mosaic Hall `sc_vault_crown_mosaic_hall` | 13-17 | - | **south** -> Lower Pump Chamber `sc_vault_lower_pump_chamber`<br>**west** -> Chain-Pulley Dead End `sc_vault_chain_pulley_deadend`<br>**east** -> Oath-Shield Grotto `sc_vault_oath_shield_grotto` | **down** -> Pumped-Out Sunken Treasury `sc_vault_sunken_treasury` [flag `sc_lower_vault_drained`, hidden] | - |
| Chain-Pulley Dead End `sc_vault_chain_pulley_deadend` | 13-17 | - | **east** -> Crown Mosaic Hall `sc_vault_crown_mosaic_hall` | - | - |
| Pumped-Out Sunken Treasury `sc_vault_sunken_treasury` | 13-17 | - | **up** -> Crown Mosaic Hall `sc_vault_crown_mosaic_hall` | - | - |
| Oath-Shield Grotto `sc_vault_oath_shield_grotto` | 13-17 | - | **west** -> Crown Mosaic Hall `sc_vault_crown_mosaic_hall`<br>**north** -> Knight-Captain’s Watch `sc_vault_knight_watch` | - | - |
| Knight-Captain’s Watch `sc_vault_knight_watch` | 13-17 | - | **south** -> Oath-Shield Grotto `sc_vault_oath_shield_grotto`<br>**east** -> The Sunken Vaults: Drowned Oathhall `sunken_crown_marsh_boss_chamber` | - | - |
| The Sunken Vaults: Drowned Oathhall `sunken_crown_marsh_boss_chamber` | 13-17 | - | **west** -> Knight-Captain’s Watch `sc_vault_knight_watch`<br>**north** -> Buried Titan Highway: Marshward Gate `glasswind_expanse_crossroads` (Glasswind Expanse) | - | - |

## Glasswind Expanse

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| Buried Titan Highway: Marshward Gate `glasswind_expanse_crossroads` | 17-22 | - | **south** -> The Sunken Vaults: Drowned Oathhall `sunken_crown_marsh_boss_chamber` (Sunken Crown Marsh)<br>**east** -> Buried Titan Highway: Stone-Rib Mile `gw_highway_stone_rib`<br>**north** -> Ajuna Camp: Starcloth Gate `gw_ajuna_camp_gate` | - | - |
| Buried Titan Highway: Stone-Rib Mile `gw_highway_stone_rib` | 17-22 | - | **west** -> Buried Titan Highway: Marshward Gate `glasswind_expanse_crossroads`<br>**east** -> Buried Titan Highway: Mirage Well `gw_highway_mirage_well`<br>**south** -> Buried Titan Finger Cache `gw_buried_titan_finger_cache` | - | - |
| Buried Titan Finger Cache `gw_buried_titan_finger_cache` | 17-22 | - | **north** -> Buried Titan Highway: Stone-Rib Mile `gw_highway_stone_rib` | - | - |
| Buried Titan Highway: Mirage Well `gw_highway_mirage_well` | 17-22 | - | **west** -> Buried Titan Highway: Stone-Rib Mile `gw_highway_stone_rib`<br>**east** -> Buried Titan Highway: Dhanor Turn `gw_highway_dhanor_turn`<br>**north** -> Azure Mirage Tower: Blue Base `gw_azure_mirage_tower_base`<br>**south** -> Saltflat Raid Site `gw_saltflat_raid_site` | - | - |
| Saltflat Raid Site `gw_saltflat_raid_site` | 17-22 | - | **north** -> Buried Titan Highway: Mirage Well `gw_highway_mirage_well`<br>**east** -> Veilglass Sink `gw_veilglass_sink` | - | - |
| Veilglass Sink `gw_veilglass_sink` | 17-22 | - | **west** -> Saltflat Raid Site `gw_saltflat_raid_site` | - | - |
| Buried Titan Highway: Dhanor Turn `gw_highway_dhanor_turn` | 17-22 | - | **west** -> Buried Titan Highway: Mirage Well `gw_highway_mirage_well`<br>**east** -> Buried Titan Highway: Titan-Spine Causeway `gw_highway_titan_spine`<br>**south** -> Dhanor Camp: Brass Yard `gw_dhanor_camp_yard`<br>**north** -> Ember Mirage Tower: Brass Base `gw_ember_mirage_tower_base` | - | - |
| Buried Titan Highway: Titan-Spine Causeway `gw_highway_titan_spine` | 17-22 | - | **west** -> Buried Titan Highway: Dhanor Turn `gw_highway_dhanor_turn`<br>**east** -> Buried Titan Highway: Shakni Turn `gw_highway_shakni_turn`<br>**south** -> Sunblistered Waystone `gw_sunblistered_waystone` | - | - |
| Sunblistered Waystone `gw_sunblistered_waystone` | 17-22 | - | **north** -> Buried Titan Highway: Titan-Spine Causeway `gw_highway_titan_spine` | - | - |
| Buried Titan Highway: Shakni Turn `gw_highway_shakni_turn` | 17-22 | - | **west** -> Buried Titan Highway: Titan-Spine Causeway `gw_highway_titan_spine`<br>**east** -> Buried Titan Highway: Invisible Barrier Basin `gw_highway_barrier_basin`<br>**north** -> Shakni Camp: Ring of White Cloth `gw_shakni_camp_ring`<br>**south** -> Ivory Mirage Tower: Silent Base `gw_ivory_mirage_tower_base` | - | - |
| Buried Titan Highway: Invisible Barrier Basin `gw_highway_barrier_basin` | 17-22 | - | **west** -> Buried Titan Highway: Shakni Turn `gw_highway_shakni_turn`<br>**east** -> Buried Titan Highway: Eastern Arch of Blue Veils `gw_highway_eastern_arch` | **in** -> Invisible Dungeon: Absent Threshold `gw_invisible_threshold` [flag `gw_invisible_barrier_dropped`, hidden] | - |
| Buried Titan Highway: Eastern Arch of Blue Veils `gw_highway_eastern_arch` | 17-22 | - | **west** -> Buried Titan Highway: Invisible Barrier Basin `gw_highway_barrier_basin`<br>**north** -> Duskfall Coast: Saltflat Border Road `dc_saltflat_border_road` (Duskfall Coast) | - | - |
| Ajuna Camp: Starcloth Gate `gw_ajuna_camp_gate` | 17-22 | - | **south** -> Buried Titan Highway: Marshward Gate `glasswind_expanse_crossroads`<br>**in** -> Ajuna Camp: Starcloth Pavilion `gw_ajuna_starcloth_pavilion`<br>**east** -> Ajuna Camp: Lens Yard `gw_ajuna_lens_yard` | - | - |
| Ajuna Camp: Starcloth Pavilion `gw_ajuna_starcloth_pavilion` | 17-22 | - | **out** -> Ajuna Camp: Starcloth Gate `gw_ajuna_camp_gate`<br>**east** -> Ajuna Camp: Guest Mat Circle `gw_ajuna_guest_mat`<br>**north** -> Ajuna Camp: Formula Scroll Wagon `gw_ajuna_scroll_wagon` | - | - |
| Ajuna Camp: Lens Yard `gw_ajuna_lens_yard` | 17-22 | - | **west** -> Ajuna Camp: Starcloth Gate `gw_ajuna_camp_gate` | - | - |
| Ajuna Camp: Guest Mat Circle `gw_ajuna_guest_mat` | 17-22 | - | **west** -> Ajuna Camp: Starcloth Pavilion `gw_ajuna_starcloth_pavilion` | - | - |
| Ajuna Camp: Formula Scroll Wagon `gw_ajuna_scroll_wagon` | 17-22 | - | **south** -> Ajuna Camp: Starcloth Pavilion `gw_ajuna_starcloth_pavilion` | - | - |
| Dhanor Camp: Brass Yard `gw_dhanor_camp_yard` | 17-22 | - | **north** -> Buried Titan Highway: Dhanor Turn `gw_highway_dhanor_turn`<br>**in** -> Dhanor Camp: Brass-Eye Workshop `gw_dhanor_brass_workshop`<br>**east** -> Dhanor Camp: Map Tent `gw_dhanor_map_tent`<br>**south** -> Dhanor Camp: Caravan Corral `gw_dhanor_caravan_corral` | - | - |
| Dhanor Camp: Brass-Eye Workshop `gw_dhanor_brass_workshop` | 17-22 | - | **out** -> Dhanor Camp: Brass Yard `gw_dhanor_camp_yard`<br>**up** -> Dhanor Camp: Blue Pot Teahouse `gw_dhanor_teahouse` | - | - |
| Dhanor Camp: Map Tent `gw_dhanor_map_tent` | 17-22 | - | **west** -> Dhanor Camp: Brass Yard `gw_dhanor_camp_yard` | - | - |
| Dhanor Camp: Caravan Corral `gw_dhanor_caravan_corral` | 17-22 | - | **north** -> Dhanor Camp: Brass Yard `gw_dhanor_camp_yard` | - | - |
| Dhanor Camp: Blue Pot Teahouse `gw_dhanor_teahouse` | 17-22 | - | **down** -> Dhanor Camp: Brass-Eye Workshop `gw_dhanor_brass_workshop` | - | - |
| Shakni Camp: Ring of White Cloth `gw_shakni_camp_ring` | 17-22 | - | **south** -> Buried Titan Highway: Shakni Turn `gw_highway_shakni_turn`<br>**in** -> Shakni Camp: Silent Library `gw_shakni_silent_library`<br>**east** -> Shakni Camp: Glassflute Tents `gw_shakni_glassflute_tents` | - | - |
| Shakni Camp: Silent Library `gw_shakni_silent_library` | 17-22 | - | **out** -> Shakni Camp: Ring of White Cloth `gw_shakni_camp_ring`<br>**north** -> Shakni Camp: Sandclock Stage `gw_shakni_sandclock_stage` | - | - |
| Shakni Camp: Glassflute Tents `gw_shakni_glassflute_tents` | 17-22 | - | **west** -> Shakni Camp: Ring of White Cloth `gw_shakni_camp_ring` | - | - |
| Shakni Camp: Sandclock Stage `gw_shakni_sandclock_stage` | 17-22 | - | **south** -> Shakni Camp: Silent Library `gw_shakni_silent_library` | - | - |
| Azure Mirage Tower: Blue Base `gw_azure_mirage_tower_base` | 17-22 | - | **south** -> Buried Titan Highway: Mirage Well `gw_highway_mirage_well`<br>**up** -> Azure Mirage Tower: Lens Stair `gw_azure_tower_lens_stair` | - | - |
| Azure Mirage Tower: Lens Stair `gw_azure_tower_lens_stair` | 17-22 | - | **down** -> Azure Mirage Tower: Blue Base `gw_azure_mirage_tower_base`<br>**up** -> Azure Mirage Tower: Mirror Deck `gw_azure_tower_mirror_deck` | - | - |
| Azure Mirage Tower: Mirror Deck `gw_azure_tower_mirror_deck` | 17-22 | - | **down** -> Azure Mirage Tower: Lens Stair `gw_azure_tower_lens_stair` | - | - |
| Ember Mirage Tower: Brass Base `gw_ember_mirage_tower_base` | 17-22 | - | **south** -> Buried Titan Highway: Dhanor Turn `gw_highway_dhanor_turn`<br>**up** -> Ember Mirage Tower: Scriptorium `gw_ember_tower_scriptorium` | - | - |
| Ember Mirage Tower: Scriptorium `gw_ember_tower_scriptorium` | 17-22 | - | **down** -> Ember Mirage Tower: Brass Base `gw_ember_mirage_tower_base`<br>**up** -> Ember Mirage Tower: Mirror Deck `gw_ember_tower_mirror_deck` | **in** -> Ember Mirage Tower: Hidden Spell Cache `gw_ember_spell_cache` [flag `gw_ember_spell_cache_opened`, hidden] | - |
| Ember Mirage Tower: Hidden Spell Cache `gw_ember_spell_cache` | 17-22 | - | **out** -> Ember Mirage Tower: Scriptorium `gw_ember_tower_scriptorium` | - | - |
| Ember Mirage Tower: Mirror Deck `gw_ember_tower_mirror_deck` | 17-22 | - | **down** -> Ember Mirage Tower: Scriptorium `gw_ember_tower_scriptorium` | - | - |
| Ivory Mirage Tower: Silent Base `gw_ivory_mirage_tower_base` | 17-22 | - | **north** -> Buried Titan Highway: Shakni Turn `gw_highway_shakni_turn`<br>**up** -> Ivory Mirage Tower: Whisper Stair `gw_ivory_tower_whisper_stair` | - | - |
| Ivory Mirage Tower: Whisper Stair `gw_ivory_tower_whisper_stair` | 17-22 | - | **down** -> Ivory Mirage Tower: Silent Base `gw_ivory_mirage_tower_base`<br>**up** -> Ivory Mirage Tower: Mirror Deck `gw_ivory_tower_mirror_deck` | - | - |
| Ivory Mirage Tower: Mirror Deck `gw_ivory_tower_mirror_deck` | 17-22 | - | **down** -> Ivory Mirage Tower: Whisper Stair `gw_ivory_tower_whisper_stair` | - | - |
| Invisible Dungeon: Absent Threshold `gw_invisible_threshold` | 17-22 | - | **out** -> Buried Titan Highway: Invisible Barrier Basin `gw_highway_barrier_basin`<br>**north** -> Invisible Dungeon: Unseen Foyer `gw_unseen_foyer` | - | - |
| Invisible Dungeon: Unseen Foyer `gw_unseen_foyer` | 17-22 | - | **south** -> Invisible Dungeon: Absent Threshold `gw_invisible_threshold`<br>**east** -> Invisible Dungeon: Absent Wall Gallery `gw_absent_wall_gallery`<br>**west** -> Invisible Dungeon: Hall of Wrong Shadows `gw_hall_of_wrong_shadows`<br>**up** -> Invisible Dungeon: Upside-Down Stairs `gw_upside_down_stairs` | - | - |
| Invisible Dungeon: Absent Wall Gallery `gw_absent_wall_gallery` | 17-22 | - | **west** -> Invisible Dungeon: Unseen Foyer `gw_unseen_foyer`<br>**north** -> Invisible Dungeon: Null-Sun Chamber `gw_null_sun_chamber` | - | - |
| Invisible Dungeon: Null-Sun Chamber `gw_null_sun_chamber` | 17-22 | - | **south** -> Invisible Dungeon: Absent Wall Gallery `gw_absent_wall_gallery`<br>**east** -> Invisible Dungeon: Whisperless Kennel `gw_whisperless_kennel`<br>**down** -> Invisible Dungeon: Prism Bath `gw_prism_bath` | - | - |
| Invisible Dungeon: Whisperless Kennel `gw_whisperless_kennel` | 17-22 | - | **west** -> Invisible Dungeon: Null-Sun Chamber `gw_null_sun_chamber` | - | - |
| Invisible Dungeon: Hall of Wrong Shadows `gw_hall_of_wrong_shadows` | 17-22 | - | **east** -> Invisible Dungeon: Unseen Foyer `gw_unseen_foyer`<br>**north** -> Invisible Dungeon: Refracted Crossing `gw_refracted_crossing`<br>**down** -> Invisible Dungeon: Prism Bath `gw_prism_bath` | - | - |
| Invisible Dungeon: Prism Bath `gw_prism_bath` | 17-22 | - | **up** -> Invisible Dungeon: Hall of Wrong Shadows `gw_hall_of_wrong_shadows`<br>**east** -> Invisible Dungeon: Null-Sun Chamber `gw_null_sun_chamber` | - | - |
| Invisible Dungeon: Refracted Crossing `gw_refracted_crossing` | 17-22 | - | **south** -> Invisible Dungeon: Hall of Wrong Shadows `gw_hall_of_wrong_shadows`<br>**east** -> Invisible Dungeon: Room of Cartographers Who Lied `gw_invisible_map_room`<br>**west** -> Invisible Dungeon: Glass-Bone Roost `gw_glass_bone_roost`<br>**north** -> Invisible Dungeon: Shed-Skin Cache `gw_wyrm_shed_cache` | - | - |
| Invisible Dungeon: Room of Cartographers Who Lied `gw_invisible_map_room` | 17-22 | - | **west** -> Invisible Dungeon: Refracted Crossing `gw_refracted_crossing` | - | - |
| Invisible Dungeon: Glass-Bone Roost `gw_glass_bone_roost` | 17-22 | - | **east** -> Invisible Dungeon: Refracted Crossing `gw_refracted_crossing`<br>**down** -> Invisible Dungeon: Glass Wyrm’s Crucible `glasswind_expanse_boss_chamber` | - | - |
| Invisible Dungeon: Shed-Skin Cache `gw_wyrm_shed_cache` | 17-22 | - | **south** -> Invisible Dungeon: Refracted Crossing `gw_refracted_crossing` | - | - |
| Invisible Dungeon: Upside-Down Stairs `gw_upside_down_stairs` | 17-22 | - | **down** -> Invisible Dungeon: Unseen Foyer `gw_unseen_foyer`<br>**north** -> Invisible Dungeon: Glass Wyrm’s Crucible `glasswind_expanse_boss_chamber` | - | - |
| Invisible Dungeon: Glass Wyrm’s Crucible `glasswind_expanse_boss_chamber` | 17-22 | - | **south** -> Invisible Dungeon: Upside-Down Stairs `gw_upside_down_stairs`<br>**up** -> Invisible Dungeon: Glass-Bone Roost `gw_glass_bone_roost`<br>**north** -> Duskfall Coast: Saltflat Border Road `dc_saltflat_border_road` (Duskfall Coast) | - | - |

## Duskfall Coast

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| Duskfall Coast: Saltflat Border Road `dc_saltflat_border_road` | 22-27 | - | **south** -> Buried Titan Highway: Eastern Arch of Blue Veils `gw_highway_eastern_arch` (Glasswind Expanse)<br>**north** -> Tidebound League Checkpoint `dc_tidebound_checkpoint`<br>**east** -> Burnt Caravan Pullout `dc_burnt_caravan_pullout` | - | - |
| Burnt Caravan Pullout `dc_burnt_caravan_pullout` | 22-27 | - | **west** -> Duskfall Coast: Saltflat Border Road `dc_saltflat_border_road` | - | - |
| Tidebound League Checkpoint `dc_tidebound_checkpoint` | 22-27 | - | **south** -> Duskfall Coast: Saltflat Border Road `dc_saltflat_border_road`<br>**north** -> Saltmarsh Boardwalk `dc_saltmarsh_boardwalk`<br>**west** -> Gullwatch Bluff `dc_gullwatch_bluff`<br>**east** -> Smuggler Reed-Ditch `dc_smuggler_reed_ditch` | - | - |
| Gullwatch Bluff `dc_gullwatch_bluff` | 22-27 | - | **east** -> Tidebound League Checkpoint `dc_tidebound_checkpoint`<br>**down** -> Smuggler’s Step Path `dc_smugglers_step_path` | - | - |
| Smuggler’s Step Path `dc_smugglers_step_path` | 22-27 | - | **up** -> Gullwatch Bluff `dc_gullwatch_bluff`<br>**east** -> Hidden Kelp Beach `dc_hidden_kelp_beach` | - | - |
| Hidden Kelp Beach `dc_hidden_kelp_beach` | 22-27 | - | **west** -> Smuggler’s Step Path `dc_smugglers_step_path` | - | - |
| Smuggler Reed-Ditch `dc_smuggler_reed_ditch` | 22-27 | - | **west** -> Tidebound League Checkpoint `dc_tidebound_checkpoint` | - | - |
| Saltmarsh Boardwalk `dc_saltmarsh_boardwalk` | 22-27 | - | **south** -> Tidebound League Checkpoint `dc_tidebound_checkpoint`<br>**north** -> Terrecester Wharf: South Gate `dc_terrecester_south_gate`<br>**east** -> Kobold Raft Reeds `dc_kobold_raft_reeds`<br>**west** -> Reefmist Shrine `dc_reefmist_shrine` | - | - |
| Kobold Raft Reeds `dc_kobold_raft_reeds` | 22-27 | - | **west** -> Saltmarsh Boardwalk `dc_saltmarsh_boardwalk` | - | - |
| Reefmist Shrine `dc_reefmist_shrine` | 22-27 | - | **east** -> Saltmarsh Boardwalk `dc_saltmarsh_boardwalk` | - | - |
| Terrecester Wharf: South Gate `dc_terrecester_south_gate` | 22-27 | - | **south** -> Saltmarsh Boardwalk `dc_saltmarsh_boardwalk`<br>**north** -> Terrecester Wharf: Harbor Market `dc_wharf_market`<br>**east** -> Tidebound Barracks `dc_tidebound_barracks`<br>**west** -> Cedar Net Yard `dc_cedar_net_yard` | - | - |
| Cedar Net Yard `dc_cedar_net_yard` | 22-27 | - | **east** -> Terrecester Wharf: South Gate `dc_terrecester_south_gate` | - | - |
| Tidebound Barracks `dc_tidebound_barracks` | 22-27 | - | **west** -> Terrecester Wharf: South Gate `dc_terrecester_south_gate`<br>**up** -> Signal Platform `dc_signal_platform`<br>**in** -> Barracks Armory `dc_barracks_armory` | - | - |
| Signal Platform `dc_signal_platform` | 22-27 | - | **down** -> Tidebound Barracks `dc_tidebound_barracks` | - | - |
| Barracks Armory `dc_barracks_armory` | 22-27 | - | **out** -> Tidebound Barracks `dc_tidebound_barracks` | - | - |
| Terrecester Wharf: Harbor Market `dc_wharf_market` | 22-27 | - | **south** -> Terrecester Wharf: South Gate `dc_terrecester_south_gate`<br>**north** -> Captain’s Green `dc_captains_green`<br>**east** -> Fishmarket Arcade `dc_fishmarket_arcade`<br>**west** -> Shipwright Lane `dc_shipwright_lane`<br>**in** -> Terrecester Ferry Ticket Office `dc_ferry_ticket_office` | - | - |
| Terrecester Ferry Ticket Office `dc_ferry_ticket_office` | 22-27 | - | **out** -> Terrecester Wharf: Harbor Market `dc_wharf_market`<br>**west** -> Terrecester Tidepier `dc_terrecester_tidepier` | - | - |
| Terrecester Tidepier `dc_terrecester_tidepier` | 22-27 | - | **east** -> Terrecester Ferry Ticket Office `dc_ferry_ticket_office`<br>**west** -> Outer Breakwater Under Bombardment `dc_outer_breakwater`<br>**north** -> Ferry Watchtower `dc_ferry_watchtower`<br>**south** -> Tidebound Ferry: Hearthwatch Crossing Run `dc_hearthwatch_ferry_crossing` | - | - |
| Ferry Watchtower `dc_ferry_watchtower` | 22-27 | - | **south** -> Terrecester Tidepier `dc_terrecester_tidepier` | - | - |
| Tidebound Ferry: Hearthwatch Crossing Run `dc_hearthwatch_ferry_crossing` | 22-27 | - | **north** -> Warehouse District: Ferry Landing `ferry_landing` (Hearthwatch Crossing)<br>**south** -> Terrecester Tidepier `dc_terrecester_tidepier` | - | requires item `dc_ferry_ticket` |
| Fishmarket Arcade `dc_fishmarket_arcade` | 22-27 | - | **west** -> Terrecester Wharf: Harbor Market `dc_wharf_market`<br>**east** -> Customs House of Salt and Scale `dc_customs_house`<br>**north** -> Kelpcook Kitchens `dc_kelpcook_kitchens` | - | - |
| Customs House of Salt and Scale `dc_customs_house` | 22-27 | - | **west** -> Fishmarket Arcade `dc_fishmarket_arcade` | - | - |
| Kelpcook Kitchens `dc_kelpcook_kitchens` | 22-27 | - | **south** -> Fishmarket Arcade `dc_fishmarket_arcade` | - | - |
| Shipwright Lane `dc_shipwright_lane` | 22-27 | - | **east** -> Terrecester Wharf: Harbor Market `dc_wharf_market`<br>**west** -> The Long Ropewalk `dc_ropewalk`<br>**north** -> League Drydock `dc_drydock` | - | - |
| The Long Ropewalk `dc_ropewalk` | 22-27 | - | **east** -> Shipwright Lane `dc_shipwright_lane` | - | - |
| League Drydock `dc_drydock` | 22-27 | - | **south** -> Shipwright Lane `dc_shipwright_lane` | - | - |
| Captain’s Green `dc_captains_green` | 22-27 | - | **south** -> Terrecester Wharf: Harbor Market `dc_wharf_market`<br>**north** -> Temple of the Returning Tide `dc_sea_temple`<br>**east** -> Tidebound League Hall `dc_league_hall`<br>**west** -> Wharf Magehouse `dc_wharf_magehouse` | - | - |
| Tidebound League Hall `dc_league_hall` | 22-27 | - | **west** -> Captain’s Green `dc_captains_green`<br>**in** -> League Chart Room `dc_chart_room` | - | - |
| League Chart Room `dc_chart_room` | 22-27 | - | **out** -> Tidebound League Hall `dc_league_hall` | - | - |
| Wharf Magehouse `dc_wharf_magehouse` | 22-27 | - | **east** -> Captain’s Green `dc_captains_green` | - | - |
| Temple of the Returning Tide `dc_sea_temple` | 22-27 | - | **south** -> Captain’s Green `dc_captains_green`<br>**east** -> Storm Cellar Beneath the Temple `dc_storm_cellar` | - | - |
| Storm Cellar Beneath the Temple `dc_storm_cellar` | 22-27 | - | **west** -> Temple of the Returning Tide `dc_sea_temple` | - | - |
| Outer Breakwater Under Bombardment `dc_outer_breakwater` | 22-27 | - | **east** -> Terrecester Tidepier `dc_terrecester_tidepier`<br>**west** -> Skiff Launch to the Glendes Islands `dc_skiff_launch`<br>**north** -> Privateer Bombardment Line `dc_privateer_bombardment_line` | - | - |
| Privateer Bombardment Line `dc_privateer_bombardment_line` | 22-27 | - | **south** -> Outer Breakwater Under Bombardment `dc_outer_breakwater` | - | - |
| Skiff Launch to the Glendes Islands `dc_skiff_launch` | 22-27 | - | **east** -> Outer Breakwater Under Bombardment `dc_outer_breakwater`<br>**west** -> Thesmeda Sea Crossing `dc_thesmeda_crossing` | - | - |
| Thesmeda Sea Crossing `dc_thesmeda_crossing` | 22-27 | - | **east** -> Skiff Launch to the Glendes Islands `dc_skiff_launch`<br>**west** -> Glendes Islands: East Beach `dc_glendes_east_beach` | - | - |
| Glendes Islands: East Beach `dc_glendes_east_beach` | 22-27 | - | **east** -> Thesmeda Sea Crossing `dc_thesmeda_crossing`<br>**north** -> Shellbone Cove `dc_shellbone_cove`<br>**west** -> Glendes Island Jungle Path `dc_island_jungle_path`<br>**south** -> Wrecked Privateer Camp `dc_wrecked_privateer_camp` | - | - |
| Shellbone Cove `dc_shellbone_cove` | 22-27 | - | **south** -> Glendes Islands: East Beach `dc_glendes_east_beach` | - | - |
| Wrecked Privateer Camp `dc_wrecked_privateer_camp` | 22-27 | - | **north** -> Glendes Islands: East Beach `dc_glendes_east_beach` | - | - |
| Glendes Island Jungle Path `dc_island_jungle_path` | 22-27 | - | **east** -> Glendes Islands: East Beach `dc_glendes_east_beach`<br>**west** -> Buried Labyrinth: Ruin Forecourt `dc_ruin_forecourt`<br>**north** -> Overgrown Terrace Trap Cache `dc_terrace_trap_cache`<br>**south** -> Tide-Pool Grotto `dc_tide_pool_grotto` | - | - |
| Overgrown Terrace Trap Cache `dc_terrace_trap_cache` | 22-27 | - | **south** -> Glendes Island Jungle Path `dc_island_jungle_path` | - | - |
| Tide-Pool Grotto `dc_tide_pool_grotto` | 22-27 | - | **north** -> Glendes Island Jungle Path `dc_island_jungle_path` | - | - |
| Buried Labyrinth: Ruin Forecourt `dc_ruin_forecourt` | 22-27 | - | **east** -> Glendes Island Jungle Path `dc_island_jungle_path`<br>**in** -> The Buried Labyrinth: Sunken Entry `dc_buried_labyrinth_entry` | - | - |
| The Buried Labyrinth: Sunken Entry `dc_buried_labyrinth_entry` | 22-27 | - | **out** -> Buried Labyrinth: Ruin Forecourt `dc_ruin_forecourt`<br>**north** -> Buried Labyrinth: Compass Hall `dc_labyrinth_compass_hall`<br>**east** -> Labyrinth Dead End: Sand Chute `dc_sand_chute_deadend` | - | - |
| Labyrinth Dead End: Sand Chute `dc_sand_chute_deadend` | 22-27 | - | **west** -> The Buried Labyrinth: Sunken Entry `dc_buried_labyrinth_entry` | - | - |
| Buried Labyrinth: Compass Hall `dc_labyrinth_compass_hall` | 22-27 | - | **south** -> The Buried Labyrinth: Sunken Entry `dc_buried_labyrinth_entry`<br>**east** -> Buried Labyrinth: Mirrored Trench `dc_mirrored_trench`<br>**west** -> Buried Labyrinth: Tidal Gallery `dc_tidal_gallery`<br>**north** -> Buried Labyrinth: Serpent Tile Walk `dc_serpent_tile_walk` | - | - |
| Buried Labyrinth: Mirrored Trench `dc_mirrored_trench` | 22-27 | - | **west** -> Buried Labyrinth: Compass Hall `dc_labyrinth_compass_hall`<br>**north** -> Scissor-Gate Crossing `dc_scissor_gate_crossing`<br>**down** -> Trap Drop: Pitch-Black Cistern `dc_pitfall_cistern` | - | - |
| Trap Drop: Pitch-Black Cistern `dc_pitfall_cistern` | 22-27 | - | **up** -> Buried Labyrinth: Mirrored Trench `dc_mirrored_trench`<br>**west** -> Underwater Sluice Cache `dc_underwater_sluice_cache` | - | - |
| Underwater Sluice Cache `dc_underwater_sluice_cache` | 22-27 | - | **east** -> Trap Drop: Pitch-Black Cistern `dc_pitfall_cistern` | - | - |
| Buried Labyrinth: Tidal Gallery `dc_tidal_gallery` | 22-27 | - | **east** -> Buried Labyrinth: Compass Hall `dc_labyrinth_compass_hall`<br>**north** -> Crab Crypt `dc_crab_crypt`<br>**west** -> Gallery Supply Cache `dc_gallery_supply_cache` | - | - |
| Gallery Supply Cache `dc_gallery_supply_cache` | 22-27 | - | **east** -> Buried Labyrinth: Tidal Gallery `dc_tidal_gallery` | - | - |
| Crab Crypt `dc_crab_crypt` | 22-27 | - | **south** -> Buried Labyrinth: Tidal Gallery `dc_tidal_gallery`<br>**north** -> Lower Crossing of Three Floods `dc_lower_crossing` | - | - |
| Buried Labyrinth: Serpent Tile Walk `dc_serpent_tile_walk` | 22-27 | - | **south** -> Buried Labyrinth: Compass Hall `dc_labyrinth_compass_hall`<br>**east** -> Scissor-Gate Crossing `dc_scissor_gate_crossing`<br>**west** -> False Sanctuary of Dry Stone `dc_false_sanctuary`<br>**north** -> The Knot Crossing `dc_knot_crossing` | - | - |
| Scissor-Gate Crossing `dc_scissor_gate_crossing` | 22-27 | - | **south** -> Buried Labyrinth: Mirrored Trench `dc_mirrored_trench`<br>**west** -> Buried Labyrinth: Serpent Tile Walk `dc_serpent_tile_walk`<br>**north** -> Rope Bridge Over the Buried Chasm `dc_rope_bridge_chasm` | - | - |
| False Sanctuary of Dry Stone `dc_false_sanctuary` | 22-27 | - | **east** -> Buried Labyrinth: Serpent Tile Walk `dc_serpent_tile_walk`<br>**north** -> Lower Crossing of Three Floods `dc_lower_crossing`<br>**west** -> Drowned Reliquary Dead End `dc_drowned_reliquary_deadend` | - | - |
| Drowned Reliquary Dead End `dc_drowned_reliquary_deadend` | 22-27 | - | **east** -> False Sanctuary of Dry Stone `dc_false_sanctuary` | - | - |
| Lower Crossing of Three Floods `dc_lower_crossing` | 22-27 | - | **south** -> Crab Crypt `dc_crab_crypt`<br>**east** -> The Knot Crossing `dc_knot_crossing`<br>**west** -> False Sanctuary of Dry Stone `dc_false_sanctuary`<br>**down** -> Submerged Underpath `dc_submerged_underpath` | - | - |
| Submerged Underpath `dc_submerged_underpath` | 22-27 | - | **up** -> Lower Crossing of Three Floods `dc_lower_crossing`<br>**north** -> Hidden Pearl Cache `dc_hidden_pearl_cache` | - | - |
| Hidden Pearl Cache `dc_hidden_pearl_cache` | 22-27 | - | **south** -> Submerged Underpath `dc_submerged_underpath` | - | - |
| The Knot Crossing `dc_knot_crossing` | 22-27 | - | **south** -> Buried Labyrinth: Serpent Tile Walk `dc_serpent_tile_walk`<br>**east** -> Rope Bridge Over the Buried Chasm `dc_rope_bridge_chasm`<br>**west** -> Lower Crossing of Three Floods `dc_lower_crossing`<br>**north** -> The Buried Labyrinth: Saltblind Maze `dc_saltblind_maze` | - | - |
| Rope Bridge Over the Buried Chasm `dc_rope_bridge_chasm` | 22-27 | - | **south** -> Scissor-Gate Crossing `dc_scissor_gate_crossing`<br>**west** -> The Knot Crossing `dc_knot_crossing`<br>**north** -> Obsidian Drop Dead End `dc_obsidian_drop` | - | - |
| Obsidian Drop Dead End `dc_obsidian_drop` | 22-27 | - | **south** -> Rope Bridge Over the Buried Chasm `dc_rope_bridge_chasm` | - | - |
| The Buried Labyrinth: Saltblind Maze `dc_saltblind_maze` | 22-27 | - | **out** -> The Knot Crossing `dc_knot_crossing` | - | maze `north,west,north,east,south` -> `dc_labyrinth_worthy_threshold` |
| Threshold of the Worthy Tide `dc_labyrinth_worthy_threshold` | 22-27 | - | **south** -> The Buried Labyrinth: Saltblind Maze `dc_saltblind_maze`<br>**north** -> Antechamber of the Tide-Eyed `dc_serpent_antechamber` | - | - |
| Antechamber of the Tide-Eyed `dc_serpent_antechamber` | 22-27 | - | **south** -> Threshold of the Worthy Tide `dc_labyrinth_worthy_threshold`<br>**north** -> Sanctum of Eshdru, the Tide-Eyed `dc_ancient_serpent_sanctum` | - | - |
| Sanctum of Eshdru, the Tide-Eyed `dc_ancient_serpent_sanctum` | 22-27 | - | **south** -> Antechamber of the Tide-Eyed `dc_serpent_antechamber`<br>**north** -> Glendes North Landing `dc_glendes_north_landing` | - | - |
| Glendes North Landing `dc_glendes_north_landing` | 22-27 | - | **south** -> Sanctum of Eshdru, the Tide-Eyed `dc_ancient_serpent_sanctum`<br>**north** -> Duskfall North Cliff Road `dc_north_cliff_road` | - | - |
| Duskfall North Cliff Road `dc_north_cliff_road` | 22-27 | - | **south** -> Glendes North Landing `dc_glendes_north_landing`<br>**north** -> Stormbreak Foothills `thundervale_peaks_crossroads` (Thundervale Peaks) | - | - |

## Thundervale Peaks

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| Stormbreak Foothills `thundervale_peaks_crossroads` | 27-32 | - | **south** -> Duskfall North Cliff Road `dc_north_cliff_road` (Duskfall Coast)<br>**north** -> Pilgrim’s Switchback: Lower Turn `tv_pilgrims_switchback_lower`<br>**east** -> Windsplit Shepherd Path `tv_windsplit_shepherd_path` | - | - |
| Windsplit Shepherd Path `tv_windsplit_shepherd_path` | 27-32 | - | **west** -> Stormbreak Foothills `thundervale_peaks_crossroads`<br>**north** -> Shepherd’s Eyrie Gate `tv_shepherds_eyrie_gate`<br>**east** -> Sky-Goat Pastures `tv_sky_goat_pastures` | - | - |
| Sky-Goat Pastures `tv_sky_goat_pastures` | 27-32 | - | **west** -> Windsplit Shepherd Path `tv_windsplit_shepherd_path`<br>**in** -> Stormgoat Shelter `tv_stormgoat_shelter`<br>**north** -> East Rune Outcrop `tv_east_rune_outcrop` | - | - |
| Stormgoat Shelter `tv_stormgoat_shelter` | 27-32 | - | **out** -> Sky-Goat Pastures `tv_sky_goat_pastures` | - | - |
| East Rune Outcrop `tv_east_rune_outcrop` | 27-32 | - | **south** -> Sky-Goat Pastures `tv_sky_goat_pastures`<br>**west** -> Thunderfall Bridge: South Anchorage `tv_thunderfall_bridge_south` | - | - |
| Pilgrim’s Switchback: Lower Turn `tv_pilgrims_switchback_lower` | 27-32 | - | **south** -> Stormbreak Foothills `thundervale_peaks_crossroads`<br>**up** -> Pilgrim’s Switchback: Upper Turn `tv_pilgrims_switchback_upper`<br>**east** -> Old Switchback Cache `tv_wild_switchback_cache` | - | - |
| Old Switchback Cache `tv_wild_switchback_cache` | 27-32 | - | **west** -> Pilgrim’s Switchback: Lower Turn `tv_pilgrims_switchback_lower` | - | - |
| Pilgrim’s Switchback: Upper Turn `tv_pilgrims_switchback_upper` | 27-32 | - | **down** -> Pilgrim’s Switchback: Lower Turn `tv_pilgrims_switchback_lower`<br>**north** -> Thunderfall Bridge: South Anchorage `tv_thunderfall_bridge_south`<br>**west** -> Shepherd’s Eyrie Gate `tv_shepherds_eyrie_gate` | - | - |
| Shepherd’s Eyrie Gate `tv_shepherds_eyrie_gate` | 27-32 | - | **south** -> Windsplit Shepherd Path `tv_windsplit_shepherd_path`<br>**east** -> Pilgrim’s Switchback: Upper Turn `tv_pilgrims_switchback_upper`<br>**in** -> Shepherd’s Eyrie Common `tv_shepherds_eyrie_common` | - | - |
| Shepherd’s Eyrie Common `tv_shepherds_eyrie_common` | 27-32 | - | **out** -> Shepherd’s Eyrie Gate `tv_shepherds_eyrie_gate`<br>**north** -> Stormwatch Inn `tv_stormwatch_inn`<br>**east** -> Eyrie Rope-Market `tv_eyrie_market`<br>**west** -> Griffon Perch `tv_griffon_perch` | - | storage |
| Stormwatch Inn `tv_stormwatch_inn` | 27-32 | - | **south** -> Shepherd’s Eyrie Common `tv_shepherds_eyrie_common` | - | - |
| Eyrie Rope-Market `tv_eyrie_market` | 27-32 | - | **west** -> Shepherd’s Eyrie Common `tv_shepherds_eyrie_common`<br>**north** -> Skyhook Ropewalk `tv_skyhook_ropewalk` | - | - |
| Skyhook Ropewalk `tv_skyhook_ropewalk` | 27-32 | - | **south** -> Eyrie Rope-Market `tv_eyrie_market`<br>**up** -> Shrine of the First Thunder `tv_ledge_shrine` | - | - |
| Shrine of the First Thunder `tv_ledge_shrine` | 27-32 | - | **down** -> Skyhook Ropewalk `tv_skyhook_ropewalk` | - | - |
| Griffon Perch `tv_griffon_perch` | 27-32 | - | **east** -> Shepherd’s Eyrie Common `tv_shepherds_eyrie_common`<br>**up** -> High-Wind Roost `tv_high_wind_roost` | - | - |
| High-Wind Roost `tv_high_wind_roost` | 27-32 | - | **down** -> Griffon Perch `tv_griffon_perch` | - | - |
| Thunderfall Bridge: South Anchorage `tv_thunderfall_bridge_south` | 27-32 | - | **south** -> Pilgrim’s Switchback: Upper Turn `tv_pilgrims_switchback_upper`<br>**east** -> East Rune Outcrop `tv_east_rune_outcrop`<br>**north** -> Thunderfall Bridge: Open Span `tv_thunderfall_bridge_span` | - | - |
| Thunderfall Bridge: Open Span `tv_thunderfall_bridge_span` | 27-32 | - | **south** -> Thunderfall Bridge: South Anchorage `tv_thunderfall_bridge_south`<br>**north** -> Thunderfall Bridge: North Anchorage `tv_thunderfall_bridge_north`<br>**down** -> Thunderfall Underbridge `tv_thunderfall_underbridge` | - | - |
| Thunderfall Underbridge `tv_thunderfall_underbridge` | 27-32 | - | **up** -> Thunderfall Bridge: Open Span `tv_thunderfall_bridge_span`<br>**east** -> Rain-Rune Cleft `tv_rain_rune_cleft` | - | - |
| Rain-Rune Cleft `tv_rain_rune_cleft` | 27-32 | - | **west** -> Thunderfall Underbridge `tv_thunderfall_underbridge` | - | - |
| Thunderfall Bridge: North Anchorage `tv_thunderfall_bridge_north` | 27-32 | - | **south** -> Thunderfall Bridge: Open Span `tv_thunderfall_bridge_span`<br>**north** -> Giant-Step Causeway `tv_giant_step_causeway`<br>**east** -> Lightning-Scarred Raider Camp `tv_lightning_scarred_camp` | - | - |
| Lightning-Scarred Raider Camp `tv_lightning_scarred_camp` | 27-32 | - | **west** -> Thunderfall Bridge: North Anchorage `tv_thunderfall_bridge_north` | - | - |
| Giant-Step Causeway `tv_giant_step_causeway` | 27-32 | - | **south** -> Thunderfall Bridge: North Anchorage `tv_thunderfall_bridge_north`<br>**north** -> Broken Storm-Rune Terrace `tv_broken_storm_rune`<br>**east** -> Overlook of Vhal Torunn `tv_overlook_of_vhal_torunn` | - | - |
| Overlook of Vhal Torunn `tv_overlook_of_vhal_torunn` | 27-32 | - | **west** -> Giant-Step Causeway `tv_giant_step_causeway` | - | - |
| Broken Storm-Rune Terrace `tv_broken_storm_rune` | 27-32 | - | **south** -> Giant-Step Causeway `tv_giant_step_causeway`<br>**north** -> Lower Vhal Torunn Gate `tv_lower_vhal_torunn_gate` | - | - |
| Lower Vhal Torunn Gate `tv_lower_vhal_torunn_gate` | 27-32 | - | **south** -> Broken Storm-Rune Terrace `tv_broken_storm_rune`<br>**in** -> Lower Vhal Torunn Hall `tv_lower_vhal_torunn_hall` | - | - |
| Lower Vhal Torunn Hall `tv_lower_vhal_torunn_hall` | 27-32 | - | **out** -> Lower Vhal Torunn Gate `tv_lower_vhal_torunn_gate`<br>**north** -> Prophecy Steps `tv_prophecy_steps`<br>**east** -> Stormlift Base `tv_stormlift_base`<br>**west** -> Cloud-Smith Workbench `tv_cloudsmith_workbench` | - | - |
| Cloud-Smith Workbench `tv_cloudsmith_workbench` | 27-32 | - | **east** -> Lower Vhal Torunn Hall `tv_lower_vhal_torunn_hall` | - | - |
| Prophecy Steps `tv_prophecy_steps` | 27-32 | - | **south** -> Lower Vhal Torunn Hall `tv_lower_vhal_torunn_hall`<br>**up** -> Lower Tempest Archive `tv_tempest_archive_lower`<br>**north** -> Audience Beneath Thunder `tv_giant_audience_chamber` | - | - |
| Lower Tempest Archive `tv_tempest_archive_lower` | 27-32 | - | **down** -> Prophecy Steps `tv_prophecy_steps`<br>**east** -> Rune Index Gallery `tv_rune_index_gallery` | - | - |
| Rune Index Gallery `tv_rune_index_gallery` | 27-32 | - | **west** -> Lower Tempest Archive `tv_tempest_archive_lower` | - | - |
| Audience Beneath Thunder `tv_giant_audience_chamber` | 27-32 | - | **south** -> Prophecy Steps `tv_prophecy_steps`<br>**east** -> Stormlift Base `tv_stormlift_base`<br>**west** -> Oracle Balcony `tv_oracle_balcony` | - | - |
| Oracle Balcony `tv_oracle_balcony` | 27-32 | - | **east** -> Audience Beneath Thunder `tv_giant_audience_chamber` | - | - |
| Stormlift Base `tv_stormlift_base` | 27-32 | - | **west** -> Lower Vhal Torunn Hall `tv_lower_vhal_torunn_hall`<br>**up** -> Upper Stormlift Landing `tv_upper_stormlift_landing` [flag `tv_stormlift_awakened`] | - | - |
| Upper Stormlift Landing `tv_upper_stormlift_landing` | 27-32 | - | **down** -> Stormlift Base `tv_stormlift_base`<br>**north** -> Cloud-Hung Battlements `tv_cloud_hung_battlements`<br>**east** -> Upper Rain Court `tv_upper_rain_court` | - | - |
| Upper Rain Court `tv_upper_rain_court` | 27-32 | - | **west** -> Upper Stormlift Landing `tv_upper_stormlift_landing`<br>**north** -> Tempest Archive `tv_tempest_archive` | - | - |
| Cloud-Hung Battlements `tv_cloud_hung_battlements` | 27-32 | - | **south** -> Upper Stormlift Landing `tv_upper_stormlift_landing`<br>**east** -> Tempest Archive `tv_tempest_archive`<br>**north** -> Hollow Thunderforge Gate `tv_thunderforge_gate`<br>**west** -> Cloud Cache Lintel `tv_cloud_cache_lintel` | - | - |
| Cloud Cache Lintel `tv_cloud_cache_lintel` | 27-32 | - | **east** -> Cloud-Hung Battlements `tv_cloud_hung_battlements` | - | - |
| Tempest Archive `tv_tempest_archive` | 27-32 | - | **west** -> Cloud-Hung Battlements `tv_cloud_hung_battlements`<br>**south** -> Upper Rain Court `tv_upper_rain_court`<br>**north** -> Sky-Throne Anteroom `tv_sky_throne_anteroom` | - | - |
| Sky-Throne Anteroom `tv_sky_throne_anteroom` | 27-32 | - | **south** -> Tempest Archive `tv_tempest_archive` | - | - |
| Hollow Thunderforge Gate `tv_thunderforge_gate` | 27-32 | - | **south** -> Cloud-Hung Battlements `tv_cloud_hung_battlements`<br>**in** -> The Hollow Thunderforge: Entry Vault `tv_hollow_thunderforge_entry` | - | - |
| The Hollow Thunderforge: Entry Vault `tv_hollow_thunderforge_entry` | 27-32 | - | **out** -> Hollow Thunderforge Gate `tv_thunderforge_gate`<br>**north** -> The Hollow Thunderforge: Giant Hall `tv_thunderforge_giant_hall`<br>**east** -> The Hollow Thunderforge: Maintenance Tunnels `tv_thunderforge_maintenance_tunnels` | - | - |
| The Hollow Thunderforge: Giant Hall `tv_thunderforge_giant_hall` | 27-32 | - | **south** -> The Hollow Thunderforge: Entry Vault `tv_hollow_thunderforge_entry`<br>**north** -> The Hollow Thunderforge: Grounding Conduit `tv_thunderforge_grounding_conduit`<br>**west** -> The Hollow Thunderforge: False Ore Spur `tv_thunderforge_dead_end_ore` | - | - |
| The Hollow Thunderforge: False Ore Spur `tv_thunderforge_dead_end_ore` | 27-32 | - | **east** -> The Hollow Thunderforge: Giant Hall `tv_thunderforge_giant_hall` | - | - |
| The Hollow Thunderforge: Maintenance Tunnels `tv_thunderforge_maintenance_tunnels` | 27-32 | - | **west** -> The Hollow Thunderforge: Entry Vault `tv_hollow_thunderforge_entry`<br>**north** -> The Hollow Thunderforge: Sump Ladders `tv_thunderforge_sump_ladders`<br>**east** -> The Hollow Thunderforge: Tool Cache `tv_thunderforge_tool_cache` | - | - |
| The Hollow Thunderforge: Tool Cache `tv_thunderforge_tool_cache` | 27-32 | - | **west** -> The Hollow Thunderforge: Maintenance Tunnels `tv_thunderforge_maintenance_tunnels` | - | - |
| The Hollow Thunderforge: Sump Ladders `tv_thunderforge_sump_ladders` | 27-32 | - | **south** -> The Hollow Thunderforge: Maintenance Tunnels `tv_thunderforge_maintenance_tunnels`<br>**down** -> The Hollow Thunderforge: Flooded Cistern `tv_thunderforge_flooded_cistern` | - | - |
| The Hollow Thunderforge: Flooded Cistern `tv_thunderforge_flooded_cistern` | 27-32 | - | **up** -> The Hollow Thunderforge: Sump Ladders `tv_thunderforge_sump_ladders`<br>**north** -> The Hollow Thunderforge: Storm-Spirit Pen `tv_thunderforge_storm_spirit_pen` | - | - |
| The Hollow Thunderforge: Grounding Conduit `tv_thunderforge_grounding_conduit` | 27-32 | - | **south** -> The Hollow Thunderforge: Giant Hall `tv_thunderforge_giant_hall`<br>**east** -> The Hollow Thunderforge: Corpse-Lightning Coils `tv_thunderforge_corpse_lightning_coils`<br>**north** -> The Hollow Thunderforge: Storm-Spirit Pen `tv_thunderforge_storm_spirit_pen` | - | - |
| The Hollow Thunderforge: Corpse-Lightning Coils `tv_thunderforge_corpse_lightning_coils` | 27-32 | - | **west** -> The Hollow Thunderforge: Grounding Conduit `tv_thunderforge_grounding_conduit`<br>**north** -> The Hollow Thunderforge: Bone Gantry `tv_thunderforge_bone_gantry`<br>**down** -> The Hollow Thunderforge: Pitfall Floor `tv_thunderforge_pitfall_floor` | - | - |
| The Hollow Thunderforge: Pitfall Floor `tv_thunderforge_pitfall_floor` | 27-32 | - | **up** -> The Hollow Thunderforge: Corpse-Lightning Coils `tv_thunderforge_corpse_lightning_coils`<br>**east** -> The Hollow Thunderforge: Hidden Weather Cache `tv_thunderforge_hidden_cache` | - | - |
| The Hollow Thunderforge: Hidden Weather Cache `tv_thunderforge_hidden_cache` | 27-32 | - | **west** -> The Hollow Thunderforge: Pitfall Floor `tv_thunderforge_pitfall_floor` | - | - |
| The Hollow Thunderforge: Storm-Spirit Pen `tv_thunderforge_storm_spirit_pen` | 27-32 | - | **south** -> The Hollow Thunderforge: Grounding Conduit `tv_thunderforge_grounding_conduit`<br>**east** -> The Hollow Thunderforge: Bone Gantry `tv_thunderforge_bone_gantry`<br>**down** -> The Hollow Thunderforge: Flooded Cistern `tv_thunderforge_flooded_cistern` | - | - |
| The Hollow Thunderforge: Bone Gantry `tv_thunderforge_bone_gantry` | 27-32 | - | **south** -> The Hollow Thunderforge: Corpse-Lightning Coils `tv_thunderforge_corpse_lightning_coils`<br>**west** -> The Hollow Thunderforge: Storm-Spirit Pen `tv_thunderforge_storm_spirit_pen`<br>**north** -> The Hollow Thunderforge: Blackened Dynamo `tv_thunderforge_blackened_dynamo`<br>**east** -> The Hollow Thunderforge: False Pressure Gallery `tv_false_pressure_gallery` | - | - |
| The Hollow Thunderforge: False Pressure Gallery `tv_false_pressure_gallery` | 27-32 | - | **west** -> The Hollow Thunderforge: Bone Gantry `tv_thunderforge_bone_gantry` | - | - |
| The Hollow Thunderforge: Blackened Dynamo `tv_thunderforge_blackened_dynamo` | 27-32 | - | **south** -> The Hollow Thunderforge: Bone Gantry `tv_thunderforge_bone_gantry`<br>**north** -> The Hollow Thunderforge: Command Circle `thundervale_peaks_boss_chamber` | - | - |
| The Hollow Thunderforge: Command Circle `thundervale_peaks_boss_chamber` | 27-32 | - | **south** -> The Hollow Thunderforge: Blackened Dynamo `tv_thunderforge_blackened_dynamo`<br>**east** -> Thunderheart Aegis Chamber `tv_thunderheart_aegis_chamber` | - | - |
| Thunderheart Aegis Chamber `tv_thunderheart_aegis_chamber` | 27-32 | - | **west** -> The Hollow Thunderforge: Command Circle `thundervale_peaks_boss_chamber`<br>**north** -> The Blackfall Descent `um_blackfall_descent` (Umbralwyrm Depths) | - | - |

## Umbralwyrm Depths

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| The Blackfall Descent `um_blackfall_descent` | 32-37 | blackfall_descent | **south** -> Thunderheart Aegis Chamber `tv_thunderheart_aegis_chamber` (Thundervale Peaks)<br>**down** -> Blackfall Ropewalk `um_blackfall_ropewalk` | - | requires item `thundervale_peaks_relic` |
| Blackfall Ropewalk `um_blackfall_ropewalk` | 32-37 | blackfall_descent | **up** -> The Blackfall Descent `um_blackfall_descent`<br>**down** -> Lanternless Threshold `um_lanternless_threshold`<br>**east** -> Collapsed Expedition Camp `um_collapsed_expedition_camp`<br>**west** -> Dripstone Overlook `um_dripstone_overlook` | - | - |
| Collapsed Expedition Camp `um_collapsed_expedition_camp` | 32-37 | blackfall_descent | **west** -> Blackfall Ropewalk `um_blackfall_ropewalk` | - | - |
| Dripstone Overlook `um_dripstone_overlook` | 32-37 | blackfall_descent | **east** -> Blackfall Ropewalk `um_blackfall_ropewalk`<br>**down** -> Basin of Whispering Water `um_water_diviner_basin` | - | - |
| Basin of Whispering Water `um_water_diviner_basin` | 32-37 | blackfall_descent | **up** -> Dripstone Overlook `um_dripstone_overlook` | - | - |
| Lanternless Threshold `um_lanternless_threshold` | 32-37 | lanternless_warrens | **up** -> Blackfall Ropewalk `um_blackfall_ropewalk`<br>**north** -> Blindstone Warren `um_blindstone_warren`<br>**east** -> Lightfall Quarry `um_lightfall_quarry`<br>**west** -> Cartographer’s Nook `um_cartographer_nook` | - | - |
| Cartographer’s Nook `um_cartographer_nook` | 32-37 | lanternless_warrens | **east** -> Lanternless Threshold `um_lanternless_threshold` | - | - |
| Lightfall Quarry `um_lightfall_quarry` | 32-37 | lanternless_warrens | **west** -> Lanternless Threshold `um_lanternless_threshold`<br>**north** -> Ashen Switchback `um_ashen_switchback` | - | - |
| Ashen Switchback `um_ashen_switchback` | 32-37 | lanternless_warrens | **south** -> Lightfall Quarry `um_lightfall_quarry`<br>**north** -> Gate to the Ashen Exchange `um_ashen_exchange_gate` | - | - |
| Blindstone Warren `um_blindstone_warren` | 32-37 | lanternless_warrens | **south** -> Lanternless Threshold `um_lanternless_threshold`<br>**north** -> Outer Gate of Glowcap Commons `um_outer_glowcap_gate`<br>**east** -> Echo Crack `um_echo_crack`<br>**west** -> Stolen Lantern Hollow `um_stolen_lantern_hollow` | - | - |
| Echo Crack `um_echo_crack` | 32-37 | lanternless_warrens | **west** -> Blindstone Warren `um_blindstone_warren`<br>**down** -> Whispering Pool `um_whispering_pool` | - | - |
| Whispering Pool `um_whispering_pool` | 32-37 | lanternless_warrens | **up** -> Echo Crack `um_echo_crack`<br>**north** -> Mycelial Rootway `um_mycelial_rootway` | - | - |
| Mycelial Rootway `um_mycelial_rootway` | 32-37 | mycelial_choir | **south** -> Whispering Pool `um_whispering_pool`<br>**north** -> Mycelial Choir Grove `um_mycelial_choir_grove` | - | - |
| Stolen Lantern Hollow `um_stolen_lantern_hollow` | 32-37 | lanternless_warrens | **east** -> Blindstone Warren `um_blindstone_warren` | - | - |
| Outer Gate of Glowcap Commons `um_outer_glowcap_gate` | 32-37 | glowcap_commons | **south** -> Blindstone Warren `um_blindstone_warren`<br>**north** -> Glowcap Commons Entry `um_glowcap_commons_entrance`<br>**east** -> Compact Watchfire `um_compact_watchfire`<br>**west** -> Spore Toll Stand `um_spore_toll_stand` | - | - |
| Compact Watchfire `um_compact_watchfire` | 32-37 | glowcap_commons | **west** -> Outer Gate of Glowcap Commons `um_outer_glowcap_gate` | - | - |
| Spore Toll Stand `um_spore_toll_stand` | 32-37 | glowcap_commons | **east** -> Outer Gate of Glowcap Commons `um_outer_glowcap_gate` | - | - |
| Glowcap Commons Entry `um_glowcap_commons_entrance` | 32-37 | glowcap_commons | **south** -> Outer Gate of Glowcap Commons `um_outer_glowcap_gate`<br>**north** -> Glowcap Central Bazaar `um_glowcap_central_bazaar`<br>**east** -> Safe-Lantern Provisioner `um_safe_lantern_shop`<br>**west** -> Quiet Bloom Spore-Healing Grotto `um_spore_healer_grotto` | - | requires item `um_glowcap_safe_lantern` |
| Safe-Lantern Provisioner `um_safe_lantern_shop` | 32-37 | glowcap_commons | **west** -> Glowcap Commons Entry `um_glowcap_commons_entrance` | - | - |
| Quiet Bloom Spore-Healing Grotto `um_spore_healer_grotto` | 32-37 | glowcap_commons | **east** -> Glowcap Commons Entry `um_glowcap_commons_entrance` | - | - |
| Glowcap Central Bazaar `um_glowcap_central_bazaar` | 32-37 | glowcap_commons | **south** -> Glowcap Commons Entry `um_glowcap_commons_entrance`<br>**north** -> Gate to the Ashen Exchange `um_ashen_exchange_gate`<br>**east** -> Fungus Farmlanes `um_fungus_farmlanes`<br>**west** -> Bone-Map Archives `um_bone_map_archives`<br>**down** -> Deep Roads Lift `um_deep_roads_lift` | - | - |
| Bone-Map Archives `um_bone_map_archives` | 32-37 | glowcap_commons | **east** -> Glowcap Central Bazaar `um_glowcap_central_bazaar` | - | - |
| Fungus Farmlanes `um_fungus_farmlanes` | 32-37 | glowcap_commons | **west** -> Glowcap Central Bazaar `um_glowcap_central_bazaar`<br>**north** -> Mycelial Choir Grove `um_mycelial_choir_grove`<br>**east** -> Grief-Spore Cleft `um_grief_spore_cleft` | - | - |
| Grief-Spore Cleft `um_grief_spore_cleft` | 32-37 | mycelial_choir | **west** -> Fungus Farmlanes `um_fungus_farmlanes` | - | - |
| Mycelial Choir Grove `um_mycelial_choir_grove` | 32-37 | mycelial_choir | **south** -> Fungus Farmlanes `um_fungus_farmlanes`<br>**north** -> Dreamspore Sanctum `um_dreamspore_sanctum`<br>**west** -> Spore Memory Chamber `um_spore_memory_chamber` | - | - |
| Dreamspore Sanctum `um_dreamspore_sanctum` | 32-37 | mycelial_choir | **south** -> Mycelial Choir Grove `um_mycelial_choir_grove` | - | - |
| Spore Memory Chamber `um_spore_memory_chamber` | 32-37 | mycelial_choir | **east** -> Mycelial Choir Grove `um_mycelial_choir_grove` | - | - |
| Deep Roads Lift `um_deep_roads_lift` | 32-37 | glowcap_commons | **up** -> Glowcap Central Bazaar `um_glowcap_central_bazaar`<br>**down** -> Ashen Exchange Market `um_ashen_exchange_market` | - | - |
| Gate to the Ashen Exchange `um_ashen_exchange_gate` | 32-37 | ashen_exchange | **south** -> Glowcap Central Bazaar `um_glowcap_central_bazaar`<br>**north** -> Ashen Exchange Market `um_ashen_exchange_market`<br>**east** -> Freehammer Deep Forge `um_duergar_free_forge`<br>**west** -> Drow Exile Gallery `um_drow_exile_gallery` | - | - |
| Freehammer Deep Forge `um_duergar_free_forge` | 32-37 | ashen_exchange | **west** -> Gate to the Ashen Exchange `um_ashen_exchange_gate` | - | - |
| Drow Exile Gallery `um_drow_exile_gallery` | 32-37 | ashen_exchange | **east** -> Gate to the Ashen Exchange `um_ashen_exchange_gate` | - | - |
| Ashen Exchange Market `um_ashen_exchange_market` | 32-37 | ashen_exchange | **south** -> Gate to the Ashen Exchange `um_ashen_exchange_gate`<br>**north** -> Wyrmglass Chasm: South Ledge `um_wyrmglass_chasm_south`<br>**east** -> Debt-Token Den `um_debt_token_den`<br>**west** -> Blackwater Cistern `um_blackwater_cistern` | - | - |
| Debt-Token Den `um_debt_token_den` | 32-37 | ashen_exchange | **west** -> Ashen Exchange Market `um_ashen_exchange_market` | - | - |
| Blackwater Cistern `um_blackwater_cistern` | 32-37 | ashen_exchange | **east** -> Ashen Exchange Market `um_ashen_exchange_market` | - | - |
| Wyrmglass Chasm: South Ledge `um_wyrmglass_chasm_south` | 32-37 | wyrmglass_chasm | **south** -> Ashen Exchange Market `um_ashen_exchange_market`<br>**north** -> Wyrmglass Bridge `um_chasm_bridge`<br>**east** -> Steps to the Shattered Observatory `um_shattered_observatory_steps`<br>**west** -> Echo-Bat Roost `um_echo_bat_roost`<br>**down** -> Wyrmglass Lower Shelf `um_wyrmglass_lower_shelf` | - | - |
| Echo-Bat Roost `um_echo_bat_roost` | 32-37 | wyrmglass_chasm | **east** -> Wyrmglass Chasm: South Ledge `um_wyrmglass_chasm_south` | - | - |
| Steps to the Shattered Observatory `um_shattered_observatory_steps` | 32-37 | shattered_observatory | **west** -> Wyrmglass Chasm: South Ledge `um_wyrmglass_chasm_south`<br>**up** -> Shattered Drow Observatory `um_shattered_drow_observatory` | - | - |
| Shattered Drow Observatory `um_shattered_drow_observatory` | 32-37 | shattered_observatory | **down** -> Steps to the Shattered Observatory `um_shattered_observatory_steps`<br>**north** -> Inverted Starwell `um_inverted_starwell`<br>**west** -> Wyrmglass Bridge `um_chasm_bridge` | - | - |
| Inverted Starwell `um_inverted_starwell` | 32-37 | shattered_observatory | **south** -> Shattered Drow Observatory `um_shattered_drow_observatory` | - | - |
| Wyrmglass Bridge `um_chasm_bridge` | 32-37 | wyrmglass_chasm | **south** -> Wyrmglass Chasm: South Ledge `um_wyrmglass_chasm_south`<br>**north** -> Wyrmglass Chasm: North Landing `um_chasm_north_landing`<br>**east** -> Suspended Gnomon `um_suspended_gnomon`<br>**west** -> Shattered Drow Observatory `um_shattered_drow_observatory` | - | - |
| Suspended Gnomon `um_suspended_gnomon` | 32-37 | wyrmglass_chasm | **west** -> Wyrmglass Bridge `um_chasm_bridge` | - | - |
| Wyrmglass Chasm: North Landing `um_chasm_north_landing` | 32-37 | wyrmglass_chasm | **south** -> Wyrmglass Bridge `um_chasm_bridge`<br>**down** -> Wyrmglass Lower Shelf `um_wyrmglass_lower_shelf` | - | - |
| Wyrmglass Lower Shelf `um_wyrmglass_lower_shelf` | 32-37 | wyrmglass_chasm | **up** -> Wyrmglass Chasm: South Ledge `um_wyrmglass_chasm_south`<br>**north** -> Approach to the Shadowed Ossuary `um_ossuary_approach`<br>**east** -> Blackscale Roost `um_blackscale_roost` | - | - |
| Blackscale Roost `um_blackscale_roost` | 32-37 | wyrmglass_chasm | **west** -> Wyrmglass Lower Shelf `um_wyrmglass_lower_shelf` | - | - |
| Approach to the Shadowed Ossuary `um_ossuary_approach` | 32-37 | shadowed_ossuary | **south** -> Wyrmglass Lower Shelf `um_wyrmglass_lower_shelf`<br>**in** -> The Shadowed Ossuary Gate `um_shadowed_ossuary_gate` | - | - |
| The Shadowed Ossuary Gate `um_shadowed_ossuary_gate` | 32-37 | shadowed_ossuary | **out** -> Approach to the Shadowed Ossuary `um_ossuary_approach`<br>**north** -> Ribbed Hall `um_ribbed_hall`<br>**east** -> Sun-Mote Outer Cache `um_sunmote_outer_cache` | - | - |
| Sun-Mote Outer Cache `um_sunmote_outer_cache` | 32-37 | shadowed_ossuary | **west** -> The Shadowed Ossuary Gate `um_shadowed_ossuary_gate` | - | requires item `um_wyrmglass_lens` |
| Ribbed Hall `um_ribbed_hall` | 32-37 | shadowed_ossuary | **south** -> The Shadowed Ossuary Gate `um_shadowed_ossuary_gate`<br>**north** -> Ossuary Crossroads `um_ossuary_crossroads`<br>**east** -> Silent Hammer Cache `um_silent_hammer_cache`<br>**west** -> Echoing Catacomb `um_echoing_catacomb` | - | - |
| Silent Hammer Cache `um_silent_hammer_cache` | 32-37 | shadowed_ossuary | **west** -> Ribbed Hall `um_ribbed_hall` | - | - |
| Echoing Catacomb `um_echoing_catacomb` | 32-37 | shadowed_ossuary | **east** -> Ribbed Hall `um_ribbed_hall`<br>**down** -> Lower Bone Shaft `um_lower_bone_shaft` | - | - |
| Lower Bone Shaft `um_lower_bone_shaft` | 32-37 | shadowed_ossuary | **up** -> Echoing Catacomb `um_echoing_catacomb`<br>**north** -> Sunken Rib Cache `um_sunken_rib_cache` | - | - |
| Sunken Rib Cache `um_sunken_rib_cache` | 32-37 | shadowed_ossuary | **south** -> Lower Bone Shaft `um_lower_bone_shaft` | - | - |
| Ossuary Crossroads `um_ossuary_crossroads` | 32-37 | shadowed_ossuary | **south** -> Ribbed Hall `um_ribbed_hall`<br>**north** -> Blackflame Altar `um_blackflame_altar`<br>**east** -> Wyrmchain Cage `um_wyrmchain_cage`<br>**west** -> Shadowglass Chapel `um_shadowglass_chapel`<br>**down** -> Ossuary Underpath `um_ossuary_underpath` | - | - |
| Shadowglass Chapel `um_shadowglass_chapel` | 32-37 | shadowed_ossuary | **east** -> Ossuary Crossroads `um_ossuary_crossroads` | - | - |
| Wyrmchain Cage `um_wyrmchain_cage` | 32-37 | shadowed_ossuary | **west** -> Ossuary Crossroads `um_ossuary_crossroads` | - | - |
| Ossuary Underpath `um_ossuary_underpath` | 32-37 | shadowed_ossuary | **up** -> Ossuary Crossroads `um_ossuary_crossroads`<br>**north** -> Ossuary Sun-Mote Chamber `um_sunmote_chamber` | - | - |
| Ossuary Sun-Mote Chamber `um_sunmote_chamber` | 32-37 | shadowed_ossuary | **south** -> Ossuary Underpath `um_ossuary_underpath` | - | requires item `um_wyrmglass_lens` |
| Blackflame Altar `um_blackflame_altar` | 32-37 | shadowed_ossuary | **south** -> Ossuary Crossroads `um_ossuary_crossroads`<br>**north** -> Nhalira’s Ritual Laboratory `um_nhalira_ritual_laboratory` | - | - |
| Nhalira’s Ritual Laboratory `um_nhalira_ritual_laboratory` | 32-37 | shadowed_ossuary | **south** -> Blackflame Altar `um_blackflame_altar`<br>**north** -> Wyrmchain Necromancer’s Circle `um_nhalira_boss_chamber`<br>**east** -> Bone-Lamplighter Vault `um_bone_lamplighter_vault` | - | - |
| Bone-Lamplighter Vault `um_bone_lamplighter_vault` | 32-37 | shadowed_ossuary | **west** -> Nhalira’s Ritual Laboratory `um_nhalira_ritual_laboratory` | - | - |
| Wyrmchain Necromancer’s Circle `um_nhalira_boss_chamber` | 32-37 | shadowed_ossuary | **south** -> Nhalira’s Ritual Laboratory `um_nhalira_ritual_laboratory`<br>**north** -> Broken Chain Arch `um_broken_chain_arch` | - | - |
| Broken Chain Arch `um_broken_chain_arch` | 32-37 | shadowed_ossuary | **south** -> Wyrmchain Necromancer’s Circle `um_nhalira_boss_chamber`<br>**north** -> Nightscale Reliquary `um_nightscale_reliquary`<br>**east** -> Bargain Antechamber `um_bargain_antechamber`<br>**west** -> Binding Control Room `um_binding_control_room` | - | - |
| Bargain Antechamber `um_bargain_antechamber` | 32-37 | shadowed_ossuary | **west** -> Broken Chain Arch `um_broken_chain_arch` | - | - |
| Binding Control Room `um_binding_control_room` | 32-37 | shadowed_ossuary | **east** -> Broken Chain Arch `um_broken_chain_arch` | - | - |
| Nightscale Reliquary `um_nightscale_reliquary` | 32-37 | shadowed_ossuary | **south** -> Broken Chain Arch `um_broken_chain_arch`<br>**north** -> Wyrmheart Cavern `um_wyrmheart_cavern` | - | - |
| Wyrmheart Cavern `um_wyrmheart_cavern` | 32-37 | shadowed_ossuary | **south** -> Nightscale Reliquary `um_nightscale_reliquary`<br>**north** -> The Last Breath Before Stars `um_last_breath_before_stars` | - | - |
| The Last Breath Before Stars `um_last_breath_before_stars` | 37 | - | **south** -> Wyrmheart Cavern `um_wyrmheart_cavern` | **north** -> Citadel Threshold of Falling Seals `ac_threshold_falling_seals` (Astral Crown Citadel) [flag `astral_crown_gate_opened`, hidden] | - |

## Astral Crown Citadel

| Room | Level | District | Normal Exits | Hidden Exits | Notes |
|---|---|---|---|---|---|
| Citadel Threshold of Falling Seals `ac_threshold_falling_seals` | 37-40 | - | **south** -> The Last Breath Before Stars `um_last_breath_before_stars` (Umbralwyrm Depths)<br>**north** -> Refuge of Broken Chains `ac_refuge_broken_chains` | - | locks after exit |
| Refuge of Broken Chains `ac_refuge_broken_chains` | 37-40 | - | **south** -> Citadel Threshold of Falling Seals `ac_threshold_falling_seals`<br>**north** -> Barricade of Stolen Shields `ac_barricade_stolen_shields`<br>**east** -> Crate-Market of the Lost `ac_crate_market_lost`<br>**west** -> Makeshift Infirmary `ac_makeshift_infirmary`<br>**up** -> War Table of the Unclaimed `ac_war_table_unclaimed` | - | storage; rest |
| Makeshift Infirmary `ac_makeshift_infirmary` | 37-40 | - | **east** -> Refuge of Broken Chains `ac_refuge_broken_chains` | - | rest |
| Crate-Market of the Lost `ac_crate_market_lost` | 37-40 | - | **west** -> Refuge of Broken Chains `ac_refuge_broken_chains` | - | - |
| War Table of the Unclaimed `ac_war_table_unclaimed` | 37-40 | - | **down** -> Refuge of Broken Chains `ac_refuge_broken_chains` | - | - |
| Barricade of Stolen Shields `ac_barricade_stolen_shields` | 37-40 | - | **south** -> Refuge of Broken Chains `ac_refuge_broken_chains`<br>**north** -> Cabal Breach Stair `ac_cabal_breach_stair`<br>**east** -> Right Breach Flank `ac_breach_right_flank`<br>**west** -> Left Breach Flank `ac_breach_left_flank` | - | - |
| Left Breach Flank `ac_breach_left_flank` | 37-40 | - | **east** -> Barricade of Stolen Shields `ac_barricade_stolen_shields` | - | - |
| Right Breach Flank `ac_breach_right_flank` | 37-40 | - | **west** -> Barricade of Stolen Shields `ac_barricade_stolen_shields` | - | - |
| Cabal Breach Stair `ac_cabal_breach_stair` | 37-40 | - | **south** -> Barricade of Stolen Shields `ac_barricade_stolen_shields`<br>**north** -> Hall of Unfinished Materialization `ac_hall_unfinished_materialization` | - | - |
| Hall of Unfinished Materialization `ac_hall_unfinished_materialization` | 37-40 | - | **south** -> Cabal Breach Stair `ac_cabal_breach_stair`<br>**east** -> Planar Chain Gallery `ac_planar_chain_gallery`<br>**west** -> Room of Falling Roads `ac_room_falling_roads`<br>**north** -> Cabal Siege Post `ac_cabal_siege_post` | - | - |
| Planar Chain Gallery `ac_planar_chain_gallery` | 37-40 | - | **west** -> Hall of Unfinished Materialization `ac_hall_unfinished_materialization`<br>**north** -> Crownworks Rampart `ac_crownworks_rampart`<br>**east** -> Astral Masonry Yard `ac_astral_masonry_yard` | - | - |
| Astral Masonry Yard `ac_astral_masonry_yard` | 37-40 | - | **west** -> Planar Chain Gallery `ac_planar_chain_gallery` | - | - |
| Room of Falling Roads `ac_room_falling_roads` | 37-40 | - | **east** -> Hall of Unfinished Materialization `ac_hall_unfinished_materialization`<br>**up** -> Suspended Road Cache `ac_suspended_road_cache` | - | - |
| Suspended Road Cache `ac_suspended_road_cache` | 37-40 | - | **down** -> Room of Falling Roads `ac_room_falling_roads` | - | - |
| Cabal Siege Post `ac_cabal_siege_post` | 37-40 | - | **south** -> Hall of Unfinished Materialization `ac_hall_unfinished_materialization`<br>**north** -> Seal Gate of Survival `ac_seal_gate_survival` | - | - |
| Crownworks Rampart `ac_crownworks_rampart` | 37-40 | - | **south** -> Planar Chain Gallery `ac_planar_chain_gallery`<br>**north** -> Seal Gate of Survival `ac_seal_gate_survival` | - | - |
| Seal Gate of Survival `ac_seal_gate_survival` | 37-40 | - | **south** -> Cabal Siege Post `ac_cabal_siege_post` | **north** -> The Concordance Halls `ac_concordance_halls` [flag `ac_survival_gate_opened`, hidden]<br>**east** -> Survival Seal Cache `ac_survival_cache` [flag `ac_survival_gate_opened`, hidden] | - |
| Survival Seal Cache `ac_survival_cache` | 37-40 | - | **west** -> Seal Gate of Survival `ac_seal_gate_survival` | - | - |
| The Concordance Halls `ac_concordance_halls` | 37-40 | - | **south** -> Seal Gate of Survival `ac_seal_gate_survival`<br>**north** -> Hall of Barrow Oaths `ac_hall_barrow_oaths`<br>**east** -> Thorn-Mirror Court `ac_thorn_mirror_court`<br>**west** -> Sun-Iron Judgment Forge `ac_sun_iron_judgment_forge`<br>**down** -> Drowned King’s Witness `ac_drowned_kings_witness` | - | - |
| Hall of Barrow Oaths `ac_hall_barrow_oaths` | 37-40 | - | **south** -> The Concordance Halls `ac_concordance_halls`<br>**north** -> Cabal Interrogatory `ac_cabal_interrogatory` | - | - |
| Thorn-Mirror Court `ac_thorn_mirror_court` | 37-40 | - | **west** -> The Concordance Halls `ac_concordance_halls` | - | - |
| Sun-Iron Judgment Forge `ac_sun_iron_judgment_forge` | 37-40 | - | **east** -> The Concordance Halls `ac_concordance_halls` | - | - |
| Drowned King’s Witness `ac_drowned_kings_witness` | 37-40 | - | **up** -> The Concordance Halls `ac_concordance_halls` | - | - |
| Cabal Interrogatory `ac_cabal_interrogatory` | 37-40 | - | **south** -> Hall of Barrow Oaths `ac_hall_barrow_oaths`<br>**north** -> Archive of Stolen Names `ac_archive_stolen_names` | - | - |
| Archive of Stolen Names `ac_archive_stolen_names` | 37-40 | - | **south** -> Cabal Interrogatory `ac_cabal_interrogatory`<br>**north** -> Seal Gate of Memory `ac_seal_gate_memory` | - | - |
| Seal Gate of Memory `ac_seal_gate_memory` | 37-40 | - | **south** -> Archive of Stolen Names `ac_archive_stolen_names` | **north** -> Starless Reliquary Entry `ac_starless_reliquary_entry` [flag `ac_memory_gate_opened`, hidden]<br>**east** -> Memory Seal Cache `ac_memory_cache` [flag `ac_memory_gate_opened`, hidden] | - |
| Memory Seal Cache `ac_memory_cache` | 37-40 | - | **west** -> Seal Gate of Memory `ac_seal_gate_memory` | - | - |
| Starless Reliquary Entry `ac_starless_reliquary_entry` | 37-40 | - | **south** -> Seal Gate of Memory `ac_seal_gate_memory`<br>**east** -> Mirage Alignment Chamber `ac_mirage_alignment_chamber`<br>**west** -> Pearl-Tide Observatory `ac_pearl_tide_observatory`<br>**north** -> Thunderheart Conduit `ac_thunderheart_conduit` | - | - |
| Mirage Alignment Chamber `ac_mirage_alignment_chamber` | 37-40 | - | **west** -> Starless Reliquary Entry `ac_starless_reliquary_entry`<br>**north** -> Dead-Star Orrery `ac_dead_star_orrery` | - | - |
| Pearl-Tide Observatory `ac_pearl_tide_observatory` | 37-40 | - | **east** -> Starless Reliquary Entry `ac_starless_reliquary_entry` | - | - |
| Thunderheart Conduit `ac_thunderheart_conduit` | 37-40 | - | **south** -> Starless Reliquary Entry `ac_starless_reliquary_entry`<br>**north** -> Seal Gate of Direction `ac_seal_gate_direction` | - | - |
| Dead-Star Orrery `ac_dead_star_orrery` | 37-40 | - | **south** -> Mirage Alignment Chamber `ac_mirage_alignment_chamber`<br>**west** -> Seal Gate of Direction `ac_seal_gate_direction` | - | - |
| Seal Gate of Direction `ac_seal_gate_direction` | 37-40 | - | **south** -> Thunderheart Conduit `ac_thunderheart_conduit`<br>**east** -> Dead-Star Orrery `ac_dead_star_orrery` | **north** -> The Lich’s Processional `ac_lich_processional` [flag `ac_direction_gate_opened`, hidden]<br>**west** -> Reliquary of Wrong Horizons `ac_reliquary_wrong_horizons` [flag `ac_direction_gate_opened`, hidden] | - |
| Reliquary of Wrong Horizons `ac_reliquary_wrong_horizons` | 37-40 | - | **east** -> Seal Gate of Direction `ac_seal_gate_direction`<br>**north** -> Astral Collapse Bridge `ac_astral_collapse_bridge` | - | - |
| Astral Collapse Bridge `ac_astral_collapse_bridge` | 37-40 | - | **south** -> Reliquary of Wrong Horizons `ac_reliquary_wrong_horizons`<br>**east** -> The Lich’s Processional `ac_lich_processional` | - | - |
| The Lich’s Processional `ac_lich_processional` | 37-40 | - | **south** -> Seal Gate of Direction `ac_seal_gate_direction`<br>**east** -> Crownless Choir Nave `ac_crownless_choir_nave`<br>**west** -> The Unbreathing Armory `ac_unbreathing_armory`<br>**north** -> Reliquary of Failed Crowns `ac_reliquary_failed_crowns` | - | - |
| Crownless Choir Nave `ac_crownless_choir_nave` | 37-40 | - | **west** -> The Lich’s Processional `ac_lich_processional` | - | - |
| The Unbreathing Armory `ac_unbreathing_armory` | 37-40 | - | **east** -> The Lich’s Processional `ac_lich_processional` | - | - |
| Reliquary of Failed Crowns `ac_reliquary_failed_crowns` | 37-40 | - | **south** -> The Lich’s Processional `ac_lich_processional`<br>**north** -> Black-Star Door `ac_black_star_door`<br>**east** -> Prison of Unfinished Bodies `ac_prison_unfinished_bodies`<br>**west** -> Nightscale Shadow Alcove `ac_nightscale_shadow_alcove` | - | - |
| Prison of Unfinished Bodies `ac_prison_unfinished_bodies` | 37-40 | - | **west** -> Reliquary of Failed Crowns `ac_reliquary_failed_crowns` | - | - |
| Nightscale Shadow Alcove `ac_nightscale_shadow_alcove` | 37-40 | - | **east** -> Reliquary of Failed Crowns `ac_reliquary_failed_crowns` | - | - |
| Black-Star Door `ac_black_star_door` | 37-40 | - | **south** -> Reliquary of Failed Crowns `ac_reliquary_failed_crowns` | **north** -> Throne Antechamber `ac_throne_antechamber` [flag `ac_black_star_door_opened`, hidden] | - |
| Throne Antechamber `ac_throne_antechamber` | 37-40 | - | **south** -> Black-Star Door `ac_black_star_door`<br>**north** -> The Crownless Throne `ac_crownless_throne` | - | - |
| The Crownless Throne `ac_crownless_throne` | 37-40 | - | **south** -> Throne Antechamber `ac_throne_antechamber`<br>**east** -> The Astral Crown Reassembled `ac_astral_crown_reassembled` | - | - |
| The Astral Crown Reassembled `ac_astral_crown_reassembled` | 37-40 | - | **west** -> The Crownless Throne `ac_crownless_throne` | - | - |
