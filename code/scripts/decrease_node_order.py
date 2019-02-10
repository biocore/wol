#!/usr/bin/env python3
"""Re-arrange tree nodes in decreasing order.

Usage:
    decrease_node_order.py input.nwk > output.nwk

Notes:
    Clades with less descendants are ranked higher.
"""

import sys
import fileinput
from skbio import TreeNode
from utils.tree import order_nodes

from io import StringIO
import unittest
from unittest.mock import patch, mock_open


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with fileinput.input() as f:
        tree = TreeNode.read(f)
    tree = order_nodes(tree, False)
    tree.write(sys.stdout)


class Tests(unittest.TestCase):
    def test_main(self):
        nwk = '(((a,b),(c,d,e)),((f,g),h));'
        exp = '((h,(f,g)),((a,b),(c,d,e)));\n'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)


if __name__ == "__main__":
    main()
