"""Generate a matrix of pairwise phylogenetic distances (sum of branch
lengths) from a tree.

Usage:
    phylo_distmat.py input.nwk > output.dm
"""

import sys
import fileinput
from skbio import TreeNode


def main():
    with fileinput.input() as f:
        tree = TreeNode.read(f)
    mat = tree.tip_tip_distances()
    mat.write(sys.stdout)


if __name__ == '__main__':
    main()
