# Hands the player the complete Starforge arsenal.
# Usage:  /function starforge:arsenal
loot give @s loot starforge:arsenal
playsound minecraft:block.beacon.activate master @s ~ ~ ~ 1 1.4
tellraw @s [{"text":"","italic":false},{"text":"[Starforge] ","italic":false,"color":"gold","bold":true},{"text":"The forge answers. The full arsenal is yours.","italic":false,"color":"white"}]
