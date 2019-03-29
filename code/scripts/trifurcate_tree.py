#!/usr/bin/env python3
"""Remove the arbitrary rooting from a tree.

Usage:
    trifurcate_tree.py input.nwk > output.nwk

Notes:
    Some programs (e.g., ASTRAL) root a tree at an arbitrary taxon. This script
    converts the "root" of the tree to a three-branch polytomic node, i.e., an
    unroot tree.
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
    if len(tree.children) != 2:
        raise ValueError('Error: Not a bifurcating tree.')
    if not tree.children[0].is_tip():
        raise ValueError('Error: Tree is not rooted at a taxon.')
    t = tree.children[1]
    if t.name is not None:
        raise ValueError('Error: Node to be removed has a label.')

    # remove the original node and append its children to the root
    tree.remove(t)
    tree.extend(t.children)

    tree.write(sys.stdout)


class Tests(unittest.TestCase):
    def test_main(self):
        nwk = '(a,((b,c),(d,e)));'
        exp = '(a,(b,c),(d,e));\n'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)

        nwk = '(a,(b,c),(d,e));'
        msg = 'Error: Not a bifurcating tree.'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with self.assertRaisesRegex(ValueError, msg):
                main()

        nwk = '((b,(c,d)),((e,f),(g,h)));'
        msg = 'Error: Tree is not rooted at a taxon.'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with self.assertRaisesRegex(ValueError, msg):
                main()

        nwk = '(a,((b,c),(d,e))x);'
        msg = 'Error: Node to be removed has a label.'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with self.assertRaisesRegex(ValueError, msg):
                main()


if __name__ == "__main__":
    main()
