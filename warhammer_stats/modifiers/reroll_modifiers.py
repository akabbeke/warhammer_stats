
from ..utils.pmf import PMFCollection
from . import Modifier

class ReRollOnes(Modifier):
    priority = 1

    def modify_re_roll(self, col: PMFCollection, *_) -> PMFCollection:
        return col.map(lambda x: x.re_roll_value(1))


class ReRollFailed(Modifier):
    priority = 99

    def modify_re_roll(self, col: PMFCollection, thresh: int, mod_thresh: int) -> PMFCollection:
        rr_thresh = min(thresh, mod_thresh)
        return col.map(lambda x: x.re_roll_less_than(rr_thresh))


class ReRollOneDice(Modifier):
    def modify_re_roll(self, col: PMFCollection, thresh: int, _) -> PMFCollection:
        pmfs = col.pmfs
        if not pmfs:
            return col
        pmfs[0] = pmfs[0].re_roll_less_than(thresh)
        return PMFCollection(pmfs)


class ReRollOneDiceVolume(Modifier):
    def modify_re_roll(self, col: PMFCollection, *_) -> PMFCollection:
        pmfs = col.pmfs
        if not pmfs:
            return col
        pmfs[0] = pmfs[0].re_roll_less_than(pmfs[0].mean())
        return PMFCollection(pmfs)


class ReRollAll(Modifier):
    priority = 100

    def modify_re_roll(self, col: PMFCollection, _, mod_thresh: int) -> PMFCollection:
        return col.map(lambda x: x.re_roll_less_than(mod_thresh))


class ReRollLessThanExpectedValue(Modifier):
    priority = 98

    def modify_re_roll(self, col: PMFCollection, *_) -> PMFCollection:
        return col.map(lambda x: x.re_roll_less_than(x.mean()))
