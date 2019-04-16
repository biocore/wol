## Microbial community ecology

- [Overview](#Overview)
- [Core notion: gOTU](#Core-notion:-gOTU)
- [Sequence mapping](#Sequence-mapping)
- [gOTU table generation](#gOTU-table-generation)
- [gOTU analysis using QIIME2](#gOTU-analysis-using-QIIME2)


### Overview

Here we introduce that, by using the current genome catalog and reference phylogeny, one can analyze whole-genome shotgun (WGS) sequencing data (a.k.a., metagenomic data) using classical bioinformatic methods designed for amplicon (e.g., 16S rRNA) sequencing data, such as [UniFrac](https://en.wikipedia.org/wiki/UniFrac) for beta diversity, and [Faith's PD](https://en.wikipedia.org/wiki/Phylogenetic_diversity) for alpha diversity, and more.

With an existing sequence aligner (e.g., [Bowtie2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml) or [BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi)), and a [**Python script**](../code/scripts/gOTU_from_maps.py) developed by us, one can generate a [BIOM](http://biom-format.org/) table, in which every row is an individual genome (here we refer to it as "**gOTU**"), and every column is a sample (microbiome). This BIOM table can be analyzed using a familiar bioinformatic pipeline (e.g., [QIIME2](https://qiime2.org/)) and familiar functions.

The entire analysis is **taxonomy-free**, although one can always get taxonomic information in parallel (see [genome database](genome_database)).


### Core notion: gOTU

The term **OTU** (operational taxonomic unit) was conventionally used in 16S data analysis. In practice, sequences are clustered at a similarity threshold of 97%, and each cluster is considered a basic unit of the community. Recent years have seen this classical term evolving into **sOTU**, where every exact 16S sequence is treated as the basic unit (i.e., an sOTU), hence improving resolution.

sOTU analysis using [Deblur](https://github.com/biocore/deblur) or [DADA2](https://benjjneb.github.io/dada2/) is well-supported in QIIME2. See [details](https://docs.qiime2.org/2019.1/tutorials/qiime2-for-experienced-microbiome-researchers/#denoising).
{: .notice}

The notion we introduce here, gOTU, means to be an analogue to sOTU, but for WGS data analysis. Previously, diversity analyses on WGS data were typically performed at a particular taxonomic rank, such as genus or species. This limits resolution, and introduces artifacts due to the limitation of taxonomic assignment itself. In this protocol, _we do NOT assign taxonomy_, but directly consider individual sequence-genome association as the basic unit of the microbiome.


### Sequence mapping

Any sequence aligner, such as Bowtie2 or BLAST, or more complicated metagenome classifier, such as [SHOGUN](https://github.com/knights-lab/SHOGUN) or [Centrifuge](https://ccb.jhu.edu/software/centrifuge/), as long as it directly associates query sequences with reference genome sequences, can be used for this analysis. For the later, this process does not block the original analysis (i.e., taxonomic classication). It just makes use of the intermediate files (read maps)

(Evaluation of individual aligners in the context of gOTU analysis is currently ongoing.)

Example 1: Taxonomic profiling using SHOGUN, with Bowtie2 as aligner:

```bash
shogun align -t 32 -d /path/to/db -a bowtie2 -i input.fa -o .
```

Example 2: Taxonomic profiling using Centrifuge:

```bash
centrifuge -p 32 -x /path/to/db -1 input.R1.fq.gz -2 input.R2.fq.gz -S output.map
```


### gOTU table generation

#### gOTU from maps

We provide a Python script [**gOTU_from_maps.py**](../code/scripts/gOTU_from_maps.py) to convert mapping files of multiple samples into a BIOM table (i.e., the gOTU table). This script supports multiple mapping file formats, including:
- [SAM format](https://en.wikipedia.org/wiki/SAM_(file_format)) (used by Bowtie2, BWA, etc.),
- [BLAST tabular output](http://www.metagenomics.wiki/tools/blast/blastn-output-format-6) (a.k.a., `m8`, used by BLAST, USEARCH, BURST, etc.),
- Centrifuge mapping file, and
- Simple "query \<tab\> subject" map.

Place all mapping files in one directory. The stem filenames represent sample IDs. Compressed files (`.gz`, `.bz2`, `.xz` etc.) are acceptable. Then execute the script.

Example 1: SHOGUN by Bowtie2 maps:

```bash
gOTU_from_maps.py bowtie2_result_dir output -m bowtie2 -e .sam.bz2 -t nucl2g.txt
```

- The `nucl2g.txt` is a map of genome sequences (nucleotide) to genome IDs. We provide [**this file**](../data/genomes/nucl2g.txt.bz2) in this repository. One may also customize it.
- `.sam.bz2` is the extension filename of each mapping file (SAM format). We assume that it was already compressed using `bzip2`.

Example 2: Centrifuge maps:

```bash
gOTU_from_maps.py centrifuge_result_dir output -m centrifuge -e .map.xz -t nucl2g.txt
```

The script generates three gOTU tables. They differ by the way _non-unique_ hits are treated:

- `all.tsv`: Includes all hits to each genome, regardless of ambiguity.
- `uniq.tsv`: Only considers unique hits per genome (i.e., query sequences simultaneously mapped to multiple genomes are not considered).
- `norm.tsv`: When one query sequence is mapped to _k_ genomes, each genome receives 1 / _k_ hit.

Either one can be used for the downstream analyses. Choice depends on specific research goal and experimental design. Let's use `uniq.tsv` as an example hereafter.

#### Data formatting

One can further convert the .tsv file into the [BIOM](http://biom-format.org/) format, which is the standard for microbiome studies and broader bioinformatics.

```bash
biom convert -i table.tsv -o table.biom --table-type="OTU table" --to-hdf5
```

To work with BIOM format one needs the Python package [`biom-format`](https://pypi.org/project/biom-format/). Multiple bioinformatics packages such as QIIME2 already include it. 
{: .notice}

#### Data refining

A microbiome dataset usually needs to be refined in order to obtain optimal results. Please refer to QIIME2 tutorials for data [filtering](https://docs.qiime2.org/2019.1/tutorials/filtering/) and [rarefaction](https://docs.qiime2.org/2019.1/plugins/available/feature-table/rarefy/).

In addition, we provide [filter_otus_per_sample.py](../code/scripts/filter_otus_per_sample.py), which allows filtering by threshold at a per-sample base, which is useful in some cases, especially when **false positive** mapping is a concern. For example:

```bash
filter_otus_per_sample.py input.biom 0.0001 output.biom
```

- This command filters out gOTUs with less than 0.01% assignments per sample.


### gOTU analysis using QIIME2

#### Importing data

We recommend using [QIIME2](https://qiime2.org/) to analyze microbiome datasets. To do so, one needs to convert the BIOM table into a QIIME2 [artifact](https://docs.qiime2.org/2019.1/concepts/#data-files-qiime-2-artifacts):

```bash
qiime tools import --type FeatureTable[Frequency] --input-path table.biom --output-path table.qza
```

The reference [**phylogeny**](../data/trees/astral/branch_length/cons/collapsed/astral.cons.nid.e5p50.nwk) provided in the also needs to be imported into QIIME2 as an artifact:

```bash
qiime tools import --type Phylogeny[Rooted] --input-path tree.nwk --output-path tree.qza
```

#### Lazy person's all-in-one solution

Here you go:

```bash
qiime diversity core-metrics-phylogenetic \
  --i-phylogeny tree.qza \
  --i-table table.qza \
  --p-sampling-depth 1000 \
  --m-metadata-file metadata.tsv \
  --output-dir .
```

And enjoy the output!

This might be overly simple (and the sampling depth 1,000 is arbitrary). We would rather you spend bit more time reading and understanding the analyses under the hood. QIIME2's [“Moving Pictures” tutorial](https://docs.qiime2.org/2019.1/tutorials/moving-pictures/) is a good starting point. We also list individual relevant analyses below.

#### Alpha diversity analysis using Faith's PD

[Alpha diversity](https://en.wikipedia.org/wiki/Alpha_diversity) describes the microbial diversity within each community. **Faith's PD** ([Faith, 1992](https://www.sciencedirect.com/science/article/abs/pii/0006320792912013)) is an alpha diversity metric that incorporates phylogenetic distances (i.e., branch lengths) in the equation. It can be calculated using QIIME2' [alpha-phylogenetic](https://docs.qiime2.org/2019.1/plugins/available/diversity/alpha-phylogenetic/) command:

```bash
qiime diversity alpha-phylogenetic \
  --i-phylogeny tree.qza \
  --i-table table.qza \
  --p-metric faith_pd \
  --output-dir .
```

#### Beta diversity analysis using UniFrac

[Beta diversity](https://en.wikipedia.org/wiki/Beta_diversity) describes the microbial diversity across different communities. [**UniFrac**](https://en.wikipedia.org/wiki/UniFrac) ([Lozupone and Knight, 2006](https://aem.asm.org/content/71/12/8228)) is a group of beta diversity metrics that concern the phylogenetic distances among OTUs. Recently, we improved the implementation of UniFrac ([McDonald et al., 2018](https://www.nature.com/articles/s41592-018-0187-8)), allowing efficient analysis of very large datasets (e.g., 100k+ samples). These are provided by QIIME2's [beta-phylogenetic](https://docs.qiime2.org/2019.1/plugins/available/diversity/beta-phylogenetic/) command.

```bash
qiime diversity alpha-phylogenetic \
  --i-phylogeny tree.qza \
  --i-table table.qza \
  --p-metric weighted_unifrac \
  --output-dir .
```

- Here we used the **weighted UniFrac** metric as an example, which considers the relative abundances of gOTUs. It is usually encouranged to test other metrics too and compare the results.

The beta diversity analysis generates a distance matrix among samples, on which multiple downstream analyses can be performed. Examples are [PCoA](https://docs.qiime2.org/2019.1/plugins/available/diversity/pcoa/) and subsequent [visualization](https://docs.qiime2.org/2019.1/plugins/available/emperor/plot/), [PERMANOVA](https://docs.qiime2.org/2019.1/plugins/available/diversity/beta-group-significance/), [Mantel test](https://docs.qiime2.org/2019.1/plugins/available/diversity/mantel/), [kNN classification](https://docs.qiime2.org/2019.1/plugins/available/sample-classifier/classify-samples-from-dist/). We encourage you to explore the QIIME2 documentation and workshops to find out more!
