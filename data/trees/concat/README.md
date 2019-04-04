# CONCAT species trees

The CONCAT trees were built using maximum likelihood (ML) based on the concatenated alignments of the 381 global marker genes (i.e., a "supermatrix"). The topology was inferred using [RAxML](https://sco.h-its.org/exelixis/web/software/raxml/index.html) under the LG + CAT model. The branch lengths were optimized using [IQ-TREE](http://www.iqtree.org/) under the LG + Gamma model. Branch supports are 100 rapid bootstraps (**xboot**).

- [**cons**](cons): Based on up to 100 **most conserved** sites per gene, as selected using the Trident algorithm.
- [**rand**](rand): Based on 100 sites **randomly selected** from sites with less than 50% gaps.
- Tree collapsed by xboot threshold = 50 are provided.

In addition, there is:

- [**fast**](fast): Based on all sites with less than 50% gaps, using the faster but less accurate ML implementation [FastTree](http://www.microbesonline.org/fasttree/). Branch supports are 100 classical bootstraps (**boot**).

Also see:

- [**1k**](1k): Downsampled to **1,000 taxa** to allow using more complex models (PMSF) or more sites.

For comparative purpose, there is:

- [**rpls**](rpls): Based on 30 **ribosomal proteins** instead of the 381 global markers. Because the total lengths of sequences are short, we used all sites with less than 50% gaps.
