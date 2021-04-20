# taxdump

The NCBI taxonomy database, updated on March 7, 2017.

Retrieved from the NCBI FTP server, at:
- ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz

Shrinked so that it only contains taxonomy IDs of the 10,575 sampled genomes and their higher-level taxonomic groups.

- [**names.dmp**](names.dmp)
- [**nodes.dmp**](nodes.dmp)

The original version is available from our [Globus](https://www.globus.org/) endpoint: [**WebOfLife**](https://app.globus.org/file-manager/collections/31acbeb8-c62f-11ea-bef9-0e716405a293).

We provide [**shrink_taxdump.py**](../../../../code/scripts/shrink_taxdump.py), the script for shrinking taxdump to contain only given taxa and their higher rank taxa, which may be generally useful.