#!/usr/bin/env python3
"""Re-root a tree with a given set of taxa as the outgroup.

Usage:
    root_by_outgroup.py input.nwk outgroup.list > output.nwk
"""

import sys
from skbio import TreeNode
from utils.tree import assign_supports, root_by_outgroup

import unittest
from os import remove
from io import StringIO
from tempfile import mkstemp
from unittest.mock import patch


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    tree = TreeNode.read(sys.argv[1])
    assign_supports(tree)
    with open(sys.argv[2], 'r') as f:
        outgroup = f.read().splitlines()
    tree = root_by_outgroup(tree, outgroup)
    support_to_label(tree)
    tree.write(sys.stdout)


def support_to_label(tree):
    for node in tree.non_tips():
        if node.support is not None:
            if node.name is not None and node.name != '':
                node.name = '%s:%s' % (node.support, node.name)
            else:
                node.name = '%s' % node.support


class Tests(unittest.TestCase):
    def test_main(self):
        tfd, tpath = mkstemp()
        with open(tfd, 'w') as f:
            f.write('(a,(b,(c,d)),(e,f));')
        ofd, opath = mkstemp()
        with open(ofd, 'w') as f:
            f.write('e\nf\n')
        exp = '((e,f),(a,(b,(c,d))));\n'
        with patch('sys.argv', [None, tpath, opath]):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)
        remove(tpath)
        remove(opath)


if __name__ == "__main__":
    main()
