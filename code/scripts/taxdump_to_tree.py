# Build tree based on NCBI taxonomy hierarchy
# Usage: python me.py taxdump_dir output.nwk

from sys import argv
from os.path import join
from skbio import TreeNode

# use actual taxon names instead of TaxIDs
write_name = False
# write_name = True

# tips will be at this rank only
tip_rank = None
# tip_rank = 'species'

# only keep taxa under the given TaxID(s)
# for example, "2,2157" will keep bacterial and archaeal taxa only
taxon_range = None
# taxon_range = '2,2157'

# add a uniform branch length to each taxon
branch_length = None
# branch_length = 1.0

# keep space or convert to underscore
# keep_space = True
keep_space = False

taxdump = {}

# read taxon hierarchy (nodes.dmp)
with open(join(argv[1], 'nodes.dmp'), 'r') as f:
    for line in f:
        # format: taxid | parent taxid | rank | more info...
        x = line.rstrip('\r\n').replace('\t|', '').split('\t')
        taxdump[x[0]] = {'parent': x[1], 'rank': x[2], 'name': '',
                         'children': set()}

# read taxon names (names.dmp)
if write_name:
    with open(join(argv[1], 'names.dmp'), 'r') as f:
        for line in f:
            # format: taxid | name | unique name | name class |
            x = line.rstrip('\r\n').replace('\t|', '').split('\t')
            if x[3] == 'scientific name':
                taxdump[x[0]]['name'] = x[1]

# identify child taxids
for tid in taxdump:
    pid = taxdump[tid]['parent']
    # skip root whose taxid equals its parent
    if tid != pid:
        # cut tree at tip rank
        if tip_rank is None or taxdump[pid]['rank'] != tip_rank:
            taxdump[pid]['children'].add(tid)

# record TaxIDs equal or ancestral to the taxon range
if taxon_range is not None:
    tids = set(taxon_range.split(','))
    ancs = set()
    for tid in tids:
        cid = tid
        while True:
            pid = taxdump[cid]['parent']
            ancs.add(pid)
            if cid == pid:
                break
            cid = pid
    # break at TaxIDs that are not equal or ancestral to taxon range
    for anc in ancs:
        cids_to_keep = set()
        for cid in taxdump[anc]['children']:
            if cid in ancs or cid in tids:
                cids_to_keep.add(cid)
        taxdump[anc]['children'] = cids_to_keep

# create the tree from root
tree = TreeNode('1', branch_length)


# iteratively attach child nodes to parent node
def iter_node(node):
    # sort nodes by # children then by taxid, so results are replicable
    for cid in sorted(taxdump[node.name]['children'],
                      key=lambda x: (len(taxdump[x]['children']), int(x))):
        child = TreeNode(cid, branch_length)
        node.extend([child])
        iter_node(child)


iter_node(tree)

# prune tree so that tips are on a given rank
if tip_rank is not None:
    tids = [k for k, v in taxdump.items() if v['rank'] == tip_rank]
    tree = tree.shear(tree.subset().intersection(tids))

# replace TaxIDs with taxon names
if write_name:
    for node in tree.traverse():
        node.name = taxdump[node.name]['name']

# write tree
if not keep_space:
    tree.write(argv[2])
else:
    with open(argv[2], 'w') as f:
        # modified from scikit-bio's _tree_node_to_newick
        operators = set(",:_;()[] ")
        current_depth = 0
        nodes_left = [(tree, 0)]
        while len(nodes_left) > 0:
            entry = nodes_left.pop()
            node, node_depth = entry
            if node.children and node_depth >= current_depth:
                f.write('(')
                nodes_left.append(entry)
                nodes_left += ((child, node_depth + 1) for child in
                               reversed(node.children))
                current_depth = node_depth + 1
            else:
                if node_depth < current_depth:
                    f.write(')')
                    current_depth -= 1
                if node.name:
                    escaped = "%s" % node.name.replace("'", "''")
                    if any(t in operators for t in node.name):
                        f.write("'")
                        f.write(escaped)
                        f.write("'")
                    else:
                        # don't convert spaces to underscores
                        f.write(escaped)
                if node.length is not None:
                    f.write(':')
                    f.write("%s" % node.length)
                if nodes_left and nodes_left[-1][1] == current_depth:
                    f.write(',')
        f.write(';\n')
