"""Generate every JSON/mcfunction file the Starforge mod ships.

Run with:  python3 tools/gen_content.py

Every format in here was checked against the real 1.21.11 vanilla data
(enchantment effects, item components, loot functions, advancement display)
rather than written from memory.
"""
import json
import os
import shutil

MOD_ID = "starforge"
MOD_NAME = "Starforge"
VERSION = "1.0.0"
MC = "1.21.11"

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "src/main/resources")
DATA = os.path.join(RES, "data")
ASSETS = os.path.join(RES, "assets")

WRITTEN = []


def write(relpath, obj):
    path = os.path.join(RES, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        if isinstance(obj, str):
            fh.write(obj)
        else:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    WRITTEN.append(relpath)


def txt(s, color=None, bold=False, italic=False):
    d = {"text": s, "italic": italic}
    if color:
        d["color"] = color
    if bold:
        d["bold"] = True
    return d


def lin(base, per):
    return {"type": "minecraft:linear", "base": base, "per_level_above_first": per}


def add(value):
    return {"type": "minecraft:add", "value": value}


def cost(base, per):
    return {"base": base, "per_level_above_first": per}


def particles(particle, speed=0.4, v_base=0.12, h_scale=0.0):
    """Mirrors the vanilla soul_speed spawn_particles shape exactly."""
    return {
        "type": "minecraft:spawn_particles",
        "particle": {"type": particle},
        "horizontal_position": {"type": "in_bounding_box"},
        "horizontal_velocity": {"movement_scale": h_scale},
        "vertical_position": {"type": "entity_position", "offset": 0.4},
        "vertical_velocity": {"base": v_base},
        "speed": speed,
    }


DIRECT_HIT = {
    "condition": "minecraft:damage_source_properties",
    "predicate": {"is_direct": True},
}


def chance(base, per):
    return {
        "condition": "minecraft:random_chance",
        "chance": {"type": "minecraft:enchantment_level", "amount": lin(base, per)},
    }


def attr(attribute, amount, ident, operation="add_value"):
    return {
        "attribute": attribute,
        "amount": amount,
        "id": f"{MOD_ID}:enchantment.{ident}",
        "operation": operation,
    }


# ===========================================================================
# 1. Enchantments
# ===========================================================================
ENCHANTMENTS = {}

ENCHANTMENTS["starfall"] = {
    "description": {"translate": "enchantment.starforge.starfall"},
    "supported_items": "#minecraft:enchantable/sharp_weapon",
    "primary_items": "#minecraft:enchantable/melee_weapon",
    "exclusive_set": "#minecraft:exclusive_set/damage",
    "weight": 3, "max_level": 5, "anvil_cost": 4,
    "min_cost": cost(8, 11), "max_cost": cost(30, 11),
    "slots": ["mainhand"],
    "effects": {
        "minecraft:damage": [{"effect": add(lin(2.0, 1.5))}],
        "minecraft:post_attack": [{
            "affected": "victim", "enchanted": "attacker",
            "effect": {"type": "minecraft:all_of", "effects": [
                particles("minecraft:end_rod", speed=0.6, v_base=0.2),
                {"type": "minecraft:play_sound",
                 "sound": "minecraft:entity.firework_rocket.blast",
                 "volume": 0.7, "pitch": 1.6},
            ]},
            "requirements": DIRECT_HIT,
        }],
    },
}

ENCHANTMENTS["cinderbrand"] = {
    "description": {"translate": "enchantment.starforge.cinderbrand"},
    "supported_items": "#minecraft:enchantable/fire_aspect",
    "primary_items": "#minecraft:enchantable/melee_weapon",
    "exclusive_set": "#starforge:exclusive_set/ignition",
    "weight": 2, "max_level": 3, "anvil_cost": 4,
    "min_cost": cost(12, 20), "max_cost": cost(62, 20),
    "slots": ["mainhand"],
    "effects": {
        "minecraft:post_attack": [{
            "affected": "victim", "enchanted": "attacker",
            "effect": {"type": "minecraft:all_of", "effects": [
                {"type": "minecraft:ignite", "duration": lin(6.0, 5.0)},
                {"type": "minecraft:apply_mob_effect",
                 "to_apply": "minecraft:weakness",
                 "min_duration": 4.0, "max_duration": lin(4.0, 2.0),
                 "min_amplifier": 0.0, "max_amplifier": 1.0},
            ]},
            "requirements": DIRECT_HIT,
        }],
    },
}

ENCHANTMENTS["soulrend"] = {
    "description": {"translate": "enchantment.starforge.soulrend"},
    "supported_items": "#minecraft:enchantable/sharp_weapon",
    "primary_items": "#minecraft:enchantable/melee_weapon",
    "weight": 2, "max_level": 3, "anvil_cost": 8,
    "min_cost": cost(14, 20), "max_cost": cost(70, 20),
    "slots": ["mainhand"],
    "effects": {
        "minecraft:post_attack": [
            {
                "affected": "victim", "enchanted": "attacker",
                "effect": {"type": "minecraft:apply_mob_effect",
                           "to_apply": "minecraft:wither",
                           "min_duration": 3.0, "max_duration": lin(3.0, 2.0),
                           "min_amplifier": 0.0, "max_amplifier": lin(0.0, 1.0)},
                "requirements": DIRECT_HIT,
            },
            {
                "affected": "attacker", "enchanted": "attacker",
                "effect": {"type": "minecraft:apply_mob_effect",
                           "to_apply": "minecraft:regeneration",
                           "min_duration": 2.0, "max_duration": lin(2.0, 1.5),
                           "min_amplifier": 0.0, "max_amplifier": 0.0},
                "requirements": {"condition": "minecraft:all_of", "terms": [
                    DIRECT_HIT, chance(0.35, 0.2)]},
            },
        ],
    },
}

ENCHANTMENTS["stormcaller"] = {
    "description": {"translate": "enchantment.starforge.stormcaller"},
    "supported_items": "#minecraft:enchantable/melee_weapon",
    "weight": 1, "max_level": 3, "anvil_cost": 8,
    "min_cost": cost(20, 22), "max_cost": cost(70, 22),
    "slots": ["mainhand"],
    "effects": {
        "minecraft:post_attack": [{
            "affected": "victim", "enchanted": "attacker",
            "effect": {"type": "minecraft:all_of", "effects": [
                {"type": "minecraft:summon_entity", "entity": "minecraft:lightning_bolt"},
                {"type": "minecraft:play_sound",
                 "sound": "minecraft:item.trident.thunder",
                 "volume": 2.0, "pitch": 1.0},
            ]},
            "requirements": {"condition": "minecraft:all_of", "terms": [
                DIRECT_HIT, chance(0.08, 0.07)]},
        }],
    },
}

ENCHANTMENTS["skybreaker"] = {
    "description": {"translate": "enchantment.starforge.skybreaker"},
    "supported_items": "#minecraft:enchantable/mace",
    "exclusive_set": "#starforge:exclusive_set/smash",
    "weight": 2, "max_level": 5, "anvil_cost": 4,
    "min_cost": cost(15, 9), "max_cost": cost(65, 9),
    "slots": ["mainhand"],
    "effects": {
        "minecraft:smash_damage_per_fallen_block": [{"effect": add(lin(0.75, 0.75))}],
        "minecraft:post_attack": [{
            "affected": "victim", "enchanted": "attacker",
            "effect": particles("minecraft:gust", speed=0.8, v_base=0.25),
            "requirements": DIRECT_HIT,
        }],
    },
}

ENCHANTMENTS["aegis"] = {
    "description": {"translate": "enchantment.starforge.aegis"},
    "supported_items": "#minecraft:enchantable/armor",
    "exclusive_set": "#minecraft:exclusive_set/armor",
    "weight": 3, "max_level": 5, "anvil_cost": 2,
    "min_cost": cost(5, 10), "max_cost": cost(45, 10),
    "slots": ["armor"],
    "effects": {
        "minecraft:damage_protection": [{
            "effect": add(lin(1.5, 1.5)),
            "requirements": {
                "condition": "minecraft:damage_source_properties",
                "predicate": {"tags": [
                    {"id": "minecraft:bypasses_invulnerability", "expected": False}]},
            },
        }],
    },
}

ENCHANTMENTS["titanheart"] = {
    "description": {"translate": "enchantment.starforge.titanheart"},
    "supported_items": "#minecraft:enchantable/chest_armor",
    "weight": 1, "max_level": 3, "anvil_cost": 8,
    "min_cost": cost(22, 22), "max_cost": cost(75, 22),
    "slots": ["chest"],
    "effects": {
        "minecraft:attributes": [
            attr("minecraft:max_health", lin(4.0, 4.0), "titanheart.health"),
            attr("minecraft:knockback_resistance", lin(0.15, 0.15), "titanheart.knockback"),
            attr("minecraft:armor_toughness", lin(2.0, 1.5), "titanheart.toughness"),
        ],
    },
}

ENCHANTMENTS["voidstep"] = {
    "description": {"translate": "enchantment.starforge.voidstep"},
    "supported_items": "#minecraft:enchantable/foot_armor",
    "weight": 2, "max_level": 3, "anvil_cost": 4,
    "min_cost": cost(12, 18), "max_cost": cost(60, 18),
    "slots": ["feet"],
    "effects": {
        "minecraft:attributes": [
            attr("minecraft:movement_speed", lin(0.04, 0.03), "voidstep.speed"),
            attr("minecraft:safe_fall_distance", lin(6.0, 6.0), "voidstep.fall"),
            attr("minecraft:step_height", lin(0.5, 0.25), "voidstep.step"),
        ],
        "minecraft:tick": [{
            "effect": particles("minecraft:portal", speed=0.2, v_base=0.02),
            "requirements": {
                "condition": "minecraft:entity_properties", "entity": "this",
                "predicate": {"flags": {"is_on_ground": True}, "periodic_tick": 6},
            },
        }],
    },
}

ENCHANTMENTS["gravitas"] = {
    "description": {"translate": "enchantment.starforge.gravitas"},
    "supported_items": "#minecraft:enchantable/leg_armor",
    "weight": 1, "max_level": 3, "anvil_cost": 8,
    "min_cost": cost(20, 20), "max_cost": cost(72, 20),
    "slots": ["legs"],
    "effects": {
        "minecraft:attributes": [
            attr("minecraft:gravity", lin(-0.012, -0.008), "gravitas.gravity"),
            attr("minecraft:jump_strength", lin(0.08, 0.06), "gravitas.jump"),
            attr("minecraft:fall_damage_multiplier", lin(-0.2, -0.15), "gravitas.fall"),
        ],
    },
}

ENCHANTMENTS["starlight"] = {
    "description": {"translate": "enchantment.starforge.starlight"},
    "supported_items": "#minecraft:enchantable/head_armor",
    "weight": 2, "max_level": 3, "anvil_cost": 4,
    "min_cost": cost(14, 16), "max_cost": cost(60, 16),
    "slots": ["head"],
    "effects": {
        "minecraft:attributes": [
            attr("minecraft:luck", lin(1.0, 1.0), "starlight.luck"),
            attr("minecraft:oxygen_bonus", lin(2.0, 2.0), "starlight.oxygen"),
            attr("minecraft:submerged_mining_speed", lin(0.25, 0.25), "starlight.mining"),
        ],
    },
}

ENCHANTMENTS["quarrymind"] = {
    "description": {"translate": "enchantment.starforge.quarrymind"},
    "supported_items": "#minecraft:enchantable/mining",
    "exclusive_set": "#minecraft:exclusive_set/mining",
    "weight": 3, "max_level": 5, "anvil_cost": 2,
    "min_cost": cost(6, 10), "max_cost": cost(56, 10),
    "slots": ["mainhand"],
    "effects": {
        "minecraft:attributes": [
            attr("minecraft:mining_efficiency",
                 {"type": "minecraft:levels_squared", "added": 2.0}, "quarrymind.speed"),
        ],
        "minecraft:block_experience": [
            {"effect": {"type": "minecraft:multiply", "factor": lin(1.5, 0.5)}},
        ],
    },
}

ENCHANTMENTS["eternal"] = {
    "description": {"translate": "enchantment.starforge.eternal"},
    "supported_items": "#minecraft:enchantable/durability",
    "exclusive_set": "#starforge:exclusive_set/durability",
    "weight": 2, "max_level": 5, "anvil_cost": 4,
    "min_cost": cost(10, 9), "max_cost": cost(60, 9),
    "slots": ["any"],
    "effects": {
        "minecraft:item_damage": [
            {"effect": {"type": "minecraft:remove_binomial",
                        "chance": {"type": "minecraft:fraction",
                                   "numerator": lin(3.0, 1.0),
                                   "denominator": lin(4.0, 1.0)}}},
        ],
        "minecraft:repair_with_xp": [
            {"effect": {"type": "minecraft:multiply", "factor": lin(1.0, 0.5)}},
        ],
    },
}


# A custom damage type so Soulrend kills read differently in chat.
ENCHANTMENTS["soulrend"]["effects"]["minecraft:post_attack"].append({
    "affected": "victim", "enchanted": "attacker",
    "effect": {"type": "minecraft:damage_entity",
               "damage_type": "starforge:soulrend",
               "min_damage": 2.0, "max_damage": 5.0},
    "requirements": {"condition": "minecraft:all_of",
                     "terms": [DIRECT_HIT, chance(0.45, 0.25)]},
})

TREASURE = {"titanheart", "gravitas", "stormcaller"}
IN_TABLE = [k for k in ENCHANTMENTS if k not in TREASURE]


# ===========================================================================
# 2. Gear - vanilla bases carrying custom components, models and textures
# ===========================================================================
def gear(base, model, name, colour, lore, rarity="epic", glint=True, **extra):
    c = {
        "minecraft:item_model": f"{MOD_ID}:{model}",
        "minecraft:item_name": txt(name, colour, bold=True),
        "minecraft:rarity": rarity,
        "minecraft:lore": [txt(line, "gray") for line in lore],
    }
    if glint:
        c["minecraft:enchantment_glint_override"] = True
    c.update(extra)
    return {"base": base, "model": model, "components": c}


def mods(*entries):
    return list(entries)


def am(kind, amount, ident, slot, operation="add_value"):
    return {"type": f"minecraft:{kind}", "amount": amount,
            "id": f"{MOD_ID}:{ident}", "operation": operation, "slot": slot}


ARMOUR_EQUIP = {"asset_id": f"{MOD_ID}:starforge",
                "equip_sound": "minecraft:item.armor.equip_netherite"}

GEAR = {}

GEAR["starsteel_ingot"] = gear(
    "minecraft:netherite_ingot", "starsteel_ingot", "Starsteel Ingot", "gold",
    ["Star-metal, quenched in void water.", "Still faintly warm."],
    rarity="rare", glint=False)

GEAR["voidshard"] = gear(
    "minecraft:echo_shard", "voidshard", "Voidshard", "light_purple",
    ["A splinter of the space between places.", "It hums when you are not looking."],
    rarity="rare", glint=False)

GEAR["astral_core"] = gear(
    "minecraft:nether_star", "astral_core", "Astral Core", "yellow",
    ["The heart of a collapsed star.", "Every Starforge relic begins here."],
    rarity="epic")

GEAR["starfall_blade"] = gear(
    "minecraft:netherite_sword", "starfall_blade", "Starfall Blade", "gold",
    ["Forged from a star that fell before", "the world had a name."],
    **{
        "minecraft:max_damage": 4096,
        "minecraft:attribute_modifiers": mods(
            am("attack_damage", 13.0, "starfall_blade.damage", "mainhand"),
            am("attack_speed", -2.2, "starfall_blade.speed", "mainhand"),
            am("entity_interaction_range", 1.5, "starfall_blade.reach", "mainhand"),
            am("sweeping_damage_ratio", 0.85, "starfall_blade.sweep", "mainhand"),
        ),
        "minecraft:enchantments": {
            f"{MOD_ID}:starfall": 5, f"{MOD_ID}:cinderbrand": 3,
            f"{MOD_ID}:stormcaller": 3, f"{MOD_ID}:soulrend": 3,
            f"{MOD_ID}:eternal": 5, "minecraft:looting": 5,
            "minecraft:sweeping_edge": 3,
        },
    })

GEAR["worldbreaker"] = gear(
    "minecraft:mace", "worldbreaker", "Worldbreaker", "red",
    ["Gravity is not a law here.", "It is a weapon."],
    **{
        "minecraft:max_damage": 3200,
        "minecraft:attribute_modifiers": mods(
            am("attack_damage", 11.0, "worldbreaker.damage", "mainhand"),
            am("attack_speed", -3.0, "worldbreaker.speed", "mainhand"),
            am("fall_damage_multiplier", -0.5, "worldbreaker.fall", "mainhand"),
        ),
        "minecraft:enchantments": {
            f"{MOD_ID}:skybreaker": 5, f"{MOD_ID}:eternal": 5,
            f"{MOD_ID}:cinderbrand": 3, "minecraft:wind_burst": 3,
        },
    })

GEAR["voidpiercer"] = gear(
    "minecraft:bow", "voidpiercer", "Voidpiercer", "dark_purple",
    ["Its arrows leave before they are loosed."],
    **{
        "minecraft:max_damage": 2048,
        "minecraft:enchantments": {
            "minecraft:power": 7, "minecraft:punch": 4, "minecraft:flame": 1,
            "minecraft:infinity": 1, f"{MOD_ID}:eternal": 5,
        },
    })

GEAR["starforge_pickaxe"] = gear(
    "minecraft:netherite_pickaxe", "starforge_pickaxe", "Starforge Pickaxe", "aqua",
    ["Stone remembers being dust."],
    **{
        "minecraft:max_damage": 4096,
        "minecraft:attribute_modifiers": mods(
            am("attack_damage", 7.0, "starforge_pickaxe.damage", "mainhand"),
            am("attack_speed", -2.6, "starforge_pickaxe.speed", "mainhand"),
            am("block_interaction_range", 2.0, "starforge_pickaxe.reach", "mainhand"),
        ),
        "minecraft:enchantments": {
            f"{MOD_ID}:quarrymind": 5, f"{MOD_ID}:eternal": 5,
            "minecraft:fortune": 5, "minecraft:efficiency": 8,
        },
    })

_ARMOUR = [
    ("starforge_helmet", "minecraft:netherite_helmet", "head", "Starforge Helm",
     6.0, 5.0, ["The sky looks closer through this visor."],
     {f"{MOD_ID}:starlight": 3, f"{MOD_ID}:aegis": 5, "minecraft:respiration": 3,
      "minecraft:aqua_affinity": 1, f"{MOD_ID}:eternal": 5}),
    ("starforge_chestplate", "minecraft:netherite_chestplate", "chest",
     "Starforge Cuirass", 12.0, 6.0, ["Plated with the skin of a dead star."],
     {f"{MOD_ID}:titanheart": 3, f"{MOD_ID}:aegis": 5, "minecraft:thorns": 3,
      f"{MOD_ID}:eternal": 5}),
    ("starforge_leggings", "minecraft:netherite_leggings", "legs",
     "Starforge Greaves", 9.0, 5.0, ["You weigh a little less than you should."],
     {f"{MOD_ID}:gravitas": 3, f"{MOD_ID}:aegis": 5, "minecraft:swift_sneak": 3,
      f"{MOD_ID}:eternal": 5}),
    ("starforge_boots", "minecraft:netherite_boots", "feet", "Starforge Sabatons",
     6.0, 5.0, ["Every step lands somewhere slightly else."],
     {f"{MOD_ID}:voidstep": 3, f"{MOD_ID}:aegis": 5, "minecraft:feather_falling": 4,
      "minecraft:depth_strider": 3, f"{MOD_ID}:eternal": 5}),
]

for key, base, slot, name, armour, tough, lore, ench in _ARMOUR:
    GEAR[key] = gear(
        base, key, name, "gold", lore,
        **{
            "minecraft:max_damage": 2400,
            "minecraft:equippable": dict(ARMOUR_EQUIP, slot=slot),
            "minecraft:attribute_modifiers": mods(
                am("armor", armour, f"{key}.armor", slot),
                am("armor_toughness", tough, f"{key}.toughness", slot),
                am("knockback_resistance", 0.15, f"{key}.knockback", slot),
                am("max_absorption", 2.0, f"{key}.absorption", slot),
            ),
            "minecraft:enchantments": ench,
        })

GEAR["heart_of_the_star"] = gear(
    "minecraft:totem_of_undying", "heart_of_the_star", "Heart of the Star", "gold",
    ["Death is a suggestion.", "This declines it."],
    **{
        "minecraft:death_protection": {"death_effects": [
            {"type": "minecraft:clear_all_effects"},
            {"type": "minecraft:apply_effects", "effects": [
                {"id": "minecraft:regeneration", "duration": 1200, "amplifier": 3,
                 "show_icon": True},
                {"id": "minecraft:absorption", "duration": 2400, "amplifier": 4,
                 "show_icon": True},
                {"id": "minecraft:resistance", "duration": 600, "amplifier": 2,
                 "show_icon": True},
                {"id": "minecraft:fire_resistance", "duration": 1200, "amplifier": 0,
                 "show_icon": True},
                {"id": "minecraft:strength", "duration": 600, "amplifier": 1,
                 "show_icon": True},
            ]},
        ]},
    })

GEAR["astral_elixir"] = gear(
    "minecraft:enchanted_golden_apple", "astral_elixir", "Astral Elixir", "light_purple",
    ["Bottled starlight. Drink responsibly."],
    **{
        "minecraft:max_stack_size": 16,
        "minecraft:food": {"nutrition": 10, "saturation": 20.0,
                           "can_always_eat": True},
        "minecraft:consumable": {
            "consume_seconds": 1.2,
            "animation": "drink",
            "sound": "minecraft:entity.generic.drink",
            "on_consume_effects": [{
                "type": "minecraft:apply_effects",
                "effects": [
                    {"id": "minecraft:regeneration", "duration": 1200, "amplifier": 2,
                     "show_icon": True},
                    {"id": "minecraft:absorption", "duration": 3600, "amplifier": 5,
                     "show_icon": True},
                    {"id": "minecraft:resistance", "duration": 1800, "amplifier": 1,
                     "show_icon": True},
                    {"id": "minecraft:fire_resistance", "duration": 3600, "amplifier": 0,
                     "show_icon": True},
                    {"id": "minecraft:night_vision", "duration": 3600, "amplifier": 0,
                     "show_icon": True},
                    {"id": "minecraft:strength", "duration": 1200, "amplifier": 1,
                     "show_icon": True},
                ],
            }],
        },
    })


# ===========================================================================
# 3. Recipes
# ===========================================================================
def result_of(key, count=1):
    g = GEAR[key]
    return {"id": g["base"], "count": count, "components": g["components"]}


def shapeless(key, ingredients, category="misc", count=1):
    return {"type": "minecraft:crafting_shapeless", "category": category,
            "ingredients": ingredients, "result": result_of(key, count)}


def shaped(key, pattern, keymap, category="equipment", count=1):
    return {"type": "minecraft:crafting_shaped", "category": category,
            "pattern": pattern, "key": keymap, "result": result_of(key, count)}


STAR = "minecraft:nether_star"
STEEL = "minecraft:netherite_ingot"
VOID = "minecraft:echo_shard"

RECIPES = {
    "starsteel_ingot": shapeless("starsteel_ingot", [
        STEEL, VOID, VOID, "minecraft:blaze_powder", "minecraft:amethyst_shard"]),
    "voidshard": shapeless("voidshard", [
        VOID, "minecraft:amethyst_shard", "minecraft:amethyst_shard",
        "minecraft:ender_pearl", "minecraft:obsidian"]),
    "astral_core": shaped("astral_core", ["nvn", "vSv", "nvn"],
                          {"n": STEEL, "v": VOID, "S": STAR}),
    "starfall_blade": shaped("starfall_blade", [" S ", " s ", " r "],
                             {"S": STAR, "s": "minecraft:netherite_sword",
                              "r": "minecraft:breeze_rod"}),
    "worldbreaker": shaped("worldbreaker", [" S ", "nmn", " h "],
                           {"S": STAR, "n": STEEL, "m": "minecraft:mace",
                            "h": "minecraft:heavy_core"}),
    "voidpiercer": shaped("voidpiercer", [" S ", "vbv", " n "],
                          {"S": STAR, "v": VOID, "b": "minecraft:bow", "n": STEEL}),
    "starforge_pickaxe": shaped("starforge_pickaxe", ["nSn", " p "],
                                {"S": STAR, "n": STEEL,
                                 "p": "minecraft:netherite_pickaxe"}),
    "heart_of_the_star": shaped("heart_of_the_star", ["gSg", "gtg", "ggg"],
                                {"S": STAR, "g": "minecraft:gold_block",
                                 "t": "minecraft:totem_of_undying"}),
    "astral_elixir": shaped("astral_elixir", ["gdg", "dSd", "gdg"],
                            {"S": STAR, "g": "minecraft:ghast_tear",
                             "d": "minecraft:dragon_breath"}, category="misc"),
}

for key, base, *_ in _ARMOUR:
    RECIPES[key] = shaped(key, ["nSn", " b "], {"S": STAR, "n": STEEL, "b": base})


# ===========================================================================
# 4. Loot tables - how /function starforge:arsenal hands the set out
# ===========================================================================
def gear_pool(key):
    g = GEAR[key]
    return {
        "rolls": 1,
        "entries": [{
            "type": "minecraft:item",
            "name": g["base"],
            "functions": [{"function": "minecraft:set_components",
                           "components": g["components"]}],
        }],
    }


ARSENAL_ORDER = [
    "starfall_blade", "worldbreaker", "voidpiercer", "starforge_pickaxe",
    "starforge_helmet", "starforge_chestplate", "starforge_leggings",
    "starforge_boots", "heart_of_the_star", "astral_elixir",
    "starsteel_ingot", "voidshard", "astral_core",
]


# ===========================================================================
# 5. Client assets
# ===========================================================================
SIMPLE_MODELS = {
    "starfall_blade": "minecraft:item/handheld",
    "worldbreaker": "minecraft:item/handheld",
    "starforge_pickaxe": "minecraft:item/handheld",
    "starsteel_ingot": "minecraft:item/generated",
    "voidshard": "minecraft:item/generated",
    "astral_core": "minecraft:item/generated",
    "astral_elixir": "minecraft:item/generated",
    "heart_of_the_star": "minecraft:item/generated",
    "starforge_helmet": "minecraft:item/generated",
    "starforge_chestplate": "minecraft:item/generated",
    "starforge_leggings": "minecraft:item/generated",
    "starforge_boots": "minecraft:item/generated",
}


def write_client_assets():
    for name, parent in SIMPLE_MODELS.items():
        write(f"assets/{MOD_ID}/models/item/{name}.json",
              {"parent": parent, "textures": {"layer0": f"{MOD_ID}:item/{name}"}})
        write(f"assets/{MOD_ID}/items/{name}.json",
              {"model": {"type": "minecraft:model", "model": f"{MOD_ID}:item/{name}"}})

    # Bow: four models plus the vanilla draw-state dispatch.
    for suffix in ("", "_pulling_0", "_pulling_1", "_pulling_2"):
        write(f"assets/{MOD_ID}/models/item/voidpiercer{suffix}.json",
              {"parent": "minecraft:item/bow",
               "textures": {"layer0": f"{MOD_ID}:item/voidpiercer{suffix}"}})
    write(f"assets/{MOD_ID}/items/voidpiercer.json", {
        "model": {
            "type": "minecraft:condition",
            "property": "minecraft:using_item",
            "on_false": {"type": "minecraft:model",
                         "model": f"{MOD_ID}:item/voidpiercer"},
            "on_true": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:use_duration",
                "scale": 0.05,
                "fallback": {"type": "minecraft:model",
                             "model": f"{MOD_ID}:item/voidpiercer_pulling_0"},
                "entries": [
                    {"threshold": 0.65,
                     "model": {"type": "minecraft:model",
                               "model": f"{MOD_ID}:item/voidpiercer_pulling_1"}},
                    {"threshold": 0.9,
                     "model": {"type": "minecraft:model",
                               "model": f"{MOD_ID}:item/voidpiercer_pulling_2"}},
                ],
            },
        },
    })

    write(f"assets/{MOD_ID}/equipment/starforge.json", {
        "layers": {
            "humanoid": [{"texture": f"{MOD_ID}:starforge"}],
            "humanoid_leggings": [{"texture": f"{MOD_ID}:starforge"}],
        },
    })


