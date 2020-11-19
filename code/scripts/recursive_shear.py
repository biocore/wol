#!/usr/bin/env python3
"""Shear a tree recursively so that eventually all tips match given taxa.

Internal node labels are considered as taxa, too. Optionally, they can be
converted to tips branching from their original positions.

Optionally, the branch connecting a collapsed clade will be extended by the
median depth of all terminal taxa in this clade.

Usage:
    recursive_shear.py input.nwk taxa.list [0/1] [0/1] output.nwk

Flags:
    #1: Convert internal nodes into tips.
    #2: Extend branch length by median depth of taxa in collapsed clade.
"""

from sys import argv
from statistics import median
from skbio import TreeNode


# whether convert internal nodes into tips
int2tip = argv[3] == '1'

# whether extend collapsed branch length
exbrlen = argv[4] == '1'

tree = TreeNode.read(argv[1])
print('Tips in tree: %d.' % tree.count(tips=True))

taxa_in_tree = [x.name for x in tree.traverse() if x.name is not None]
print('Taxa in tree: %d.' % len(taxa_in_tree))

with open(argv[2], 'r') as f:
    taxa_in_list = set(f.read().splitlines())
print('Taxa in list: %d.' % len(taxa_in_list))

taxa_to_keep = taxa_in_list.intersection(taxa_in_tree)
print('Taxa to keep: %d.' % len(taxa_to_keep))

# calculate depths for all nodes
if exbrlen:
    for node in tree.postorder():
        if node.is_tip():
            node.depths = [0.0]
            node.mdepth = 0.0
        else:
            node.depths = [y + (x.length or 0) for x in node.children
                           for y in x.depths]
            node.mdepth = median(node.depths)

# recursively remove tips that are not in the given list
# the reason for not using scikit-bio's `shear` is because it calls `prune`
# when done, which collapses single-child internal nodes.
while True:
    tips_to_remove = []
    for tip in tree.tips():
        if tip.name not in taxa_to_keep:
            tips_to_remove.append(tip)
    if len(tips_to_remove) > 0:
        for tip in tips_to_remove:
            tip.parent.remove(tip)
    else:
        break

# extend branch lengths for collapsed clades
if exbrlen:
    for tip in tree.tips():
        tip.length = (tip.length or 0) + tip.mdepth

print('Remaining tips in tree after shearing: %d.' % tree.count(tips=True))

# converting internal nodes that are in given list into tips
if int2tip is True:
    for node in tree.non_tips():
        taxon = node.name
        if taxon is not None and taxon in taxa_to_keep:
            node.name = None
            node.parent.extend([TreeNode(
                taxon, node.mdepth if exbrlen else None)])
    print('Remaining tips in tree after extension: %d.'
          % tree.count(tips=True))

# write output
tree.write(argv[5])
