## Genome database

### Goal

Generate a custom refernce genome database, _with curated taxonomy_, for downstream applications such as metagenome profiling. This protocols involves no new tool, but utilizes existing tools and pipelines of your choice, and plug in the new database.


### Getting genomes

Please refer to this [guide](../data/genomes).

### Getting taxonomy

We provide NCBI or GTDB, original or curated taxonomy in multiple formats. See [taxonomy](../data/taxonomy) for full details.

For programs (e.g., Kraken) that prefer taxonomy in the format of [NCBI taxdump](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/). We provide a mini taxdump which only contains genomes in the phylogeny, and their higher-level ancestors. We also provide the original full taxdump at Globus. See [details](../data/taxonomy/ncbi/taxdump).

- Note: taxdump is only available for NCBI, but not GTDB.

Then one will need a genome ID to TaxID map. This exists in the [genome metadata](../data/genome/metadata.tsv.bz2) under column `taxid` (original NCBI TaxIDs), or in the curated taxonomy file: [rank_tids.tips.tsv](../data/taxonomy/ncbi/curation/rank_tids.tips.tsv.bz2), under the last column `species`.

For programs (e.g., QIIME, SHOGUN) that prefer [Greengenes](http://greengenes.lbl.gov/Download/)-style lineage strings, e.g.,

```
G000006965      k__Bacteria; p__Proteobacteria; c__Alphaproteobacteria; o__Rhizobiales; f__Rhizobiaceae; g__Sinorhizobium; s__Sinorhizobium meliloti
```

We provide lineage string files.

### Example - SHOGUN

Bowtie2

### Example - Kraken