# ===========================================================================
# 6. Paintings and damage types
# ===========================================================================
PAINTINGS = {
    "voidgate": (1, 1), "forgeheart": (2, 1), "starfall": (2, 2),
}

DAMAGE_TYPES = {
    "soulrend": {"message_id": "soulrend", "exhaustion": 0.1,
                 "scaling": "when_caused_by_living_non_player"},
}


# ===========================================================================
# 7. Advancements
# ===========================================================================
def icon_of(key):
    g = GEAR[key]
    return {"id": g["base"], "count": 1,
            "components": {"minecraft:item_model": g["components"]["minecraft:item_model"]}}


def has_gear(*keys):
    """Inventory predicate matching our gear by its item_model component."""
    return [{"items": GEAR[k]["base"],
             "components": {"minecraft:item_model":
                            GEAR[k]["components"]["minecraft:item_model"]}}
            for k in keys]


ADVANCEMENTS = [
    # key, parent, icon gear, frame, needed gear, title, description, xp
    ("root", None, "astral_core", "task", None,
     "Starforge", "The sky owes you metal. Come and collect.", 0),
    ("voidshard", "root", "voidshard", "task", ["voidshard"],
     "Splinter of Nowhere", "Cut a shard out of the space between places.", 20),
    ("starsteel", "root", "starsteel_ingot", "task", ["starsteel_ingot"],
     "Star-Metal", "Quench netherite in void water and see what survives.", 20),
    ("astral_core", "starsteel", "astral_core", "goal", ["astral_core"],
     "The Heart of It", "Fold a dead star down into something you can hold.", 50),
    ("starfall_blade", "astral_core", "starfall_blade", "goal", ["starfall_blade"],
     "Catch a Falling Star", "Forge the blade that falls with it.", 100),
    ("worldbreaker", "astral_core", "worldbreaker", "goal", ["worldbreaker"],
     "Bring Down the Sky", "Forge a mace that argues with gravity.", 100),
    ("voidpiercer", "astral_core", "voidpiercer", "goal", ["voidpiercer"],
     "Loose the Dark", "String a bow with a piece of the void.", 100),
    ("starforge_pickaxe", "astral_core", "starforge_pickaxe", "goal",
     ["starforge_pickaxe"],
     "Unmake the Mountain", "Forge the pick that remembers stone as dust.", 100),
    ("full_plate", "astral_core", "starforge_chestplate", "goal",
     ["starforge_helmet", "starforge_chestplate", "starforge_leggings",
      "starforge_boots"],
     "Wrapped in Starlight", "Carry the whole Starforge plate at once.", 150),
    ("heart_of_the_star", "full_plate", "heart_of_the_star", "challenge",
     ["heart_of_the_star"],
     "Decline the Offer", "Death made a suggestion. Refuse it.", 250),
    ("ascendant", "heart_of_the_star", "starfall_blade", "challenge",
     ["starfall_blade", "worldbreaker", "voidpiercer", "starforge_pickaxe",
      "starforge_chestplate", "heart_of_the_star"],
     "Ascendant", "Hold the complete Starforge arsenal in one inventory.", 500),
]


