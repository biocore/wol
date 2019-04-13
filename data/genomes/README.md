Genomes
=======

The bacterial and archaeal genomes analyzed in this project. This GitHub directory hosts the metadata of the **10,575** genomes included in the reference phylogeny ([metadata.tsv](metadata.tsv.bz2)), and that of all **86,200** genomes ([metadata.ext.tsv](metadata.ext.tsv.bz2)) from which the genomes were sampled.

## Download

There are several ways one can obtain the genome sequences (*.fna).

**Recommended**: We host all genome sequences at our [Globus](https://www.globus.org/) endpoint: [**WebOfLife**](https://www.globus.org/app/transfer?origin_id=23fd07dc-b6c8-11e8-8bf8-0a1d4c5c824a&origin_path=%2F) (owner: [jdereus@globusid.org](mailto:jdereus@globusid.org)). Downloading bulk data using Globus is free, fast and secure. To find out how please see this [guide](https://docs.globus.org/how-to/get-started/).

**Alternative**: The genome data were directly pulled from NCBI. Therefore, one may also choose to download the original data from the [NCBI FTP server](ftp://ftp.ncbi.nlm.nih.gov/genomes/all).

We provide a Python script [make_down_list.py](make_down_list.py) to generate a list of download links from the metadata:

```
make_down_list.py metadata.tsv > download.list
```

We also provide a Bash script [batch_down.sh](batch_down.sh) to batch-download all genome sequences in the list:

```
bash batch_down.sh download.list
```

**Moreover**, in the [metadata](../data/genomes/metadata.tsv.bz2), column `ftp_path` indicates the original path of each genome on the NCBI FTP server.


## Lineage-specific download

In the [interactive tree browser](../../empress), one can mouse over a clade of interest to display the taxonomic annotation and an "**Export**" button, which leads to choices of genome IDs, download links and subtree. The interface further allows choice of download data types (e.g., genomes, proteins, RNAs).

Then one can use [batch_down.sh](batch_down.sh) to batch-download them (see above).


## Mapping

[**nucl2g.txt**](nucl2g.txt.bz2) is a nucleotide accession to genome ID mapping file. It is useful in some downstream applications (e.g., check out our [community ecology](../../protocols/community_ecology) protocol). Although it isn't hard to generate one from the genome sequences.


## Metadata

[**metadata.tsv**](metadata.tsv.bz2) contains metadata of the **10,575** genomes selected for phylogenetic reconstruction. Definition of columns:
- **Identifier**
  - `genome`: Genome ID, which is translated from the NCBI assembly accession. For example, `GCF_000123456.1` was translated into `G000123456`.
  - `asm_name`, `assembly_accession`, `bioproject`, `biosample`, `wgs_master`: Corresponding NCBI accessions.
  - `seq_rel_date`, `submitter`: Release data and submitter.
  - `ftp_path`: The original NCBI FTP path where the genome was downloaded.
  - `img_id`: Corresponding [IMG](https://img.jgi.doe.gov/) identifier(s) (as of Dec 2018)
  - `gtdb_id`: Corresponding [GTDB](http://gtdb.ecogenomic.org/) identifier (release 86.1)
- **Category**
  - `scope`: Scope and purity of the biological sample. Retrieved from NCBI. See [here](https://www.ncbi.nlm.nih.gov/bioproject/docs/faq/#what-is-scope) for intepretations.
  - `assembly_level`, `genome_rep`, `refseq_category`, `release_type`: Metadata of the genome assembly defined by NCBI. See [here](ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/README_assembly_summary.txt) for details.
- **Taxonomy**

  Note: The information in this table follows the original NCBI taxonomy. In addition, we provide phylogeny-based taxonomic annotation and curation using two taxonomy systems: **NCBI** and **GTDB**, respectively. Relevant resources are under the [taxonomy](../taxonomy) directory.

  - `taxid`, `species_taxid`: NCBI taxonomy IDs for the organism and the species it belongs to. Note that multiple genomes may share the same `taxid`, as NCBI no longer gives unique taxonomy IDs to strains ([Benson et al., 2015](https://academic.oup.com/nar/article/43/D1/D30/2439451)).
  - `organism_name`, `infraspecific_name`, `isolate`: Taxonomic properties retrieved from NCBI. See [here](ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/README_assembly_summary.txt) for details.
  - `superkingdom`, `kingdom`, `phylum`, `class`, `order`, `family`, `genus`, `species`: NCBI taxonomy names at the eight standard taxonomic ranks. Note that **Bacteria** and **Archaea** are typically referred to as domains, but in NCBI they are superkindoms.
  - `classified`: Whether at least one of the ranks from phylum to genus has a defined taxonomy name.
  - `unique_name`: A unique name for the genome, generated based on the taxonomic properties.
  - `lv1_group`: Top level groups defined in this work. They are referred as "major clades" in the manuscript. Options are `Archaea`, `CPR` and `Eubacteria`.
  - `lv2_group`: Next level groups defined in this work. They are given color codes in the figures.
- **Quality**
  - `score_faa`, `score_fna`, `score_rrna`, `score_trna`: Quality scores for proteins, DNAs, rRNAs and tRNAs. Computed using [RepoPhlAn](https://bitbucket.org/nsegata/repophlan)'s built-in script `screen.py`, following [Land et al. (2014)](https://standardsingenomics.biomedcentral.com/articles/10.1186/1944-3277-9-20).
  - `total_length`: Total length of DNA sequences (bp).
  - `gc`: Proportion of **G** and **C** in the DNA sequences.
  - `non_atcgs`: Total number of non-A, T, C or G characters.
  - `contigs`: Number of DNA sequences.
  - `n50` and `l50`: Assembly quality statistics. See [here](https://en.wikipedia.org/wiki/N50,_L50,_and_related_statistics) for details.
  - `proteins`, `protein_length`: Number and total length (aa) of protein sequences identified by [Prodigal](https://github.com/hyattpd/Prodigal).
  - `coding_density`: Proportion of the genome that are coding sequences.
  - `completeness`, `contamination`, `strain_heterogeneity`: Bin quality statistics calculated by [CheckM](http://ecogenomics.github.io/CheckM/).
  - `markers`: Number of marker genes identified by [PhyloPhlAn](https://bitbucket.org/nsegata/phylophlan/wiki/Home). The total number is 400.
  - `5s_rrna`, `16s_rrna`, `23s_rrna`: presence of the 5S, 16S and 23S rRNA genes, as identified by [RNAmmer](http://www.cbs.dtu.dk/services/RNAmmer/).
  - `trnas`: presence of the 20 standard tRNA genes, as identified by [Aragorn](http://mbio-serv2.mbioekol.lu.se/ARAGORN/).
  - `draft_quality`: A term that describes the quality of a draft genome. Can be "high", "medium", "low" or "unmet". The criteria for assigning these terms follow the **MISAG and MIMAG standard** established in [Bowers et al. (2017)](https://www.nature.com/articles/nbt.3893). Specifically:
    - *high*: completeness > 90%, contamination < 5%, presence of 23S, 16S, 5S rRNAs and >= 18 tRNAs.
    - *medium*: completeness >= 50%, contamination < 10%
    - *low*: completeness < 50%, contamination < 10%
    - *unmet*: contamination >= 10%
  - Note that in addition to these criteria, the original standard requires reference-guided review of metagenome assemblies and bins, which does not apply here. Therefore, please treat this information with caution.
  - Also note that we do not attempt to judge whether a genome is *finished*. Please refer to column `assembly_level` for this information.

[**metadata.ext.tsv**](metadata.ext.tsv.bz2) contains metadata of all **86,200** non-duplicate bacterial and archaeal genomes. The table has two extra columns in the end:
- `selected`: Whether the genome was selected for phylogenetic reconstruction.
- `neighbor`: The closest neighbor among the selected genomes, as defined by the MinHash sketch. This allows the user to map extended genomes to the reference phylogeny. Note that this is not an ideal solution. Please stay tuned for our advanced phylogenomic solution.

[**per_program**](per_program): Metrics generated by individual programs, including:
- Aragorn, CheckM, Prodigal, QUAST, and RNAmmer
