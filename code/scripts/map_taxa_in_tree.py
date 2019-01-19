# Convert a taxonomy tree into a genome tree based on genome-to-TaxID map.
# In the taxonomy tree, internal node labels are also TaxIDs. If a genome
# is mapped to a such TaxID, it will be appended as a tip from this node.
# usage: python: me.py input.nwk g2tid.txt output.nwk

from sys import argv
from skbio import TreeNode

tree = TreeNode.read(argv[1])
print('Reference taxonomy tree has %d nodes, including %d tips.'
      % (tree.count(), tree.count(tips=True)))

gs = set()
tid2gs = {}
with open(argv[2], 'r') as f:
    for line in f:
        g, tid = line.rstrip('\r\n').split('\t')
        tid2gs.setdefault(tid, set()).add(g)
        gs.add(g)
tids = set(tid2gs.keys())
print('List has %d genomes assigned by %d TaxIDs.' % (len(gs), len(tids)))

gs_in_tree = gs
tids_in_tree = set()
for node in tree.traverse():
    if node.name in tids:
        tids_in_tree.add(node.name)
tids_left = tids - tids_in_tree
if tids_left:
    print('Warning: %s TaxIDs are missing from the tree.' % len(tids_left))
    gs_in_tree = set().union(*[tid2gs[x] for x in tids_in_tree])
else:
    print('All TaxIDs are found in the tree.')

# recursively remove tips that are not in the given list
# the reason for not using scikit-bio's `shear` is because it calls `prune`
# when done, which collapses single-child internal nodes.
while True:
    tips_to_remove = []
    for tip in tree.tips():
        if tip.name not in tids_in_tree:
            tips_to_remove.append(tip)
    if len(tips_to_remove) > 0:
        for tip in tips_to_remove:
            tip.parent.remove(tip)
    else:
        break
print('Remaining tips in tree after shearing: %d.' % tree.count(tips=True))

tips, nodes = [], []
for node in tree.traverse():
    if node.is_tip():
        tips.append(node)
    else:
        nodes.append(node)

# convert tips into genome IDs
# if the tip is uniquely assigned to one genome, then it will be renamed as the
# genome; if it is assigned to multiple genomes, then the genomes will be
# appended to it as child tips.
for tip in tips:
    gs = tid2gs[tip.name]
    if len(gs) == 1:
        tip.name = max(gs)
    else:
        tip.extend([TreeNode(x) for x in sorted(gs)])

# append genomes to internal nodes
for node in nodes:
    if node.name in tids_in_tree:
        node.extend([TreeNode(x) for x in sorted(tid2gs[node.name])])

# collapse single-child nodes
tree.prune()

# validate resulting tree
if set(x.name for x in tree.tips()) != gs_in_tree:
    raise ValueError('Resulting tree does not fully cover genomes.')

print('Resulting genome tree has %d nodes, including %d tips.'
      % (tree.count(), tree.count(tips=True)))
tree.write(argv[3])
