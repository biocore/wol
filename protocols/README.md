Protocols
=========

Protocols for building, analyzing, and using the trees and other resources in this project.


Building
--------

- [**Genome retrieval**](https://bitbucket.org/nsegata/repophlan): Download all bacterial and archaeal genomes available from NCBI GenBank and RefSeq, using RepoPhlAn.

- [**Genome sampling**](genome_sampling): Select _n_ genomes form a genome pool such that they maximize included biodiversity as measured by the _k_-mer signatures of genomes.

- [**Marker identification**](https://bitbucket.org/nsegata/phylophlan/wiki/Home): Identify and extract amino acid sequences of 400 global marker genes from genomes, using PhyloPhlAn.

- [**Tree building**](tree_building): Build phylogenetic trees of genes and species using various approaches.

- [**Tree manipulation**](tree_manipulation): manipulate phylogenetic trees using the Python scripts developed by our team.

- [**Taxon subsampling**](taxon_subsampling): Select _n_ taxa from a larger phylogenetic tree such that it maximizes representation of deep-branching, large clades.

- [**Taxonomy curation**](taxonomy_curation): Evaluate, modify and extend existing taxonomic assignments based on a phylogenetic tree.


Analysis
--------

- [**Tree comparison**](../code/notebooks/compare_trees.ipynb): Compare the phylogenetic relationships and distances indicated by individual species trees.

- [**Tree comparison by depth**](../code/notebooks/compare_trees_by_depth.ipynb): Compare the topologies of two trees with consideration of phylogenetic depth.

- [**Major clade dimension**](../code/notebooks/major_clade_dimension.ipynb): Calculate and compare the dimensions of major clades (e.g., Archaea vs. Bacteria), including distances between crown groups and distances between leaves.

- [**Shared clades**](../code/notebooks/shared_clades.ipynb): Collapse two very large trees to a shared set of large clades to enable back-to-back comparison via tanglegram.

- [**Gene tree discordance**](gene_tree_discordance): Analyze evolutionary discrepancy reflected by individual gene trees.

- [**Saturation test**](../code/notebooks/saturation.ipynb): Analyze potential amino acid substitution saturation and how it impacts estimated phylogenetic distances.

- [**GTDB translation**](../code/notebooks/gtdb_translation.ipynb): Process GTDB taxonomy and trees to enable cross-translation with our work.


Observation
-----------

- [**Tree rendering**](tree_rendering): Collapse tree at given rank(s) and generate files ready for iTOL and FigTree rendering.


Application
-----------

- [**Genome database**](genome_database): Build a reference genome database with phylogeny-curated taxonomy to improve an existing metagenomic sequence classification workflow.

- [**Community ecology**](community_ecology): Convert WGS sequence alignments into a "gOTU table" and perform microbial community ecology analyses with the reference phylogeny.

- [**Tree profiling**](tree_profiling): Modify an existing metagenomic profiling workflow to allow sequences to be directly assigned to tips and internal nodes of the reference phylogeny.
