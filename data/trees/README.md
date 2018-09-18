# Trees

Species trees of the 10,575 genomes.

## Tree-building strategies

The species trees were reconstructed using two alternate strategies:

- `astral`: Reconstructed using the gene tree summary method ASTRAL.
- `concat`: Reconstructed using the traditional gene alignment concatenation method.

In addition, there is:

- `genes`: Individual gene trees used for building the ASTRAL species tree.

## General rules

- **Rooting**: Species trees were rooted in between the two clades representing domains Bacteria and Archaea, respectively.
- **Rotating**: Internal nodes were flipped to follow the descending order (child nodes with less descendants are shown in higher position).
- **Node IDs** (`nid`): Internal nodes were assigned incremental numbers in a pre-order traversal: root = `N1`, crown Archaea = `N2`, crown Bacteria = `N3`, so on so forth. These node IDs can be used as unique identifiers in downstream analyses and applications. Each topology (regardless post-manipulations such as collapsing and branch length re-estimation) receives the same set of node IDs. Node IDs of different topologies cannot be cross compared.
- **Branch supports**: Internal nodes were labeled by branch support statistics. Specifically, `lpp` (local posterior probability) for ASTRAL and `bs` (rapid bootstrap) for CONCAT.
- **Branch collapsing**: In the trees under the `collapsed` subdirectory, branches with low supports were collapsed, i.e., they were deleted and their child clades were merged into their parental nodes, making them polytomies.
- **Identical sequences**: In the CONCAT trees and the gene trees, prior to tree-building, duplicate sequences were removed from the alignments. Those taxa were then appended to the corresponding tips of the tree as polytomies.

