# ----------------------------------------------------------------------------
# Copyright (c) 2017--, wol development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from unittest import TestCase, main

from skbio.stats.distance import DistanceMatrix
from skbio.stats.distance._base import (DissimilarityMatrixError,
                                        MissingIDError)
from skbio.util import get_data_path

from prototypeSelection import (
    _validate_parameters,
    prototype_selection_exhaustive,
    prototype_selection_constructive_maxdist,
    prototype_selection_destructive_maxdist,
    prototype_selection_constructive_protoclass,
    prototype_selection_constructive_pMedian,
    _protoclass,
    distance_sum)


class prototypeSelection(TestCase):
    def setUp(self):
        self.dm100 = DistanceMatrix.read(get_data_path('distMatrix_100.txt'))
        self.dm20 = DistanceMatrix.read(get_data_path('distMatrix_20_f5.txt'))

    def test__validate_parameters(self):
        # test that number of prototypes cannot be smaller than 2
        self.assertRaisesRegex(
            ValueError,
            ("'num_prototypes' must be >= 2, since a single prototype is "
             "useless."),
            _validate_parameters,
            self.dm20,
            1)

        self.assertRaisesRegex(
            ValueError,
            ("'num_prototypes' must be >= 2, since a single prototype is "
             "useless."),
            _validate_parameters,
            self.dm20,
            1, [])

        # test that number of prototypes cannot be greater than size of
        # distance matrix
        self.assertRaisesRegex(
            ValueError,
            ("'num_prototypes' must be smaller than the number of elements "
             "in the distance matrix, otherwise no reduction is necessary."),
            _validate_parameters,
            self.dm20,
            30)

        # test that seed set cannot contain duplicated IDs
        self.assertRaisesRegex(
            ValueError,
            "There are duplicated IDs in 'seedset'.",
            _validate_parameters,
            self.dm20,
            5,
            ['A', 'B', 'B'])

        # test that seed set cannot contain IDs absent in distance matrix
        self.assertRaisesRegex(
            ValueError,
            ("'seedset' is not a subset of the element IDs in the distance "
             "matrix."),
            _validate_parameters,
            self.dm20,
            5,
            ['A', 'B', '_'])

        # test that size of seed set cannot be larger than number of
        # prototypes to be found
        self.assertRaisesRegex(
            ValueError,
            ("Size of 'seedset' must be smaller than the number of prototypes "
             "to select."),
            _validate_parameters,
            self.dm20,
            3,
            ['A', 'B', 'C', 'D'])

    def test_distance_sum(self):
        # test that no missing IDs can be used
        self.assertRaisesRegex(
            MissingIDError,
            'The ID \'X\' is not in the dissimilarity matrix.',
            distance_sum,
            ['A', 'B', 'X'],
            self.dm20)

        # test that no ID is duplicated
        self.assertRaisesRegex(
            DissimilarityMatrixError,
            'IDs must be unique. Found the following duplicate IDs',
            distance_sum,
            ['A', 'B', 'C', 'D', 'B'],
            self.dm20)

        # test that list of IDs holds at least 1 element
        self.assertRaisesRegex(
            DissimilarityMatrixError,
            'Data must be at least 1x1 in size',
            distance_sum,
            [],
            self.dm20)

        # test for result correctness
        self.assertAlmostEqual(2454.1437464961, distance_sum(self.dm100.ids,
                                                             self.dm100))
        self.assertAlmostEqual(32.9720926186, distance_sum(
            ['550.L1S173.s.1.sequence', '550.L1S141.s.1.sequence',
             '550.L1S18.s.1.sequence', '550.L1S156.s.1.sequence',
             '550.L1S110.s.1.sequence', '550.L1S143.s.1.sequence',
             '550.L1S134.s.1.sequence', '550.L1S103.s.1.sequence',
             '550.L1S185.s.1.sequence', '550.L1S114.s.1.sequence',
             '550.L1S138.s.1.sequence', '550.L1S137.s.1.sequence'],
            self.dm100))

        self.assertAlmostEqual(81.6313, distance_sum(self.dm20.ids,
                                                     self.dm20))
        self.assertAlmostEqual(13.3887, distance_sum(
            ['A', 'C', 'F', 'G', 'M', 'N', 'P', 'T'],
            self.dm20))

    def test_exhaustive(self):
        # check if execution is rejected if number of combination is too high
        self.assertRaisesRegex(
            RuntimeError,
            'Cowardly refuse to test ',
            prototype_selection_exhaustive,
            self.dm20,
            5,
            max_combinations_to_test=1000)

        self.assertRaisesRegex(
            ValueError,
            "must be >= 2, since a single",
            prototype_selection_exhaustive,
            self.dm20,
            1)

        self.assertRaisesRegex(
            ValueError,
            "otherwise no reduction is necessary",
            prototype_selection_exhaustive,
            self.dm20,
            len(self.dm20.ids)+1)

        res = prototype_selection_exhaustive(self.dm20, 3)
        self.assertCountEqual(('A', 'P', 'Q'), res)
        self.assertAlmostEqual(1.841, distance_sum(res, self.dm20))

        res = prototype_selection_exhaustive(self.dm20, 4)
        self.assertCountEqual(('A', 'J', 'P', 'T'), res)
        self.assertAlmostEqual(3.4347, distance_sum(res, self.dm20))

        res = prototype_selection_exhaustive(self.dm20, 5)
        self.assertCountEqual(('A', 'C', 'O', 'P', 'T'), res)
        self.assertAlmostEqual(5.4494, distance_sum(res, self.dm20))

        res = prototype_selection_exhaustive(self.dm20, 18)
        self.assertCountEqual(
            ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'L', 'M', 'N',
             'O', 'P', 'Q', 'R', 'T'),
            res)
        self.assertAlmostEqual(66.94, distance_sum(res, self.dm20))

        res = prototype_selection_exhaustive(self.dm20, 19)
        self.assertCountEqual(
            ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'L', 'M', 'N',
             'O', 'P', 'Q', 'R', 'S', 'T'),
            res)
        self.assertAlmostEqual(74.1234, distance_sum(res, self.dm20))

    def test_prototype_selection_constructive_maxdist(self):
        self.assertRaisesRegex(
            ValueError,
            "must be >= 2, since a single",
            prototype_selection_constructive_maxdist,
            self.dm20,
            1)

        self.assertRaisesRegex(
            ValueError,
            "otherwise no reduction is necessary",
            prototype_selection_constructive_maxdist,
            self.dm20,
            len(self.dm20.ids)+1)

        res = prototype_selection_constructive_maxdist(self.dm20, 3)
        self.assertCountEqual(('A', 'P', 'Q'), res)
        self.assertAlmostEqual(1.8410, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_maxdist(self.dm20, 4)
        self.assertCountEqual(('A', 'P', 'Q', 'O'), res)
        self.assertAlmostEqual(3.4284, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_maxdist(self.dm20, 5)
        self.assertCountEqual(('A', 'P', 'Q', 'O', 'C'), res)
        self.assertAlmostEqual(5.4480, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_maxdist(self.dm20, 18)
        self.assertCountEqual(
            ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'L', 'M', 'N',
             'O', 'P', 'Q', 'R', 'T'),
            res)
        self.assertAlmostEqual(66.9400, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_maxdist(self.dm20, 19)
        self.assertCountEqual(
            ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'L', 'M', 'N',
             'O', 'P', 'Q', 'R', 'T', 'S'),
            res)
        self.assertAlmostEqual(74.1234, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_maxdist(self.dm100, 5)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S183.s.1.sequence',
             '550.L1S136.s.1.sequence', '550.L1S115.s.1.sequence',
             '550.L1S176.s.1.sequence'),
            res)
        self.assertAlmostEqual(6.51378126, distance_sum(res, self.dm100))

        res = prototype_selection_constructive_maxdist(self.dm100, 10)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S183.s.1.sequence',
             '550.L1S147.s.1.sequence', '550.L1S13.s.1.sequence',
             '550.L1S136.s.1.sequence', '550.L1S15.s.1.sequence',
             '550.L1S115.s.1.sequence', '550.L1S129.s.1.sequence',
             '550.L1S189.s.1.sequence', '550.L1S176.s.1.sequence'),
            res)
        self.assertAlmostEqual(26.88492051, distance_sum(res, self.dm100))

        res = prototype_selection_constructive_maxdist(self.dm100, 20)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S173.s.1.sequence',
             '550.L1S183.s.1.sequence', '550.L1S180.s.1.sequence',
             '550.L1S135.s.1.sequence', '550.L1S18.s.1.sequence',
             '550.L1S178.s.1.sequence', '550.L1S147.s.1.sequence',
             '550.L1S134.s.1.sequence', '550.L1S13.s.1.sequence',
             '550.L1S136.s.1.sequence', '550.L1S15.s.1.sequence',
             '550.L1S132.s.1.sequence', '550.L1S115.s.1.sequence',
             '550.L1S11.s.1.sequence', '550.L1S151.s.1.sequence',
             '550.L1S121.s.1.sequence', '550.L1S129.s.1.sequence',
             '550.L1S189.s.1.sequence', '550.L1S176.s.1.sequence'),
            res)
        self.assertAlmostEqual(107.02463381, distance_sum(res, self.dm100))

    def test_prototype_selection_destructive_maxdist(self):
        self.assertRaisesRegex(
            ValueError,
            "must be >= 2, since a single",
            prototype_selection_destructive_maxdist,
            self.dm20,
            1)

        self.assertRaisesRegex(
            ValueError,
            "otherwise no reduction is necessary",
            prototype_selection_destructive_maxdist,
            self.dm20,
            len(self.dm20.ids)+1)

        res = prototype_selection_destructive_maxdist(self.dm20, 3)
        self.assertCountEqual(('A', 'P', 'T'), res)
        self.assertAlmostEqual(1.8389, distance_sum(res, self.dm20))

        res = prototype_selection_destructive_maxdist(self.dm20, 4)
        self.assertCountEqual(('A', 'P', 'T', 'C'), res)
        self.assertAlmostEqual(3.4285, distance_sum(res, self.dm20))

        res = prototype_selection_destructive_maxdist(self.dm20, 5)
        self.assertCountEqual(('A', 'P', 'T', 'C', 'O'), res)
        self.assertAlmostEqual(5.4494, distance_sum(res, self.dm20))

        res = prototype_selection_destructive_maxdist(self.dm20, 18)
        self.assertCountEqual(
            ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'L', 'M', 'N',
             'O', 'P', 'Q', 'R', 'T'),
            res)
        self.assertAlmostEqual(66.9400, distance_sum(res, self.dm20))

        res = prototype_selection_destructive_maxdist(self.dm20, 19)
        self.assertCountEqual(
            ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'L', 'M', 'N',
             'O', 'P', 'Q', 'R', 'T', 'S'),
            res)
        self.assertAlmostEqual(74.1234, distance_sum(res, self.dm20))

        res = prototype_selection_destructive_maxdist(self.dm100, 5)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S13.s.1.sequence',
             '550.L1S129.s.1.sequence', '550.L1S189.s.1.sequence',
             '550.L1S176.s.1.sequence'),
            res)
        self.assertAlmostEqual(6.51661889263, distance_sum(res, self.dm100))

        res = prototype_selection_destructive_maxdist(self.dm100, 10)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S147.s.1.sequence',
             '550.L1S13.s.1.sequence', '550.L1S136.s.1.sequence',
             '550.L1S15.s.1.sequence', '550.L1S115.s.1.sequence',
             '550.L1S151.s.1.sequence', '550.L1S129.s.1.sequence',
             '550.L1S189.s.1.sequence', '550.L1S176.s.1.sequence'),
            res)
        self.assertAlmostEqual(26.8818426729, distance_sum(res, self.dm100))

        res = prototype_selection_destructive_maxdist(self.dm100, 20)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S173.s.1.sequence',
             '550.L1S183.s.1.sequence', '550.L1S180.s.1.sequence',
             '550.L1S135.s.1.sequence', '550.L1S18.s.1.sequence',
             '550.L1S175.s.1.sequence', '550.L1S147.s.1.sequence',
             '550.L1S134.s.1.sequence', '550.L1S13.s.1.sequence',
             '550.L1S136.s.1.sequence', '550.L1S15.s.1.sequence',
             '550.L1S132.s.1.sequence', '550.L1S115.s.1.sequence',
             '550.L1S11.s.1.sequence', '550.L1S151.s.1.sequence',
             '550.L1S121.s.1.sequence', '550.L1S129.s.1.sequence',
             '550.L1S189.s.1.sequence', '550.L1S176.s.1.sequence'),
            res)
        self.assertAlmostEqual(106.991415187, distance_sum(res, self.dm100))

    def test_prototype_selection_constructive_protoclass(self):
        self.assertRaisesRegex(
            RuntimeError,
            "Number of iterations exceeded before",
            prototype_selection_constructive_protoclass,
            self.dm20,
            5,
            steps=1
        )

        self.assertRaisesRegex(
            ValueError,
            "must be >= 2, since a single",
            prototype_selection_constructive_protoclass,
            self.dm20,
            1)

        self.assertRaisesRegex(
            ValueError,
            "otherwise no reduction is necessary",
            prototype_selection_constructive_protoclass,
            self.dm20,
            len(self.dm20.ids)+1)

        res = prototype_selection_constructive_protoclass(self.dm20, 3)
        self.assertCountEqual(('A', 'H', 'Q'), res)
        self.assertAlmostEqual(1.7387, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_protoclass(self.dm20, 4)
        self.assertCountEqual(('A', 'B', 'Q', 'G'), res)
        self.assertAlmostEqual(3.278799999, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_protoclass(self.dm20, 5)
        self.assertCountEqual(('H', 'C', 'G', 'Q', 'A'), res)
        self.assertAlmostEqual(5.2747, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_protoclass(self.dm20, 18)
        self.assertCountEqual(
            ('D', 'I', 'A', 'B', 'C', 'E', 'F', 'G', 'J', 'K', 'L', 'M', 'N',
             'P', 'Q', 'R', 'S', 'T'),
            res)
        self.assertAlmostEqual(66.4964, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_protoclass(self.dm20, 19)
        self.assertCountEqual(
            ('I', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M',
             'N', 'P', 'Q', 'R', 'S', 'T'),
            res)
        self.assertAlmostEqual(73.6075, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_protoclass(self.dm100, 5)
        self.assertCountEqual(
            ('550.L1S156.s.1.sequence', '550.L1S105.s.1.sequence',
             '550.L1S18.s.1.sequence', '550.L1S1.s.1.sequence',
             '550.L1S165.s.1.sequence'),
            res)
        self.assertAlmostEqual(5.72452336845315, distance_sum(res, self.dm100))

        res = prototype_selection_constructive_protoclass(self.dm100, 10)
        self.assertCountEqual(
            ('550.L1S156.s.1.sequence', '550.L1S117.s.1.sequence',
             '550.L1S14.s.1.sequence', '550.L1S182.s.1.sequence',
             '550.L1S135.s.1.sequence', '550.L1S144.s.1.sequence',
             '550.L1S1.s.1.sequence', '550.L1S146.s.1.sequence',
             '550.L1S136.s.1.sequence', '550.L1S176.s.1.sequence'),
            res)
        self.assertAlmostEqual(24.9367079851425, distance_sum(res, self.dm100))

        res = prototype_selection_constructive_protoclass(self.dm100, 20)
        self.assertCountEqual(
            ('550.L1S163.s.1.sequence', '550.L1S117.s.1.sequence',
             '550.L1S148.s.1.sequence', '550.L1S179.s.1.sequence',
             '550.L1S128.s.1.sequence', '550.L1S12.s.1.sequence',
             '550.L1S182.s.1.sequence', '550.L1S133.s.1.sequence',
             '550.L1S127.s.1.sequence', '550.L1S139.s.1.sequence',
             '550.L1S173.s.1.sequence', '550.L1S1.s.1.sequence',
             '550.L1S141.s.1.sequence', '550.L1S165.s.1.sequence',
             '550.L1S18.s.1.sequence', '550.L1S103.s.1.sequence',
             '550.L1S16.s.1.sequence', '550.L1S136.s.1.sequence',
             '550.L1S132.s.1.sequence', '550.L1S176.s.1.sequence'),
            res)
        self.assertAlmostEqual(101.104980832350, distance_sum(res, self.dm100))

    def test__protoclass(self):
        res = _protoclass(self.dm20, 0.42)
        self.assertCountEqual(('D', 'Q', 'A'), res)
        self.assertAlmostEqual(1.7409, distance_sum(res, self.dm20))

        res = _protoclass(self.dm20, 0.40)
        self.assertCountEqual(('S', 'Q', 'A', 'B'), res)
        self.assertAlmostEqual(3.1509, distance_sum(res, self.dm20))

        res = _protoclass(self.dm20, 0.38)
        self.assertCountEqual(('F', 'G', 'Q', 'A', 'B'), res)
        self.assertAlmostEqual(5.1588, distance_sum(res, self.dm20))

        res = _protoclass(self.dm20, 0.31)
        self.assertCountEqual(
            ('D', 'I', 'A', 'B', 'C', 'E', 'F', 'G', 'J', 'K', 'L', 'M', 'N',
             'P', 'Q', 'R', 'S', 'T'),
            res)
        self.assertAlmostEqual(66.4964, distance_sum(res, self.dm20))

        res = _protoclass(self.dm20, 0.305)
        self.assertCountEqual(
            ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
             'N', 'P', 'Q', 'R', 'S', 'T'),
            res)
        self.assertAlmostEqual(73.6075, distance_sum(res, self.dm20))

        res = _protoclass(self.dm100, 0.5)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S105.s.1.sequence',
             '550.L1S117.s.1.sequence', '550.L1S165.s.1.sequence',
             '550.L1S167.s.1.sequence'),
            res)
        self.assertAlmostEqual(5.38708502529887, distance_sum(res, self.dm100))

        res = _protoclass(self.dm100, 0.41)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S117.s.1.sequence',
             '550.L1S133.s.1.sequence', '550.L1S136.s.1.sequence',
             '550.L1S14.s.1.sequence', '550.L1S146.s.1.sequence',
             '550.L1S149.s.1.sequence', '550.L1S163.s.1.sequence',
             '550.L1S176.s.1.sequence', '550.L1S183.s.1.sequence'),
            res)
        self.assertAlmostEqual(25.0901634594939, distance_sum(res, self.dm100))

        res = _protoclass(self.dm100, 0.374)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S103.s.1.sequence',
             '550.L1S117.s.1.sequence', '550.L1S12.s.1.sequence',
             '550.L1S127.s.1.sequence', '550.L1S128.s.1.sequence',
             '550.L1S132.s.1.sequence', '550.L1S133.s.1.sequence',
             '550.L1S136.s.1.sequence', '550.L1S139.s.1.sequence',
             '550.L1S141.s.1.sequence', '550.L1S148.s.1.sequence',
             '550.L1S16.s.1.sequence', '550.L1S163.s.1.sequence',
             '550.L1S173.s.1.sequence', '550.L1S175.s.1.sequence',
             '550.L1S176.s.1.sequence', '550.L1S18.s.1.sequence',
             '550.L1S180.s.1.sequence', '550.L1S187.s.1.sequence'),
            res)
        self.assertAlmostEqual(101.91549799314, distance_sum(res, self.dm100))

        # test seedset function, i.e. are 'A' and 'B' included in prototypes
        res = _protoclass(self.dm20, 0.405, seedset=['A', 'B'])
        self.assertCountEqual(res, ['A', 'B', 'D', 'Q'])

        # test if at least one seed element is returned for too high epsilon
        res = _protoclass(self.dm20, 0.805, seedset=['A', 'B'])
        self.assertCountEqual(res, ['A', 'B'])

    def test_prototype_selection_constructive_pMedian(self):
        self.assertRaisesRegex(
            ValueError,
            "must be >= 2, since a single",
            prototype_selection_constructive_pMedian,
            self.dm20,
            1)

        self.assertRaisesRegex(
            ValueError,
            "otherwise no reduction is necessary",
            prototype_selection_constructive_pMedian,
            self.dm20,
            len(self.dm20.ids)+1)

        res = prototype_selection_constructive_pMedian(self.dm20, 3)
        self.assertCountEqual(('A', 'H', 'Q'), res)
        self.assertAlmostEqual(1.7387, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_pMedian(self.dm20, 4)
        self.assertCountEqual(('A', 'H', 'Q', 'E'), res)
        self.assertAlmostEqual(3.2306, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_pMedian(self.dm20, 5)
        self.assertCountEqual(('A', 'H', 'Q', 'E', 'I'), res)
        self.assertAlmostEqual(5.1449, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_pMedian(self.dm20, 18)
        self.assertCountEqual(
            ('A', 'B', 'C', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
             'P', 'Q', 'R', 'S', 'T'),
            res)
        self.assertAlmostEqual(66.4087, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_pMedian(self.dm20, 19)
        self.assertCountEqual(
            ('A', 'B', 'C', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
             'P', 'Q', 'R', 'S', 'T', 'D'),
            res)
        self.assertAlmostEqual(73.6075, distance_sum(res, self.dm20))

        res = prototype_selection_constructive_pMedian(self.dm100, 5)
        self.assertCountEqual(
            ('550.L1S167.s.1.sequence', '550.L1S117.s.1.sequence',
             '550.L1S12.s.1.sequence', '550.L1S163.s.1.sequence',
             '550.L1S148.s.1.sequence'),
            res)
        self.assertAlmostEqual(4.8783450, distance_sum(res, self.dm100))

        res = prototype_selection_constructive_pMedian(self.dm100, 10)
        self.assertCountEqual(
            ('550.L1S167.s.1.sequence', '550.L1S117.s.1.sequence',
             '550.L1S12.s.1.sequence', '550.L1S163.s.1.sequence',
             '550.L1S148.s.1.sequence', '550.L1S185.s.1.sequence',
             '550.L1S133.s.1.sequence', '550.L1S126.s.1.sequence',
             '550.L1S116.s.1.sequence', '550.L1S1.s.1.sequence'),
            res)
        self.assertAlmostEqual(23.75526307, distance_sum(res, self.dm100))

        res = prototype_selection_constructive_pMedian(self.dm100, 20)
        self.assertCountEqual(
            ('550.L1S167.s.1.sequence', '550.L1S117.s.1.sequence',
             '550.L1S12.s.1.sequence', '550.L1S163.s.1.sequence',
             '550.L1S148.s.1.sequence', '550.L1S185.s.1.sequence',
             '550.L1S133.s.1.sequence', '550.L1S126.s.1.sequence',
             '550.L1S116.s.1.sequence', '550.L1S1.s.1.sequence',
             '550.L1S139.s.1.sequence', '550.L1S175.s.1.sequence',
             '550.L1S176.s.1.sequence', '550.L1S181.s.1.sequence',
             '550.L1S173.s.1.sequence', '550.L1S136.s.1.sequence',
             '550.L1S16.s.1.sequence', '550.L1S123.s.1.sequence',
             '550.L1S141.s.1.sequence', '550.L1S13.s.1.sequence'),
            res)
        self.assertAlmostEqual(100.32727028, distance_sum(res, self.dm100))

    def test_seedset(self):
        # test seedset function, first include elements that are supposed to
        # be selected, to see if result is identical
        seedset = set(['A', 'P'])
        res = prototype_selection_exhaustive(self.dm20, 5, seedset)
        self.assertCountEqual(('A', 'P', 'T', 'C', 'O'), res)
        self.assertAlmostEqual(5.4494, distance_sum(res, self.dm20))

        seedset = set(['A', 'P'])
        res = prototype_selection_constructive_maxdist(self.dm20, 5, seedset)
        self.assertCountEqual(('A', 'P', 'Q', 'C', 'O'), res)
        self.assertAlmostEqual(5.4480, distance_sum(res, self.dm20))

        seedset = set(['A', 'H'])
        res = prototype_selection_constructive_pMedian(self.dm20, 5, seedset)
        self.assertCountEqual(('A', 'H', 'Q', 'E', 'I'), res)
        self.assertAlmostEqual(5.1449, distance_sum(res, self.dm20))

        seedset = set(['A', 'P'])
        res = prototype_selection_destructive_maxdist(self.dm20, 5, seedset)
        self.assertCountEqual(('A', 'P', 'T', 'C', 'O'), res)
        self.assertAlmostEqual(5.4494, distance_sum(res, self.dm20))

        seedset = set(['H', 'C'])
        res = prototype_selection_constructive_protoclass(
            self.dm20, 5, seedset=seedset)
        self.assertCountEqual(('H', 'C', 'Q', 'A', 'G'), res)
        self.assertAlmostEqual(5.2747, distance_sum(res, self.dm20))

        # then include different elements, to see result changes, and score
        # (sum of distances) slightly drops.
        seedset = ['G', 'I']
        res = prototype_selection_exhaustive(self.dm20, 5, seedset)
        self.assertCountEqual(('A', 'G', 'I', 'C', 'T'), res)
        self.assertAlmostEqual(5.3091, distance_sum(res, self.dm20))

        seedset = ['G', 'I']
        res = prototype_selection_constructive_maxdist(self.dm20, 5, seedset)
        self.assertCountEqual(('A', 'G', 'I', 'C', 'T'), res)
        self.assertAlmostEqual(5.3091, distance_sum(res, self.dm20))

        seedset = ['G', 'T']
        res = prototype_selection_constructive_pMedian(self.dm20, 5, seedset)
        self.assertCountEqual(('A', 'G', 'E', 'H', 'T'), res)
        self.assertAlmostEqual(5.2263, distance_sum(res, self.dm20))

        seedset = ['G', 'I']
        res = prototype_selection_destructive_maxdist(self.dm20, 5, seedset)
        self.assertCountEqual(('A', 'G', 'I', 'K', 'T'), res)
        self.assertAlmostEqual(5.3082, distance_sum(res, self.dm20))

        seedset = set(['G', 'I'])
        res = prototype_selection_constructive_protoclass(
            self.dm20, 5, seedset=seedset)
        self.assertCountEqual(('I', 'G', 'B', 'Q', 'A'), res)
        self.assertAlmostEqual(5.1918, distance_sum(res, self.dm20))

        # test on the n=100 distance matrix
        seedset = ['550.L1S18.s.1.sequence', '550.L1S142.s.1.sequence',
                   '550.L1S176.s.1.sequence']

        res = prototype_selection_constructive_maxdist(self.dm100, 10, seedset)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S15.s.1.sequence',
             '550.L1S18.s.1.sequence', '550.L1S129.s.1.sequence',
             '550.L1S115.s.1.sequence', '550.L1S136.s.1.sequence',
             '550.L1S142.s.1.sequence', '550.L1S176.s.1.sequence',
             '550.L1S178.s.1.sequence', '550.L1S189.s.1.sequence'),
            res)
        self.assertAlmostEqual(26.7929168423, distance_sum(res, self.dm100))

        res = prototype_selection_constructive_pMedian(self.dm100, 10, seedset)
        self.assertCountEqual(
            ('550.L1S117.s.1.sequence', '550.L1S18.s.1.sequence',
             '550.L1S12.s.1.sequence', '550.L1S163.s.1.sequence',
             '550.L1S149.s.1.sequence', '550.L1S185.s.1.sequence',
             '550.L1S133.s.1.sequence', '550.L1S126.s.1.sequence',
             '550.L1S176.s.1.sequence', '550.L1S142.s.1.sequence'),
            res)
        self.assertAlmostEqual(23.9872385276, distance_sum(res, self.dm100))

        res = prototype_selection_destructive_maxdist(self.dm100, 10, seedset)
        self.assertCountEqual(
            ('550.L1S1.s.1.sequence', '550.L1S15.s.1.sequence',
             '550.L1S18.s.1.sequence', '550.L1S129.s.1.sequence',
             '550.L1S132.s.1.sequence', '550.L1S136.s.1.sequence',
             '550.L1S142.s.1.sequence', '550.L1S147.s.1.sequence',
             '550.L1S176.s.1.sequence', '550.L1S189.s.1.sequence'),
            res)
        self.assertAlmostEqual(26.7457727563, distance_sum(res, self.dm100))


if __name__ == '__main__':
    main()
