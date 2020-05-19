from unittest import TestCase

from warhammer_stats.pmf import PMF

class TestAttack(TestCase):

    def setUp(self):
        self.pmf_examples = [
            PMF.dn(6),
            PMF.dn(5),
            PMF.dn(1),
            PMF.static(0),
            PMF.static(5),
            PMF.dn(6).convert_binomial(5),
            PMF.dn(6).re_roll_value(1),
        ]

    def assertRoundEqual(self, a, b):
        self.assertEqual(round(a, 10), round(b, 10))

    def test_dn(self):
        """
        Check that we propery generate d(n) PMFs
        """
        for i in range(1, 100):
            pmf = PMF.dn(i)
            # You should never be able roll a 0 on a dice
            self.assertEqual(pmf.get(0), 0)

            # Check the probability is uniform
            self.assertTrue(all([x==1/i for x in pmf.values[1:]]))

    def test_static(self):
        """
        Test we properly generate the PMF for static values
        """
        for i in range(100):
            pmf = PMF.static(i)
            self.assertEqual(pmf.get(i), 1)
            self.assertEqual(sum(pmf.values), 1)

    def test_convolve_many(self):
        """
        test convolving two PMFs
        """
        for pmf_1 in self.pmf_examples:
            for pmf_2 in self.pmf_examples:
                pmf_convolved = PMF.convolve_many([pmf_1, pmf_2])
                self.assertEqual(len(pmf_convolved.values), len(pmf_1.values) + len(pmf_2.values) - 1)
                self.assertRoundEqual(pmf_convolved.mean(), pmf_1.mean() + pmf_2.mean())

    def test_flatten(self):
        """
        test that flattening two dists into one sums to one
        """
        for pmf_1 in self.pmf_examples:
            for pmf_2 in self.pmf_examples:
                for i in range(100):
                    flattened = PMF.flatten([pmf_1 * (i/100), pmf_2 * ((100-i)/100)])
                    self.assertRoundEqual(sum(flattened.values), 1)


