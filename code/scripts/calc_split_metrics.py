#!/usr/bin/env python3
"""Calculate split-related metrics for nodes in a tree.

Usage:
    calc_split_metrics.py input.nwk > output.tsv

Notes:
    The following metrics will be calculated for each node:
    - n: number of descendants (tips)
    - splits: total number of splits from tips
    - prelevel: number of splits from root
    - lmin, lmax, lmean, lmedian, lstdev: statistics of postlevels (number of
    nodes from tips)

    These metrics are related to topology but not branch lengths.
"""

import sys
import fileinput
import statistics
from skbio import TreeNode
from utils.tree import calc_split_metrics

from io import StringIO
import unittest
from unittest.mock import patch, mock_open


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with fileinput.input() as f:
        tree = TreeNode.read(f)
    calc_split_metrics(tree)

    # print result
    columns = ('name', 'n', 'splits', 'prelevel', 'lmin', 'lmax', 'lmean',
               'lmedian', 'lstdev')
    print('\t'.join(columns))
    for node in tree.levelorder(include_self=True):
        out = ('%s\t%d\t%d\t%d'
               % (node.name, node.n, node.splits, node.prelevel))
        if node.is_tip():
            out = '%s\t1\t1\t1\t1\tna' % out
        else:
            lmean, lmedian, lstdev = [
                getattr(statistics, x)(node.postlevels) for x in (
                    'mean', 'median', 'stdev')]
            out = ('%s\t%d\t%d\t%.3g\t%.1g\t%.3g'
                   % (out, min(node.postlevels), max(node.postlevels),
                      lmean, lmedian, lstdev))
        print(out)


class Tests(unittest.TestCase):
    def test_main(self):
        """Example from Fig. 9a of Puigbo, et al., 2009, J Biol.
                                                /-A
                                      /n9------|
                            /n8------|          \\-B
                           |         |
                  /n4------|          \\-C
                 |         |
                 |         |          /-D
                 |          \n7------|
                 |                    \\-E
                 |
                 |                    /-F
        -n1------|          /n6------|
                 |         |          \\-G
                 |-n3------|
                 |         |          /-H
                 |          \n5------|
                 |                    \\-I
                 |
                 |          /-J
                  \n2------|
                            \\-K
        """
        nwk = '((((A,B)n9,C)n8,(D,E)n7)n4,((F,G)n6,(H,I)n5)n3,(J,K)n2)n1;'
        exp = """name	n	splits	prelevel	lmin	lmax	lmean	lmedian	lstdev
n1	11	9	1	3	5	4	4	0.632
n4	5	4	2	3	4	3.4	3	0.548
n3	4	3	2	3	3	3	3	0
n2	2	1	2	2	2	2	2	0
n8	3	2	3	2	3	2.67	3	0.577
n7	2	1	3	2	2	2	2	0
n6	2	1	3	2	2	2	2	0
n5	2	1	3	2	2	2	2	0
J	1	0	3	1	1	1	1	na
K	1	0	3	1	1	1	1	na
n9	2	1	4	2	2	2	2	0
C	1	0	4	1	1	1	1	na
D	1	0	4	1	1	1	1	na
E	1	0	4	1	1	1	1	na
F	1	0	4	1	1	1	1	na
G	1	0	4	1	1	1	1	na
H	1	0	4	1	1	1	1	na
I	1	0	4	1	1	1	1	na
A	1	0	5	1	1	1	1	na
B	1	0	5	1	1	1	1	na
"""
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)


if __name__ == '__main__':
    main()
