## Genome database

### Goal

Generate a custom refernce genome database, with **curated taxonomy**, for downstream applications such as metagenome profiling. This protocols involves no new tool, but utilizes existing tools and pipelines of your choice, and plug in the new database.

Note: This "normal" protocol utilizes the curated taxonomy--a side product from our reference phylogeny--but not the phylogeny itself. For the true powers of phylogeny please refer to other protocols, such as [community ecology](community_ecology) and [tree profiling](tree_profiling).
{: .notice}


### Getting genomes

Several approaches are available for getting the DNA sequences of all or some of the 10,575 genomes. Please see this [guide](../data/genomes).

### Getting taxonomy

We provide NCBI or GTDB, original or curated taxonomy in multiple formats. See [taxonomy](../data/taxonomy) for full details.

#### NCBI taxdump

For programs (e.g., Kraken, Centrifuge) that prefer taxonomy in the format of [NCBI taxdump](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/). We provide a mini taxdump which only contains genomes in the phylogeny, and their higher-level ancestors. We also provide the original full taxdump at Globus. See [details](../data/taxonomy/ncbi/taxdump).

- Note: taxdump is only available for NCBI, but not GTDB.

Then one will need a genome ID to TaxID map (`g2tid.txt`). This exists in the [genome metadata](../data/genome/metadata.tsv.bz2) under column `taxid` (original NCBI TaxIDs), or in the curated taxonomy file: [rank_tids.tips.tsv](../data/taxonomy/ncbi/curation/rank_tids.tips.tsv.bz2). For the latter case, one may extract the lowest classified rank for each genome:

```bash
cat rank_tids.tips.tsv | tail -n+2 | awk -v OFS='\t' '{print $1, $NF}' > g2tid.txt
```

In many cases one will need a nucleotide accession to TaxID map (`nucl2tid.txt`). This file can be generate using `g2tid.txt` generated above, and a nucleotide to genome map ([nucl2g.txt](../data/genomes/nucl2g.txt.bz2)) which we provide: 

```bash
join -12 -21 nucl2g.txt g2tid.txt -o1.1,2.2 -t$'\t' > nucl2tid.txt
```

#### Lineages

For programs (e.g., QIIME, SHOGUN) that prefer [Greengenes](http://greengenes.lbl.gov/Download/)-style lineage strings, e.g.,

```
G000006965      k__Bacteria; p__Proteobacteria; c__Alphaproteobacteria; o__Rhizobiales; f__Rhizobiaceae; g__Sinorhizobium; s__Sinorhizobium meliloti
```

We provide lineage string files:

- [original NCBI](../data/taxonomy/ncbi/lineages.txt.bz2), [curated NCBI](../data/taxonomy/ncbi/curation/lineages.txt.bz2), [original GTDB](../data/taxonomy/gtdb/lineages.txt.bz2), [curated GTDB](../data/taxonomy/gtdb/curation/lineages.txt.bz2).

Similarily, one can generate a nucleotide to lineage map:

```bash
join -12 -21 nucl2g.txt lineages.txt -o1.1,2.2 -t$'\t' > nucl2gg.txt
```

### Building database: genomes only

For programs that are pure sequence aligners, or separate alignment and classification in two phases, one can build a reference database as one would normally do. Here are some examples:

#### Bowtie2

```bash
bowtie2-build --seed 42 --threads 32 genomes.fna WoLr1
```

- Here `genomes.fna` is a multi-FASTA file with all genome sequences concatenated (can be done using the `cat` command); `32` is the number of CPUs; `42` is one's favorite random seed; `WoLr1` is one's favorite database name. Please customize these parameters.

### Building database: genomes + taxonomy

For programs that use a database with both genome sequences and taxonomy integrated, here are examples:

#### BLASTn

```bash
makeblastdb -in genomes.fna -out WoLr1 -dbtype nucl -parse_seqids -taxid_map nucl2tid.txt
```

#### Centrifuge

```bash
centrifuge-build --seed 42 --threads 32 \
  --conversion-table nucl2tid.txt \
  --taxonomy-tree nodes.dmp \
  --name-table names.dmp \
  genomes.fna WoLr1
```

#### Kraken

1. Create `taxonomy/`, then place `names.dmp` and `nodes.dmp` in it.
2. Create `library/added/`, then place all genome sequences (`*.fna`) in it.
3. Execute:

```bash
sed -e 's/^/TAXID\t/' nucl2tid.txt > library/added/prelim_map.txt
kraken-build --build --db . --threads 32
kraken-build --clean
```


### Building database: SHOGUN

[**SHOGUN**](https://github.com/knights-lab/SHOGUN) ([Hillmann et al., 2018](https://msystems.asm.org/content/3/6/e00069-18)) is a novel metagenomics pipeline developed by our team. It features the accurate handling of **shallow** shotgun sequencing data. With as few as 0.5 million sequences per sample (thus cost is very low as comparable to 16S rRNA sequencing), one can obtain decent classification and diversity analysis results that are comparable to the outcome of deep sequencing.

SHOGUN is composed of multiple functional modules for a series of tasks. It has a centralized database system, organized by a `metadata.yaml` that defines the paths to the database files. The content is like:

```
general:
  taxonomy: nucl2gg.txt
  fasta: genomes.fna
bowtie2: bt2/WoLr1
burst: burst/WoLr1
utree: utree/WoLr1
```

SHOGUN supports three aligners: **Bowtie2**, [**BURST**](https://github.com/knights-lab/BURST) and [**UTree**](https://github.com/knights-lab/UTree). Their databases need to be built separately:

- Bowtie2: (see above)

- BUSRT:

```bash
burst -t 32 -r genomes.fna -a WoLr1.acx -o WoLr1.edx -f -d DNA -s
```

- UTree:

```bash
utree-build_gg genomes.fna nucl2gg.txt temp.ubt 0 2
utree-compress temp.ubt WoLr1.ctr
rm temp.ubt temp.ubt.gg.log
```
