# Runs every tick (minecraft:tick tag).
execute as @a unless score @s starforge.seen matches 1.. run function starforge:greet
