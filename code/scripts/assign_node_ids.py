# Assign incremental IDs to the internal nodes of a tree.
# It starts from the root (N1) and walks down the levels (N2, N3,...).
# Usage: python me.py input.nwk output.nwk

from sys import argv
from skbio import TreeNode

tree = TreeNode.read(argv[1])

i = 1
for node in tree.levelorder():
    if not node.is_tip():
        if node.name is not None and node.name != '':
            node.name = '%s:N%d' % (node.name, i)
        else:
            node.name = 'N%d' % i
        i += 1

tree.write(argv[2])
