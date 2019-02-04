#!/usr/bin/env python3

from skbio.tree import TreeNode
from utils.tree import support

tree = TreeNode.read(['((a,b)75,(c,d)90);'])
node1, node2 = tree.children
print(str(support(node1)))
