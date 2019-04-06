#!/usr/bin/env python3
"""Remove short branches from a tree so that r8s can parse it.

Usage:
    r8s_truncate_tree.py input.nwk nsites > output.nwk

Notes:
    Short tips will be removed, and short internal branches will be collapsed.
"""

from sys import argv
from skbio import TreeNode


def main():
    tree = TreeNode.read(argv[1])
    nsites = int(argv[2])
    nnodes, ntips = tree.count(), tree.count(tips=True)
    print('Tree has %d tips and %d internal nodes.' % (ntips, nnodes - ntips))
    min_length = 0.5 / nsites
    print('Minimum branch length cutoff: %.3g' % min_length)

    print('Removing tips with short branches...')
    tips_to_keep = []
    for tip in tree.tips():
        if tip.length >= min_length:
            tips_to_keep.append(tip.name)
    tree = tree.shear(tips_to_keep)

    nnodes, ntips = tree.count(), tree.count(tips=True)
    print('Tree has %d tips and %d internal nodes.' % (ntips, nnodes - ntips))

    print('Collapsing internal nodes with short branches...')
    tree = unpack_by_func(tree, lambda x: x.length < min_length)

    print('Verifying that the resulting tree has no short branches.')
    for node in tree.traverse(include_self=False):
        if round(node.length * nsites) == 0:
            raise ValueError('Error: Zero-length branch found.')

    tree.write(argv[3])


def unpack(node):
    parent = node.parent
    blen = (node.length or 0.0)
    for child in node.children:
        clen = (child.length or 0.0)
        child.length = (clen + blen or None)
    parent.remove(node)
    parent.extend(node.children)


def unpack_by_func(tree, func):
    tcopy = tree.copy()
    nodes_to_unpack = []
    for node in tcopy.non_tips():
        if func(node):
            nodes_to_unpack.append(node)
    for node in nodes_to_unpack:
        unpack(node)
    return tcopy


if __name__ == "__main__":
    main()
