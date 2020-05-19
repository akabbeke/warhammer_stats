from .pmf import PMF, PMFCollection


class AttackSequenceResults(object):
    """
    Holds the results of an attack sequence
    """
    def __init__(self, shot_dist, hit_dist, wound_dist, pen_dist, damage_dist, drone_wound, self_wound, mortal_dist):
        self.shot_dist = shot_dist
        self.hit_dist = hit_dist
        self.wound_dist = wound_dist
        self.pen_dist = pen_dist
        self.damage_dist = damage_dist
        self.drone_wound = drone_wound
        self.self_wound = self_wound
        self.mortal_dist = mortal_dist


class Attack(object):
    """
    Generates the probability distribution for damage dealt from an attack sequence
    """
    def __init__(self, weapon, target):
        self.weapon = weapon
        self.target = target

        # Setup the controllers for the individual phases
        self.shots = AttackShots(self)
        self.hits = AttackHits(self)
        self.wounds = AttackWounds(self)
        self.drones = AttackDrones(self)
        self.pens = AttackPens(self)
        self.damage = AttackDamage(self)

    @property
    def modifiers(self):
        # Return a combined list of modifers for both the weapon ans the target
        return self.weapon.modifiers + self.target.modifiers

    def run(self):
        """
        Generate the resulting PMF
        """
        # Keeping track of mortal wounds generated in the hit and wound phase
        mortal_dists = []

        # Generate the PMF for the number of shots
        shot_dist = self.shots.calc_dist()

        # Generate the PMFs for the number of hits, mortal wounds, and self inflicted
        # mortal wounds in the hit phase
        hit_dist, mortal_dist, self_dist = self.hits.calc_dist(shot_dist)
        mortal_dists.append(mortal_dist)

        # Generate the PMFs for the number of wounds, mortal wounds, and self inflicted
        # mortal wounds in the wound phase
        wound_dist, mortal_dist = self.wounds.calc_dist(hit_dist)
        mortal_dists.append(mortal_dist)

        # Generate the PMFs for the number of wounds that penetrate saviour protocols and
        # how many drones die
        drone_pen, drone_wound = self.drones.calc_dist(wound_dist)

        # Generate the PMFs for the number of failed saves in the armor save phase
        pen_dist = self.pens.calc_dist(drone_pen)

        # Generate the PMFs for the danage dealt in the damage calculation phase.
        damage_dist = self.damage.calc_dist(pen_dist)

        return AttackSequenceResults(
            shot_dist,
            hit_dist,
            wound_dist,
            pen_dist,
            damage_dist,
            drone_wound,
            self_dist,
            PMF.convolve_many(mortal_dists),
        )


class AttackSegment(object):
    """
    The base class for the various attack segments
    """
    def __init__(self, attack):
        self.attack = attack
        self._thresh_mod = None

    def calc_dist(self):
        # Stub
        pass

    @property
    def thresh_mod(self):
        # cache the threshold modifier
        if self._thresh_mod is None:
            self._thresh_mod = self._get_thresh_mod()
        return self._thresh_mod

    def _get_thresh_mod(self):
        return 0

    def _calc_exp_dist(self, dice_dists):
        # Calculate the exploding dice distributions
        dist_col = PMFCollection.add_many([
        self._mod_extra_dist().thresh_mod(self.thresh_mod),
        self._extra_dist(),
        ])

        if dist_col:
            return dist_col.mul_col(dice_dists).convolve()
        else:
            return PMF.static(0)

    def _mod_extra_dist(self):
        # Stub
        return PMFCollection.empty()

    def _extra_dist(self):
        # Stub
        return PMFCollection.empty()

    def _calc_mortal_dist(self, dice_dists):
        # Calculate how many mortal wounds are generated
        dist_col = PMFCollection.add_many([
        self._mod_mortal_dist().thresh_mod(self.thresh_mod),
        self._mortal_dist(),
        ])
        if dist_col:
            return dist_col.mul_col(dice_dists).convolve()
        else:
            return PMF.static(0)

    def _mod_mortal_dist(self):
        # Stub
        return PMFCollection.empty()

    def _mortal_dist(self):
        # Stub
        return PMFCollection.empty()


