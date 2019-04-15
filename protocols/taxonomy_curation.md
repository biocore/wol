## Taxonomy curation

### Goals

1. Modify existing taxonomic assignments of genomes based on a phylogenetic tree.
2. Evaluate degree of consistency between existing taxonomic units and the tree.
3. Annotate tips and internal nodes of the tree with taxonomic lineages.

### Summary

We use [**tax2tree**](https://github.com/biocore/tax2tree) ([McDonald et al., 2012](https://www.nature.com/articles/ismej2011139)), which was originally developed by our team, and was used to curate multiple reference databases such as [Greengenes](http://qiime.org/home_static/dataFiles.html) and [GTDB](http://gtdb.ecogenomic.org/).

### Naming rule

This analysis does NOT create new taxonomic units.

If a taxonomic unit is strongly **polyphyletic** (i.e., members of this unit form multiple separate clades in a tree), tax2tree will append a numeric suffix to it for each clade, sorted by taxon number from high to low (e.g., `Firmicutes_1`, `Firmicutes_2`...).


### Code

We provide the whole pipeline in [tax2tree_curation.ipynb](../code/notebooks/tax2tree_curation.ipynb). It explains how to run tax2tree, and performs subsequent manipulations to generate a range of useful files, including per-rank tables and lineage strings at tips and internal nodes.
