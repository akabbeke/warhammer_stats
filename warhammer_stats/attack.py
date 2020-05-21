"""
Classes related to simulating an attack in Warhammer 40000 8th edition
"""

from __future__ import annotations

from .pmf import PMF, PMFCollection
from .weapon import Weapon
from .target import Target
from .modifiers import ModifierCollection



# pylint: disable=R0201,C0302,R0913,R0902,R0903,R0904,R0913

class AttackResults:
    """Holds the results of an attack sequence.

    Args:
        shot_volume_results (PMF): The results from determining the shot volume
        to_hit_results (PMF): The results from the to-hit phase
        to_wound_results (PMF): The results from the to-wound phase
        saviour_protocol_results (PMF): The results from applying saviour protocols
        armour_save_results (PMF): The results from the saving throws phase
        damage_results (PMF): The results from appling wounds phase

    """
    def __init__(self, shot_volume_results: ShotVolumePhaseResults,
                 to_hit_results: ToHitPhaseResults,
                 to_wound_results: ToWoundPhaseResults,
                 saviour_protocol_results: SaviourProtocolPhaseResults,
                 armour_save_results: ArmourSavePhaseResults,
                 damage_results: DamagePhaseResults):

        self.shot_volume_results = shot_volume_results
        self.to_hit_results = to_hit_results
        self.to_wound_results = to_wound_results
        self.saviour_protocol_results = saviour_protocol_results
        self.armour_save_results = armour_save_results
        self.damage_results = damage_results

    @property
    def damage_dist(self) -> PMF:
        """
        The final damage distribution
        """
        return self.damage_results.damage_dist

    @property
    def mortal_wound_dist(self) -> PMF:
        """
        The combined damage distribution from the hit and wound phase
        """
        return PMF.convolve_many([
            self.to_hit_results.mortal_wound_dist,
            self.to_wound_results.mortal_wound_dist,
        ])

    @property
    def total_wounds_dist(self) -> PMF:
        """
        The combined damage distribution from regular and mortal wounds
        """
        return PMF.convolve_many([
            self.mortal_wound_dist,
            self.damage_dist,
        ])

class ShotVolumePhaseResults:
    """Holds the results of determining the number of attacks.

    Args:
        shot_dist (PMF): The distribution of shots to be made
    """
    def __init__(self, shots_dist: PMF):
        self.shots_dist = shots_dist


class ToHitPhaseResults:
    """Holds the results from the to hit phase of the attack

    Args:
        hit_dist (PMF): The distribution of successful hits
        exploding_dice_dists (PMF): The distribution of successful hits generated from
            exploding dice
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
        self_inflicted_dist (PMF): The distribution of wounds inflicted on the attacker
    """
    def __init__(self, hit_dist: PMF, exploding_dice_dist: PMF, mortal_wound_dist: PMF,
                 self_inflicted_dist: PMF):
        self.hit_dist = hit_dist
        self.exploding_dice_dist = exploding_dice_dist
        self.mortal_wound_dist = mortal_wound_dist
        self.self_inflicted_dist = self_inflicted_dist

    @property
    def combined_hit_dists(self) -> PMF:
        """
        The combined damage distribution from the hit and exploding wounds
        """
        return PMF.convolve_many([self.hit_dist, self.exploding_dice_dist])

    @classmethod
    def empty(cls) -> ToHitPhaseResults:
        """
        Return an empty set of results
        """
        return ToHitPhaseResults(
            hit_dist=PMF.static(0),
            exploding_dice_dist=PMF.static(0),
            mortal_wound_dist=PMF.static(0),
            self_inflicted_dist=PMF.static(0),
        )


class ToWoundPhaseResults:
    """Holds the results from the to wound phase of the attack

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def __init__(self, wound_dist: PMF, exploding_dice_dist: PMF, mortal_wound_dist: PMF):
        self.wound_dist = wound_dist
        self.exploding_dice_dist = exploding_dice_dist
        self.mortal_wound_dist = mortal_wound_dist


class SaviourProtocolPhaseResults:
    """Holds the results from saviour protocols

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def __init__(self, failed_save_dist: PMF, drone_wound_dist: PMF):
        self.failed_save_dist = failed_save_dist
        self.drone_wound_dist = drone_wound_dist


