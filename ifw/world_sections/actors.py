from __future__ import annotations

import xml.etree.ElementTree as ET

from ..models import (
    CurrencyExchangeRate,
    Enemy,
    LootDrop,
    MonsterPool,
    MonsterPoolEntry,
    NPC,
    PickpocketTarget,
    Spell,
    Vendor,
)
from ..world_loader_xml import (
    _first_attr,
    _optional_text,
    _parse_bool,
    _parse_classes,
    _parse_id_list,
    _parse_int,
    _required_attr,
    _required_attr_any,
)


def parse_spells(root: ET.Element) -> dict[str, Spell]:
    spells: dict[str, Spell] = {}
    for spell_element in root.findall("./spells/spell"):
        school = _required_attr(spell_element, "school").lower()
        duration = _parse_int(spell_element.get("duration"))
        skip_turns = _parse_int(
            spell_element.get("skip_turns")
            or spell_element.get("block_turns")
            or spell_element.get("prevent_attack_turns")
        )
        if skip_turns == 0 and school in {"control", "disable", "attack_block"}:
            skip_turns = duration
        cure_poison = _parse_bool(
            _first_attr(
                spell_element,
                "cure_poison",
                "cures_poison",
                "remove_poison",
                "removes_poison",
            ),
            default=False,
        ) or school in {"cure", "cleanse", "cleansing", "poison_cure", "cure_poison"}
        spell = Spell(
            spell_id=_required_attr(spell_element, "id"),
            name=_required_attr(spell_element, "name"),
            description=_optional_text(spell_element.find("description")),
            school=school,
            mp_cost=_parse_int(_required_attr(spell_element, "mp_cost")),
            power=_parse_int(spell_element.get("power")),
            attack_bonus=_parse_int(spell_element.get("attack_bonus")),
            armor_bonus=_parse_int(spell_element.get("armor_bonus")),
            pickpocket_bonus=_parse_int(
                _first_attr(spell_element, "pickpocket_bonus", "pickpocket")
            ),
            lockpick_bonus=_parse_int(
                _first_attr(spell_element, "lockpick_bonus", "lockpick")
            ),
            duration=duration,
            skip_turns=skip_turns,
            cure_poison=cure_poison,
            allowed_classes=_parse_classes(
                spell_element.get("classes")
                or spell_element.get("allowed_classes")
                or spell_element.get("class")
            ),
        )
        spells[spell.spell_id] = spell
    return spells


def parse_enemies(root: ET.Element) -> dict[str, Enemy]:
    enemies: dict[str, Enemy] = {}
    for enemy_element in root.findall("./enemies/enemy"):
        enemy_id = _required_attr(enemy_element, "id")
        loot = [
            LootDrop(
                item_id=_required_attr(drop_element, "item"),
                chance=float(drop_element.get("chance", "1.0")),
            )
            for drop_element in enemy_element.findall("./loot/drop")
        ]
        enemies[enemy_id] = Enemy(
            enemy_id=enemy_id,
            name=_required_attr(enemy_element, "name"),
            description=_optional_text(enemy_element.find("description")),
            level=_parse_int(_required_attr(enemy_element, "level")),
            max_hp=_parse_int(_required_attr(enemy_element, "hp")),
            attack=_parse_int(_required_attr(enemy_element, "attack")),
            defense=_parse_int(_required_attr(enemy_element, "defense")),
            exp_reward=_parse_int(_required_attr(enemy_element, "exp_reward")),
            gold_reward=_parse_int(_required_attr(enemy_element, "gold_reward")),
            defeat_text=_optional_text(enemy_element.find("defeat_text")),
            respawns=_parse_bool(enemy_element.get("respawns"), default=True),
            loot=loot,
            prevent_attack_chance=_parse_int(
                enemy_element.get("prevent_attack_chance")
                or enemy_element.get("attack_block_chance")
                or enemy_element.get("daze_chance")
            ),
            prevent_attack_turns=_parse_int(
                enemy_element.get("prevent_attack_turns")
                or enemy_element.get("attack_block_turns")
                or enemy_element.get("daze_turns"),
                default=1,
            ),
            prevent_attack_text=_optional_text(enemy_element.find("prevent_attack_text")),
            poison_chance=_parse_int(
                enemy_element.get("poison_chance")
                or enemy_element.get("poison_attack_chance")
                or enemy_element.get("venom_chance")
            ),
            poison_text=_optional_text(enemy_element.find("poison_text")),
        )
    return enemies


