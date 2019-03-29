#!/usr/bin/env python3
"""Restore rooting scenario of a tree based on another.

Usage:
    restore_rooting.py source.nwk target.nwk > output.nwk

Notes:
    Typical use case: applications like RAxML re-estimates branch lengths or
    branch suppport values based on an exisiting tree topology, but the
    resulting tree has lost the original rooting. This script will generate a
    tree with original rooting scenario and new branch lengths or support
    values.
"""

import sys
from skbio import TreeNode
from utils.tree import assign_supports, support_to_label, restore_rooting

import unittest
from os import remove
from io import StringIO
from tempfile import mkstemp
from unittest.mock import patch


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    source = TreeNode.read(sys.argv[1])
    target = TreeNode.read(sys.argv[2])
    assign_supports(target)
    result = restore_rooting(source, target)
    support_to_label(result)
    result.write(sys.stdout)


class Tests(unittest.TestCase):
    def _test_nwks(self, src, trg, exp):
        fd1, path1 = mkstemp()
        with open(fd1, 'w') as f:
            f.write(src)
        fd2, path2 = mkstemp()
        with open(fd2, 'w') as f:
            f.write(trg)
        args = [None, path1, path2]
        with patch('sys.argv', args):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)
        remove(path1)
        remove(path2)

    def test_main(self):
        src = '(((e,f),g),((c,d),(b,a)));'
        trg = '(((a,b)95,(c,d)90)80,(e,f)100,g);'
        exp = '(((e,f)100,g)80,((c,d)90,(b,a)95)80);\n'
        self._test_nwks(src, trg, exp)


if __name__ == "__main__":
    main()
