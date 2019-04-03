#!/usr/bin/env python3
"""Restore an r8s-ultrametricized tree, which was truncated to remove zero-
length branches, back to the original taxon set.

Usage:
    r8s_restore_tree.py origin.nwk r8s.nwk > output.nwk
"""

import sys
from statistics import mean
from math import isclose
from skbio import TreeNode

# hard-coded r8s branch length precision
digits = 6


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)

    # read original tree
    t0 = TreeNode.read(sys.argv[1])

    # generate node to parent / descendants maps
    nid2pid, nid2desc = {}, {}
    for node in t0.postorder(include_self=False):
        nid = node.name
        nid2pid[nid] = node.parent.name
        if node.is_tip():
            nid2desc[nid] = set([])
        else:
            nid2desc[nid] = set().union(
                *[nid2desc[x.name] for x in node.children])
            nid2desc[nid].update([x.name for x in node.children])

    # read r8s-ultrametricized tree
    t8 = TreeNode.read(sys.argv[2])

    # calculate node depths
    depths = {}
    for node in t8.postorder(include_self=True):
        if node.length is None:
            node.length = 0.0
        depths[node.name] = [0.0] if node.is_tip() else [
            y + x.length for x in node.children for y in depths[x.name]]

    # check total height
    h8 = mean(depths[t8.name])
    abs_tol = 10 ** (1 - digits)
    for d_ in depths[t8.name]:
        if not isclose(d_, h8, abs_tol=abs_tol):
            raise ValueError('Error: The tree is not ultrametric.')

    # identify missing nodes and tips
    toadd = set([x.name for x in t0.traverse()])\
        - set([x.name for x in t8.traverse()])

    # restore missing nodes
    for nid in sorted(toadd, key=lambda x: (len(x), int(x[1:]))):

        # find parent node
        pname = nid2pid[nid]
        pdepth = round(mean(depths[pname]), digits)
        pnode = t8.find(pname)

        # find original children
        # cnodes = [x for x in pnode.children if nid2pid[x.name] == nid]
        cnodes = [x for x in pnode.children if x.name in nid2desc[nid]]

        # if the node to be added
        # ... is an internal node:
        if len(cnodes) > 0:

            # detach children from parent node
            pnode.children = [
                x for x in pnode.children if not any([x is y for y in cnodes])]

            # create a new node with zero length, and attach children
            node = TreeNode(nid, length=0.0, children=cnodes)

            # re-calculate depths
            depths[nid] = [
                y + x.length for x in cnodes for y in depths[x.name]]

        # ... is a leave:
        else:

            # create a new tip which extends to tree surface
            if t0.find(nid).is_tip():
                node = TreeNode(nid, length=pdepth)
                depths[nid] = [0.0]

            # create an empty internal node
            else:
                node = TreeNode(nid, length=0.0)
                depths[nid] = depths[pname]

        # append node to parent
        pnode.append(node)

    t8.write(sys.stdout)


if __name__ == "__main__":
    main()
