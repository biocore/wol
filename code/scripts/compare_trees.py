#!/usr/bin/env python3
"""Compare two trees by taxon set, topology and branch lengths.

Usage:
    compare_trees.py tree1.nwk tree2.nwk [-t]

Notes:
    Add -t to compare tip distances (slow for large trees)
"""

import sys
from skbio import TreeNode
from utils.tree import compare_branch_lengths, compare_topology

import unittest
from os import remove
from io import StringIO
from tempfile import mkstemp
from unittest.mock import patch


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    tree1 = TreeNode.read(sys.argv[1])
    tree2 = TreeNode.read(sys.argv[2])

    # tip counts
    counts = [x.count(tips=True) for x in (tree1, tree2)]
    print('Taxa in tree 1: %d.' % counts[0])
    print('Taxa in tree 2: %d.' % counts[1])

    # shared taxon count
    shared = tree1.subset().intersection(tree2.subset())
    print('Shared taxa: %d.' % len(shared))

    # subsets (sets of tip names under each clade)
    ss = tree1.compare_subsets(tree2, exclude_absent_taxa=True)
    print('Subsets: %f.' % ss)

    # Robinson-Foulds distance
    rfd = tree1.compare_rfd(tree2)
    rfdf = rfd / len(list(tree1.non_tips()) + list(tree2.non_tips()))
    print('RF distance: %d (%f).' % (rfd, rfdf))

    # tip-to-tip distance matrix (slow)
    if len(sys.argv) > 3 and sys.argv[3] == '-t':
        td = tree1.compare_tip_distances(tree2)
        print('Tip distance: %f.' % td)

    if rfd == 0.0:
        # internal node names
        ct = compare_topology(tree1, tree2)
        print('Internal node names are %s.'
              % ('identical' if ct else 'different'))

        # branch lengths
        cbr = compare_branch_lengths(tree1, tree2)
        print('Branch lengths of matching nodes are %s.'
              % ('identical' if cbr else 'different'))


class Tests(unittest.TestCase):
    def _test_nwks(self, nwk1, nwk2, exp, td=False):
        fd1, path1 = mkstemp()
        with open(fd1, 'w') as f:
            f.write(nwk1)
        fd2, path2 = mkstemp()
        with open(fd2, 'w') as f:
            f.write(nwk2)
        args = [None, path1, path2]
        if td:
            args.append('-t')
        with patch('sys.argv', args):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)
        remove(path1)
        remove(path2)

    def test_main(self):
        exp = ('Taxa in tree 1: 4.\n'
               'Taxa in tree 2: 4.\n'
               'Shared taxa: 4.\n'
               'Subsets: 0.500000.\n'
               'RF distance: 2 (0.500000).\n')
        self._test_nwks('((a,b),(c,d));\n',
                        '(((a,b),c),d);\n', exp)

        exp = ('Taxa in tree 1: 4.\n'
               'Taxa in tree 2: 5.\n'
               'Shared taxa: 4.\n'
               'Subsets: 0.000000.\n'
               'RF distance: 0 (0.000000).\n'
               'Tip distance: 0.039384.\n'
               'Internal node names are different.\n'
               'Branch lengths of matching nodes are different.\n')
        self._test_nwks('((a:1.1,b:1.7):2.3,(c:1.5,d:2.4):0.8);\n',
                        '((c:0.8,d:0.1,e:0.0):1.2,(a:0.2,b:0.4):0.9);\n',
                        exp, True)


if __name__ == "__main__":
    main()
