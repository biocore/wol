#!/usr/bin/env python3
"""Re-arrange tree so that the two basal clades are in increasing and
decreasing node order, respectively. If the input tree is already midpoint-
rooted, the output tree will shape like a triangle.

Usage:
    trianglize_tree.py input.nwk > output.nwk
"""

import sys
import fileinput
from skbio import TreeNode


def main():
    with fileinput.input() as f:
        tree = TreeNode.read(f)

    for i, clade in enumerate(tree.children):
        for node in clade.postorder():
            if node.is_tip():
                node.n = 1
            else:
                node.n = sum(x.n for x in node.children)
        for node in clade.postorder():
            if not node.is_tip():
                child2n = {x: x.n for x in node.children}
                node.children = []
                for child in sorted(child2n, key=child2n.get,
                                    reverse=bool(1 - i)):
                    node.append(child)
        for node in clade.postorder():
            delattr(node, 'n')

    tree.write(sys.stdout)


if __name__ == '__main__':
    main()