def parse_monster_pools(root: ET.Element) -> dict[str, MonsterPool]:
    monster_pools: dict[str, MonsterPool] = {}
    pool_elements = root.findall("./monster_pools/pool") + root.findall("./enemies/monster_pools/pool")
    for pool_element in pool_elements:
        pool_id = _required_attr(pool_element, "id")
        monster_pools[pool_id] = MonsterPool(
            pool_id=pool_id,
            name=pool_element.get("name", "").strip(),
            entries=[
                MonsterPoolEntry(
                    enemy_id=_required_attr(enemy_ref, "id"),
                    weight=_parse_int(enemy_ref.get("weight"), default=1),
                )
                for enemy_ref in pool_element.findall("./enemy_ref")
            ],
        )
    return monster_pools


def parse_npcs(root: ET.Element) -> dict[str, NPC]:
    npcs: dict[str, NPC] = {}
    for npc_element in root.findall("./npcs/npc"):
        quest_ids: list[str] = []
        legacy_quest_id = npc_element.get("quest_id")
        if legacy_quest_id:
            quest_ids.append(legacy_quest_id)
        quest_ids.extend(
            _required_attr(quest_ref, "id")
            for quest_ref in npc_element.findall("./quests/quest_ref")
        )
        dialogue_lines = [
            line
            for line in (
                _optional_text(line_element)
                for line_element in npc_element.findall("./dialogue_lines/line")
            )
            if line
        ]
        recruit_missing_item_text = (
            _optional_text(npc_element.find("recruit_missing_item_text"))
            or _optional_text(npc_element.find("missing_recruit_item_text"))
            or _first_attr(
                npc_element,
                "recruit_missing_item_text",
                "missing_recruit_item_text",
            )
            or ""
        )
        npc = NPC(
            npc_id=_required_attr(npc_element, "id"),
            name=_required_attr(npc_element, "name"),
            dialogue=_optional_text(npc_element.find("dialogue")),
            faction_id=_first_attr(npc_element, "faction", "faction_id"),
            quest_id=quest_ids[0] if quest_ids else None,
            active_dialogue=_optional_text(npc_element.find("active_dialogue")),
            completed_dialogue=_optional_text(npc_element.find("completed_dialogue")),
            dialogue_lines=dialogue_lines,
            quest_ids=quest_ids,
            can_recruit=(
                _parse_bool(
                    _first_attr(
                        npc_element,
                        "companion",
                        "recruitable",
                        "can_recruit",
                        "is_companion",
                    ),
                    default=False,
                )
                or bool(_first_attr(npc_element, "companion_class", "player_class", "class"))
            ),
            companion_class=(
                (_first_attr(npc_element, "companion_class", "player_class", "class") or "").lower()
                or None
            ),
            recruit_required_item=_first_attr(
                npc_element,
                "recruit_item",
                "recruit_required_item",
                "required_recruit_item",
                "companion_required_item",
            ),
            recruit_missing_item_text=recruit_missing_item_text,
            consume_recruit_item=_parse_bool(
                _first_attr(
                    npc_element,
                    "consume_recruit_item",
                    "consume_required_item",
                    "consume_companion_item",
                ),
                default=True,
            ),
            pickpocket_targets=parse_pickpocket_targets(npc_element),
        )
        npcs[npc.npc_id] = npc
    return npcs


def parse_pickpocket_targets(holder_element: ET.Element) -> list[PickpocketTarget]:
    targets: list[PickpocketTarget] = []
    for target_element in (
        holder_element.findall("./pickpocket/item_ref")
        + holder_element.findall("./pickpocket/item")
        + holder_element.findall("./pickpocket_targets/item_ref")
        + holder_element.findall("./pickpocket_targets/item")
    ):
        targets.append(
            PickpocketTarget(
                item_id=_required_attr(target_element, "id"),
                difficulty=_parse_int(
                    _first_attr(target_element, "difficulty", "dc", "penalty"),
                    default=0,
                ),
                success_text=(
                    _optional_text(target_element.find("success_text"))
                    or _first_attr(target_element, "success_text")
                    or ""
                ),
                failure_text=(
                    _optional_text(target_element.find("failure_text"))
                    or _first_attr(target_element, "failure_text")
                    or ""
                ),
            )
        )
    return targets


