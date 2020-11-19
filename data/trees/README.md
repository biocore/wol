Trees
=====

Phylogenetic trees of the 10,575 genomes.

## Quick start

- [**tree.nwk**](tree.nwk) is the recommended reference phylogeny. It is identical to [astral](astral) - [branch_length](astral/branch_length) - [cons](astral/branch_length/cons) - [collapsed](astral/branch_length/cons/collapsed) - [astral.cons.nid.e5p50.nwk](astral/branch_length/cons/collapsed/astral.cons.nid.e5p50.nwk). See below for details.
- [**tree.qza**](tree.qza) is a pre-compiled [QIIME 2](https://qiime2.org/) reference phylogeny, which can be directly feed into phylogeny-aware analyses such as [UniFrac](https://docs.qiime2.org/2020.2/plugins/available/diversity/beta-phylogenetic/) and [Faith's PD](https://docs.qiime2.org/2020.2/plugins/available/diversity/alpha-phylogenetic/).


## Tree-building strategies

The species trees were reconstructed using two alternate strategies:

- [**astral**](astral): Reconstructed using the gene tree summary method ASTRAL.
- [**concat**](concat): Reconstructed using the traditional gene alignment concatenation method.

In addition, there is:

- [**genes**](genes): Individual gene trees used for building the ASTRAL species tree.
- [**ranks**](ranks): Species trees collapsed to individual taxonomic ranks.


## General rules

- **Rooting**: Species trees were rooted in between the two clades representing domains Bacteria and Archaea, respectively.

- **Rotating**: Internal nodes were flipped to follow the descending order (child nodes with less descendants are shown in higher position).

- **Node IDs** (`nid`): Internal nodes were assigned incremental numbers in a pre-order traversal: root = `N1`, crown Archaea = `N2`, crown Bacteria = `N3`, so on so forth. These node IDs can be used as unique identifiers in downstream analyses and applications. Each topology (regardless post-manipulations such as collapsing and branch length re-estimation) receives the same set of node IDs. Node IDs of different topologies cannot be cross compared.

- **Branch supports**: Internal nodes were labeled by branch support statistics (see below).

- **Branch collapsing**: In the trees under the **collapsed** subdirectories, branches with low supports were collapsed, i.e., they were deleted and their child clades were merged into their parental nodes, making them polytomies.

- **Identical sequences**: In the CONCAT trees and the gene trees, prior to tree-building, duplicate sequences were removed from the alignments. Those taxa were then appended to the corresponding tips of the tree as polytomies.


## Node metrics

Node metrics are provided in separate files, in the format of node ID to metric(s) mappings.

- **supports** ([example](astral/astral.supports.tsv.bz2)): Branch support values. Different types of branch support statistics are used by different methods.

- **splits** ([example](astral/astral.splits.tsv.bz2)): Metrics of branch splits (unrelated to branch lengths), including:
  - `taxa`: Number of descendants (tips) under current node.
  - `prelevels`: Number of splits from root to current node.
  - `lmin`, `lmax`, `lmean`, `lmedian`, and `lstdev`: Statistics of number of splits from all descendants (tips) to current node (i.e., postlevels).
  - `splits`: Total number of splits from all tips to current node.

- **lengths** ([example](astral/branch_length/cons/astral.cons.lengths.tsv.bz2)): Metrics of branch lengths, including:

  - `length`: Length of branch connecting current node and its parent.
  - `height`: Sum of branch lengths from root to current node.
  - `dmin`, `dmax`, `dmean`, `dmedian`, and `dstdev`: Statistics of sums of branch lengths from all descendants (tips) to current node (i.e., depth).
  - `red`: Relative evolutionary divergence (**RED**), introduced by [Parks, et al. (2018)](https://www.nature.com/articles/nbt.4229):

        RED = p + (d / u) * (1 - p)
    
    where _p_ = RED of parent node, _d_ = branch length, _u_ = `dmean` of parent node.

Please also find taxonomic annotation of nodes (internal nodes and tips) under the [taxonomy](../taxonomy) directory.
