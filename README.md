# Warhammer Stats
This is a Python library providing components to generate PMFs for Warhammer 40000. This code was taken from the backend of https://www.warhammer-stats-engine.com/ and split out into its own package to make is easier for other developers to use.

# Usage
You can use pip to fetch the latest version of the library. https://pypi.org/project/warhammer-stats/

`pipenv install warhammer-stats`

# Example Usage
The example script:

```python
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

```

Output:

```bash
> python example.py
shuriken_results AttackResults(
  Mortal Wounds        - avg: 0.0000, std: 0.0000
  Self Wounds          - avg: 0.0000, std: 0.0000
  Total Damage         - avg: 0.2083, std: 0.4320
  Kills                - avg: 0.0109, std: 0.1036
)
battle_canon_results AttackResults(
  Mortal Wounds        - avg: 0.0000, std: 0.0000
  Self Wounds          - avg: 0.0000, std: 0.0000
  Total Damage         - avg: 3.2406, std: 2.3625
  Kills                - avg: 1.4002, std: 1.1346
)
combined_results AttackResults(
  Mortal Wounds        - avg: 0.0000, std: 0.0000
  Self Wounds          - avg: 0.0000, std: 0.0000
  Total Damage         - avg: 3.4489, std: 2.4017
  Kills                - avg: 1.4111, std: 1.1394
)
battle_canon_results.kills_dist [0.2307, 0.3573, 0.2522, 0.1132, 0.0362, 0.0086, 0.0016, 0.0002, 0.0, 0.0]
battle_canon_results.kills_dist.cumulative [1.0, 0.7693, 0.412, 0.1598, 0.0466, 0.0104, 0.0018, 0.0002, 0.0, 0.0]
```