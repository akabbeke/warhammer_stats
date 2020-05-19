from .modifiers import ModifierCollection

class Target(object):
    """
    Holds params of a target
    """
    def __init__(self, toughness, save, invuln, fnp, wounds, modifiers=None):
        self.toughness = toughness
        self.save = save
        self.invuln = invuln
        self.fnp = fnp
        self.wounds = wounds
        self.modifiers = modifiers or ModifierCollection()