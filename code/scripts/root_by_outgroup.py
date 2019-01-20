#!/usr/bin/env python3
"""Re-root a tree with a given set of taxa as the outgroup.

Usage:
    root_by_outgroup.py input.nwk taxa.txt output.nwk
"""

from sys import argv
from skbio import TreeNode


def main():
    tree = TreeNode.read(argv[1])
    with open(argv[2], 'r') as f:
        outgroup = f.read().splitlines()
    out = root_by_outgroup(tree, outgroup)
    out.write(argv[3])


def walk_copy(node, src):
    """Directionally and recursively copy a tree node and its neighbors.

    Parameters
    ----------
    node : skbio.TreeNode
        node and its neighbors to be copied
    src : skbio.TreeNode
        an upstream node determining the direction of walking (src -> node)

    Returns
    -------
    skbio.TreeNode
        copied node and its neighbors

    Notes
    -----
    After manipulation, `src` will become the parent of `node`, and all other
    neighbors of `node` will become children of it.

    Unlike scikit-bio's `unrooted_copy` function, this function has special
    treatment at root: For an unrooted tree, its "root" will be retained as a
    regular node; for a rooted tree, its root will be deleted, and all basal
    nodes will become immediate children of the basal node where the source is
    located.

    The function determines whether a tree is rooted or unrooted in such way:
    rooted: root has two children; unrooted: root has one or more than two
    children.

    Logic (pseudocode):
    if node is root:
        if tree is rooted:
            raise error
        else:
            if src in node.children:
                append node.other_child
            else:
                raise error
    elif node is basal (i.e., child of root):
        if tree is rooted:
            if src in node.siblings:
                append node.children
            elif src in node.children:
                append node.sibling and node.other_children
            else:
                raise error
        else:
            if src is node.parent (i.e., root):
                append node.children
            elif src in node.children:
                append node.parent and node.other_children
            else:
                raise error
    else: (i.e., node is derived)
        if src is node.parent:
            append node.children
        elif src in node.children:
            append node.parent and node.other_children
        else:
            raise error
    """
    parent = node.parent
    children = node.children

    # position of node
    pos = ('root' if node.is_root() else 'basal' if parent.is_root()
           else 'derived')

    # whether tree is rooted
    rooted = ((True if len(children) == 2 else False) if pos == 'root'
              else (True if len(parent.children) == 2 else False)
              if pos == 'basal'
              else None)  # don't determine root status if node is derived
    if rooted:
        if pos == 'root':
            raise ValueError('Cannot walk from root of an rooted tree.')
        elif pos == 'basal':
            sibling = [x for x in node.siblings()][0]

    # direction of walking
    move = (('bottom' if src is sibling else 'top' if src in children
            else 'n/a') if rooted and pos == 'basal'
            else ('down' if src is parent else 'up' if src in children
            else 'n/a'))
    if move == 'n/a':
        raise ValueError('Source and node are not neighbors.')

    # create a new node
    res = TreeNode(node.name)

    # determine length of the new node
    res.length = (node.length if move == 'down'
                  else src.length + node.length if move == 'bottom'
                  else src.length)  # up or top

    # append children except for src (if applies)
    res.extend([walk_copy(c, node) for c in children if c is not src])

    # append parent if walking up (except at root)
    if move == 'up' and pos != 'root':
        res.append(walk_copy(parent, node))

    # append sibling if walking from one basal node to another
    if move == 'top':
        res.append(walk_copy(sibling, node))

    return res


def root_above(node, name=None):
    """Re-root a tree between a give node and its parent.

    Parameters
    ----------
    node : skbio.TreeNode
        node above which the new root will be placed
    name : str, optional
        name of the new root

    Returns
    -------
    skbio.TreeNode
        resulting rooted tree

    Notes
    -----
    Unlike scikit-bio's `root_at` function which actually generates an
    unrooted tree, this function generates a rooted tree (the root of
    which has exactly two children).
    """
    # walk down from self node
    left = walk_copy(node, node.parent)

    # walk up from parent node
    right = walk_copy(node.parent, node)

    # set basal branch lengths to be half of the original, i.e., midpoint
    left.length = right.length = node.length / 2

    # create new root
    return TreeNode(name, children=[left, right])


def root_by_outgroup(tree, outgroup):
    """Root a tree with a given set of taxa as outgroup.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to root
    outgroup : list of str
        list of taxa to be set as outgroup

    Returns
    -------
    skbio.TreeNode
        resulting rooted tree
    """
    outgroup = set(outgroup)
    if not outgroup < set([x.name for x in tree.tips()]):
        raise ValueError('Outgroup is not a subset of tree tips.')

    # create new tree
    res = tree.copy()

    if not check_labels(res):
        print('1st')

    # locate the lowest common ancestor (LCA) of outgroup in the target tree
    lca = res.lca(outgroup)

    # if LCA is root rather than derived (i.e., outgroup is split across basal
    # clades), swap the tree and locate LCA again
    if lca is res:
        for tip in tree.tips():
            if tip.name not in outgroup:
                res = root_above(tip.parent)
                if not check_labels(res):
                    print('2nd')
                break
        lca = res.lca(outgroup)
        if lca is res:
            raise ValueError('Outgroup is not monophyletic in the tree.')

    if not check_labels(root_above(lca)):
        print('3rd')

    # re-root the target tree between LCA of outgroup and LCA of ingroup
    return root_above(lca)


def check_labels(tree):
    for node in tree.non_tips():
        if node.name is None or node.name == '':
            return False
    return True


if __name__ == "__main__":
    main()
