#!/usr/bin/env python3
"""Restore ordering of nodes in one tree based on another.

Usage:
    restore_node_order.py source.nwk target.nwk > output.nwk
"""

import sys
from skbio import TreeNode
from utils.tree import restore_node_order

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
    result = restore_node_order(source, target)
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
        src = '(((a,b),(c,d)),((e,f),g));'
        trg = '((g,(e,f)100),((d,c)80,(a,b)90));'
        exp = '(((a,b)90,(c,d)80),((e,f)100,g));\n'
        self._test_nwks(src, trg, exp)


if __name__ == "__main__":
    main()