class ArmourSavePhaseResults:
    """Holds the results from the armour save phase

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def __init__(self, failed_save_dist: PMF):
        self.failed_save_dist = failed_save_dist


class DamagePhaseResults:
    """Holds the results from the armour save phase

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def __init__(self, damage_dist: PMF):
        self.damage_dist = damage_dist


class Attack:
    """Generates the probability distribution for damage dealt from an attack sequence

    Note:
        This can be pretty computaionally expensive to run. Don't go crazy with the number
        attacks and expect it to run quickly.

    Args:
        weapon (Weapon): The weapon being used to make the attack
        target (Target): The target of the the attack

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """
    def __init__(self, weapon: Weapon, target: Target):
        self.weapon = weapon
        self.target = target

    def _shot_volume_phase(self):
        return ShotVolumePhase(self.weapon, self.target, self.modifiers)

    def _to_hit_phase(self):
        return ToHitPhase(self.weapon, self.target, self.modifiers)

    def _to_wound_phase(self):
        return ToWoundPhase(self.weapon, self.target, self.modifiers)

    def _saviour_protocol_phase(self):
        return SaviourProtocolPhase(self.weapon, self.target, self.modifiers)

    def _armour_save_phase(self):
        return ArmourSavePhase(self.weapon, self.target, self.modifiers)

    def _damage_phase_phase(self):
        return DamagePhase(self.weapon, self.target, self.modifiers)

    @property
    def modifiers(self) -> ModifierCollection:
        """Return a combined list of modifers for both the weapon and the target"""
        return self.weapon.modifiers + self.target.modifiers

    def run(self) -> AttackResults:
        """
        Generate the resulting PMF
        """


        # Generate the PMF for the number of shots
        shot_volume_results = self._shot_volume_phase().calc_dist()

        # Generate the PMFs for the number of hits, mortal wounds, and self inflicted
        # mortal wounds in the hit phase
        to_hit_results = self._to_hit_phase().calc_dist(
            dist=shot_volume_results.shots_dist,
            can_recurse=True,
        )

        # Generate the PMFs for the number of wounds, mortal wounds, and self inflicted
        # mortal wounds in the wound phase
        to_wound_results = self._to_wound_phase().calc_dist(dist=to_hit_results.combined_hit_dists)

        # Generate the PMFs for the number of wounds that penetrate saviour protocols and
        # how many drones die
        saviour_protocol_results = self._saviour_protocol_phase().calc_dist(
            to_wound_results.wound_dist,
        )

        # Generate the PMFs for the number of failed saves in the armor save phase
        armour_save_results = self._armour_save_phase().calc_dist(
            saviour_protocol_results.failed_save_dist,
        )

        # Generate the PMFs for the danage dealt in the damage calculation phase.
        damage_results = self._damage_phase_phase().calc_dist(
            armour_save_results.failed_save_dist,
        )

        return AttackResults(
            shot_volume_results=shot_volume_results,
            to_hit_results=to_hit_results,
            to_wound_results=to_wound_results,
            saviour_protocol_results=saviour_protocol_results,
            armour_save_results=armour_save_results,
            damage_results=damage_results,
        )