def parse_vendors(root: ET.Element) -> dict[str, Vendor]:
    vendors: dict[str, Vendor] = {}
    for vendor_element in root.findall("./vendors/vendor"):
        stock_elements = vendor_element.findall("./stock/item")
        recipe_elements = vendor_element.findall("./recipes/recipe_ref")
        spell_elements = vendor_element.findall("./spells/spell_ref")
        stock = {
            _required_attr(stock_element, "id"): _parse_int(_required_attr(stock_element, "price"))
            for stock_element in stock_elements
        }
        recipe_stock = {
            _required_attr(recipe_element, "id"): _parse_int(_required_attr(recipe_element, "price"))
            for recipe_element in recipe_elements
        }
        spell_stock = {
            _required_attr(spell_element, "id"): _parse_int(_required_attr(spell_element, "price"))
            for spell_element in spell_elements
        }
        vendor = Vendor(
            vendor_id=_required_attr(vendor_element, "id"),
            name=_required_attr(vendor_element, "name"),
            dialogue=_optional_text(vendor_element.find("dialogue")),
            stock=stock,
            recipe_stock=recipe_stock,
            spell_stock=spell_stock,
            buyback=float(vendor_element.get("buyback", "0.5")),
            accepted_currencies=parse_vendor_currencies(vendor_element),
            stock_currencies=parse_stock_currencies(stock_elements),
            recipe_currencies=parse_stock_currencies(recipe_elements),
            spell_currencies=parse_stock_currencies(spell_elements),
            exchange_rates=parse_exchange_rates(vendor_element),
            is_exchange=_parse_bool(
                _first_attr(vendor_element, "exchange", "currency_exchange", "exchanges"),
                default=False,
            ),
            pickpocket_targets=parse_pickpocket_targets(vendor_element),
        )
        vendors[vendor.vendor_id] = vendor
    return vendors


def parse_vendor_currencies(vendor_element: ET.Element) -> list[str]:
    currencies = _parse_id_list(
        _first_attr(
            vendor_element,
            "currency",
            "currencies",
            "accepted_currency",
            "accepted_currencies",
        )
    )
    currencies.extend(
        _required_attr_any(currency_element, "id", "currency")
        for currency_element in vendor_element.findall("./currencies/currency")
    )
    return list(dict.fromkeys(currencies))


def parse_stock_currencies(stock_elements: list[ET.Element]) -> dict[str, str]:
    currencies: dict[str, str] = {}
    for stock_element in stock_elements:
        currency_id = _first_attr(stock_element, "currency", "currency_id")
        if currency_id:
            currencies[_required_attr(stock_element, "id")] = currency_id
    return currencies


def parse_exchange_rates(vendor_element: ET.Element) -> list[CurrencyExchangeRate]:
    rates: list[CurrencyExchangeRate] = []
    rate_elements = (
        vendor_element.findall("./exchange_rates/rate")
        + vendor_element.findall("./exchanges/rate")
        + vendor_element.findall("./exchange/rate")
    )
    for rate_element in rate_elements:
        from_currency = _required_attr_any(rate_element, "from", "from_currency")
        to_currency = _required_attr_any(rate_element, "to", "to_currency")
        from_amount = _parse_int(
            _first_attr(rate_element, "from_amount", "from_value", "cost"),
            default=1,
        )
        to_amount_text = _first_attr(rate_element, "to_amount", "to_value", "received")
        if to_amount_text:
            to_amount = _parse_int(to_amount_text)
        else:
            rate_text = _required_attr(rate_element, "rate")
            rate = float(rate_text)
            if rate <= 0:
                to_amount = 0
            elif rate < 1 and from_amount == 1:
                reciprocal = 1 / rate
                if abs(round(reciprocal) - reciprocal) < 0.000001:
                    from_amount = int(round(reciprocal))
                    to_amount = 1
                else:
                    to_amount = max(1, int(from_amount * rate))
            else:
                to_amount = max(1, int(from_amount * rate))
        rates.append(
            CurrencyExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                from_amount=from_amount,
                to_amount=to_amount,
            )
        )
    return rates
