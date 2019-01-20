#!/usr/bin/env python3
"""Remove branch support values from a tree.

Usage:
    remove_supports.py input.nwk > output.nwk
"""

import sys
import fileinput
from skbio import TreeNode


def main():
    with fileinput.input() as f:
        tree = TreeNode.read(f)

    for node in tree.non_tips():
        if support(node) is not None:
            if ':' in node.name:
                node.name = ':'.join(node.name.split(':')[1:])
            else:
                node.name = None

    tree.write(sys.stdout)


def support(node):
    try:
        return float(node.name.split(':')[0])
    except (ValueError, AttributeError):
        return None


if __name__ == '__main__':
    main()
