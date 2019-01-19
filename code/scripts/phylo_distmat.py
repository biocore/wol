# Generate a matrix of pairwise phylogenetic distance (sum of branch lengths)
# from a tree.
# Usage: python me.py input.nwk output.dm

from sys import argv
from skbio import TreeNode

tree = TreeNode.read(argv[1])

mat = tree.tip_tip_distances()

mat.write(argv[2])