def write_advancements():
    for key, parent, icon, frame, needed, title, desc, xp in ADVANCEMENTS:
        display = {
            "icon": icon_of(icon),
            "title": {"translate": f"advancements.{MOD_ID}.{key}.title"},
            "description": {"translate": f"advancements.{MOD_ID}.{key}.description"},
            "frame": frame,
            "show_toast": True,
            "announce_to_chat": True,
            "hidden": False,
        }
        adv = {"display": display, "sends_telemetry_event": False}
        if parent is None:
            display["background"] = f"{MOD_ID}:gui/advancements/backgrounds/starforge"
            display["announce_to_chat"] = False
            adv["criteria"] = {"joined": {"trigger": "minecraft:tick"}}
            adv["requirements"] = [["joined"]]
        else:
            adv["parent"] = f"{MOD_ID}:{parent}"
            adv["criteria"] = {
                "obtained": {
                    "trigger": "minecraft:inventory_changed",
                    "conditions": {"items": has_gear(*needed)},
                },
            }
            adv["requirements"] = [["obtained"]]
        if xp:
            adv["rewards"] = {"experience": xp}
        write(f"data/{MOD_ID}/advancement/{key}.json", adv)

    # Hidden advancement that drops every Starforge recipe into the recipe book.
    write(f"data/{MOD_ID}/advancement/recipes/unlock_all.json", {
        "criteria": {"has_star": {
            "trigger": "minecraft:inventory_changed",
            "conditions": {"items": [{"items": STAR}]},
        }},
        "requirements": [["has_star"]],
        "rewards": {"recipes": [f"{MOD_ID}:{r}" for r in sorted(RECIPES)]},
        "sends_telemetry_event": False,
    })


