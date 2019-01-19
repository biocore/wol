# Shear a tree recursively so that eventually all tips match a given taxon set.
# Internal node labels are considered as taxa, too. Optionally, they cat be
# converted to tips branching from their original positions.
# Usage: python me.py input.nwk taxa.list [0/1] output.nwk

from sys import argv
from skbio import TreeNode

# whether to convert internal nodes into tips
int2tip = True if argv[3] == '1' else False

tree = TreeNode.read(argv[1])
print('Tips in tree: %d.' % tree.count(tips=True))

taxa_in_tree = [x.name for x in tree.traverse() if x.name is not None]
print('Taxa in tree: %d.' % len(taxa_in_tree))

with open(argv[2], 'r') as f:
    taxa_in_list = set(f.read().splitlines())
print('Taxa in list: %d.' % len(taxa_in_list))

taxa_to_keep = taxa_in_list.intersection(taxa_in_tree)
print('Taxa to keep: %d.' % len(taxa_to_keep))

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
print('Remaining tips in tree after shearing: %d.' % tree.count(tips=True))

# converting internal nodes that are in the given list into tips
if int2tip is True:
    for node in tree.non_tips():
        taxon = node.name
        if taxon is not None and taxon in taxa_to_keep:
            node.name = None
            node.parent.extend([TreeNode(taxon)])
    print('Remaining tips in tree after extension: %d.'
          % tree.count(tips=True))

tree.write(argv[4])
