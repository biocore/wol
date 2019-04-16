Python scripts
==============

Go to [GitHub directory](https://github.com/biocore/wol/tree/master/code/scripts).

These scripts may be generally or specifically useful in research. All scripts have a simple command-line interface indicating its purpose and usage. All scripts depend on Python 3.5+ with [scikit-bio](http://scikit-bio.org/) 0.5.1+, unless otherwise stated.


Basic tree operations
---------------------

[**count_nodes.py**](count_nodes.py): Count tips and internal nodes in a tree.

[**bifurcate_tree.py**](bifurcate_tree.py): Bifurcate a tree.

[**trifurcate_tree.py**](trifurcate_tree.py): Remove arbitrary rooting from a tree.

[**assign_node_ids.py**](assign_node_ids.py): Assign incremental node IDs to a tree in level order.

[**remove_supports.py**](remove_supports.py): Remove node support values from a tree.

[**decrease_node_order.py**](decrease_node_order.py): Re-order nodes of a tree in decreasing order.

[**export_supports.py**](export_supports.py): Export node labels (e.g., branch support values) to a table.

[**unpack_low_support.py**](unpack_low_support.py): Unpack (collapse) internal nodes with branch support value lower than given cutoff.

[**append_taxa.py**](append_taxa.py): Append extra taxa to a tree as polytomies based on a tip-to-taxa map.

[**match_label_support.py**](match_label_support.py): Generate a nodel label to branch support value table.

[**round_lengths.py**](round_lengths.py): Reduced the number of digits in branch lengths.


Specialized tree operations
---------------------------

[**trianglize_tree.py**](trianglize_tree.py): Re-order nodes of tree in a way such that the two basal clades are in increasing and decreasing order, respectively. If the input tree is already midpoint-rooted, the output tree will shape like a triangle.

[**root_by_outgroup.py**](root_by_outgroup.py): Re-root a tree with a given set of taxa as the outgroup.

[**restore_rooting.py**](restore_rooting.py): Restore rooting scenario of a tree based on another. 

[**subsample_tree.py**](subsample_tree.py): Shrink a tree to a given number of taxa which maximize the sum of phylogenetic distances.

[**make_rfd_matrix.py**](make_rfd_matrix.py): Generate a matrix of Robinson-Foulds distances among all trees.

[**calc_length_metrics.py**](calc_length_metrics.py): Calculate branch length-related metrics, including height, depths and relative evolutionary divergence (RED) for all nodes.

[**calc_split_metrics.py**](calc_split_metrics.py): Calculate split-related metrics, including number of descendants, number of splits from tip or from root.

[**calc_bidi_metrics.py**](calc_bidi_metrics.py): Calculate bidirectional levels and depths for nodes in a tree.


Advanced analyses
-----------------

[**align_distmat.py**](align_distmat.py): Generate a matrix of pairwise Hamming distances among sequences in an alignment, excluding gaps.

[**phylo_distmat.py**](phylo_distmat.py): Generate a matrix of phylogenetic distance (sum of branch lengths) among taxa in a tree.

[**sample_ab_dists.py**](sample_ab_dists.py): Sample pairwise phylogenetic and sequential distances inter- and intra-domains (Archaea and Bacteria).


Tool-specific utilities
-----------------------

[**phylophlan_summarize.py**](phylophlan_summarize.py): Generate marker map and summarize genome to marker matches.

[**phylophlan_extract.py**](phylophlan_extract.py): Extract marker gene sequences based on PhyloPhlAn result.

[**phylosift_summarize.py**](phylosift_summarize.py): Summarize the number of hits per marker per genome.

[**phylosift_extract.py**](phylosift_extract.py): Extract marker gene sequences from search result.

[**dm_to_phylip.py**](dm_to_phylip.py): Convert a distance matrix into the Phylip format (lower triangle) which can then be parsed by ClearCut.

[**r8s_summarize_result.py**](r8s_summarize_result.py): Summarize r8s divergence time estimation results.

[**raxml_duplicate_map.py**](make_duplicate_map.py): Generate a core-to-duplicate map for an MSA filtered by RAxML.


Taxonomy utilities
------------------

[**shrink_taxdump.py**](shrink_taxdump.py): Shrink the standard NCBI taxdump files `nodes.dmp` and `names.dmp` so that they only contain given TaxIDs and their ancestors.

[**recursive_shear.py**](recursive_shear.py): Shear a tree recursively so that eventually all tips match a given taxon set.

[**map_taxa_in_tree.py**](map_taxa_in_tree.py): Convert a taxonomy tree into a genome tree based on a TaxID-to-genome(s) map.

[**taxdump_to_ranks.py**](taxdump_to_ranks.py): Extract parental taxa at given ranks from NCBI taxonomy for genomes.

[**taxdump_to_tree.py**](taxdump_to_tree.py): Build a tree based on NCBI taxdump.

[**tree_to_taxonomy.py**](tree_to_taxonomy.py): Generate pseudo taxonomic hierarchies based on a tree.

[**ranks_to_tree.py**](ranks_to_tree.py): Convert a genome-to-ranks table into a tree.


Community analysis utilities
----------------------------

[**gOTU_from_maps.py**](gOTU_from_maps.py): Generate a "gOTU table" from WGS sequence alignment results.

[**normalize_to_cpm.py**](normalize_to_cpm.py): Normalize a BIOM table to copies per million sequences (cpm).

[**filter_otus_per_sample.py**](filter_otus_per_sample.py): Filter out low-abundance OTUs within each sample in a BIOM table.
