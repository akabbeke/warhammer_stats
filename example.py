from warhammer_stats import Attack, Weapon, Target, PMFCollection
from warhammer_stats.modifiers import ModifierCollection, ReRollOnes

# Define a re-roll ones weapon modifier
weapon_mods = ModifierCollection(
    hit_mods=[ReRollOnes()]
)

# Define the weapon. In this case it is the relic battle cannon with
# flat three damage. It is firing twice so we specify two D6s as the
# number of shots. We specify that we are using the re-roll ones
# modifier.
weapon = Weapon(
    bs=3,
    shots=PMFCollection.mdn(2, 6),
    strength=4,
    ap=2,
    damage=PMFCollection.static(3),
    modifiers=weapon_mods
)

# Define the target. In this case it is a space marine with one wound.
# He has no invulnerable or FNP so both are 7+ saves.
target = Target(
    toughness=4,
    save=3,
    invuln=7,
    fnp=7,
    wounds=1
)

# Create an attack with the weapon and target.
attack = Attack(weapon, target)

# Run the calculation.
result = attack.run()

# Print the mean of the damage distribution
print(f'Average: {result.damage_dist.mean()}')

# Get the probabiltiy of scoring EXACTLY two wounds
print(f'Probabiltiy == 2: {result.damage_dist.get(2)}')

# Get the probabiltiy of scoring AT LEAST two wounds
print(f'Probabiltiy >= 2: {result.damage_dist.cumulative().get(2)}')

# Print the full PMF
print(result.damage_dist.values)
