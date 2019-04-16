Quick-Start Guide
=================

- [What it is(n't)](#what-it-is-and-isnt)
- [How it was made](#how-it-was-made)
- [How to get it](#how-to-get-it)
- [How to view it](#how-to-view-it)
- [How to use it in research](#how-to-use-it-in-research)
- [Information for users of...](#information-for-users-of)
- [How to cite it](#how-to-cite-it)

***


## What it is (and isn't)

We present a **reference phylogenetic tree** (or more precisely, mutiple trees depending on your choice) for bacterial and archaeal genomes that are publicly available from [NCBI RefSeq](https://www.ncbi.nlm.nih.gov/refseq/) and [GenBank](https://www.ncbi.nlm.nih.gov/genbank/). It means to serve as a reference for researchers to explore the evolution and diversity of microbes, and to improve the study of microbial communities.

We do not attempt to create a new taxonomy. However we provide annotations (and curations) for the tree and the genome catalog based on either [NCBI](https://www.ncbi.nlm.nih.gov/taxonomy) or [GTDB](http://gtdb.ecogenomic.org/) taxonomy.


## How it was made

In brief, we used [**ASTRAL**](https://github.com/smirarab/ASTRAL) to generate a consensus tree by summarizing individual trees of [**381**](data/markers) single-copy marker genes extracted from [**10,575**](data/genomes) genomes sampled to maximize covered biodiversity.

For comparative purpose, we also generated multiple trees using the conventional gene alignment concatenation strategy, and using multiple alternative genome and gene sampling rules. Detailed [protocols](protocols) are provided.


## How to get it

We recommend using this [**tree**](data/trees/astral/branch_length/cons/collapsed/astral.cons.nid.e5p50.nwk) as the reference phylogeny for observations and downstream applications, together with the genome [**metadata**](data/genomes/metadata.tsv.bz2).

Multiple trees, built using different input data and methodology, together with the corresponding metadata, curated taxonomy and other information, are provided in this repository. Please browse the [**data**](data) directory for details.

The genome and protein sequences, multiple sequence alignments and other large data files are available at [Globus](https://www.globus.org/), with endpoint name [**WebOfLife**](https://www.globus.org/app/transfer?origin_id=23fd07dc-b6c8-11e8-8bf8-0a1d4c5c824a&origin_path=%2F) (owner: jdereus@globusid.org). For instruction on how to transfer files via Globus, please read this [guide](https://docs.globus.org/how-to/get-started/).


## How to view it

We present an [interactive visualization](empress) of the tree. You can zoom, collapse, label, and color the tree. Mouse over individual tips or nodes to view its taxonomy (NCBI or GTDB), to navigate to external databases, or to export download links or subtree.

We also provide high-resolution PDF images in multiple layouts and collapsed at multiple ranks, and their [FigTree](http://tree.bio.ed.ac.uk/software/figtree/) and [iTOL](https://itol.embl.de/)-ready rendering packages, as well as the protocol and source code for rendering, at [**gallery**](gallery).

Alternatively, you can always start with the raw Newick files, and metadata of taxa and nodes provided at [data](data) to build your own view!


## How to use it in research

In addition to direct eyeballing, you can use the reference phylogeny in actual research to extend the understanding of the composition and diversity of microbial communities.

### Genome and taxonomy database

The 10,575-genome catalog, with its _curated_ taxonomy, can be compiled into a reference genome database, and plugged into your existing analysis workflow (e.g., for metagenomic profiling). See this [protocol](protocols/genome_database).

### Microbial community ecology

This reference phylogeny enables classical diversity analyses designed during the 16S rRNA era, such as [**UniFrac**](https://en.wikipedia.org/wiki/UniFrac) for beta diversity, and [**Faith's PD**](https://en.wikipedia.org/wiki/Phylogenetic_diversity) for alpha diversity, on WGS datasets. Finer-grained output is enabled at per-genome level resolution (we call it  "**gOTU**"). See this [protocol](protocols/community_ecology) and corresponding source code.

### Phylogeny-based profiling

We present a novel metagenomic profiling strategy, which _solely relies on phylogeny, and NOT taxonomy_, to enable higher-resolution and more accurate classification, and new insights in light of evolution. WGS data are directly assigned to internal nodes of the tree, and can be visualized in our interface. See this [protocol](protocols/tree_profiling) and corresponding source code.


## Information for users of

### NCBI

IDs of our genome pool are directly translated from NCBI assembly accessions. Duplicate genomes are merged. Copies of genome sequences are hosted at our Globus endpoint. Instructions are provided to download genomes fresh from the original NCBI server. See [details](data/genomes).

### GTDB

Mappings to GTDB genomes IDs are provided in the genome metadata. In the current release, 9,732 (92.03%) of the 10,575 genomes have corresponding GTDB IDs. Annotation (and curation) of our tree using GTDB taxonomy are provided. The relative evolutionary divergence (RED) ([Parks et al., 2018](https://www.nature.com/articles/nbt.4229)) of tree nodes (which are mapped to taxonomic groups) are provided.

### IMG

Mappings to IMG genome/taxon IDs. are provided in the genome metadata. In the current release, 6,758 (63.91%) of the 10,575 genomes have corresponding IMG IDs.

### QIIME

The reference tree can be used for the diversity analysis of shotgun metagenomes, using phylogeny-aware algorithms such as [**UniFrac**](https://en.wikipedia.org/wiki/UniFrac) for beta diversity, and [**Faith's PD**](https://en.wikipedia.org/wiki/Phylogenetic_diversity) for alpha diversity. See this [protocol](protocols/community_ecology).

A derivative for 16S rRNA-based analysis is under development. Please stay tuned.

### PhyloPhlAn

The 381 marker genes used to build the tree are a curated subsample of the 400 marker genes originally implemented in [PhyloPhlAn](https://bitbucket.org/nsegata/phylophlan/wiki/Home). For each marker gene, we provide functional annotation, gene tree and its degree of congruence with the species evolution. Please see [data/markers](data/markers) and [data/trees/genes](data/trees/genes).

Please also check out [PhyloPhlAn2](https://bitbucket.org/nsegata/phylophlan/wiki/phylophlan2).

### Kraken / Centrifuge

Two things can be done for each program: (**basic**) The genome pool and a _curated taxonomy_ can be compiled into an improved reference genome database for metagenomic profiling. See this [protocol](protocols/genome_database) for details.

(**advanced**) The reference phylogeny can replace the NCBI taxonomy hierarchy used in a Kraken / Centrifuge analysis to guide the classification process. Query sequences are directly assigned to nodes instead of taxonomic ranks. See this [protocol](protocols/tree_profiling).

### SHOGUN

The genome pool, the curated taxonomy and the phylogenetic tree itself can be compiled into a reference database to improve metagenomic profiling. The intermediate files can be further used for community ecology analysis. See these protocols: [1](protocols/genome_database), [2](protocols/community_ecology) and [3](protocols/tree_profiling).

### TIPP

We will integrate the reference phylogeney with [TIPP](https://github.com/smirarab/sepp/blob/master/tutorial/tipp-tutorial.md), a phylogenetic placement-based metagenomic sequence classifier. Please stay tuned.


## How to cite it

If you use the data, code or protocols developed in this work, please directly cite our website: [https://biocore.github.io/wol/](https://biocore.github.io/wol/). A manuscript detailing this work is current under peer review. Please stay tuned.

Please forward any questions to the project leader: **Dr. Qiyun Zhu** ([qiz173@ucsd.edu](mailto:qiz173@ucsd.edu)) or the senior PI: **Dr. Rob Knight** ([robknight@ucsd.edu](mailto:robknight@ucsd.edu)).
