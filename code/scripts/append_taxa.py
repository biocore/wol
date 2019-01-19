# Append extra taxa to a tree based on a tip-to-taxa map.
# Useful in adding taxa of identical sequences after building a tree.
# Usage: python me.py input.nwk taxa.txt output.nwk
# Format of taxa.txt:
#   taxon1 <tab> taxon2,taxon3,taxon4...
#   In which taxon1 is present in the tree while taxon 2-n are to be appended
#   as polytomic tips to taxon1.

from sys import argv
from skbio import TreeNode


def main():
    tree = TreeNode.read(argv[1])
    clusters = {}
    with open(argv[2], 'r') as f:
        for line in f:
            x = line.rstrip('\r\n').split('\t')
            clusters[x[0]] = set(x[1].split(','))
    out = append_taxa(tree, clusters)
    out.write(argv[3])


def append_taxa(tree, clusters, at_tip=True):
    """Add extra taxa to tree tips to form polytomic clades.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to add taxa
    clusters : dict of set of str
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
        raise ValueError('Some cores are absent in the tree.')

    res = tree.copy()

    for core, extra in clusters.items():
        tip = res.find(core)
        if not tip.is_tip():
            raise ValueError('Cannot append taxa to an internal node.')
        if at_tip:
            tip.append(TreeNode(tip.name, 0.0))
            tip.extend([TreeNode(x, 0.0) for x in extra])
            tip.name = None
        else:
            tip.parent.extend([TreeNode(x, tip.length) for x in extra])

    return res


if __name__ == "__main__":
    main()
