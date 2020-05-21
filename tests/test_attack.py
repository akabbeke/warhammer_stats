from unittest import TestCase

from warhammer_stats import Attack, Weapon, Target, PMFCollection
from warhammer_stats.modifiers import ModifierCollection, ReRollOnes

import warhammer_stats

class TestAttack(TestCase):
    def test_is_string(self):
        # Re-roll ones to hit modifier
        weapon_mods = ModifierCollection(hit_mods=[ReRollOnes()])

        # Sample weapon and target
        weapon = Weapon(bs=4, shots=PMFCollection.static(10), strength=4, ap=0, damage=PMFCollection.static(1))
        target = Target(toughness=4, save=4, invuln=7, fnp=7, wounds=7)

        # Attack with no modifier
        no_modifier = Attack(weapon, target).run().damage_dist.mean()

        # Should be 1.25 = 10(shots) * 0.5(hit) * 0.5(wound) * 0.5(failed save)
        # Rounding here due to float precision
        self.assertEqual(round(no_modifier, 10), 1.25)

        # Add the modifier
        weapon.modifiers = weapon_mods

        # Attack with no modifier
        with_modifier = Attack(weapon, target).run().total_wounds_dist.mean()

        # Should be ~1.4583 = 1.25 *(7/6) times higher now
        self.assertEqual(round(with_modifier, 10), round(no_modifier * (7/6), 10) )
