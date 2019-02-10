#!/usr/bin/env python3
"""Count tips and internal nodes in a tree.

Usage:
    count_nodes.py tree.nwk
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
    n = tree.count(tips=True)
    m = tree.count() - n
    print('Tree has %s tips and %s internal nodes.' % (n, m))


class Tests(unittest.TestCase):
    def test_main(self):
        nwk = '(((a,b),(c,d),e),((f,g),h));'
        exp = 'Tree has 8 tips and 6 internal nodes.\n'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)


if __name__ == "__main__":
    main()
