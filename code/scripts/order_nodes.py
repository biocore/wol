# Re-arrange tree in increasing or decreasing node order.
# Usage: python me.py input.nwk 0/1 output.nwk
# 0 - increasing, 1 - decreasing

from sys import argv
from skbio import TreeNode


def main():
    tree = TreeNode.read(argv[1])
    increase = True if argv[2] == '0' else False
    out = order_nodes(tree, increase)
    out.write(argv[3])


def order_nodes(tree, increase=True):
    """Rotate internal nodes of a tree so that child nodes are ordered by the
    number of descendants.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to order
    increase : bool, optional
        order nodes in increasing (True) or decreasing (False) order

    Returns
    -------
    skbio.TreeNode
        resulting ordered tree
    """
    res = tree.copy()
    for node in res.postorder():
        if node.is_tip():
            node.n = 1
        else:
            node.n = sum(x.n for x in node.children)
    for node in res.postorder():
        if not node.is_tip():
            child2n = {x: x.n for x in node.children}
            node.children = []
            for child in sorted(child2n, key=child2n.get, reverse=increase):
                node.append(child)
    for node in res.postorder():
        delattr(node, 'n')
    return res


if __name__ == "__main__":
    main()
