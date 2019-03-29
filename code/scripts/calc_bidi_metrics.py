#!/usr/bin/env python3
"""Calculate bidirectional levels and depths for nodes in a tree.

Usage:
    calc_bidi_metrics.py input.nwk > output.tsv

Notes:
    The following metrics will be calculated for each node:
    - minlevel
    - mindepth
"""

import sys
import fileinput
from skbio import TreeNode
from utils.tree import calc_bidi_minlevels, calc_bidi_mindepths


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with fileinput.input() as f:
        tree = TreeNode.read(f)
    calc_bidi_minlevels(tree)
    calc_bidi_mindepths(tree)

    # print result
    print('\t'.join(('name', 'minlevel', 'mindepth')))
    for node in tree.levelorder(include_self=True):
        print('%s\t%d\t%f' % (node.name, node.minlevel, node.mindepth))


if __name__ == '__main__':
    main()
