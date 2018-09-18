# tax2tree curation

Curation of taxonomy was performed using [tax2tree](https://github.com/biocore/tax2tree), based on the topology of each of the six species trees. We recommend using `astral.e5p50` as the reference phylogeny for your applications.

- `decorated.nwk`: Tree with taxon labels appended to internal nodes.
- `rank_names.nodes.tsv`: Curated taxonomy names of internal nodes at ranks.
- `rank_names.tips.tsv`: Curated taxonomy names of tips (genomes) at ranks.
- `rank_tids.nodes.tsv`: Curated taxonomy IDs of internal nodes at ranks.
- `rank_tids.tips.tsv`: Curated taxonomy IDs of tips (genomes) at ranks.

Note: For para/polyphyletic taxonomic groups, an incremental numeric suffix was appended to the taxonomy name, ordered by the number of descendants. For example, `Firmicutes_1` is the largest clade assigned to the paraphyletic phylum **Firmicutes**, followed by `Firmicutes_2`, `Firmicutes_3`, etc. Their taxonomy IDs remain the same (i.e., the original NCBI taxonomy ID: `1239`).