class AttackPhase:
    """The base class for attack segments

    Note:
        This is just a base class that contains a number of common methods

    Args:
        attack (Attack): A reference to the attack being made
    """
    def __init__(self, weapon: Weapon, target: Target, modifiers: ModifierCollection):
        self.weapon = weapon
        self.target = target
        self.modifiers = modifiers
        self._thresh_mod = None

    @property
    def thresh_mod(self) -> int:
        """
        A cached copy of the threshold modifier
        """
        # cache the threshold modifier
        if self._thresh_mod is None:
            self._thresh_mod = self._get_thresh_mod()
        return self._thresh_mod

    def _get_thresh_mod(self) -> int:
        return 0

    def _calc_exp_dist(self, dice_dists: PMF) -> PMF:
        # Calculate the exploding dice distributions
        dist_col = PMFCollection.add_many([
            self._mod_extra_dist().thresh_mod(self.thresh_mod),
            self._extra_dist(),
        ])

        if dist_col:
            return dist_col.mul_col(dice_dists).convolve()
        return PMF.static(0)

    def _mod_extra_dist(self) -> PMFCollection:
        # Stub
        return PMFCollection.empty()

    def _extra_dist(self) -> PMFCollection:
        # Stub
        return PMFCollection.empty()

    def _calc_mortal_dist(self, dice_dists) -> PMF:
        # Calculate how many mortal wounds are generated
        dist_col = PMFCollection.add_many([
            self._mod_mortal_dist().thresh_mod(self.thresh_mod),
            self._mortal_dist(),
        ])
        if dist_col:
            return dist_col.mul_col(dice_dists).convolve()
        return PMF.static(0)

    def _mod_mortal_dist(self) -> PMFCollection:
        # Stub
        return PMFCollection.empty()

    def _mortal_dist(self) -> PMFCollection:
        # Stub
        return PMFCollection.empty()


class ShotVolumePhase(AttackPhase):
    """
    Generate the PMF for the number of shots
    """
    def calc_dist(self, *_) -> ShotVolumePhaseResults:
        """Calculate the probability distiribution for the number of shots made in the attack
        for weapons with a fixed value this is a static number but some can be the convolution
        of more than one PMF. eg: 'roll two d6'
        """
        # Apply the shot volume modifiers
        shots_dists = self.modifiers.modify_shot_dice(self.weapon.shots)

        # Convolve the resulting PMFs
        return ShotVolumePhaseResults(
            shots_dist=shots_dists.convolve()
        )


