from warhammer_stats import Attack, MultiAttack, PMFCollection, Target, Weapon
from warhammer_stats.modifiers.splitter_modifiers import \
    OnAModifiableRollOfNAddAP
from warhammer_stats.utils.modifier_collection import ModifierCollection

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
    modifiers=weapon_mods,
    name='Shuriken Catapult',
)

# Define the weapon. In this case it is a bolter with 2 shots, strength 4, AP 0 and damage 1.
battle_canon = Weapon(
    bs=4,
    shots=PMFCollection.mdn(2, 6),
    strength=8,
    ap=2,
    damage=PMFCollection.mdn(1, 3),
    name='Battle Canon',
)

# Define the target. In this case it is a space marine eradicator with three wounds.
# He has no invulnerable or FNP so both are 7+ saves. He has a 4+ save.
space_marine = Target(
    toughness=4,
    save=3,
    invuln=7,
    fnp=7,
    wounds=2,
    name='Space Marine',
)

shuriken_results = Attack(shuriken_catapult, space_marine).run()
battle_canon_results = Attack(battle_canon, space_marine).run()
combined_results = MultiAttack([shuriken_catapult, battle_canon], space_marine).run()

# Print the mean of the kill distribution

print('shuriken_results', shuriken_results)
print('battle_canon_results', battle_canon_results)
print('combined_results', combined_results)


# If we want we can drill down into the results and see the probability distribution for each phase.
# For example, we can see the full probability distribution for the number of kills.
print('battle_canon_results.kills_dist', battle_canon_results.kills_dist)


# We can also see the cumulative probability distribution for the number of kills.
print('battle_canon_results.kills_dist.cumulative', battle_canon_results.kills_dist.cumulative())