#!/usr/bin/env python3
"""Reduced the number of digits in branch lengths.

Usage:
    round_lengths.py input.nwk max_f max_e > output.nwk
"""

import sys
from skbio import TreeNode
from utils.tree import format_newick


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tree = TreeNode.read(sys.argv[1])
    max_f = int(sys.argv[2])
    max_e = int(sys.argv[3]) if len(sys.argv) > 3 else max_f
    print(format_newick(tree, max_f=max_f, max_e=max_e))


if __name__ == "__main__":
    main()
