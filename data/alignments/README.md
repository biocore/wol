Alignments
==========

The multiple sequence alignments (MSAs) used for building phylogenetic trees.

- [**genes**](genes): Full-length alignments per gene.

Concatenated alignments (and maps of duplicates) (go to [GitHub directory](https://github.com/biocore/wol/tree/master/data/alignments) for download):

- **cons**: 381 marker genes, up to 100 most conserved sites per gene (selected using the "trident" algorithm ([Valdar, 2002](https://onlinelibrary.wiley.com/doi/full/10.1002/prot.10146)) implemented in [PhyloPhlAn](https://bitbucket.org/nsegata/phylophlan/wiki/Home)).
- **rand**: 381 marker genes, 100 sites per gene, randomly selected from sites with less than 50% gaps.
- **rpls**: 30 ribosomal proteins, identified using [PhyloSift](https://phylosift.wordpress.com/) (for comparative purpose only).

Notes:

- MSA files (with extension name `*.xz`) were compressed using [LZMA](https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Markov_chain_algorithm) to minimize disk space consumption. This format is natively supported in most Linux systems. MacOS users may install `xz` using [homebrew](https://brew.sh/) to gain support for it.

- These MSA files are already de-duplicated, i.e., if there are multiple identical sequences in the dataset, only one is retained. In addition, we provide mapping files (`*.map`) from the kept ones to their likes, and a Python script [append_taxa.py](../../code/scripts/append_taxa.py) to append those additional taxa to a phylogenetic tree.

MSAs are also available from our [Globus endpoint](https://www.globus.org/app/transfer?origin_id=23fd07dc-b6c8-11e8-8bf8-0a1d4c5c824a&origin_path=%2F).
