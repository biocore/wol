## Phylogeny-based profiling


### Overview

This protocol introduces how to perform metagenomic profiling using existing tools (e.g., Kraken, Centrifuge, SHOGUN), but instead of classifying sequences by taxonomy, it directly assigns sequences to **tips or internal nodes** of the reference phylogeny. This delivers higher resolution, more accurate assignment, and enables better intepretation of data in light of evolution.


### Generate fake taxonomy from tree

We provide [**tree_to_taxonomy.py**](../code/scripts/tree_to_taxonomy.py), which converts a phylogeney tree into "fake" taxonomy files:

```bash
tree_to_taxonomy.py tree.nwk
```

- Optionally, this script allows the user to specify branch support and branch length cutoffs. Please see its command line inteface.

This script generates fake taxdump files (`names.dmp` and `nodes.dmp`), a genome ID to fake TaxID map (`g2tid.txt`), and a fake lineage map (`g2lineage.txt`).

One may also want to generate a nucleotide accession to fake TaxID map. This can be done using a Bash command:

```bash
join -12 -21 nucl2g.txt g2tid.txt -o1.1,2.2 -t$'\t' > nucl2tid.txt
```

- The file [nucl2g.txt](../data/genomes/nucl2g.txt.bz2) is provided in this repository.


### Kraken

[**Kraken**](https://ccb.jhu.edu/software/kraken/) ([Wood and Salzberg, 2014](https://genomebiology.biomedcentral.com/articles/10.1186/gb-2014-15-3-r46)) is a widely used taxonomic profiler for WGS data. It relies on the taxonomic hierarchy to determine the lowest common ancestor (LCA) of reference genomes where (_k_-mers of) the query sequence is mapped to.

Here we show how to replace the default taxonomic hierarchy (the NCBI taxdump) with our reference phylogeny. We will use Kraken 1.0 for example.

#### Build the database

1. Specify a directory to host the Kraken database, say, `dbdir`.

2. Create subdirectory `taxonomy`. Place the fake taxdump files (`names.dmp` and `nodes.dmp`) we generated above into it.

3. Create subdirectory `library/added/`. Place the uncompressed genome sequences (e.g., `G000123456.fna`) into this directory.

4. In `library/added/`, create a file `prelim_map.txt`. Its content is like:

```
TAXID <tab> NC_000001.1 <tab> 12345
TAXID <tab> NC_000002.1 <tab> 6789
...
```

This can be done using a simple Bash command, from the file `nucl2tid.txt` we already generated above:

```bash
sed -e 's/^/TAXID\t/' nucl2tid.txt > library/added/prelim_map.txt
```

5. Now build the Kraken database:

```bash
kraken-build --build --db dbdir --threads 32
```

- Here `32` is the number of CPUs equipped in your system. Please customize.

6. Finally, clean up the database directory. 

```bash
kraken-build --clean
```

#### Use the database

The commands are exactly the same as one does with a regular (original) Kraken database:

```bash
kraken --db dbdir --threads 32 --paired R1.fq.gz R2.fq.gz --output output.tsv 2> log.txt
kraken-report --db dbdir output.tsv > output.report
```

Now take a look at `output.report`. You will see a list of number of sequences and relative abundances of tip (starting with `G`) and internal nodes (starting with `N`).


### Centrifuge

[**Centrifuge**](https://ccb.jhu.edu/software/centrifuge/) ([Kim et al., 2016](https://genome.cshlp.org/content/26/12/1721.long)) is a metagenomic classifier which features the compression of closely related reference genomes. The classification step is also guided by the taxonomic hierarchy. Similarily, we can replace the taxonomy with phylogeny.

Build database:

```bash
centrifuge_build --seed 42 --threads 32 --conversion-table nucl2tid.txt --taxonomy-tree nodes.dmp --name-table names.dmp nucl.fna dbname
```

Run search:

```bash
centrifuge --seed 42 -p 32 -1 R1.fq.gz -2 R2.fq.gz -x dbname -S output.map --report-file output.report
```

Generate a Kraken-style report we explained above:

```bash
centrifuge-kreport -x dbname output.tsv > output.kreport
```


### SHOGUN - UTree

[**SHOGUN**](https://github.com/knights-lab/SHOGUN) ([Hillmann et al., 2018](https://msystems.asm.org/content/3/6/e00069-18)) is a novel metagenomics pipeline developed by our team. It features the accurate handling of **shallow** shotgun sequencing data. With as few as 0.5 million sequences per sample (thus cost is very low as comparable to 16S rRNA sequencing), one can obtain decent classification and diversity analysis results that are comparable to the outcome of deep sequencing.

SHOGUN provides three classification tools for user choice: Bowtie2, UTree and BURST. Bowtie2 and BURST are pure sequence aligners, and taxonomic classification step is performed after the map is obtained. Therefore they can take advantage of the curated taxonomy (see [genome database](genome_database) for how) but not the phylogenetic tree itself.

[**UTree**](https://github.com/knights-lab/UTree) is a _k_-mer profile & taxonomic hierarechy-guided classifier. In this sense it is similar to Kraken, but it is significantly faster and consumes significantly less computational resource (especially memory).

The support for phylogeny instead of taxonomy is built-in in UTree.

Build database:

```bash
utree-build_gg reference.fna nucl2tid.txt temp.ubt 0 2
utree-compress temp.ubt dbname.ctr
rm temp.ubt temp.ubt.gg.log
```

Run search by directly calling UTree:

```bash
utree-search_gg dbname.ctr input.fa output.txt 32 RC
```

Or via the SHOGUN interface:

```bash
shogun align -t 32 -d dbdir -a utree -i input.fa -o .
```

UTree generates a mapping file, in which each query sequence is directly assigned to a taxonomic lineage (here phylogenetic clade).
