from unittest import TestCase

from warhammer_stats import Attack, Weapon, Target, PMFCollection
from warhammer_stats.utils.modifier_collection import ModifierCollection
from warhammer_stats.modifiers.additive_modifiers import AddNToAP, AddND6, AddND3, AddNToInvuln, AddNToSave, AddNToThreshold, AddNToVolume
from warhammer_stats.modifiers.generator_modifiers import (GenerateD3MortalWoundsModifiable, GenerateD3MortalWoundsUnmodifiable,
                                                           GenerateD6MortalWoundsModifiable, GenerateD6MortalWoundsUnmodifiable,
                                                           GenerateExtraAutomaticHitsModifiable, GenerateExtraAutomaticHitsUnmodifiable,
                                                           GenerateExtraAutomaticWoundsModifiable, GenerateExtraAutomaticWoundsUnmodifiable,
                                                           GenerateMortalWoundsModifiable, GenerateExtraHitRollsModifiable,
                                                           GenerateExtraHitRollsUnmodifiable, GenerateMortalWoundsUnmodifiable)
from warhammer_stats.modifiers.reroll_modifiers import ReRollAll, ReRollFailed, ReRollLessThanExpectedValue, ReRollOneDice, ReRollOneDiceVolume, ReRollOnes
from warhammer_stats.modifiers.splitter_modifiers import OnAModifiableRollOfNAddAP, OnAModifiableRollOfNAddDamage, OnAnUnmodifiableRollOfNAddAP, OnAnUnmodifiableRollOfNAddDamage
class TestAttack(TestCase):
    def test_every_modifiers(self):
        # Re-roll ones to hit modifier
        weapon_mods = ModifierCollection(
            attacks_mods=[AddND3(1), AddNToVolume(1), ReRollOneDiceVolume()],
            hit_mods=[
                AddNToThreshold(1),
                GenerateExtraAutomaticHitsModifiable(6, 1),
                GenerateExtraAutomaticHitsUnmodifiable(6, 1),
                GenerateExtraAutomaticWoundsModifiable(6, 1),
                GenerateMortalWoundsModifiable(6, 1),
                GenerateExtraHitRollsModifiable(6, 1),
                GenerateExtraHitRollsUnmodifiable(6, 1),
                ReRollFailed(),
                OnAModifiableRollOfNAddAP(6, 1),
                OnAnUnmodifiableRollOfNAddDamage(6, 1),
            ],
            wound_mods=[
                GenerateD3MortalWoundsModifiable(6, 1),
                GenerateD3MortalWoundsUnmodifiable(6, 1),
                GenerateD6MortalWoundsModifiable(6, 1),
                GenerateD6MortalWoundsUnmodifiable(6, 1),
                GenerateExtraAutomaticWoundsUnmodifiable(6, 1),
                GenerateMortalWoundsUnmodifiable(6, 1),
                ReRollAll(),
                OnAModifiableRollOfNAddDamage(6, 2),
                OnAnUnmodifiableRollOfNAddAP(6, 4)
            ],
            save_mods=[AddNToAP(1),AddNToInvuln(1), AddNToSave(1), ReRollOneDice()],
            fnp_mods=[],
            damage_mods=[AddND6(1), ReRollLessThanExpectedValue()],
        )

        # Sample weapon and target
        weapon = Weapon(
            bs=4,
            shots=PMFCollection.static(10),
            strength=4,
            ap=0,
            damage=PMFCollection.static(1),
            modifiers=weapon_mods,
        )
        target = Target(toughness=4, save=4, invuln=7, fnp=7, wounds=7)

        Attack(weapon, target).run().damage_dist.mean()

    def test_sample_attack(self):
        # Re-roll ones to hit modifier
        weapon_mods = ModifierCollection(hit_mods=[ReRollOnes()])

        # Sample weapon and target
        weapon = Weapon(bs=4, shots=PMFCollection.static(10), strength=4, ap=0, damage=PMFCollection.static(1))
        target = Target(toughness=4, save=4, invuln=7, fnp=7, wounds=7)

        # Attack with no modifier
        no_modifier = Attack(weapon, target).run().damage_dist.mean()

        # Should be 1.25 = 10(shots) * 0.5(hit) * 0.5(wound) * 0.5(failed save)
        # Rounding here due to float precision
        self.assertEqual(round(no_modifier, 2), 1.25)

        # Add the modifier
        weapon.modifiers = weapon_mods

        # Attack with no modifier
        with_modifier = Attack(weapon, target).run().total_damage_dist.mean()

        # Should be ~1.4583 = 1.25 *(7/6) times higher now
        self.assertEqual(round(with_modifier, 2), round(no_modifier * (7/6), 2) )
