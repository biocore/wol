#!/usr/bin/env python3
"""Calculate branch length-related metrics for nodes in a tree.

Usage:
    calc_length_metrics.py input.nwk > output.tsv

Notes:
    The following metrics will be calculated for each node:
    - length: length of branch connecting current node and its parent.
    - height: sum of branch lengths from the root to the node.
    - depth_mean, depth_median, and depth_stdev: statistics of sums of branch
    lengths from all descendants to current node.
    - red: relative evolutionary divergence (RED) (Parks, et al., 2018)
"""

import sys
import fileinput
import statistics
from skbio import TreeNode
from utils.tree import calc_length_metrics

from io import StringIO
import unittest
from unittest.mock import patch, mock_open


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with fileinput.input() as f:
        tree = TreeNode.read(f)
    calc_length_metrics(tree)

    # print result
    print('name\tlength\theight\tdepth_mean\tdepth_median\tdepth_stdev\tred')
    for node in tree.levelorder(include_self=True):
        if node.is_tip():
            print('%s\t%f\t%f\tna\tna\tna\t1.00000' %
                  (node.name, node.length, node.height))
        else:
            stats = [getattr(statistics, x)(node.depths)
                     for x in ('mean', 'median', 'stdev')]
            print('%s\t%f\t%f\t%f\t%f\t%f\t%.5f' %
                  (node.name, node.length, node.height,
                   stats[0], stats[1], stats[2],
                   node.red))


class Tests(unittest.TestCase):
    def test_main(self):
        """Example from Fig. 1a of Parks et al. (2018)..
                                   /--1--A
                          /n3--1--|
                         |         \--1--B
             /n2----2----|
            |            |             /--1--C
        -n1-|             \n4----2----|
            |                          \----2----D
            |
             \------3------E
        """
        nwk = '(((A:1,B:1)n3:1,(C:1,D:2)n4:2)n2:2,E:3)n1;'
        exp = """name	length	height	depth_mean	depth_median	depth_stdev	red
n1	0.000000	0.000000	4.400000	4.000000	1.140175	0.00000
n2	2.000000	2.000000	2.750000	2.500000	0.957427	0.42105
E	3.000000	3.000000	na	na	na	1.00000
n3	1.000000	3.000000	1.000000	1.000000	0.000000	0.71053
n4	2.000000	4.000000	1.500000	1.500000	0.707107	0.75188
A	1.000000	4.000000	na	na	na	1.00000
B	1.000000	4.000000	na	na	na	1.00000
C	1.000000	5.000000	na	na	na	1.00000
D	2.000000	6.000000	na	na	na	1.00000
"""
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)


if __name__ == '__main__':
    main()
