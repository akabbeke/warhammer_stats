
from ..utils.pmf import PMFCollection
from . import Modifier

class ReRollOnes(Modifier):
    priority = 1

    def modify_re_roll(self, collection: PMFCollection, thresh: int, mod_thresh: int) -> PMFCollection:
        return collection.map(lambda x: x.re_roll_value(1))


class ReRollFailed(Modifier):
    priority = 99

    def modify_re_roll(self, collection: PMFCollection, thresh: int, mod_thresh: int) -> PMFCollection:
        rr_thresh = min(thresh, mod_thresh)
        return collection.map(lambda x: x.re_roll_less_than(rr_thresh))


class ReRollOneDice(Modifier):
    def modify_re_roll(self, collection: PMFCollection, thresh: int, mod_thresh: int) -> PMFCollection:
        collection_pmfs = collection.pmfs
        if not collection_pmfs:
            return collection
        collection_pmfs[0] = collection_pmfs[0].re_roll_less_than(thresh)
        return PMFCollection(collection_pmfs)


class ReRollOneDiceVolume(Modifier):
    def modify_re_roll(self, collection: PMFCollection, thresh: int, mod_thresh: int) -> PMFCollection:
        collection_pmfs = collection.pmfs
        if not collection_pmfs:
            return collection
        collection_pmfs[0] = collection_pmfs[0].re_roll_less_than(collection_pmfs[0].mean())
        return PMFCollection(collection_pmfs)


class ReRollAll(Modifier):
    priority = 100

    def modify_re_roll(self, collection: PMFCollection, _, mod_thresh: int) -> PMFCollection:
        return collection.map(lambda x: x.re_roll_less_than(mod_thresh))


class ReRollLessThanExpectedValue(Modifier):
    priority = 98

    def modify_re_roll(self, collection: PMFCollection, *_) -> PMFCollection:
        return collection.map(lambda x: x.re_roll_less_than(x.mean()))
