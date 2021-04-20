Markers
=======

The 400 global marker genes for inferring phylogenetic relationships of bacterial and archaeal genomes. Originally implemented in [PhyloPhlAn](https://bitbucket.org/nsegata/phylophlan/wiki/Home).

- [**metadata.xlsx**](metadata.xlsx): Metadata of the 400 markers. Same as Data File S4 of the [paper](https://www.nature.com/articles/s41467-019-13443-4). Including functional annotation, taxon and site distribution, alignment statistics, amino acid substitution model, gene tree statistics, phylogenetic distances from species tree, and relative Archaea-Bacteria distance.
- [**annotation.tsv**](annotation.tsv): UniProt and GO annotations of the markers.
- [**profile.tsv**](profile.tsv.xz): Presence (1) and absence (0) of the marker genes in the selected genomes.
- [**nj.nwk**](nj.nwk): Neighbor joining (NJ) tree based on the Jaccard distance matrix inferred from the profile.
- [**pcoa1-10.txt**](pcoa1-10.txt.xz): Principal coordinate analysis (PCoA) of the genomes based on the Jaccard distance matrix. To save disk space, only coordinates of the top 10 axes were included. This file can be directly imported as type `PCoAResult` by [QIIME 2](https://qiime2.org/).
- [**pcoa.qzv**](pcoa.qzv): Interactive visualization of the PCoA result. This file was generated using QIIME 2. To display this file, navigate to [https://view.qiime2.org/](https://view.qiime2.org/), and drag & drop the file as indicated.
