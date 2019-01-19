# Generate pseudo taxonomic hierarchies based on a tree
# Usage: python me.py tree.nwk [node_support_cutoff] [branch_length_cutoff]

from sys import argv
from skbio import TreeNode

tree = TreeNode.read(argv[1])

print('Number of nodes: %d.' % tree.count())
# print(tree.ascii_art())


def collapse(nodes):
    """Collapse internal nodes of a tree."""
    for node in nodes:
        length = node.length
        parent = node.parent
        for child in node.children:
            child.length += length
        parent.remove(node)
        parent.extend(node.children)


# collapse poorly supported nodes
if len(argv) > 2:
    support_cutoff = float(argv[2])
    nodes_to_collapse = []
    for node in tree.non_tips():
        if node.name is not None:
            support = float(node.name)
            if support < support_cutoff:
                nodes_to_collapse.append(node)
    collapse(nodes_to_collapse)
    print('Number of nodes: %d.' % tree.count())
    # print(tree.ascii_art())

# collapse short branches
if len(argv) > 3:
    length_cutoff = float(argv[3])
    while True:
        nodes_to_collapse = []
        for node in tree.non_tips():
            if node.length < length_cutoff:
                nodes_to_collapse.append(node)
        if not nodes_to_collapse:
            break
        collapse(nodes_to_collapse)
    print('Number of nodes: %d.' % tree.count())
    # print(tree.ascii_art())

# assign node IDs if not already done
if tree.name != 'N1':
    idx = 1
    for node in tree.levelorder():
        if not node.is_tip():
            node.name = 'N%d' % idx
            idx += 1
    print('Internal node labels N1..N%d assigned.' % idx)
    # print(tree.ascii_art())

    tree.write('tree.nids.nwk')

# generate Greengenes-style lineage map:
# taxon <tab> N1;N5;N12;N46;N113
lineages = {}
for tip in tree.tips():
    node = tip
    lineage = [tip.name]
    while True:
        if node.parent is not None:
            node = node.parent
            if node.is_root():
                break
            lineage.append(node.name)
    lineages[tip.name] = ';'.join(lineage[::-1])
with open('g2lineage.txt', 'w') as f:
    for taxon, lineage in lineages.items():
        f.write('%s\t%s\n' % (taxon, lineage))

# generate fake TaxID map
tip2idx = {}
idx = 1
for node in tree.non_tips():
    idx = max(idx, int(node.name[1:]) + 1)
for tip in tree.tips():
    tip2idx[tip.name] = str(idx)
    idx += 1
with open('g2tid.txt', 'w') as f:
    for tip in sorted(tip2idx):
        f.write('%s\t%s\n' % (tip, tip2idx[tip]))

# generate NCBI-style taxdump files:
fnodes = open('nodes.dmp', 'w')
fnames = open('names.dmp', 'w')
for node in tree.levelorder():
    taxid = tip2idx[node.name] if node.is_tip() else node.name[1:]
    parent_taxid = node.parent.name[1:] if node.parent is not None else '1'
    fnodes.write('%s\t|\t%s\t|\tno rank\t|\n'
                 % (taxid, parent_taxid))
    fnames.write('%s\t|\t%s\t|\t\t|\tscientific name\t|\n'
                 % (taxid, node.name))
fnodes.close()
fnames.close()
