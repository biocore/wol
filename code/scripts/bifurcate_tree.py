#!/usr/bin/env python3
"""Bifurcate a tree.

Usage:
    bifurcate_tree.py input.nwk > output.nwk
"""

import sys
import fileinput
from skbio import TreeNode

import unittest
from io import StringIO
from unittest.mock import patch, mock_open


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with fileinput.input() as f:
        tree = TreeNode.read(f)
    tree.bifurcate()
    tree.write(sys.stdout)


class Tests(unittest.TestCase):
    def test_main(self):
        # example from scikit-bio's bifurcate function's doctest
        nwk = '((a,b,g,h)c,(d,e)f)root;'
        exp = '((h,(g,(a,b)))c,(d,e)f)root;\n'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)


if __name__ == "__main__":
    main()
