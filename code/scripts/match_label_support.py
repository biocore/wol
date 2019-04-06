#!/usr/bin/env python3
"""Generate a nodel label to branch support value table.

Usage:
    match_label_support.py label.nwk support.nwk [default] > output.tsv

"""

import sys
from skbio import TreeNode
from utils.tree import assign_supports, restore_node_labels

import unittest
from os import remove
from io import StringIO
from tempfile import mkstemp
from unittest.mock import patch


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)

    ltree = TreeNode.read(sys.argv[1])
    stree = TreeNode.read(sys.argv[2])
    default_s = sys.argv[3] if len(sys.argv) > 3 else ''

    assign_supports(stree)
    otree = restore_node_labels(ltree, stree)
    for node in otree.levelorder(include_self=False):
        if node.is_tip():
            continue
        print('%s\t%s' % (node.name, (node.support or default_s)))


class Tests(unittest.TestCase):
    def test_main(self):
        fdl, pathl = mkstemp()
        with open(fdl, 'w') as f:
            f.write('((a,b)n2,(c,d)n3)n1;')
        fds, paths = mkstemp()
        with open(fds, 'w') as f:
            f.write('((a,b)100,(c,d)95);')
        args = [None, pathl, paths]
        exp = 'n2\t100\nn3\t95\n'
        with patch('sys.argv', args):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)
        remove(pathl)
        remove(paths)


if __name__ == "__main__":
    main()
