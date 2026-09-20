"""Validate every generated Starforge file against the real Minecraft 1.21.11 data.

This mod cannot be smoke-tested by launching the game in this environment, so
instead every id the mod references is checked against the vanilla registry
dump for 1.21.11, and every asset a model points at is checked on disk.

Run with:  python3 tools/validate.py
Exit code 0 means every check passed.
"""
import json
import os
import sys
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "src/main/resources")
MOD_ID = "starforge"
MC = "1.21.11"
CACHE = os.environ.get(
    "STARFORGE_REGISTRY_CACHE",
    os.path.join(ROOT, ".cache", f"registries-{MC}.json"))
URL = (f"https://raw.githubusercontent.com/misode/mcmeta/refs/tags/"
       f"{MC}-summary/registries/data.min.json")

errors = []
checks = [0]


def fail(msg):
    errors.append(msg)


def load_registries():
    if os.path.exists(CACHE):
        with open(CACHE) as fh:
            return json.load(fh)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    print(f"fetching vanilla {MC} registries ...")
    with urllib.request.urlopen(URL, timeout=120) as r:
        raw = r.read()
    with open(CACHE, "wb") as fh:
        fh.write(raw)
    return json.loads(raw)


REG = load_registries()


def known(registry, ident, where, extra=()):
    """Check a namespaced id against a vanilla registry (plus our own ids)."""
    checks[0] += 1
    if not isinstance(ident, str):
        return fail(f"{where}: expected an id string, got {ident!r}")
    if ident.startswith("#"):
        return                                  # tags are checked separately
    ns, _, path = ident.partition(":")
    if not path:
        ns, path = "minecraft", ns
    if ns == MOD_ID:
        if path not in extra:
            fail(f"{where}: unknown {MOD_ID} {registry} '{ident}'")
        return
    if ns != "minecraft":
        return fail(f"{where}: unexpected namespace in '{ident}'")
    if path not in REG.get(registry, []):
        fail(f"{where}: '{ident}' is not in the vanilla {registry} registry")


