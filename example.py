from warhammer_stats import Attack, Weapon, Target, PMFCollection
from warhammer_stats.modifiers import ModifierCollection, ReRollOnes

weapon_mods = ModifierCollection(hit_mods=[ReRollOnes()])
weapon = Weapon(bs=4, shots=PMFCollection.static(10), strength=4, ap=0, damage=PMFCollection.static(1), modifiers=weapon_mods)
target = Target(toughness=4, save=4, invuln=7, fnp=7, wounds=7)

attack = Attack(weapon, target)

result = attack.run()
print(10*(7/6)*0.5*0.5*0.5)
print(result.damage_with_mortals.mean())