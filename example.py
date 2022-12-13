from warhammer_stats import Attack, Weapon, Target, PMFCollection
from warhammer_stats.utils.modifier_collection import ModifierCollection
from warhammer_stats.modifiers.splitter_modifiers import OnAModifiableRollOfNAddAP

# Define a modifier such that on a 6 to wound, add 3 AP to the
# attack.
weapon_mods = ModifierCollection(
    wound_mods=[OnAModifiableRollOfNAddAP(6, 3)]
)

# Define the weapon. In this case it is a shuriken catapult with 2 shots, strength 4, AP 0 and damage 1.
# It has the modifiers defined above.
shuriken_catapult = Weapon(
    bs=4,
    shots=PMFCollection.static(2),
    strength=4,
    ap=0,
    damage=PMFCollection.static(1),
    modifiers=weapon_mods
)

# Define the weapon. In this case it is a bolter with 2 shots, strength 4, AP 0 and damage 1.
bolter = Weapon(
    bs=4,
    shots=PMFCollection.static(2),
    strength=4,
    ap=0,
    damage=PMFCollection.static(1),
)

# Define the target. In this case it is a space marine eradicator with three wounds.
# He has no invulnerable or FNP so both are 7+ saves. He has a 4+ save.
space_marine = Target(
    toughness=4,
    save=3,
    invuln=7,
    fnp=7,
    wounds=2
)

shuriken_results = Attack(shuriken_catapult, space_marine).run()
bolter_results = Attack(bolter, space_marine).run()

# Print the mean of the kill distribution
print(f'Average: {shuriken_results.total_damage_dist.mean()}')

print(f'Average: {bolter_results.total_damage_dist.mean()}')

print(shuriken_results.total_damage_dist.mean()/bolter_results.total_damage_dist.mean())