# ===========================================================================
# 8. Functions
# ===========================================================================
def j(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def write_functions():
    arsenal = "\n".join([
        "# Hands the player the complete Starforge arsenal.",
        "# Usage:  /function starforge:arsenal",
        f"loot give @s loot {MOD_ID}:arsenal",
        "playsound minecraft:block.beacon.activate master @s ~ ~ ~ 1 1.4",
        "tellraw @s " + j([
            txt("", None), txt("[Starforge] ", "gold", bold=True),
            txt("The forge answers. The full arsenal is yours.", "white"),
        ]),
        "",
    ])
    write(f"data/{MOD_ID}/function/arsenal.mcfunction", arsenal)

    lines = [
        "# Prints a short guide to the mod.",
        "# Usage:  /function starforge:help",
        "tellraw @s " + j([txt(""), txt("=== STARFORGE ===", "gold", bold=True)]),
        "tellraw @s " + j([txt(""), txt("Craft ", "gray"),
                           txt("Starsteel Ingots", "yellow"),
                           txt(" and ", "gray"), txt("Voidshards", "light_purple"),
                           txt(", fold them into an ", "gray"),
                           txt("Astral Core", "gold"),
                           txt(", then forge the arsenal.", "gray")]),
        "tellraw @s " + j([txt(""), txt("12 new enchantments appear at the "
                                        "enchanting table, anvil and in trades.",
                                        "gray")]),
        "tellraw @s " + j([txt(""), txt("Creative shortcut: ", "gray"),
                           txt("/function starforge:arsenal", "aqua")]),
        "",
    ]
    write(f"data/{MOD_ID}/function/help.mcfunction", "\n".join(lines))


# ===========================================================================
# 9. Tags
# ===========================================================================
def write_tags():
    ns = lambda names: {"values": [f"{MOD_ID}:{n}" for n in names]}
    write("data/minecraft/tags/enchantment/non_treasure.json", ns(sorted(IN_TABLE)))
    write("data/minecraft/tags/enchantment/treasure.json", ns(sorted(TREASURE)))
    write("data/minecraft/tags/enchantment/tradeable.json", ns(sorted(ENCHANTMENTS)))
    write("data/minecraft/tags/enchantment/on_random_loot.json",
          ns(sorted(ENCHANTMENTS)))
    write("data/minecraft/tags/painting_variant/placeable.json", ns(sorted(PAINTINGS)))

    write(f"data/{MOD_ID}/tags/enchantment/exclusive_set/ignition.json",
          {"values": ["minecraft:fire_aspect", f"{MOD_ID}:cinderbrand"]})
    write(f"data/{MOD_ID}/tags/enchantment/exclusive_set/smash.json",
          {"values": ["minecraft:density", f"{MOD_ID}:skybreaker"]})
    write(f"data/{MOD_ID}/tags/enchantment/exclusive_set/durability.json",
          {"values": ["minecraft:unbreaking", f"{MOD_ID}:eternal"]})


# ===========================================================================
# 10. Language file
# ===========================================================================
ENCH_NAMES = {
    "starfall": ("Starfall", "Each hit drives a sliver of falling star into the target."),
    "cinderbrand": ("Cinderbrand", "Sets the target alight and saps its strength."),
    "soulrend": ("Soulrend", "Withers what you cut, and mends what cut it."),
    "stormcaller": ("Stormcaller", "A chance to call lightning down on whatever you strike."),
    "skybreaker": ("Skybreaker", "Turns every block you fall into extra mace damage."),
    "aegis": ("Aegis", "A broad, heavy ward against all incoming harm."),
    "titanheart": ("Titanheart", "More health, more toughness, and a body that will not be moved."),
    "voidstep": ("Voidstep", "Faster feet, longer falls, taller steps."),
    "gravitas": ("Gravitas", "Gravity loosens its grip on you."),
    "starlight": ("Starlight", "Luck, breath, and clear sight underwater."),
    "quarrymind": ("Quarrymind", "Tears through stone and squeezes more experience from it."),
    "eternal": ("Eternal", "Your gear wears out far more slowly and drinks experience to heal."),
}

PAINTING_TITLES = {
    "voidgate": ("Voidgate", "Starforge"),
    "forgeheart": ("Forgeheart", "Starforge"),
    "starfall": ("Starfall", "Starforge"),
}


def write_lang():
    lang = {
        "modmenu.descriptionTranslation.starforge":
            "Endgame star-metal arsenal and twelve new enchantments.",
    }
    for key, (name, desc) in ENCH_NAMES.items():
        lang[f"enchantment.{MOD_ID}.{key}"] = name
        lang[f"enchantment.{MOD_ID}.{key}.desc"] = desc
    for key, (title, author) in PAINTING_TITLES.items():
        lang[f"painting.{MOD_ID}.{key}.title"] = title
        lang[f"painting.{MOD_ID}.{key}.author"] = author
    for key, _p, _i, _f, _n, title, desc, _xp in ADVANCEMENTS:
        lang[f"advancements.{MOD_ID}.{key}.title"] = title
        lang[f"advancements.{MOD_ID}.{key}.description"] = desc
    lang["death.attack.soulrend"] = "%1$s came apart at the seams"
    lang["death.attack.soulrend.player"] = "%1$s was unmade by %2$s"
    write(f"assets/{MOD_ID}/lang/en_us.json", lang)


# ===========================================================================
# 11. Mod metadata
# ===========================================================================
FABRIC_MOD_JSON = {
    "schemaVersion": 1,
    "id": MOD_ID,
    "version": VERSION,
    "name": MOD_NAME,
    "description": (
        "Starforge adds an endgame star-metal progression to Minecraft: three new "
        "crafting materials, a full arsenal of forged relics with their own art, a "
        "matching armour set, and twelve new enchantments that show up at the "
        "enchanting table, the anvil and in villager trades."
    ),
    "authors": [MOD_NAME],
    "license": "MIT",
    "icon": f"assets/{MOD_ID}/icon.png",
    "environment": "*",
    "depends": {
        "fabricloader": ">=0.16.0",
        "minecraft": "~1.21.11",
        "java": ">=21",
        "fabric-resource-loader-v0": "*",
    },
}


# ===========================================================================
def main():
    # Wipe only what this script owns; textures are gen_textures.py's business.
    for rel in ("data",
                f"assets/{MOD_ID}/lang",
                f"assets/{MOD_ID}/items",
                f"assets/{MOD_ID}/models",
                f"assets/{MOD_ID}/equipment"):
        shutil.rmtree(os.path.join(RES, rel), ignore_errors=True)

    write("fabric.mod.json", FABRIC_MOD_JSON)

    for name, body in ENCHANTMENTS.items():
        write(f"data/{MOD_ID}/enchantment/{name}.json", body)
    for name, body in RECIPES.items():
        write(f"data/{MOD_ID}/recipe/{name}.json", body)
    for key in ARSENAL_ORDER:
        write(f"data/{MOD_ID}/loot_table/gear/{key}.json",
              {"pools": [gear_pool(key)]})
    write(f"data/{MOD_ID}/loot_table/arsenal.json",
          {"pools": [gear_pool(k) for k in ARSENAL_ORDER]})
    for name, (w, h) in PAINTINGS.items():
        write(f"data/{MOD_ID}/painting_variant/{name}.json", {
            "asset_id": f"{MOD_ID}:{name}", "width": w, "height": h,
            "title": {"translate": f"painting.{MOD_ID}.{name}.title", "color": "yellow"},
            "author": {"translate": f"painting.{MOD_ID}.{name}.author", "color": "gray"},
        })
    for name, body in DAMAGE_TYPES.items():
        write(f"data/{MOD_ID}/damage_type/{name}.json", body)

    write_advancements()
    write_functions()
    write_tags()
    write_client_assets()
    write_lang()

    print(f"{len(WRITTEN)} content files generated")
    for rel in sorted(WRITTEN):
        print("  ", rel)


if __name__ == "__main__":
    main()