def walk(obj, fn, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            fn(k, v, f"{path}.{k}")
            walk(v, fn, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, fn, f"{path}[{i}]")


def read(rel):
    with open(os.path.join(RES, rel), encoding="utf-8") as fh:
        return json.load(fh)


def files(subdir, ext=".json"):
    base = os.path.join(RES, subdir)
    out = []
    for dirpath, _dirs, names in os.walk(base):
        for n in sorted(names):
            if n.endswith(ext):
                full = os.path.join(dirpath, n)
                out.append((os.path.relpath(full, RES),
                            os.path.relpath(full, base)[:-len(ext)]))
    return out


# --------------------------------------------------------------------------
# 0. every JSON file parses
# --------------------------------------------------------------------------
ALL_JSON = []
for dirpath, _d, names in os.walk(RES):
    for n in names:
        if n.endswith(".json"):
            rel = os.path.relpath(os.path.join(dirpath, n), RES)
            ALL_JSON.append(rel)
            try:
                read(rel)
                checks[0] += 1
            except Exception as exc:                       # noqa: BLE001
                fail(f"{rel}: invalid JSON - {exc}")

OUR_ENCH = {n for _r, n in files(f"data/{MOD_ID}/enchantment")}
OUR_DAMAGE = {n for _r, n in files(f"data/{MOD_ID}/damage_type")}
OUR_PAINTING = {n for _r, n in files(f"data/{MOD_ID}/painting_variant")}
OUR_RECIPES = {n for _r, n in files(f"data/{MOD_ID}/recipe")}
OUR_LOOT = {n.replace(os.sep, "/") for _r, n in files(f"data/{MOD_ID}/loot_table")}
OUR_ITEM_DEFS = {n for _r, n in files(f"assets/{MOD_ID}/items")}
OUR_MODELS = {n.replace(os.sep, "/") for _r, n in files(f"assets/{MOD_ID}/models")}
OUR_EQUIPMENT = {n for _r, n in files(f"assets/{MOD_ID}/equipment")}

ENCH_EFFECT_TYPES = set(REG["enchantment_entity_effect_type"]) | \
    set(REG["enchantment_value_effect_type"]) | \
    set(REG["enchantment_location_based_effect_type"]) | \
    set(REG["loot_number_provider_type"])          # e.g. enchantment_level in chances
LEVEL_TYPES = set(REG["enchantment_level_based_value_type"])
SLOT_GROUPS = {"any", "mainhand", "offhand", "hand", "feet", "legs", "chest",
               "head", "armor", "body", "saddle"}


def check_components(comps, where):
    """A data component map: keys must be real components, values sane ids."""
    for key, val in comps.items():
        known("data_component_type", key, f"{where} component key")
        if key == "minecraft:enchantments":
            for eid, lvl in val.items():
                known("enchantment", eid, f"{where} enchantment", OUR_ENCH)
                checks[0] += 1
                if not isinstance(lvl, int) or not 1 <= lvl <= 255:
                    fail(f"{where}: enchantment level {lvl} for {eid} out of range")
        elif key == "minecraft:attribute_modifiers":
            for m in val:
                known("attribute", m["type"], f"{where} modifier")
                checks[0] += 1
                if m.get("slot") not in SLOT_GROUPS:
                    fail(f"{where}: bad attribute slot {m.get('slot')!r}")
        elif key == "minecraft:equippable":
            if val.get("slot") not in SLOT_GROUPS:
                fail(f"{where}: bad equippable slot {val.get('slot')!r}")
            if "equip_sound" in val:
                known("sound_event", val["equip_sound"], f"{where} equip_sound")
            asset = val.get("asset_id")
            checks[0] += 1
            if asset and asset.startswith(f"{MOD_ID}:") and \
                    asset.split(":", 1)[1] not in OUR_EQUIPMENT:
                fail(f"{where}: equippable asset_id '{asset}' has no equipment file")
        elif key == "minecraft:item_model":
            checks[0] += 1
            if val.startswith(f"{MOD_ID}:") and val.split(":", 1)[1] not in OUR_ITEM_DEFS:
                fail(f"{where}: item_model '{val}' has no assets/{MOD_ID}/items entry")

        def mob_effects(k, v, p):
            if k == "id" and isinstance(v, str) and ".effects[" in p:
                known("mob_effect", v, f"{where}{p}")
        walk(val, mob_effects, f".{key}")


# --------------------------------------------------------------------------
# 1. enchantments
# --------------------------------------------------------------------------
ENCH_KEYS = {"description", "exclusive_set", "supported_items", "primary_items",
             "weight", "max_level", "min_cost", "max_cost", "anvil_cost",
             "slots", "effects"}

for rel, name in files(f"data/{MOD_ID}/enchantment"):
    e = read(rel)
    checks[0] += 1
    unknown = set(e) - ENCH_KEYS
    if unknown:
        fail(f"{rel}: unknown enchantment fields {sorted(unknown)}")
    for req in ("description", "supported_items", "weight", "max_level",
                "min_cost", "max_cost", "anvil_cost", "slots", "effects"):
        if req not in e:
            fail(f"{rel}: missing required field '{req}'")
    for slot in e.get("slots", []):
        checks[0] += 1
        if slot not in SLOT_GROUPS:
            fail(f"{rel}: bad slot {slot!r}")
    if not 1 <= e.get("max_level", 0) <= 255:
        fail(f"{rel}: max_level {e.get('max_level')} out of range")
    for field in ("supported_items", "primary_items"):
        if field in e:
            v = e[field]
            checks[0] += 1
            if isinstance(v, str) and v.startswith("#minecraft:"):
                if v[1:].split(":", 1)[1] not in REG["tag/item"]:
                    fail(f"{rel}: {field} references unknown item tag {v}")
            elif isinstance(v, str):
                known("item", v, f"{rel} {field}")
    if "exclusive_set" in e:
        v = e["exclusive_set"]
        checks[0] += 1
        if v.startswith(f"#{MOD_ID}:"):
            tag = v.split(":", 1)[1]
            if not os.path.exists(os.path.join(
                    RES, f"data/{MOD_ID}/tags/enchantment/{tag}.json")):
                fail(f"{rel}: exclusive_set tag {v} has no tag file")
        elif v.startswith("#minecraft:"):
            if v[1:].split(":", 1)[1] not in REG["tag/enchantment"]:
                fail(f"{rel}: unknown vanilla enchantment tag {v}")

    for comp in e["effects"]:
        known("enchantment_effect_component_type", comp, f"{rel} effects key")

    def ench_ids(k, v, p, rel=rel):
        if k == "type" and isinstance(v, str):
            base = v.split(":", 1)[-1]
            if base in ENCH_EFFECT_TYPES or base in LEVEL_TYPES:
                checks[0] += 1
                return
            if base in ("in_bounding_box", "entity_position"):
                return
            if p.endswith(".particle.type"):
                return known("particle_type", v, f"{rel}{p}")
            fail(f"{rel}{p}: unrecognised effect type '{v}'")
        elif k == "attribute":
            known("attribute", v, f"{rel}{p}")
        elif k == "to_apply":
            known("mob_effect", v, f"{rel}{p}")
        elif k == "sound":
            known("sound_event", v, f"{rel}{p}")
        elif k == "entity" and p.endswith(".entity") and isinstance(v, str) \
                and v not in ("this", "attacker", "victim", "direct_attacker"):
            known("entity_type", v, f"{rel}{p}")
        elif k == "damage_type":
            known("damage_type", v, f"{rel}{p}", OUR_DAMAGE)
        elif k == "condition":
            known("loot_condition_type", v, f"{rel}{p}")
    walk(e["effects"], ench_ids, "")


# --------------------------------------------------------------------------
# 2. recipes
# --------------------------------------------------------------------------
def check_ingredient(v, where):
    if isinstance(v, str):
        if v.startswith("#"):
            checks[0] += 1
            if v[1:].split(":", 1)[-1] not in REG["tag/item"]:
                fail(f"{where}: unknown item tag {v}")
        else:
            known("item", v, where)
    elif isinstance(v, list):
        for i in v:
            check_ingredient(i, where)
    else:
        fail(f"{where}: bad ingredient {v!r}")


for rel, name in files(f"data/{MOD_ID}/recipe"):
    r = read(rel)
    known("recipe_serializer", r["type"], f"{rel} type")
    if r["type"] == "minecraft:crafting_shaped":
        pattern = r["pattern"]
        checks[0] += 1
        if not 1 <= len(pattern) <= 3 or any(not 1 <= len(row) <= 3 for row in pattern):
            fail(f"{rel}: pattern must be at most 3x3, got {pattern}")
        if len({len(row) for row in pattern}) != 1:
            fail(f"{rel}: pattern rows have differing widths: {pattern}")
        used = {ch for row in pattern for ch in row if ch != " "}
        declared = set(r["key"])
        if used - declared:
            fail(f"{rel}: pattern uses undeclared keys {sorted(used - declared)}")
        if declared - used:
            fail(f"{rel}: key declares unused symbols {sorted(declared - used)}")
        for sym, ing in r["key"].items():
            check_ingredient(ing, f"{rel} key[{sym}]")
    elif r["type"] == "minecraft:crafting_shapeless":
        checks[0] += 1
        if not 1 <= len(r["ingredients"]) <= 9:
            fail(f"{rel}: shapeless needs 1-9 ingredients")
        for i, ing in enumerate(r["ingredients"]):
            check_ingredient(ing, f"{rel} ingredients[{i}]")
    res = r["result"]
    known("item", res["id"], f"{rel} result")
    if "components" in res:
        check_components(res["components"], rel)


# --------------------------------------------------------------------------
# 3. loot tables
# --------------------------------------------------------------------------
for rel, name in files(f"data/{MOD_ID}/loot_table"):
    t = read(rel)
    for pi, pool in enumerate(t["pools"]):
        for ei, entry in enumerate(pool["entries"]):
            known("loot_pool_entry_type", entry["type"], f"{rel} pool{pi} entry{ei}")
            if entry["type"] == "minecraft:item":
                known("item", entry["name"], f"{rel} pool{pi} entry{ei} name")
            for fn in entry.get("functions", []):
                known("loot_function_type", fn["function"], f"{rel} function")
                if fn["function"] == "minecraft:set_components":
                    check_components(fn["components"], rel)


# --------------------------------------------------------------------------
# 4. advancements
# --------------------------------------------------------------------------
FRAMES = {"task", "goal", "challenge"}
adv_names = {n.replace(os.sep, "/") for _r, n in files(f"data/{MOD_ID}/advancement")}
for rel, name in files(f"data/{MOD_ID}/advancement"):
    a = read(rel)
    for cname, crit in a["criteria"].items():
        known("trigger_type", crit["trigger"], f"{rel} criteria[{cname}] trigger")
        for item in crit.get("conditions", {}).get("items", []):
            known("item", item["items"], f"{rel} criteria[{cname}] item")
            if "components" in item:
                check_components(item["components"], rel)
    flat = {c for group in a["requirements"] for c in group}
    checks[0] += 1
    if flat != set(a["criteria"]):
        fail(f"{rel}: requirements {sorted(flat)} do not match criteria "
             f"{sorted(a['criteria'])}")
    if "parent" in a:
        checks[0] += 1
        parent = a["parent"].split(":", 1)[1]
        if parent not in adv_names:
            fail(f"{rel}: parent '{a['parent']}' does not exist")
    if "display" in a:
        d = a["display"]
        checks[0] += 1
        if d.get("frame", "task") not in FRAMES:
            fail(f"{rel}: bad frame {d.get('frame')!r}")
        known("item", d["icon"]["id"], f"{rel} display icon")
        if "components" in d["icon"]:
            check_components(d["icon"]["components"], rel)
    for recipe in a.get("rewards", {}).get("recipes", []):
        checks[0] += 1
        if recipe.split(":", 1)[1] not in OUR_RECIPES:
            fail(f"{rel}: reward recipe '{recipe}' does not exist")
    for loot in a.get("rewards", {}).get("loot", []):
        checks[0] += 1
        if loot.split(":", 1)[1] not in OUR_LOOT:
            fail(f"{rel}: reward loot table '{loot}' does not exist")


# --------------------------------------------------------------------------
# 5. tags, paintings, damage types
# --------------------------------------------------------------------------
TAG_REGISTRY = {"enchantment": "enchantment", "painting_variant": "painting_variant"}
for rel, _n in files("data/minecraft/tags") + files(f"data/{MOD_ID}/tags"):
    t = read(rel)
    kind = rel.split("tags/", 1)[1].split("/", 1)[0]
    registry = TAG_REGISTRY.get(kind)
    ours = {"enchantment": OUR_ENCH, "painting_variant": OUR_PAINTING}.get(kind, set())
    for v in t["values"]:
        if registry:
            known(registry, v, f"{rel} value", ours)

for rel, name in files(f"data/{MOD_ID}/painting_variant"):
    p = read(rel)
    checks[0] += 1
    if not (1 <= p["width"] <= 16 and 1 <= p["height"] <= 16):
        fail(f"{rel}: painting size out of range")
    asset = p["asset_id"].split(":", 1)[1]
    tex = os.path.join(RES, f"assets/{MOD_ID}/textures/painting/{asset}.png")
    checks[0] += 1
    if not os.path.exists(tex):
        fail(f"{rel}: missing painting texture {asset}.png")
    else:
        from PIL import Image
        w, h = Image.open(tex).size
        checks[0] += 1
        if (w, h) != (p["width"] * 16, p["height"] * 16):
            fail(f"{rel}: texture is {w}x{h}, expected "
                 f"{p['width'] * 16}x{p['height'] * 16}")

for rel, name in files(f"data/{MOD_ID}/damage_type"):
    d = read(rel)
    checks[0] += 1
    if d.get("scaling") not in ("never", "when_caused_by_living_non_player", "always"):
        fail(f"{rel}: bad scaling {d.get('scaling')!r}")
    if "message_id" not in d or "exhaustion" not in d:
        fail(f"{rel}: damage type needs message_id and exhaustion")


# --------------------------------------------------------------------------
# 6. client assets: models, item definitions, equipment, textures
# --------------------------------------------------------------------------
def texture_path(ident):
    ns, _, path = ident.partition(":")
    if not path:
        ns, path = "minecraft", ns
    return ns, os.path.join(RES, f"assets/{ns}/textures/{path}.png")


VANILLA_MODEL_PARENTS = {"minecraft:item/generated", "minecraft:item/handheld",
                         "minecraft:item/bow", "minecraft:item/handheld_rod"}
for rel, name in files(f"assets/{MOD_ID}/models"):
    m = read(rel)
    parent = m.get("parent")
    checks[0] += 1
    if parent and parent.startswith("minecraft:") and parent not in VANILLA_MODEL_PARENTS:
        fail(f"{rel}: unexpected vanilla parent '{parent}' (not on the known list)")
    for layer, ident in m.get("textures", {}).items():
        ns, path = texture_path(ident)
        checks[0] += 1
        if ns == MOD_ID and not os.path.exists(path):
            fail(f"{rel}: {layer} points at missing texture {ident}")

referenced_models = set()
for rel, name in files(f"assets/{MOD_ID}/items"):
    d = read(rel)

    def collect(k, v, p):
        if k == "model" and isinstance(v, str):
            referenced_models.add(v)
    walk(d, collect)
    if isinstance(d["model"].get("model"), str):
        referenced_models.add(d["model"]["model"])

for ident in sorted(referenced_models):
    ns, _, path = ident.partition(":")
    checks[0] += 1
    if ns == MOD_ID and path not in OUR_MODELS:
        fail(f"item definition references missing model '{ident}'")

for rel, name in files(f"assets/{MOD_ID}/equipment"):
    eq = read(rel)
    for layer, entries in eq["layers"].items():
        checks[0] += 1
        if layer not in ("humanoid", "humanoid_leggings", "horse_body",
                         "llama_body", "wolf_body", "wings"):
            fail(f"{rel}: unexpected equipment layer '{layer}'")
        for entry in entries:
            ns, _, path = entry["texture"].partition(":")
            tex = os.path.join(
                RES, f"assets/{ns}/textures/entity/equipment/{layer}/{path}.png")
            checks[0] += 1
            if ns == MOD_ID and not os.path.exists(tex):
                fail(f"{rel}: layer {layer} missing texture {entry['texture']}")
            elif os.path.exists(tex):
                from PIL import Image
                if Image.open(tex).size != (64, 32):
                    fail(f"{rel}: {tex} must be 64x32")

bg = os.path.join(RES,
                  f"assets/{MOD_ID}/textures/gui/advancements/backgrounds/starforge.png")
checks[0] += 1
if not os.path.exists(bg):
    fail("missing advancement background texture")

from PIL import Image  # noqa: E402
for rel in sorted(os.path.relpath(os.path.join(dp, n), RES)
                  for dp, _d, ns_ in os.walk(os.path.join(RES, f"assets/{MOD_ID}/textures/item"))
                  for n in ns_ if n.endswith(".png")):
    w, h = Image.open(os.path.join(RES, rel)).size
    checks[0] += 1
    if (w, h) != (16, 16):
        fail(f"{rel}: item textures must be 16x16, got {w}x{h}")


# --------------------------------------------------------------------------
# 7. functions and mod metadata
# --------------------------------------------------------------------------
for dirpath, _d, names in os.walk(os.path.join(RES, f"data/{MOD_ID}/function")):
    for n in sorted(names):
        if not n.endswith(".mcfunction"):
            continue
        rel = os.path.relpath(os.path.join(dirpath, n), RES)
        with open(os.path.join(RES, rel), encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                checks[0] += 1
                if line.startswith("tellraw "):
                    payload = line.split(" ", 2)[2]
                    try:
                        json.loads(payload)
                    except Exception as exc:               # noqa: BLE001
                        fail(f"{rel}:{lineno}: tellraw payload is not JSON - {exc}")
                if " loot " in line and f"{MOD_ID}:" in line:
                    ref = line.rsplit(" ", 1)[-1].split(":", 1)[1]
                    if ref not in OUR_LOOT:
                        fail(f"{rel}:{lineno}: references missing loot table '{ref}'")

fm = read("fabric.mod.json")
checks[0] += 1
for field in ("schemaVersion", "id", "version", "name", "description", "license",
              "icon", "environment", "depends"):
    if field not in fm:
        fail(f"fabric.mod.json: missing '{field}'")
if fm.get("id") != MOD_ID:
    fail(f"fabric.mod.json: id is {fm.get('id')!r}")
icon = os.path.join(RES, fm["icon"])
checks[0] += 1
if not os.path.exists(icon):
    fail(f"fabric.mod.json: icon {fm['icon']} does not exist")
else:
    w, h = Image.open(icon).size
    checks[0] += 1
    if w != h:
        fail(f"mod icon must be square, got {w}x{h}")
checks[0] += 1
if "~1.21.11" not in fm["depends"].get("minecraft", ""):
    fail("fabric.mod.json: minecraft dependency should target 1.21.11")
if fm["depends"].get("java") != ">=21":
    fail("fabric.mod.json: java dependency should be >=21")


# --------------------------------------------------------------------------
print(f"checked {len(ALL_JSON)} JSON files, {checks[0]} assertions")
if errors:
    print(f"\n{len(errors)} PROBLEM(S):")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("all checks passed")
