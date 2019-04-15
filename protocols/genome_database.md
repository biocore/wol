## Genome database

### Goal

Generate a custom refernce genome database, with **curated taxonomy**, for downstream applications such as metagenome profiling. This protocols involves no new tool, but utilizes existing tools and pipelines of your choice, and plug in the new database.

Note: This "normal" protocol utilizes the curated taxonomy--a side product from our reference phylogeny--but not the phylogeny itself. For the true powers of phylogeny please refer to other protocols, such as [community ecology](community_ecology) and [tree profiling](tree_profiling).
{: .notice}


### Getting genomes

Please refer to this [guide](../data/genomes).

### Getting taxonomy

We provide NCBI or GTDB, original or curated taxonomy in multiple formats. See [taxonomy](../data/taxonomy) for full details.

For programs (e.g., Kraken, Centrifuge) that prefer taxonomy in the format of [NCBI taxdump](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/). We provide a mini taxdump which only contains genomes in the phylogeny, and their higher-level ancestors. We also provide the original full taxdump at Globus. See [details](../data/taxonomy/ncbi/taxdump).

- Note: taxdump is only available for NCBI, but not GTDB.

Then one will need a genome ID to TaxID map. This exists in the [genome metadata](../data/genome/metadata.tsv.bz2) under column `taxid` (original NCBI TaxIDs), or in the curated taxonomy file: [rank_tids.tips.tsv](../data/taxonomy/ncbi/curation/rank_tids.tips.tsv.bz2), under the last column `species`.

For programs (e.g., QIIME, SHOGUN) that prefer [Greengenes](http://greengenes.lbl.gov/Download/)-style lineage strings, e.g.,

```
G000006965      k__Bacteria; p__Proteobacteria; c__Alphaproteobacteria; o__Rhizobiales; f__Rhizobiaceae; g__Sinorhizobium; s__Sinorhizobium meliloti
```

We provide lineage string files.

### Example - Kraken


### Example - SHOGUN

[**SHOGUN**](https://github.com/knights-lab/SHOGUN) ([Hillmann et al., 2018](https://msystems.asm.org/content/3/6/e00069-18)) is a novel metagenomics pipeline developed by our team. It features the accurate handling of **shallow** shotgun sequencing data. With as few as 0.5 million sequences per sample (thus cost is very low as comparable to 16S rRNA sequencing), one can obtain decent classification and diversity analysis results that are comparable to the outcome of deep sequencing.

SHOGUN is composed of multiple functional modules for a series of tasks. It has a centralized database system, organized by a `metadata.yaml` that defines the paths to the database files. The content is like (let's use `WoLr1` as the database name):

```
general:
  taxonomy: WoLr1.tax
  fasta: WoLr1.fna
  shear: WoLr1.shear
burst: burst/WoLr1
bowtie2: bt2/WoLr1
utree: utree/WoLr1.gg
```
