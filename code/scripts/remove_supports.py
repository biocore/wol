#!/usr/bin/env python3
"""Remove branch support values from a tree.

Usage:
    remove_supports.py input.nwk > output.nwk
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
    for node in tree.non_tips():
        if node.name is not None and ':' in node.name:
            node.name = node.name.rsplit(':')[1]
    tree.write(sys.stdout)


class Tests(unittest.TestCase):
    def test_main(self):
        nwk = "((a,b)'100:n2',(c,d)'95:n3',(e,f)n4)n1;"
        exp = '((a,b)n2,(c,d)n3,(e,f)n4)n1;\n'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)


if __name__ == '__main__':
    main()