class ToHitPhase(AttackPhase):
    """
    Simulate the hits phase of the attack
    """
    def calc_dist(self, dist: PMF, can_recurse: bool, *_) -> ToHitPhaseResults: # pylint: disable=too-many-locals
        """Calculate the probability distiribution of the number of sucessful hits in
        in the attack phase. This takes into account modifiers and other effects as
        extra hits and shots.
        """
        hit_dists = []
        exploding_dice_dists = []
        mortal_wound_dists = []
        self_inflicted_dists = []

        # The bare threshold to hit is the weapons to hit value
        thresh = self.weapon.bs

        # Check for any modifers to the to hit roll
        mod_thresh = self.modifiers.modify_hit_thresh(self.weapon.bs)

        # Check for the threshhold for self inflicted wounds
        thresh_self_wounds = self.modifiers.self_wound_thresh()

        # Generate the resulting hit distributon for each value of the shots PMF then
        # multipy by the probability of that value and sum them
        for dice_count, event_prob in enumerate(dist.values):
            # If the probability is zero then no-op
            if event_prob == 0:
                continue

            # Create a dice distribution for 'dice_count' d6 dice
            dice_dists = PMFCollection.mdn(dice_count, 6)

            # Apply modifiers to the dice distribution
            dice_dists = self.modifiers.modify_hit_dice(dice_dists, thresh, mod_thresh)

            # If self inflicted wounds are possible calculate them
            if thresh_self_wounds:
                self_thresh = max(thresh_self_wounds+mod_thresh-thresh, 0)
                self_inflicted_dist = dice_dists.convert_binomial_less_than(self_thresh).convolve()
            else:
                self_inflicted_dist = PMF.static(0)


            # Convert the dice dist into a binomial distribution with the modified to hit value.
            # We are bsically flatteing all the individual d6 down into d2 True/False for if it hit.
            hit_dist = dice_dists.convert_binomial(mod_thresh).convolve()

            # Calculate the distirbution for exploding automatic hits. Since extra shots cannot
            # generate more hits return a zero prob if we are recusing
            exp_dist = self._calc_exp_dist(dice_dists) if can_recurse else PMF.static(0)

            # Calculate the ditributons for exploding extra chances to hit. This requires us
            # to calcuate. The whole to-hit phase again for the sub hits
            explosive_shot_result = self._calc_exp_shot_dist(dice_dists, can_recurse)

            # Calculate the mortal wounds gnerated
            mrt_dist = self._calc_mortal_dist(dice_dists)

            # Multiply the resulting hit distributions by the probability of this number of dice
            # and append them to the totals
            hit_dists.append(hit_dist * event_prob)
            combined_exploding_dice = PMF.convolve_many([exp_dist, explosive_shot_result.hit_dist])
            combined_mortal_wounds = PMF.convolve_many(
                [mrt_dist, explosive_shot_result.mortal_wound_dist],
            )
            combined_self_inflicted = PMF.convolve_many(
                [self_inflicted_dist, explosive_shot_result.self_inflicted_dist],
            )

            # Add these to the list
            exploding_dice_dists.append(combined_exploding_dice * event_prob)
            mortal_wound_dists.append(combined_mortal_wounds * event_prob)
            self_inflicted_dists.append(combined_self_inflicted * event_prob)

        # Flattening the dists means we are summing the probabilites of each value across all the
        # dists. This is how we find the total probability distribution of the phase.

        return ToHitPhaseResults(
            hit_dist=PMF.flatten(hit_dists),
            exploding_dice_dist=PMF.flatten(exploding_dice_dists),
            mortal_wound_dist=PMF.flatten(mortal_wound_dists),
            self_inflicted_dist=PMF.static(0) if not self_inflicted_dists else \
                PMF.flatten(self_inflicted_dists)
        )

    def _get_thresh_mod(self):
        # This is a bit of a hack to get the delta between the threshold and the modified threshold
        return self.modifiers.modify_hit_thresh(6) - 6

    def _calc_exp_shot_dist(self, dice_dists: PMF, can_recurse: bool) -> ToHitPhaseResults:
        # This handles generating extra chances to hit and then calculating the distribution of
        # resulting successful hits

        # If we are alread recusing then return zeros
        if not can_recurse:
            return ToHitPhaseResults.empty()

        # Since to hit modifers can modify the number of extra chances to hit generate that now
        dist_col = PMFCollection.add_many([
            self._get_mod_extra_shot().thresh_mod(self.thresh_mod),
            self._get_extra_shot(),
        ])

        if dist_col:
            return self.calc_dist(dist_col.mul_col(dice_dists).convolve(), can_recurse=False)
        return ToHitPhaseResults.empty()

    def _mod_extra_dist(self):
        return self.modifiers.get_mod_extra_hit()

    def _extra_dist(self):
        return self.modifiers.get_extra_hit()

    def _get_mod_extra_shot(self):
        return self.modifiers.get_mod_extra_shot()

    def _get_extra_shot(self):
        return self.modifiers.get_extra_shot()

    def _mod_mortal_dist(self):
        return self.modifiers.hit_mod_mortal_wounds()

    def _mortal_dist(self):
        return self.modifiers.hit_mortal_wounds()


