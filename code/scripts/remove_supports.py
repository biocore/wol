# Remove node support values from a tree.
# Usage: python me.py input.nwk output.nwk

from sys import argv
from skbio import TreeNode

tree = TreeNode.read(argv[1])


def support(node):
    try:
        return float(node.name.split(':')[0])
    except (ValueError, AttributeError):
        return None


for node in tree.non_tips():
    if support(node) is not None:
        if ':' in node.name:
            node.name = ':'.join(node.name.split(':')[1:])
        else:
            node.name = None

tree.write(argv[2])
