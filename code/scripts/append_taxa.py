#!/usr/bin/env python3
"""Append extra taxa to a tree based on a tip-to-taxa map.

Useful in adding taxa of identical sequences after building a tree.

Usage:
    append_taxa.py input.nwk taxa.map > output.nwk

Notes:
    Format of taxa.map:
        taxon1 <tab> taxon2,taxon3,taxon4...
    In which taxon1 is present in the tree while taxon2..n are to be
    appended as polytomic tips to taxon1.
"""

import sys
from skbio import TreeNode

import unittest
from os import remove
from io import StringIO
from tempfile import mkstemp
from unittest.mock import patch


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit()
    tree = TreeNode.read(sys.argv[1])
    clusters = {}
    with open(sys.argv[2], 'r') as f:
        for line in f:
            x = line.rstrip('\r\n').split('\t')
            clusters[x[0]] = x[1].split(',')
    res = append_taxa(tree, clusters)
    res.write(sys.stdout)


def append_taxa(tree, clusters, at_tip=True):
    """Add extra taxa to tree tips to form polytomic clades.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to add taxa
    clusters : dict of iterable of str
        map of existing tip name to extra taxon name(s)
    at_tip : bool
        if True, create new node and set existing and extra taxa as
        zero-branch length tips of the new node; if False, append
        extra taxa to parent node with equal branch length as existing tip

    Returns
    -------
    skbio.TreeNode
        resulting tree
    """
    if not set(clusters).issubset([x.name for x in tree.tips()]):
        raise ValueError('Error: Some core taxa are absent from the tree.')

    res = tree.copy()

    for core, extra in clusters.items():
        tip = res.find(core)
        if at_tip:
            tip.append(TreeNode(tip.name))
            tip.extend([TreeNode(x) for x in extra])
            tip.name = None
        else:
            tip.parent.extend([TreeNode(x, tip.length) for x in extra])

    return res


class Tests(unittest.TestCase):
    def setUp(self):
        self.tree = '(((a,b),(c,d),e),((f,g),h));'
        self.tmap = 'a\ta1,a2\nd\tx\n'

    def test_main(self):
        tfd, tpath = mkstemp()
        with open(tfd, 'w') as f:
            f.write(self.tree)
        mfd, mpath = mkstemp()
        with open(mfd, 'w') as f:
            f.write(self.tmap)
        exp = '((((a,a1,a2),b),(c,(d,x)),e),((f,g),h));\n'
        with patch('sys.argv', [None, tpath, mpath]):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)
        remove(tpath)
        remove(mpath)

    def test_append_taxa(self):
        tree = TreeNode.read([self.tree])
        tmap = {'a': ['a1', 'a2'], 'd': ['x']}
        obs = str(append_taxa(tree, tmap))
        exp = '((((a,a1,a2),b),(c,(d,x)),e),((f,g),h));\n'
        self.assertEqual(obs, exp)

        obs = str(append_taxa(tree, tmap, at_tip=False))
        exp = '(((a,b,a1,a2),(c,d,x),e),((f,g),h));\n'
        self.assertEqual(obs, exp)

        tmap = {'x': ['x1', 'x2'], 'a': ['a1']}
        msg = 'Error: Some core taxa are absent from the tree.'
        with self.assertRaisesRegex(ValueError, msg):
            append_taxa(tree, tmap)


if __name__ == "__main__":
    main()
