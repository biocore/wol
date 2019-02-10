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


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with fileinput.input() as f:
        tree = TreeNode.read(f)
    tree = order_nodes(tree, False)
    tree.write(sys.stdout)


if __name__ == "__main__":
    main()