class ToWoundPhase(AttackPhase):
    """
    Generate the PMF for the wounds
    """
    def calc_dist(self, dist: PMF, *_) -> ToWoundPhaseResults:
        """Calculate the probability distiribution of the number of sucessful wounds in
        in the wound phase. This takes into account modifiers and other effects as
        extra automatic wounds.
        """
        wnd_dists = []
        exploding_dice_dists = []
        mortal_wound_dist = []

        # Calculate the wound threshold from the strength of the weapon and the toughness
        # of the target
        thresh = self._calc_wound_thresh(
            self.weapon.strength,
            self.target.toughness
        )

        # Apply any modifers to the wound threshold
        mod_thresh = self.modifiers.modify_wound_thresh(thresh)

        # Generate the resulting hit distributon for each value of the shots PMF then
        # multipy by the probability of that value and sum them
        for dice_count, event_prob in enumerate(dist.values):
            # If the probability is zero then no-op
            if event_prob == 0:
                continue

            # Create a dice distribution for 'dice_count' d6 dice
            dice_dists = PMFCollection.mdn(dice_count, 6)

            # Apply modifiers to the dice distribution
            dice_dists = self.modifiers.modify_wound_dice(dice_dists, thresh, mod_thresh)

            # Convert the dice dist into a binomial distribution with the modified to wound value.
            # We are bsically flatteing all the individual d6 down into d2 True/False for if it
            # wounded.
            wnd_dist = dice_dists.convert_binomial(mod_thresh).convolve()

            # Calculate exploding auto-wounds
            exp_dist = self._calc_exp_dist(dice_dists)

            # Generate mortal wounds
            mrt_dist = self._calc_mortal_dist(dice_dists)

            wnd_dists.append(wnd_dist * event_prob)
            exploding_dice_dists.append(exp_dist * event_prob)
            mortal_wound_dist.append(mrt_dist * event_prob)

        # Flatten the distros down
        return ToWoundPhaseResults(
            wound_dist=PMF.flatten(wnd_dists),
            exploding_dice_dist=PMF.flatten(exploding_dice_dists),
            mortal_wound_dist=PMF.flatten(mortal_wound_dist),
        )

    def _calc_wound_thresh(self, strength: int, toughness: int) -> int:
        # Generate the wound threshold
        if strength <= toughness/2.0: # pylint: disable=no-else-return
            # If the toughness is greater than twice the strength wound on a 6+
            return 6
        elif strength >= toughness*2:
            # If the stength is greater than twice the toughness wound on a 2+
            return 2
        elif toughness > strength:
            # Else if toughness is greater than strength wound on a 5_
            return 5
        elif toughness == strength:
            # Else if they are equal then wound on a 4+
            return 4
        else:
            # If the strength is greater than toughness wound on a 3+
            return 3

    def _get_thresh_mod(self) -> int:
        return self.modifiers.modify_wound_thresh(6) - 6

    def _mod_extra_dist(self) -> PMFCollection:
        return self.modifiers.get_mod_extra_wound()

    def _extra_dist(self) -> PMFCollection:
        return self.modifiers.get_extra_wound()

    def _mod_mortal_dist(self) -> PMFCollection:
        return self.modifiers.wound_mod_mortal_wounds()

    def _mortal_dist(self) -> PMFCollection:
        return self.modifiers.wound_mortal_wounds()


class SaviourProtocolPhase(AttackPhase):
    """
    Generate the PMF for saviour protocols
    """
    def calc_dist(self, dist: PMF) -> SaviourProtocolPhaseResults:
        """Calculate the probability distiribution of the number of failed saves from
        saviour protocol and the amount of damage dealt to drones. This takes into account \
        modifiers such as the shield drone FNP and other effects.
        """
        # Check if saviour protcols are active and if so what the threshold is and the FNP value
        drone_enabled, drone_thresh, drone_fnp = self.modifiers.modify_drone()

        # If the probability is zero then no-op
        if not drone_enabled:
            return SaviourProtocolPhaseResults(
                failed_save_dist=dist,
                drone_wound_dist=PMF.static(0),
            )

        # Calculate how many wounds pass though the savious protocols and how many wounds the
        # drones take
        pens = []
        saves = []
        for dice_count, event_prob in enumerate(dist.values):
            # If the probability is zero then no-op
            if event_prob == 0:
                continue

            # Create a dice distribution for 'dice_count' d6 dice
            dice_dists = PMFCollection.mdn(dice_count, 6)

            # Convert binomial for values less than the threshold for attacks the penetrated
            pen_dist = dice_dists.convert_binomial_less_than(drone_thresh).convolve()

            # Convert binomial for values greater than the threshold for wounds passed off to the
            # drones
            save_dist = dice_dists.convert_binomial(drone_thresh).convolve()

            pens.append(pen_dist * event_prob)
            saves.append(save_dist * event_prob)

        # Flatten the distros down
        return SaviourProtocolPhaseResults(
            failed_save_dist=PMF.flatten(pens),
            drone_wound_dist=self._calc_fnp_dist(PMF.flatten(saves), drone_fnp),
        )

    def _calc_fnp_dist(self, dist, drone_fnp) -> PMF:
        # Check how many of the wounds are removed by the drone FNP
        dists = []
        for dice, event_prob in enumerate(dist.values):
            if event_prob == 0:
                continue
            dice_dists = PMFCollection.mdn(dice, 6)
            binom_dists = dice_dists.convert_binomial_less_than(drone_fnp).convolve()
            dists.append(binom_dists * event_prob)
        return PMF.flatten(dists)


