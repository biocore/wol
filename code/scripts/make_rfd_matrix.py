#!/usr/bin/env python3
"""Generate a matrix of pairwise Robinson-Foulds distances among all trees.

Usage:
    make_rfd_matrix.py trees_dir output

Output:
    output.o.dm: matrix of number of overlapping taxa
    output.rf.dm: Robinson-Foulds distance matrix
"""

from sys import argv
from os import listdir
from os.path import join
import numpy as np
from skbio import TreeNode, DistanceMatrix

ext = '.nwk'


def main():
    names, trees = [], []
    for fname in sorted(listdir(argv[1])):
        if fname.endswith(ext):
            names.append(fname[:-len(ext)])
            trees.append(TreeNode.read(join(argv[1], fname)))
    print('%d trees read.' % len(names))

    n = len(trees)
    dmo, dmrf = np.zeros(shape=[n, n]), np.zeros(shape=[n, n])
    for i in range(n):
        for j in range(i + 1, n):
            o, rf = compare_rfd_intersect(trees[i], trees[j])
            print('%s - %s: %d, %.3f' % (names[i], names[j], o, rf))
            dmo[i, j], dmrf[i, j] = o, rf
            dmo[j, i], dmrf[j, i] = o, rf

    # number of overlapping taxa matrix
    dmo = DistanceMatrix(dmo, names)
    dmo.write('%s.o.dm' % argv[2])

    # Robinson-Foulds distance matrix
    dmrf = DistanceMatrix(dmrf, names)
    dmrf.write('%s.rf.dm' % argv[2])


def intersect_trees(tree1, tree2):
    """Shrink two trees to contain only overlapping taxa.

    Parameters
    ----------
    tree1 : skbio.TreeNode
        first tree to intersect
    tree2 : skbio.TreeNode
        second tree to intersect

    Returns
    -------
    tuple of two TreeNodes
        resulting trees containing only overlapping taxa
    """
    taxa1 = [tip.name for tip in tree1.tips()]
    taxa2 = [tip.name for tip in tree2.tips()]
    n1, n2 = len(taxa1), len(taxa2)
    taxa1, taxa2 = set(taxa1), set(taxa2)
    if n1 != len(taxa1) or n2 != len(taxa2):
        raise ValueError('Either tree has duplicated taxa.')
    taxa_lap = taxa1.intersection(taxa2)
    if len(taxa_lap) == 0:
        raise KeyError('Trees have no overlapping taxa.')
    tree1_lap = tree1.shear(taxa_lap)
    tree2_lap = tree2.shear(taxa_lap)
    return (tree1_lap, tree2_lap)


def compare_rfd_intersect(tree1, tree2):
    """Calculate the Robinson-Foulds distance of the shared taxa of two trees.

    Parameters
    ----------
    tree1 : skbio.TreeNode
        first tree to compare
    tree2 : skbio.TreeNode
        second tree to compare

    Returns
    -------
    int
        number of shared taxa
    float
        Robinson-Foulds distance in proportion, or 0.0 if there is no shared
        taxon
    """
    try:
        tree1_lap, tree2_lap = intersect_trees(tree1, tree2)
    except KeyError:
        return 0, 0.0
    o = tree1_lap.count(tips=True)
    rfd = tree1_lap.compare_rfd(tree2_lap, proportion=True)
    del tree1_lap
    del tree2_lap
    return o, rfd


if __name__ == "__main__":
    main()
