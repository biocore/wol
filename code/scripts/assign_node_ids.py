#!/usr/bin/env python3
"""Assign incremental IDs to the internal nodes of a tree.

Usage:
    assign_node_ids.py input.nwk > output.nwk

Notes:
    It starts from the root (N1) and walks down the levels (N2, N3,...).
"""

import sys
import fileinput
from skbio import TreeNode


def main():
    with fileinput.input() as f:
        tree = TreeNode.read(f)

    i = 1
    for node in tree.levelorder():
        if not node.is_tip():
            if node.name is not None and node.name != '':
                node.name = '%s:N%d' % (node.name, i)
            else:
                node.name = 'N%d' % i
            i += 1

    tree.write(sys.stdout)


if __name__ == '__main__':
    main()
