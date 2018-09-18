# CONCAT species trees

The CONCAT trees were built using maximum likelihood (ML) based on the concatenated alignments of the 381 global marker genes (i.e., a "supermatrix"). The topology was inferred using [RAxML](https://sco.h-its.org/exelixis/web/software/raxml/index.html) under the LG + CAT model. The branch lengths were optimized using [IQ-TREE](http://www.iqtree.org/) under the LG + Gamma model.

- `cons`: Based on up to 100 **most conserved** sites per gene, as selected using the Trident algorithm.
- `rand`: Based on 100 sites **randomly selected** from sites with less than 50% gaps.

In addition, there is:

- `rpls`: Based on 30 **ribosomal proteins** instead of the 381 global markers. Because the total lengths of sequences are short, we used all sites with less than 50% gaps. We do not recommend using this tree as a reference.

In addition to addition, there is:

- `fast`: Based on all sites with less than 50% gaps, using the much faster but less accurate ML implementation [FastTree](http://www.microbesonline.org/fasttree/). The branch support values are SH-like local supports. We do not recommend using this tree or its branch supports as a reference.
