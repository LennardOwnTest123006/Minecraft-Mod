# One-time welcome so it is obvious the mod loaded.
scoreboard players set @s starforge.seen 1
tellraw @s [{"text":"","italic":false},{"text":"[Starforge] ","italic":false,"color":"gold","bold":true},{"text":"loaded - 16 relics and 12 new enchantments are active.","italic":false,"color":"white"}]
tellraw @s [{"text":"","italic":false},{"text":"Every recipe is already in your ","italic":false,"color":"gray"},{"text":"recipe book","italic":false,"color":"aqua"},{"text":". Start with a ","italic":false,"color":"gray"},{"text":"Starsteel Shard","italic":false,"color":"aqua"},{"text":" (amethyst shard + copper ingot).","italic":false,"color":"gray"}]
tellraw @s [{"text":"","italic":false},{"text":"Craft the ","italic":false,"color":"gray"},{"text":"Starforge Codex","italic":false,"color":"gold"},{"text":" (book + amethyst shard) to read the full guide in game.","italic":false,"color":"gray"}]
