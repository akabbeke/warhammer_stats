
from ..utils.pmf import PMF, PMFCollection
from . import Modifier

class GeneratorModifiers(Modifier):
    """
    The base class for modifiers which generate additional effects

    Attributes
    thresh : int
        The threshold value that effect dice are generated on

    value : int
        The number of effects dice generated
    """

    def __init__(self, thresh: int, value: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # clamp the threshold between 0 and 7
        self.thresh = max(0, min(7, thresh))
        self.value = value

    def _pmf_collection(self) -> PMFCollection:
        return PMFCollection(
            [PMF.static(0) if i < self.thresh else PMFCollection.static(self.value).convolve() for i in range(8)]
        )

    def to_dict(self):
        return {
            **super().to_dict(),
            'thresh': self.thresh,
            'value': self.value,
        }


class GenerateExtraAutomaticHitsModifiable(GeneratorModifiers):
    def extra_automatic_hit_modifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateExtraAutomaticHitsUnmodifiable(GeneratorModifiers):
    def extra_automatic_hit_unmodifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateExtraHitRollsModifiable(GeneratorModifiers):
    def extra_hit_roll_modifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateExtraHitRollsUnmodifiable(GeneratorModifiers):
    def extra_hit_roll_unmodifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateExtraWoundRollsModifiable(GeneratorModifiers):
    def extra_wound_roll_modifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateExtraWoundRollsUnmodifiable(GeneratorModifiers):
    def extra_wound_roll_unmodifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateExtraAutomaticWoundsModifiable(GeneratorModifiers):
    def extra_automatic_wounds_modifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateExtraAutomaticWoundsUnmodifiable(GeneratorModifiers):
    def extra_automatic_wounds_unmodifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateMortalWoundsUnmodifiable(GeneratorModifiers):
    def extra_mortal_wound_unmodifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateMortalWoundsModifiable(GeneratorModifiers):
    def extra_mortal_wound_modifiable(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateD3MortalWoundsUnmodifiable(GeneratorModifiers):
    def extra_mortal_wound_unmodifiable(self) -> PMFCollection:
        return self._pmf_collection()

    def _pmf_collection(self) -> PMFCollection:
        return PMFCollection(
            [PMF.static(0) if i < self.thresh else PMFCollection.mdn(self.value, 3).convolve() for i in range(8)]
        )


class GenerateD3MortalWoundsModifiable(GeneratorModifiers):
    def extra_mortal_wound_modifiable(self) -> PMFCollection:
        return self._pmf_collection()

    def _pmf_collection(self) -> PMFCollection:
        return PMFCollection(
            [PMF.static(0) if i < self.thresh else PMFCollection.mdn(self.value, 3).convolve() for i in range(8)]
        )


class GenerateD6MortalWoundsUnmodifiable(GeneratorModifiers):
    def extra_mortal_wound_unmodifiable(self) -> PMFCollection:
        return self._pmf_collection()

    def _pmf_collection(self) -> PMFCollection:
        return PMFCollection(
            [PMF.static(0) if i < self.thresh else PMFCollection.mdn(self.value, 6).convolve() for i in range(8)]
        )


class GenerateD6MortalWoundsModifiable(GeneratorModifiers):
    def extra_mortal_wound_modifiable(self) -> PMFCollection:
        return self._pmf_collection()

    def _pmf_collection(self) -> PMFCollection:
        return PMFCollection(
            [PMF.static(0) if i < self.thresh else PMFCollection.mdn(self.value, 6).convolve() for i in range(8)]
        )


class EndAttackGenerator(GeneratorModifiers):
    def modify_dice(self, collection: PMFCollection, *_) -> PMFCollection:
        def null_values(x, thresh):
            values = x.values[:]
            values[0] += sum(values[thresh:])
            values[thresh:] = [0.0] * len(values[thresh:])
            return PMF(values)
        return collection.map(lambda x: null_values(x, self.thresh))


class EndAttackAndGenrateMortalWoundsModifiable(EndAttackGenerator):
    def extra_mortal_wound_modifiable(self) -> PMFCollection:
        return self._pmf_collection()


class EndAttackAndGenrateMortalWoundsUnmodifiable(EndAttackGenerator):
    def extra_mortal_wound_unmodifiable(self) -> PMFCollection:
        return self._pmf_collection()


class EndAttackAndGenrateExtraWoundsModifiable(EndAttackGenerator):
    def extra_automatic_wound_modifiable(self) -> PMFCollection:
        return self._pmf_collection()


class EndAttackAndGenrateExtraWoundsUnmodifiable(EndAttackGenerator):
    def extra_automatic_wound_unmodifiable(self) -> PMFCollection:
        return self._pmf_collection()


class Haywire(GeneratorModifiers):
    def extra_mortal_wound_modifiable(self) -> PMFCollection:
        # This is a hardcoded implementation of the haywire mechanic of generating a mortal
        # wound on 4 and 5 and D3 mortal wounds on a 6+
        col = [
            PMF.static(0),  # 0 for 0
            PMF.static(0),  # 0 for 1
            PMF.static(0),  # 0 for 2
            PMF.static(0),  # 0 for 3
            PMF.static(1),  # 1 for 4
            PMF.static(1),  # 1 for 5
            PMF.dn(3),  # d3 for 6
        ]
        return PMFCollection(col)
