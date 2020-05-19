from warhammer_stats import Attack, Weapon, Target, PMFCollection
from warhammer_stats.modifiers import ModifierCollection, ReRollOnes

# Define a re-roll ones weapon modifier
weapon_mods = ModifierCollection(hit_mods=[ReRollOnes()])

# Define the weapon. In this case it is a clasic boltgun hitting on a 4+
weapon = Weapon(
    bs=4,
    shots=PMFCollection.static(10),
    strength=4,
    ap=0,
    damage=PMFCollection.static(1),
    modifiers=weapon_mods
)

# Define the target. In this case it is a space marine
target = Target(
    toughness=4,
    save=3,
    invuln=7,
    fnp=7,
    wounds=1
)

# Create an attack
attack = Attack(weapon, target)

# Run the calculation
result = attack.run()

# print the mean of the damage distribution
print(f'Average wounds: {result.damage_dist.mean()}')