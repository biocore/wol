Taxonomy
========

We provide both [NCBI](https://www.ncbi.nlm.nih.gov/taxonomy) and [GTDB](http://gtdb.ecogenomic.org/) taxonomy, original and curated, for the 10,575 genomes in the phylogenetic trees.

- [**NCBI**](ncbi)
- [**GTDB**](gtdb)


General files
-------------

**ranks**: Name or IDs at the seven standard taxonomic ranks:

- kingdom, phylum, class, order, family, genus, species

The use of **kingdom** is to comply with the Greengenes standard. In this work, it may be "Archaea" or "Bacteria". These two taxonomic groups are defined as **superkingdom** in NCBI, or **domain** in many modern literatures.

**lineages**: [Greengenes](http://greengenes.lbl.gov/Download/)-style lineage strings. They can be used in many applications such as QIIME.


Metadata
--------

Properties and metrics of each taxonomic unit with at least two taxa represented. Columns:

- `rank`, `name`: Taxonomic rank and name
- `taxid`: NCBI taxonomic ID (TaxID).
- `count`: Number of genomes assigned to this taxon.
- `mono_strict`, `mono_relaxed`: Whether this taxonomic unit is monophyletic in the tree, considering all tips, or only tips classified at this rank.
- `consistency`: Consistency score computed using [tax2tree](https://github.com/biocore/tax2tree) (larger is better, 1.0 is equivalent to strict monophyly).
- `quartet`: Quartet score computed using [ASTRAL](https://github.com/smirarab/ASTRAL) (larger is better, 1.0 is equivalent to strict monophyly).
- `markers`: Average number of marker genes (out of 400) found in each member genome.


Curation
--------

Phylogeny-based annotation and curation were performed using [**tax2tree**](https://github.com/biocore/tax2tree) ([McDonald et al., 2012](https://www.nature.com/articles/ismej2011139)). (The same tool was used to curate Greengenes and GTDB.)

The reference phylogeny is [**astral.e5p50**](../trees/astral/collapsed/astral.nid.e5p50.nwk) (built using ASTRAL, with low-support branches collapsed). The curated lineage strings and rank tables cover both **tips** (genomes) and **internal nodes** of the tree.
We also provide curations using alternative trees.

Note that tax2tree does NOT create new taxonomic units. Instead, it modifies the assignments of genomes to existing taxonomic units. If a taxonomic unit is strongly polyphyletic, the program will append a numeric suffix to it for each clade, sorted by size from large to small (e.g., `Firmicutes_1`, `Firmicutes_2`...). We also provide curation results without this suffix (thus taxon names strictly match the original) in the **noidx** directories.
