from .pmf import PMF
from .modifiers import ModifierCollection

class Weapon(object):
    """
    Holds the params of a weapon
    """
    def __init__(self, bs, shots, strength, ap, damage, modifiers=None):
        self.bs = bs
        self.shots = shots
        self.strength = strength
        self.ap = ap
        self.damage = damage
        self.modifiers = modifiers or ModifierCollection()