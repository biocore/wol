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

We present a **reference phylogenetic tree** (or more precisely, mutiple trees depending on your choice) for bacterial and archaeal genomes that are publicly available from [NCBI RefSeq](https://www.ncbi.nlm.nih.gov/refseq/) and [GenBank](https://www.ncbi.nlm.nih.gov/genbank/). It means to server as a reference for researchers to explore the evolution and diversity of microbes, and to improve the study of microbial communities.

We do not attempt to create a new taxonomy. However we provide annotations (and curations) for the tree and the genome catalog based on either [NCBI](https://www.ncbi.nlm.nih.gov/taxonomy) or [GTDB](http://gtdb.ecogenomic.org/) taxonomy.


## How it was made

In brief, we used [**ASTRAL**](https://github.com/smirarab/ASTRAL) to generate a consensus tree by summarizing individual trees of **381** single-copy marker genes extracted from **10,575** genomes.

For comparative purpose, we also generated multiple trees using the conventional gene alignment concatenation strategy, and using multiple alternative genome and gene sampling rules. Detailed [protocols](protocols) are provided.


## How to get it

We recommend using this [**tree**](data/trees/astral/branch_length/cons/collapsed/astral.cons.nid.e5p50.nwk) as the reference phylogeny for observations and downstream applications, together with the genome [**metadata**](data/genomes/metadata.tsv.bz2).

Multiple trees, built using different input data and methodology, together with the corresponding metadata, curated taxonomy and other information, are provided in this repository. Please browse the [**data**](data) directory for details.

The genome and protein sequences, multiple sequence alignments and other large data files are available at [Globus](https://www.globus.org/), with endpoint name [**WebOfLife**](https://www.globus.org/app/transfer?origin_id=23fd07dc-b6c8-11e8-8bf8-0a1d4c5c824a&origin_path=%2F) (owner: jdereus@globusid.org). For instruction on how to transfer files via Globus, please read this [guide](https://docs.globus.org/how-to/get-started/).


## How to view it

For readers interested in exploring the evolutionary storying underlying our trees, we provide high-resolution renderings at multiple levels, using NCBI and GTDB taxonomies, as images (PDF format) or compiled packages that can be directly parsed by [FigTree](http://tree.bio.ed.ac.uk/software/figtree/) and [iTOL](https://itol.embl.de/).

We also provide the Newick files, metadata of taxa and nodes, and code for perform rendering

In addition, our group is actively developing [**Empress**](https://github.com/biocore/empress/), a novel interactive visualizer for massive trees (with hundreds of thousands of tips). Please stay tuned!


## How to use it in research

In addition to direct eyeballing, the reference tree can be used to extend the understanding of the composition and diversity of microbial communities. See [protocols](protocols).


## Information for users of

### NCBI

IDs of our genome pool are directly translated from NCBI assembly accessions. Duplicate genomes are merged.

A script is provided to download genomes fresh from the original NCBI server.

we provide mock taxdump files based on curated NCBI and GTDB taxonomy.

### GTDB

Mappings to GTDB genomes IDs are provided in the genome metadata. In the current release, 9,732 (92.03%) of the 10,575 genomes have corresponding GTDB IDs. Annotation (and curation) of our tree using GTDB taxonomy are provided. The relative evolutionary divergence (RED) ([Parks et al., 2018](https://www.nature.com/articles/nbt.4229)) of tree nodes (which are mapped to taxonomic groups) are provided.

### IMG

Mappings to IMG genome/taxon IDs. are provided in the genome metadata. In the current release, 6,758 (63.91%) of the 10,575 genomes have corresponding IMG IDs.

### QIIME

The reference tree can be used for the diversity analysis of shotgun metagenomes, using phylogeny-aware algorithms such as [**UniFrac**](https://en.wikipedia.org/wiki/UniFrac) for beta diversity, and [**Faith's PD**](https://en.wikipedia.org/wiki/Phylogenetic_diversity) for alpha diversity. See [protocols](protocols).

A derivative for 16S rRNA-based analysis is under development. Please stay tuned.

### SHOGUN

The tree can replace the NCBI taxonomy hierarchy used in a Kraken analysis to guide the heuristic search. See here for how-to.

Checkout protocol for taxonomy-free profiles

### Kraken

The tree can replace the NCBI taxonomy hierarchy used in a Kraken analysis to guide the heuristic search. See here for how-to.

### PhyloPhlAn

The 381 marker genes used to build the tree are a curated subsample of the 400 marker genes originally implemented in [PhyloPhlAn](https://bitbucket.org/nsegata/phylophlan/wiki/Home) ([Segata et al., 2013](https://www.nature.com/articles/ncomms3304)). For each marker gene, we provide functional annotation, gene tree and its degree of congruence with the species evolution. Please see [data/markers](data/markers) and [data/trees/genes](data/trees/genes).

Please stay tuned for [PhyloPhlAn2](https://bitbucket.org/nsegata/phylophlan/wiki/phylophlan2).


## How to cite it

If you use the data, code or protocols developed in this work, please directly cite our website: [https://github.com/biocore/wol](https://github.com/biocore/wol). A manuscript detailing this work is current under peer review. Please stay tuned.

Please forward any questions to the project leader: **Dr. Qiyun Zhu** ([qiyunzhu@gmail.com](qiyunzhu@gmail.com)) or the senior PI: **Dr. Rob Knight** ([robknight@ucsd.edu](robknight@ucsd.edu)).