class AttackShots(AttackSegment):
    """
    Generate the PMF for the number of shots
    """
    def calc_dist(self):
        # Apply the shot volume modifiers
        shots_dists = self.attack.modifiers.modify_shot_dice(self.attack.weapon.shots)

        # Convolve the resulting PMFs
        return shots_dists.convolve()


class AttackHits(AttackSegment):
    """
    Simulate the hits phase of the attack
    """
    def calc_dist(self, dist, can_recurse=True):
        hit_dists = []
        exp_dists = []
        mrt_dists = []
        self_dists = []

        # The bare threshold to hit is the weapons to hit value
        thresh = self.attack.weapon.bs

        # Check for any modifers to the to hit roll
        mod_thresh = self.attack.modifiers.modify_hit_thresh(self.attack.weapon.bs)

        # Check for the threshhold for self inflicted wounds
        thresh_self_wounds = self.attack.modifiers.modify_self_wounds()

        # Generate the resulting hit distributon for each value of the shots PMF then
        # multipy by the probability of that value and sum them
        for dice_count, event_prob in enumerate(dist.values):
            # If the probability is zero then no-op
            if event_prob == 0:
                continue

            # Create a dice distribution for 'dice_count' d6 dice
            dice_dists = PMFCollection.mdn(dice_count, 6)

            # Apply modifiers to the dice distribution
            dice_dists = self.attack.modifiers.modify_hit_dice(dice_dists, thresh, mod_thresh)

            # If self inflicted wounds are possible calculate them
            if thresh_self_wounds:
                self_thresh = max(thresh_self_wounds+mod_thresh-thresh, 0)
                self_dist = dice_dists.convert_binomial_less_than(self_thresh).convolve()
            else:
                self_dist = PMF.static(0)


            # Convert the dice dist into a binomial distribution with the modified to hit value.
            # We are bsically flatteing all the individual d6 down into d2 True/False for if it hit.
            hit_dist = dice_dists.convert_binomial(mod_thresh).convolve()

            # Calculate the distirbution for exploding automatic hits. Since extra shots cannot
            # generate more hits return a zero prob if we are recusing
            exp_dist = self._calc_exp_dist(dice_dists) if can_recurse else PMF.static(0)

            # Calculate the ditributons for exploding extra chances to hit. This requires us to calcuate
            # The whole to-hit phase again for the sub hits
            exp_shot_dist, exp_mrt_dist, exp_self_dist = self._calc_exp_shot_dist(dice_dists, can_recurse)

            # Calculate the mortal wounds gnerated
            mrt_dist = self._calc_mortal_dist(dice_dists)

            # Multiply the resulting hit distributions by the probability of this number of dice
            # and append them to the totals
            hit_dists.append(hit_dist * event_prob)
            exp_dists.append(PMF.convolve_many([exp_dist, exp_shot_dist]) * event_prob)
            mrt_dists.append(PMF.convolve_many([mrt_dist, exp_mrt_dist]) * event_prob)
            self_dists.append(PMF.convolve_many([self_dist, exp_self_dist]) * event_prob)

        # Flattening the dists means we are summing the probabilites of each value across all the
        # dists. This is how we find the total probability distribution of the phase.

        # Since the exploding hits happens as a kind of sidecar opperation to the main dice rolls
        # it can be considered an "AND" opperation meaning we can convolve the two distributions
        # together
        combined_hit_dists = PMF.convolve_many([PMF.flatten(hit_dists), PMF.flatten(exp_dists)])
        return (
            combined_hit_dists,
            PMF.flatten(mrt_dists),
            PMF.static(0) if not self_dists else PMF.flatten(self_dists),
        )

    def _get_thresh_mod(self):
        # This is a bit of a hack to get the delta between the threshold and the modified threshold
        return self.attack.modifiers.modify_hit_thresh(6) - 6

    def _calc_exp_shot_dist(self, dice_dists, can_recurse=True):
        # This handles generating extra chances to hit and then calculating the distribution of
        # resulting successful hits

        # If we are alread recusing then return zeros
        if not can_recurse:
            return PMF.static(0), PMF.static(0), PMF.static(0)

        # Since to hit modifers can modify the number of extra chances to hit generate that now
        dist_col = PMFCollection.add_many([
            self._get_mod_extra_shot().thresh_mod(self.thresh_mod),
            self._get_extra_shot(),
        ])

        if dist_col:
            return self.calc_dist(dist_col.mul_col(dice_dists).convolve(), can_recurse=False)
        else:
            return PMF.static(0), PMF.static(0), PMF.static(0)

    def _mod_extra_dist(self):
        return self.attack.modifiers.get_mod_extra_hit()

    def _extra_dist(self):
        return self.attack.modifiers.get_extra_hit()

    def _get_mod_extra_shot(self):
        return self.attack.modifiers.get_mod_extra_shot()

    def _get_extra_shot(self):
        return self.attack.modifiers.get_extra_shot()

    def _mod_mortal_dist(self):
        return self.attack.modifiers.hit_mod_mortal_wounds()

    def _mortal_dist(self):
        return self.attack.modifiers.hit_mortal_wounds()


