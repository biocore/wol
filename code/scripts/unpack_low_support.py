#!/usr/bin/env python3
"""Collapse nodes with branch support below a given cutoff into polytomies.

Usage:
    unpack_low_support.py input.nwk cutoff > output.nwk
"""

import sys
from skbio import TreeNode
from utils.tree import (branch_length_digits, format_newick, unpack_by_func,
                        get_support, assign_supports)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tree = TreeNode.read(sys.argv[1])
    print('Nodes before unpacking: %d.' % len(list(tree.non_tips())),
          file=sys.stderr)

    max_f, max_e = branch_length_digits(tree)
    assign_supports(tree)

    # minimum support cutoff
    th = float(sys.argv[2])

    # None is considered full support
    def unpack_func(node):
        support = get_support(node)
        return support is not None and support < th

    # unpack nodes with low-support branches
    tree = unpack_by_func(tree, unpack_func)
    print('Nodes after unpacking: %d.' % len(list(tree.non_tips())),
          file=sys.stderr)

    # keep original maximum digits (considering Python' float point error)
    print(format_newick(tree, max_f=max_f, max_e=max_e))


if __name__ == "__main__":
    main()
