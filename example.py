from warhammer_stats import Attack, Weapon, Target, PMFCollection
from warhammer_stats.modifiers import ModifierCollection, ReRollOnes

# Define a re-roll ones weapon modifier
weapon_mods = ModifierCollection(
    hit_mods=[ReRollOnes()]
)

# Define the weapon. In this case it is the battle cannon with
# d3 damage. It is firing twice so we specify two D6s as the
# number of shots. We specify that we are using the re-roll ones
# modifier.
weapon = Weapon(
    bs=3,
    shots=PMFCollection.mdn(2, 6),
    strength=8,
    ap=3,
    damage=PMFCollection.mdn(1, 6),
    modifiers=weapon_mods
)

# Define the target. In this case it is a space marine eradicator with three wounds.
# He has no invulnerable or FNP so both are 7+ saves.
target = Target(
    toughness=4,
    save=3,
    invuln=7,
    fnp=7,
    wounds=3
)

# Create an attack with the weapon and target.
attack = Attack(weapon, target, True)

# Run the calculation.
result = attack.run()

# Print the mean of the kill distribution
print(f'Average: {result.kill_dist.mean()}')

# Get the probabiltiy of scoring EXACTLY two kills
print(f'Probabiltiy == 2: {result.kill_dist.get(2)}')

# Get the probabiltiy of scoring AT LEAST two kills
print(f'Probabiltiy >= 2: {result.kill_dist.cumulative().get(2)}')

# Print the full PMF
print(result.kill_dist.cumulative().values)

