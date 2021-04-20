rRNAs
=====

Sequences and annotations of ribosomal RNA genes identified from the genomes using [RNAmmer 1.2](http://www.cbs.dtu.dk/services/RNAmmer/).

- **5S**: [sequences](5s.fa.xz), [annotations](5s.tsv.xz)
- **16S**: [sequences](16s.fa.xz), [annotations](16s.tsv.xz)
- **23S**: [sequences](23s.fa.xz), [annotations](23s.tsv.xz)

The annotation files have the following columns:

- genome, index, score, nucl, start, end, strand

The rRNA gene IDs are in the format of "genome \<underscore\> index".

- Note that one genome may have zero to multiple copies of the same rRNA gene. The indices of individual rRNA genes do not indicate the indices of the rRNA operons. For example, it is not quaranteed that 16S rRNA gene "G000123456_3" and 23S rRNA gene "G000123456_3" are located in the same operon.
