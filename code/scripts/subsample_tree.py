# Shrink a tree to a given number of taxa (k) which maximize the sum of
# phylogenetic distances.
# Usage: python me.py input.nwk k output.nwk

# Important note: for optimal result, the input tree should be ultrametric.
# Otherwise, the algorithm may favor closely related taxa with a shared long
# branch.

from sys import argv
import numpy as np
from skbio import TreeNode


def main():
    tree = TreeNode.read(argv[1])
    print('Tree has %d taxa.' % tree.count(tips=True))

    print('Calculating tip-to-tip distances...')
    dm = tree.tip_tip_distances()
    print('Sum of distances: %d.' % np.tril(dm.data).sum())

    print('Performing prototype selection...')
    prototypes = prototype_selection_destructive_maxdist(dm, int(argv[2]))
    print('Downsampled to %d taxa.' % len(prototypes))
    print('Sum of distances: %d.' % np.tril(dm.filter(prototypes).data).sum())

    out = tree.shear(prototypes)
    out.write(argv[3])


def prototype_selection_destructive_maxdist(dm, num_prototypes, seedset=None):
    """Prototype selection function (minified)."""
    numRemain = len(dm.ids)
    currDists = dm.data.sum(axis=1)
    maxVal = currDists.max()
    if seedset is not None:
        for e in seedset:
            currDists[dm.index(e)] = maxVal * 2
    minElmIdx = currDists.argmin()
    currDists[minElmIdx], numRemain = np.infty, numRemain - 1
    while (numRemain > num_prototypes):
        currDists -= dm.data[minElmIdx]
        minElmIdx = currDists.argmin()
        currDists[minElmIdx], numRemain = np.infty, numRemain - 1
    return [dm.ids[idx]
            for idx, dist in enumerate(currDists)
            if dist != np.infty]


if __name__ == "__main__":
    main()
