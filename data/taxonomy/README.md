# Taxonomy

The original NCBI taxonomy of the sampled genomes.

- `g2tid.txt`: Genome ID to NCBI taxonomy ID map.
- `rank_names.tsv`: NCBI taxonomy names at ranks.
- `rank_tids.tsv`: NCBI taxonomy IDs at ranks.
- `lineages.txt`: [Greengenes](http://greengenes.lbl.gov/Download/)-style lineage strings.
- `taxdump`: NCBI taxonomy database, shrinked to contain only entries represented by the selected genomes. For the original, complete database, please download from our [Globus endpoint](https://www.globus.org/app/transfer?origin_id=23fd07dc-b6c8-11e8-8bf8-0a1d4c5c824a&origin_path=%2F).

Properties and metrics per taxonomic group.

- `metadata.tsv`: Columns:
  - `rank`, `name`, `id`: NCBI taxonomic rank, name and ID.
  - `count`: Number of genomes assigned to this taxon.
  - `meta_count`: Number of genomes with `scope` as `Environment`, i.e., metagenome-derived.
  - `strict_mono`: Whether this taxon is monophyletic, considering all tips in the tree.
  - `relax_mono`: Whether this taxon is monophyletic, only considering tips classified at this rank.
  - `t2t_count`: Number of genomes assigned to this taxon after [tax2tree](https://github.com/biocore/tax2tree) curation.
  - `t2t_consistency`: tax2tree's consistency score (larger is better, 1.0 is equivalent to strict monophyly).
  - `quartet_score`: Quartet score (larger is better, 1.0 is equivalent to strict monophyly).
  - `mean_marker_count`: Average number of marker genes (out of 400) found in each member genome.

Curated taxonomy.

- `tax2tree`: tax2tree-curated taxonomy.

***

We recommend using `astral.e5p50` as the reference phylogeny. The curation and evaluation of taxnomic groups as recorded in the metadata table are based on this tree.

We considered the seven standard taxonomic ranks:

- kingdom, phylum, class, order, family, genus, species

The use of **kingdom** is to comply with the Greengenes standard. In this work, it may be "Archaea" or "Bacteria". These two taxonomic groups are defined as **superkingdom** in NCBI, or **domain** in most modern literatures.