class AttackWounds(AttackSegment):
    """
    Generate the PMF for the wounds
    """
    def calc_dist(self, dist):
        wnd_dists = []
        exp_dists = []
        mrt_dists = []

        # Calculate the wound threshold from the strength of the weapon and the toughness
        # of the target
        thresh = self._calc_wound_thresh(
            self.attack.weapon.strength,
            self.attack.target.toughness
        )

        # Apply any modifers to the wound threshold
        mod_thresh = self.attack.modifiers.modify_wound_thresh(thresh)

        # Generate the resulting hit distributon for each value of the shots PMF then
        # multipy by the probability of that value and sum them
        for dice_count, event_prob in enumerate(dist.values):
            # If the probability is zero then no-op
            if event_prob == 0:
                continue

            # Create a dice distribution for 'dice_count' d6 dice
            dice_dists = PMFCollection.mdn(dice_count, 6)

            # Apply modifiers to the dice distribution
            dice_dists = self.attack.modifiers.modify_wound_dice(dice_dists, thresh, mod_thresh)

            # Convert the dice dist into a binomial distribution with the modified to wound value.
            # We are bsically flatteing all the individual d6 down into d2 True/False for if it wounded.
            wnd_dist = dice_dists.convert_binomial(mod_thresh).convolve()

            # Calculate exploding auto-wounds
            exp_dist = self._calc_exp_dist(dice_dists)

            # Generate mortal wounds
            mrt_dist = self._calc_mortal_dist(dice_dists)

            wnd_dists.append(wnd_dist * event_prob)
            exp_dists.append(exp_dist * event_prob)
            mrt_dists.append(mrt_dist * event_prob)

        # Flatten the distros down
        return PMF.convolve_many([PMF.flatten(wnd_dists), PMF.flatten(exp_dists)]), PMF.flatten(mrt_dists)

    def _calc_wound_thresh(self, strength, toughness):
        # Generate the wound threshold
        if strength <= toughness/2.0:
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

    def _get_thresh_mod(self):
        return self.attack.modifiers.modify_wound_thresh(6) - 6

    def _mod_extra_dist(self):
        return self.attack.modifiers.get_mod_extra_wound()

    def _extra_dist(self):
        return self.attack.modifiers.get_extra_wound()

    def _mod_mortal_dist(self):
        return self.attack.modifiers.wound_mod_mortal_wounds()

    def _mortal_dist(self):
        return self.attack.modifiers.wound_mortal_wounds()