class ArmourSavePhase(AttackPhase):
    """
    Generate the PMF for the wounds that penetrate the
    """
    def calc_dist(self, dist: PMF) -> ArmourSavePhaseResults:
        """Calculate the probability distiribution of the number of failed armour
        saves. This takes into account modifiers and invunerable save
        """
        # Calculate the final save threshold from the save value, invunerable save, and
        # any save modifiers
        mod_thresh = self.modifiers.modify_pen_thresh(
            self.target.save,
            self.weapon.ap,
            self.target.invuln
        )

        dists = []
        for dice_count, event_prob in enumerate(dist.values):
            # If the probability is zero then no-op
            if event_prob == 0:
                continue

            # Create a dice distribution for 'dice_count' d6 dice
            dice_dists = PMFCollection.mdn(dice_count, 6)
            dice_dists = self.modifiers.modify_pen_dice(dice_dists, mod_thresh, mod_thresh)

            # Convert binomial for values less than the threshold for attacks the penetrated
            pen_dists = dice_dists.convert_binomial_less_than(mod_thresh).convolve()
            dists.append(pen_dists * event_prob)

        # Flatten the distros down
        return ArmourSavePhaseResults(
            failed_save_dist=PMF.flatten(dists)
        )


class DamagePhase(AttackPhase):
    """
    Generate the PMF for the damage dealt to the target
    """
    def calc_dist(self, dist: PMF) -> DamagePhaseResults:
        """Calculate the probability distiribution of the number of wounds dealt from a
        failed daving throw. This accounts for feel no pain, target wounds characteristic
        and other damage modifiers.

        Note: This does not take into account the inneficientcy from partially wounding
        units
        """
        # Get the distribution of each individual wound dealt
        individual_dist = self._calc_individual_damage_dist()

        damge_dists = []
        for dice, event_prob in enumerate(dist.values):
            # If the probability is zero then no-op
            if event_prob == 0:
                continue
            # Multiply the individual damage distributions by the number dice
            damge_dists.append(PMF.convolve_many([individual_dist] * dice) * event_prob)

        return DamagePhaseResults(
            damage_dist=PMF.flatten(damge_dists)
        )

    def _calc_individual_damage_dist(self) -> PMF:
        # Get the basic damage distribution
        dice_dists = self.weapon.damage

        # Apply modifers to the damage distribution
        mod_dists = self.modifiers.modify_damage_dice(dice_dists)

        # Calculate the damge distribution after the feel no pain has been applied
        fnp_dist = self._calc_fnp_dist(mod_dists.convolve())

        # Clip the damage dist to the wounds characteristic of the target
        return fnp_dist.ceiling(self.target.wounds)

    def _calc_fnp_dist(self, dist: PMF) -> PMF:
        dists = []
        mod_thresh = self.modifiers.modify_fnp_thresh(self.target.fnp)
        for dice, event_prob in enumerate(dist.values):
            if event_prob == 0:
                continue
            dice_dists = self.modifiers.modify_fnp_dice(
                PMFCollection.mdn(dice, 6),
                self.target.fnp,
                mod_thresh,
            )
            binom_dists = dice_dists.convert_binomial_less_than(mod_thresh).convolve()
            dists.append(binom_dists * event_prob)
        return PMF.flatten(dists)
