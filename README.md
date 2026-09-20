<p align="center">
  <img src="src/main/resources/assets/starforge/icon.png" width="128" alt="Starforge logo">
</p>

<h1 align="center">Starforge</h1>

<p align="center">
  An endgame star-metal arsenal for <b>Minecraft 1.21.11</b> · <b>Fabric</b> · <b>Java 21</b>
</p>

---

Starforge takes your world past netherite. Refine star-metal out of the void,
fold a dead star into an Astral Core, and forge an arsenal that comes with its
own artwork, its own armour set, and **twelve new enchantments** that show up at
the enchanting table, the anvil and in villager trades.

## Requirements

| | |
|---|---|
| Minecraft | 1.21.11 |
| Mod loader | Fabric Loader 0.16.0 or newer |
| Required mod | **Fabric API** |
| Java | 21 or newer |

## Installation

1. Install the Fabric loader for Minecraft 1.21.11.
2. Drop **Fabric API** into your `mods` folder.
3. Drop `starforge-1.1.0.jar` into the same `mods` folder.
4. Launch the Fabric profile.

## Is it working?

Load a world and you should get a chat line within a second:

> **[Starforge]** loaded - 16 relics and 12 new enchantments are active.

If you see that, the mod is running. If you don't, Starforge did not load —
check that **Fabric API** is installed and that the game is on 1.21.11.

Two more things you can check in ten seconds:

* Open your **recipe book** — every Starforge recipe is unlocked from the start.
* Put anything on an **enchanting table** — Starfall, Aegis, Voidstep and the
  rest show up alongside the vanilla enchantments.

> **Note on the creative menu.** Starforge relics do **not** appear as separate
> entries in the creative inventory. They are built as vanilla items carrying
> custom components, models and textures, so you get them by **crafting** them
> (or with `/function starforge:arsenal` if cheats are on) — not by scrolling
> the creative tabs. Adding brand-new entries to the creative inventory needs a
> compiled Java mod; see [Why there is no Java code](#why-there-is-no-java-code).

## What it adds

### Early tier — craftable in your first hour

| Item | Recipe |
|---|---|
| **Starsteel Shard** | amethyst shard + copper ingot |
| **Starforge Codex** | book + amethyst shard — the full guide, readable in game |
| **Emberbrand** | amethyst shard, iron sword and copper ingot in a column |

The Emberbrand carries Cinderbrand II and Starfall II, so Starforge is worth
something long before the Wither.

### Materials

| Item | Made from |
|---|---|
| **Starsteel Ingot** | netherite ingot + echo shards + blaze powder + amethyst |
| **Voidshard** | echo shard + amethyst + ender pearl + obsidian |
| **Astral Core** | a nether star ringed with starsteel and voidshards |

### The arsenal

| Relic | Highlights |
|---|---|
| **Starfall Blade** | 13 attack damage, extra reach, Starfall V, Cinderbrand III, Stormcaller III, Soulrend III |
| **Worldbreaker** | mace that turns every block you fall into damage — Skybreaker V, Wind Burst III |
| **Voidpiercer** | bow with Power VII, Punch IV, Flame and Infinity, with its own draw animation |
| **Starforge Pickaxe** | Quarrymind V, Fortune V, Efficiency VIII, extended reach |
| **Starforge plate** | helm, cuirass, greaves and sabatons with a custom worn-armour texture |
| **Heart of the Star** | a totem that brings you back with Regeneration IV, Absorption V and Resistance III |
| **Astral Elixir** | bottled starlight — six stacked buffs, and it stacks to 16 |

Every relic is crafted from a nether star plus its vanilla counterpart, so the
endgame progression stays gated behind the Wither.

### Enchantments

`Starfall` · `Cinderbrand` · `Soulrend` · `Stormcaller` · `Skybreaker` ·
`Aegis` · `Titanheart` · `Voidstep` · `Gravitas` · `Starlight` · `Quarrymind` ·
`Eternal`

Nine of them appear in the enchanting table. Titanheart, Gravitas and
Stormcaller are treasure enchantments — trades, loot and the anvil only.

### Also included

* A 14-step advancement tree on its own tab, with a custom background.
* Three paintings: *Voidgate*, *Forgeheart* and *Starfall*.
* A `starforge:soulrend` damage type with its own death messages.
* `/function starforge:arsenal` hands you the complete set (for creative and testing).
* `/function starforge:help` prints a short in-game guide.

## Why there is no Java code

Starforge is a **content-only Fabric mod**: it ships `assets/` and `data/` and
no compiled classes. Everything here — enchantments, gear, recipes, loot,
advancements, paintings, damage types — is data the game loads directly.

The trade-off is the one called out above: data alone cannot register a brand
new item into the item registry, so the relics ride on vanilla base items with
custom components and textures instead of appearing as separate creative-menu
entries. Everything else behaves like a normal modded item — its own name,
art, stats, durability and enchantments.

## Building from source

Starforge is a **content-only Fabric mod**: it ships no compiled classes, so it
needs no Gradle, no Loom and no Minecraft jar to build. Everything — artwork
included — is generated from the scripts in `tools/`.

```sh
python3 -m pip install Pillow
python3 tools/gen_textures.py     # draw every PNG, including the logo
python3 tools/gen_content.py      # emit every JSON and mcfunction
python3 tools/validate.py         # check it all against real 1.21.11 data
python3 tools/build_jar.py        # zip it into build/starforge-1.0.0.jar
```

`tools/validate.py` downloads the vanilla 1.21.11 registry dump once (cached in
`.cache/`) and checks every item, enchantment, attribute, particle, sound, mob
effect, loot function, advancement trigger and data component the mod
references against it, plus every texture, model, function tag and loot table
reference on disk — 1679 assertions in total.

## Layout

```
src/main/resources/
├── fabric.mod.json
├── assets/starforge/
│   ├── icon.png              mod logo (256x256)
│   ├── items/                item model definitions
│   ├── models/item/          item models
│   ├── equipment/            worn-armour asset
│   ├── lang/en_us.json
│   └── textures/             item, armour, painting and GUI art
└── data/
    ├── starforge/            enchantments, recipes, loot, advancements,
    │                         functions, paintings, damage types, tags
    └── minecraft/tags/       hooks into the enchanting table and trades
```

## License

MIT — see [LICENSE](LICENSE).
