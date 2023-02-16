Download
========

Data release of the WoL project is hosted at three locations:

1. This website provides trees, taxonomy, metadata, code, protocols and renderings.
2. Large sequence files and pre-built databases are hosted at our Globus endpoint [**WebOfLife**](https://app.globus.org/file-manager?origin_id=5055eb43-d82b-43f6-8bcb-6be9dfd32748) (see [instruction](#download-via-globus) below).
3. Data files needed for running microbiome data analyses using WoL are hosted at our FTP site: [ftp.microbio.me/pub/wol-20April2021](http://ftp.microbio.me/pub/wol-20April2021/) (total size: 7.8 GB).


## Quickest start

Click to download the [**tree**](data/trees/tree.nwk) and the [**metadata**](data/genomes/metadata.tsv.xz) and it is good to go!

[QIIME 2](https://qiime2.org/) users may download the pre-compiled [**tree.qza**](data/trees/tree.qza) and [**taxonomy.qza**](data/taxonomy/ncbi/taxonomy.qza).

Also check out the [quick-start](start) guide for (bit) more details.


## Pre-built databases

Our Globus endpoint hosts pre-built databases which work out-of-the-box with popular bioinformatics tools:

- QIIME2, BLAST, Bowtie2, SHOGUN, Kraken, Centrifuge, etc.


## Genome sequences

Genome sequences are hosted at our Globus endpoint. We also provide protocols for directly downloading genome data from NCBI. See [instruction](data/genomes).


## Interactive download

Our [interactive tree viewer](empress) allows you to select a node and download data of the corresponding clade, including a **substree**, and a list of links pointing to original NCBI data files (genomes, proteins, RNAs, etc.), which can be batch-downloaded using a [script](data/genomes/batch_down.sh) we provided.


## Download via Globus

We use the [Globus](https://www.globus.org/) service to share very large data files. Please navigate to our Globus endpoint:

 - [**WebOfLife**](https://app.globus.org/file-manager?origin_id=5055eb43-d82b-43f6-8bcb-6be9dfd32748)

If you work with centralized supercomputing facilities, you may consult your IT staff. It is possible that there is an institute account for Globus which allows you to directly transfer the data files to the supercomputer.

If you want to download the data files to your local computer, you may sign up for a [Globus ID](https://www.globusid.org/create) (it's free), download and install [Globus Connect Personal](https://www.globus.org/globus-connect-personal), search for enpoint name "WebOfLife" (or directly click the link above), then start to transfer files.

This [official tutorial](https://docs.globus.org/how-to/get-started/) explains the usage of Globus.
