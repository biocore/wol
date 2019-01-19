# Convert a genome-to-ranks map into a tree
# Usage: python me.py rank_tids.tsv output.nwk
# Output: rank_tree.nwk, genome_tree.nwk

# Note: This script does not use scikit-bio's `from_taxonomy` because it cannot
# handle missing values.

from sys import argv
from skbio import TreeNode

# Specify a name for the root.
# e.g., "1" or "cellular organism" or "root"
root_name = '1'

ranks = []
g2taxon, taxon2parent, taxon2rank = {}, {}, {}
with open(argv[1], 'r') as f:
    for line in f:
        x = line.rstrip('\r\n').split('\t')

        # read ranks from header
        if ranks == []:
            ranks = x[1:]
            continue

        g, lineage = x[0], x[1:]

        # "" and "0" are considered null assignments
        lineage = [None if x == '' or x == '0' else x for x in lineage]

        # map genome to lowest taxon
        try:
            g2taxon[g] = next(x for x in lineage[::-1] if x is not None)
        except StopIteration:
            pass

        # map lower taxon to higher taxon
        for i, taxon in enumerate(lineage):
            if taxon is None or taxon in taxon2parent:
                continue
            taxon2rank[taxon] = ranks[i]
            parent = None
            try:
                parent = next(x for x in lineage[:i][::-1] if x is not None)
            except StopIteration:
                pass
            taxon2parent[taxon] = parent

taxon2gs = {}
for g, taxon in g2taxon.items():
    taxon2gs.setdefault(taxon, []).append(g)

# generate taxon-to-child(ren) map
taxon2children = {root_name: []}
for taxon, parent in taxon2parent.items():
    if parent is None:
        taxon2children[root_name].append(taxon)
    else:
        taxon2children.setdefault(parent, []).append(taxon)

# build the taxonomy tree
tree = TreeNode(root_name)


# iteratively attach child nodes to parent node
def iter_node(node):
    try:
        for x in taxon2children[node.name]:
            child = TreeNode(x)
            node.extend([child])
            iter_node(child)
    except KeyError:
        pass


iter_node(tree)


print('Rank tree has %d nodes, including %d tips.'
      % (tree.count(), tree.count(tips=True)))
tree.write('rank_tree.nwk')

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
    gs = taxon2gs[tip.name]
    if len(gs) == 1:
        tip.name = max(gs)
    else:
        tip.extend([TreeNode(x) for x in sorted(gs)])

# append genomes to internal nodes
for node in nodes:
    if node.name in taxon2gs:
        node.extend([TreeNode(x) for x in sorted(taxon2gs[node.name])])

# collapse single-child nodes
tree.prune()

# validate resulting tree
if set(x.name for x in tree.tips()) != set(g2taxon.keys()):
    raise ValueError('Resulting tree does not fully cover genomes.')

print('Genome tree has %d nodes, including %d tips.'
      % (tree.count(), tree.count(tips=True)))
tree.write('genome_tree.nwk')
