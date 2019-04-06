Markers
=======

The 400 global marker genes for inferring phylogenetic relationships of bacterial and archaeal genomes. Originally implemented in [PhyloPhlAn](https://bitbucket.org/nsegata/phylophlan/wiki/Home).

- [**metadata.tsv**](metadata.tsv): Annotations of the markers.
- [**profile.tsv.bz2**](profile.tsv.bz2): Presence (1) and absence (0) of the marker genes in the selected genomes.
- [**nj.nwk**](nj.nwk): Neighbor joining (NJ) tree based on the Jaccard distance matrix inferred from the profile.
- [**pcoa1-10.txt**](pcoa1-10.txt): Principal coordinate analysis (PCoA) of the genomes based on the Jaccard distance matrix. To save disk space, only coordinates of the top 10 axes were included. This file can be directly imported as type `PCoAResult` by [QIIME 2](https://qiime2.org/).
- [**pcoa.qzv**](pcoa.qzv): Interactive visualization of the PCoA result. This file was generated using QIIME 2. To display this file, navigate to [https://view.qiime2.org/](https://view.qiime2.org/), and drag & drop the file as indicated.