class AttackDrones(AttackSegment):
    """
    Generate the PMF for saviour protocols
    """
    def calc_dist(self, dist):
        # Check if saviour protcols are active and if so what the threshold is and the FNP value
        drone_enabled, drone_thresh, drone_fnp = self.attack.modifiers.modify_drone()

        # If the probability is zero then no-op
        if not drone_enabled:
            return dist, PMF.static(0)

        # Calculate how many wounds pass though the savious protocols and how many wounds the drones take
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
        return PMF.flatten(pens), self._calc_fnp_dist(PMF.flatten(saves), drone_fnp)

    def _calc_fnp_dist(self, dist, drone_fnp):
        # Check how many of the wounds are removed by the drone FNP
        dists = []
        for dice, event_prob in enumerate(dist.values):
            if event_prob == 0:
                continue
            dice_dists = PMFCollection.mdn(dice, 6)
            binom_dists = dice_dists.convert_binomial_less_than(drone_fnp).convolve()
            dists.append(binom_dists * event_prob)
        return PMF.flatten(dists)


class AttackPens(AttackSegment):
    """
    Generate the PMF for the wounds that penetrate the
    """
    def calc_dist(self, dist):
        # Calculate the final save threshold from the save value, invunerable save, and
        # any save modifiers
        mod_thresh = self.attack.modifiers.modify_pen_thresh(
            self.attack.target.save,
            self.attack.weapon.ap,
            self.attack.target.invuln
        )

        dists = []
        for dice_count, event_prob in enumerate(dist.values):
            # If the probability is zero then no-op
            if event_prob == 0:
                continue

            # Create a dice distribution for 'dice_count' d6 dice
            dice_dists = PMFCollection.mdn(dice_count, 6)
            dice_dists = self.attack.modifiers.modify_pen_dice(dice_dists, mod_thresh, mod_thresh)

            # Convert binomial for values less than the threshold for attacks the penetrated
            pen_dists = dice_dists.convert_binomial_less_than(mod_thresh).convolve()
            dists.append(pen_dists * event_prob)

        # Flatten the distros down
        return PMF.flatten(dists)


class AttackDamage(AttackSegment):
    """
    Generate the PMF for the damage dealt to the target
    """
    def calc_dist(self, dist):
        # Get the distribution of each individual wound dealt
        individual_dist = self._calc_individual_damage_dist()

        damge_dists = []
        for dice, event_prob in enumerate(dist.values):
            # If the probability is zero then no-op
            if event_prob == 0:
                continue
            # Multiply the individual damage distributions by the number dice
            damge_dists.append(PMF.convolve_many([individual_dist] * dice) * event_prob)
        return PMF.flatten(damge_dists)

    def _calc_individual_damage_dist(self):
        # Get the basic damage distribution
        dice_dists = self.attack.weapon.damage

        # Apply modifers to the damage distribution
        mod_dists = self.attack.modifiers.modify_damage_dice(dice_dists)

        # Calculate the damge distribution after the feel no pain has been applied
        fnp_dist = self._calc_fnp_dist(mod_dists.convolve())

        # Clip the damage dist to the wounds characteristic of the target
        return fnp_dist.ceiling(self.attack.target.wounds)

    def _calc_fnp_dist(self, dist):
        dists = []
        mod_thresh = self.attack.modifiers.modify_fnp_thresh(self.attack.target.fnp)
        for dice, event_prob in enumerate(dist.values):
            if event_prob == 0:
                continue
            dice_dists = self.attack.modifiers.modify_fnp_dice(
                PMFCollection.mdn(dice, 6),
                self.attack.target.fnp,
                mod_thresh,
            )
            binom_dists = dice_dists.convert_binomial_less_than(mod_thresh).convolve()
            dists.append(binom_dists * event_prob)
        return PMF.flatten(dists)


