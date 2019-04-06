## Taxon subsampling

### Goal

Select a subset of taxa from a larger phylogenetic tree such that it maximizes representation of deep-branching, large clades.

### Usage

This protocol was used for selecting 1,000 taxa for testing alternative phylogenetic inference methods, and several other analyses discussed in the article. It may be generally useful for relevant applications.

### Summary

The core of this protocol is using the relative evolutionary divergence (**RED**) metric introduced by [Parks, et al. (2018)](https://www.nature.com/articles/nbt.4229) to order clades. Specifically,

    RED = p + (d / u) * (1 - p)
    
where _p_ = RED of parent node, _d_ = branch length, _u_ = mean distance from parent node to all tips.

Clades (internal nodes and tips) are ordered by RED from low to high, and sequentially added to selection. When a node is selected, its ancestral nodes are dropped from selection (if any). This operation is iterated until given number _n_ clades are selected.

Within each selected clade, the following criteria are sequentially applied to further select one taxon:

1. Number of marker genes is the highest.
2. Contamination level is the lowest.
3. DNA quality score is the highest.

The process terminates whenever there is one candidate left. Finally, one taxon is randomly chosen if there are still multiple candidates.

### Code

The whole pipeline is provided in [taxon_subsampling.ipynb](../code/notebooks/taxon_subsampling.ipynb).


In addition, we provide a function **`calc_length_metrics`** in [tree.py](../code/utils/tree.py) to calculate RED and other metrics, and a script [calc_length_metrics.py](../code/scripts/calc_length_metrics.py) to perform this calculation from command line.

