#!/usr/bin/env python3
"""Calculate branch length-related metrics for nodes in a tree.

Usage:
    calc_length_metrics.py input.nwk > output.tsv

Notes:
    The following metrics will be calculated for each node:
    - length: length of branch connecting current node and its parent
    - height: sum of branch lengths from the root to the node
    - red: relative evolutionary divergence (RED) (Parks, et al., 2018)
    - dmin, dmax, dmean, dmedian, and dstdev: statistics of depths (sums
    of branch lengths from all descendants to current node)
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
    columns = ('name', 'length', 'height', 'red', 'dmin', 'dmax', 'dmean',
               'dmedian', 'dstdev')
    print('\t'.join(columns))
    for node in tree.levelorder(include_self=True):
        if node.is_tip():
            print('%s\t%f\t%f\t1.0\t0.0\t0.0\t0.0\t0.0\tna' %
                  (node.name, node.length, node.height))
        else:
            dmean, dmedian, dstdev = [
                getattr(statistics, x)(node.depths) for x in (
                    'mean', 'median', 'stdev')]
            print('%s\t%f\t%f\t%.5f\t%f\t%f\t%f\t%f\t%f' %
                  (node.name, node.length, node.height, node.red,
                   min(node.depths), max(node.depths), dmean, dmedian, dstdev))


class Tests(unittest.TestCase):
    def test_main(self):
        """Example from Fig. 1a of Parks et al. (2018)..
                                   /--1--A
                          /n3--1--|
                         |         \\--1--B
             /n2----2----|
            |            |             /--1--C
        -n1-|             \n4----2----|
            |                          \\----2----D
            |
             \\------3------E
        """
        nwk = '(((A:1,B:1)n3:1,(C:1,D:2)n4:2)n2:2,E:3)n1;'
        exp = """name	length	height	red	dmin	dmax	dmean	dmedian	dstdev
n1	0.000000	0.000000	0.00000	3.000000	6.000000	4.400000	4.000000	1.140175
n2	2.000000	2.000000	0.42105	2.000000	4.000000	2.750000	2.500000	0.957427
E	3.000000	3.000000	1.0	0.0	0.0	0.0	0.0	na
n3	1.000000	3.000000	0.71053	1.000000	1.000000	1.000000	1.000000	0.000000
n4	2.000000	4.000000	0.75188	1.000000	2.000000	1.500000	1.500000	0.707107
A	1.000000	4.000000	1.0	0.0	0.0	0.0	0.0	na
B	1.000000	4.000000	1.0	0.0	0.0	0.0	0.0	na
C	1.000000	5.000000	1.0	0.0	0.0	0.0	0.0	na
D	2.000000	6.000000	1.0	0.0	0.0	0.0	0.0	na
"""
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)


if __name__ == '__main__':
    main()
