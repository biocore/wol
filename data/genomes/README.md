# Genomes

The metadata of genomes, including properties retrieved from NCBI and statistics calculated in our analyses. You may obtain the original genome sequences from our [Globus endpoint](https://www.globus.org/app/transfer?origin_id=23fd07dc-b6c8-11e8-8bf8-0a1d4c5c824a&origin_path=%2F), or download them from NCBI using the FTP paths provided in the table.

- `metadata.tsv` includes the **10,575** genomes selected for phylogenetic reconstruction. Definition of columns:
  - `genome`: Genome ID, which is translated from the NCBI assembly accession. For example, `GCF_000123456.1` was translated into `G000123456`.
  - `asm_name`, `assembly_accession`, `bioproject`, `biosample`, `wgs_master`: Corresponding NCBI accessions.
  - `seq_rel_date`, `submitter`: Release data and submitter.
  - `ftp_path`: The original NCBI FTP path where the genome was downloaded.
  - `scope`: Scope and purity of the biological sample. Retrieved from NCBI. See [here](https://www.ncbi.nlm.nih.gov/bioproject/docs/faq/#what-is-scope) for intepretations.
  - `assembly_level`, `genome_rep`, `refseq_category`, `release_type`: Metadata of the genome assembly defined by NCBI. See [here](ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/README_assembly_summary.txt) for details.
  - `taxid`, `species_taxid`: NCBI taxonomy IDs for the organism and the species it belongs to. Note that multiple genomes may share the same `taxid`, as NCBI no longer gives unique taxonomy IDs to strains ([Benson et al., 2015](https://academic.oup.com/nar/article/43/D1/D30/2439451)).
  - `organism_name`, `infraspecific_name`, `isolate`: Taxonomic properties retrieved from NCBI. See [here](ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/README_assembly_summary.txt) for details.
  - `superkingdom`, `kingdom`, `phylum`, `class`, `order`, `family`, `genus`, `species`: NCBI taxonomy names at the eight standard taxonomic ranks. Note that **Bacteria** and **Archaea** are typically referred to as domains, but in NCBI they are superkindoms.
  - `classified`: Whether at least one of the ranks from phylum to genus has a defined taxonomy name.
  - `unique_name`: A unique name for the genome, generated based on the taxonomic properties.
  - `lv1_group`: Top level groups defined in this work. They are referred as "major clades" in the manuscript. Options are `Archaea`, `CPR` and `Eubacteria`.
  - `lv2_group`: Next level groups defined in this work. They are given color codes in the figures.
  - `score_faa`, `score_fna`, `score_rrna`, `score_trna`: Quality scores for proteins, DNAs, rRNAs and tRNAs. Computed using [RepoPhlAn](https://bitbucket.org/nsegata/repophlan)'s built-in script `screen.py`, following [Land, et al. (2014)](https://standardsingenomics.biomedcentral.com/articles/10.1186/1944-3277-9-20).
  - `total_length`: Total length of DNA sequences (bp).
  - `contigs`: Number of DNA sequences.
  - `gc`: Proportion of **G** and **C** in the DNA sequences.
  - `n50` and `l50`: Assembly quality statistics. See [here](https://en.wikipedia.org/wiki/N50,_L50,_and_related_statistics) for details.
  - `proteins`, `protein_length`: Number and total length (aa) of protein sequences identified by [Prodigal](https://github.com/hyattpd/Prodigal).
  - `coding_density`: Proportion of the genome that are coding sequences.
  - `completeness`, `contamination`, `strain_heterogeneity`: Bin quality statistics calculated by [CheckM](http://ecogenomics.github.io/CheckM/).
  - `markers`: Number of marker genes identified by [PhyloPhlAn](https://bitbucket.org/nsegata/phylophlan/wiki/Home). The total number is 400.

- `metadata.ext.tsv` includes all **86,200** non-duplicate bacterial and archaeal genomes. The table has two extra columns in the end:
  - `selected`: Whether the genome was selected for phylogenetic reconstruction.
  - `neighbor`: The closest neighbor among the selected genomes, as defined by the MinHash sketch. This allows the user to map extended genomes to the reference phylogeny. Note that this is not an ideal solution. Please stay tuned for our advanced phylogenomic solution.
