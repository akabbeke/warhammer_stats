"""
Classes related to modeling a probability mass function and collections of them
https://en.wikipedia.org/wiki/Probability_mass_function
"""

from __future__ import annotations
import math

from typing import List, Union, Callable
from numpy import fft, zeros

# pylint: disable=too-many-public-methods

class PMF:
    """
    Discrete Probability Distribution - Used to keep track of the probability of random discrete
    events
    """
    def __init__(self, values: List[float]):
        self.values = list(values)

    def __str__(self) -> str:
        return str(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __mul__(self, other: Union[int, float]) -> PMF:
        return PMF([other*x for x in self.values])

    def __rmul__(self, other: Union[int, float]) -> PMF:
        return self.__mul__(other)

    def ceiling(self, value: Union[int, float]) -> PMF:
        """
        Sum the probability of all values >= the ceiling value
        """
        new_values = []
        for i, prob in enumerate(self.values):
            if i <= value:
                new_values.append(prob)
            else:
                new_values[value] += prob
        return PMF(new_values)

    def trim_tail(self, thresh: Union[int, float]) -> PMF:
        """
        Trim the long tail off where p < threshold
        """
        in_body = False
        trimmed_dist = []
        for element in self.values[::-1]:
            if in_body or element >= thresh:
                in_body = True
                trimmed_dist.append(element)
        return PMF(trimmed_dist[::-1])

    def cumulative(self) -> PMF:
        """
        Probability of at least each value
        """
        cumu_dist = []
        for i in range(len(self.values)):
            cumu_dist.append(sum(self.values[i:]))
        return PMF(cumu_dist)

    def re_roll_value(self, value: Union[int, float]) -> PMF:
        """
        Re-roll a specific value (eg re-roll 1's)
        """
        rr_mask = [0.0 if x == value else 1.0 for x in range(len(self))]
        rr_dist = [self.values[value] * x for x in self.values]
        new_dist = []
        for i, prob in enumerate(self.values):
            new_dist.append(rr_mask[i]*prob + rr_dist[i])
        return PMF(new_dist)

    def re_roll_less_than(self, value: Union[int, float]) -> PMF:
        """
        Re-roll all values below a specific value
        """
        rr_mask = [0.0 if i < value else x for i, x in enumerate(self.values)]
        for i, _ in enumerate(self.values):
            if i < value:
                for j, _ in enumerate(self.values):
                    rr_mask[j] += self.values[i] * self.values[j]
        return PMF(rr_mask)

    def convert_binomial(self, thresh: Union[int, float]) -> PMF:
        """
        Convert the pmf into a binomial PMF by flatteing all values above or equal to the
        threshold into 1 and all below into 0
        """
        return PMF([sum(self.values[:thresh]), sum(self.values[thresh:])])

    def convert_binomial_less_than(self, thresh: Union[int, float]) -> PMF:
        """
        Convert the pmf into a binomial PMF by flatteing all values above or equal to the
        threshold into 0 and all below into 1
        """
        return PMF([sum(self.values[thresh:]), sum(self.values[:thresh])])

    def get(self, value: int) -> float:
        """
        Fetch the probability for the value.
        """
        if value < 0:
            return 0.0
        if value > len(self.values):
            return 0.0
        return self.values[value]

    def expand_to(self, length: int) -> PMF:
        """
        Pad values with zeros to reach the desired length
        """
        return PMF(self.values + [0.0] * max(length - len(self), 0))

    def add_value(self, value: int) -> PMF:
        """
        Add an integer value to the PMF by shifting the values right
        """
        return PMF([0.0] * value + self.values)

    def max_of_two(self) -> PMF:
        """
        Produce the PMF from rolling two of this PMF and choosing the higher
        """
        return PMF.max_of_two_pmf(self, self)

    def roll(self, roll_value: int) -> PMF:
        """
        Roll the values of the PMF left or right. If rolling right pad the left with zeroes.
        If rolling left flatten values into the zero value.
        """
        if roll_value == 0: # pylint: disable=no-else-return
            return self
        elif roll_value > 0:
            return PMF([0.0] * roll_value + self.values)
        return PMF([sum(self.values[:(-1*roll_value)+1])] + self.values[(-1*roll_value)+1:])

    def div_min_one(self, divisor: Union[int, float]) -> PMF:
        """
        Divide the index values of the PMF by the divisor with a minimum of one.
        I added this to accomidate Abadons half damage ability.
        """
        new_dist = [0.0] * len(self.values)
        for i, value in enumerate(self.values):
            new_dist[math.ceil(i/divisor)] += value
        return PMF(new_dist)

    def min(self, min_val: int) -> PMF:
        """
        Sets the minimum value of the PMF by adding the sum of all probabilites less than
        the min_val to the min val.
        """
        return PMF([0.0] * min_val + [sum(self.values[:min_val+1])] + self.values[min_val+1:])

    def mean(self) -> PMF:
        """
        Return the expected value of the PMF
        """
        return sum([x*p for x, p in enumerate(self.values)])

    def std(self) -> PMF:
        """
        Return the standard deviation of the PMF
        """
        mean = self.mean()
        exp_mean = sum([(x**2)*p for x, p in enumerate(self.values)])
        return (exp_mean - mean**2)**(0.5)

    @classmethod
    def dn(cls, dice_sides: int) -> PMF: # pylint: disable=invalid-name
        """
        Return the PMD for a dice with dice_sides number of sides
        """
        return PMF([0.0] + [1/dice_sides] * dice_sides)

    @classmethod
    def static(cls, static_value: int) -> PMF:
        """
        Return the PMD for exactly the static_value
        """
        return PMF([0.0] * static_value + [1.0])

    @classmethod
    def convolve_many(cls, dists: List[PMF]) -> PMF:
        """
        Convolve a list of 1d float arrays together, using FFTs.
        The arrays need not have the same length, but each array should
        have length at least 1.

        This works becuse the convolution in the frequency space is a single
        element-wise multiplication. FFT gets us into the frequency space faster
        than the full FT
        """

        result_length = 1 + sum((len(dist) - 1) for dist in dists)

        # Copy each array into a 2d array of the appropriate shape.
        rows = zeros((len(dists), result_length))
        for i, dist in enumerate(dists):
            rows[i, :len(dist)] = dist.values

        # Transform, take the product, and do the inverse transform
        # to get the convolution.
        fft_of_rows = fft.fft(rows)
        fft_of_convolution = fft_of_rows.prod(axis=0)
        convolution = fft.ifft(fft_of_convolution)

        # Assuming real inputs, the imaginary part of the output can
        # be ignored.
        return PMF(convolution.real)

    @classmethod
    def flatten(cls, dists: List[PMF]) -> PMF:
        """
        Sum a set of distributions to produce a new distribution.
        """
        flat_dist = [0.0] * (max([len(dist) for dist in dists]))
        for dist in dists:
            for i, value in enumerate(dist.values):
                flat_dist[i] += value
        return PMF(flat_dist)

    @classmethod
    def match_sizes(cls, dists: List[PMF]) -> PMF:
        """
        Map a set of PMFs to the same size
        """
        largest = max([len(x) for x in dists])
        return [x.expand_to(largest) for x in dists]

    @classmethod
    def max_of_two_pmf(cls, dist1: PMF, dist2: PMF) -> PMF:
        """
        Compute the PMF for the max of two PMF
        """
        dist1, dist2 = cls.match_sizes([dist1, dist2])
        new_dist = []
        for value in range(len(dist1)):
            prob = dist1.get(value) * dist2.get(value)
            prob += dist1.values[value] * sum(dist2.values[:value])
            prob += dist2.values[value] * sum(dist1.values[:value])
            new_dist.append(prob)
        return PMF(new_dist)

class PMFCollection:
    """
    Discrete Probability Distribution - Used to keep track of collections of PMFs
    """
    def __init__(self, pmfs: List[PMF] = None):
        self.pmfs = pmfs or []

    def __bool__(self) -> bool:
        return len(self) > 0

    def __len__(self) -> int:
        return len(self.pmfs)

    def __str__(self) -> str:
        return str([x.values for x in self.pmfs])

    def get(self, index: int, defualt: PMF = None) -> PMF:
        """
        Fetch the PMF at the index
        """
        try:
            return self.pmfs[index]
        except IndexError:
            return defualt

    def thresh_mod(self, thresh_mod: int) -> PMFCollection:
        """
        Modify the collection based on a dice modifer
        """
        if thresh_mod == 0 or self.pmfs == []: # pylint: disable=no-else-return
            return self
        elif thresh_mod > 0:
            return PMFCollection(self.pmfs[:1] * thresh_mod + self.pmfs)
        return PMFCollection(
            (self.pmfs + self.pmfs[-1:] * (-1 * thresh_mod))[-1*len(self.pmfs):]
        )

    def mul_col(self, other_collection: PMFCollection) -> PMFCollection:
        """
        Multipy this PMFCollection byt another PMFCollection
        """
        return PMFCollection([self.mul_pmf(pmf) for pmf in other_collection.pmfs])

    def mul_pmf(self, pmf: PMF) -> PMF:
        """
        Multiply the collection with a pmf and return a convolution of the results
        """
        new_pmfs = []
        for i, value in enumerate(pmf.values):
            new_pmfs.append(self.get(i, PMF.static(0)) * value)
        return PMF.flatten(new_pmfs)

    def convolve(self) -> PMF:
        """
        Convolve the PMFs into a single PMF
        """
        return PMF.convolve_many(self.pmfs)

    def convert_binomial_less_than(self, thresh: int) -> PMFCollection:
        """
        Convert the PMFs into a Binomial distribution for values less than the thresh
        """
        return self.map(lambda x: x.convert_binomial_less_than(thresh))

    def convert_binomial(self, thresh) -> PMFCollection:
        """
        Convert the PMFs into a Binomial distribution for values greater than or equal to the thresh
        """
        return self.map(lambda x: x.convert_binomial(thresh))

    def map(self, func: Callable[[PMF], PMF]) -> PMFCollection:
        """
        Map a function over the PMFs in the PMFCollection
        """
        return PMFCollection([func(x) for x in self.pmfs])

    @classmethod
    def add_many(cls, collection_list: List[PMFCollection]) -> PMFCollection:
        """
        Adds many PMFCollection
        """
        new_pmfs = []
        for i in range(max([len(x) for x in collection_list] or [0])):
            new_pmfs.append(
                PMF.convolve_many([x.get(i, PMF.static(0)) for x in collection_list if x])
            )
        return PMFCollection(new_pmfs)

    @classmethod
    def empty(cls) -> PMFCollection:
        """
        Return an empty PMFCollection
        """
        return PMFCollection([])

    @classmethod
    def mdn(cls, number_of_dice: int, number_of_sides: int) -> PMFCollection:
        """
        Return a PMFCollection of m dn PMFs
        """
        return PMFCollection([PMF.dn(number_of_sides)] * number_of_dice)

    @classmethod
    def static(cls, static_value) -> PMFCollection:
        """
        Return a PMFCollection of a single static value
        """
        return PMFCollection([PMF.static(static_value)])
