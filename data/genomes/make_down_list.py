#!/usr/bin/env python3
"""Generate a list of download links to genome sequences.

Usage:
    bzcat metadata.tsv.bz2 | make_down_list.py > downlist.txt
"""

import fileinput


def main():
    c1, c2 = 'assembly_accession', 'asm_name'
    i1, i2 = 0, 0
    header = True
    for line in fileinput.input():
        x = line.rstrip('\r\n').split('\t')
        if header:
            try:
                i1, i2 = x.index(c1), x.index(c2)
            except ValueError:
                raise ValueError(
                    'Column "%s" or "%s" is not found.' % (c1, c2))
            header = False
        else:
            print(get_fna_path(x[i1], x[i2]))


def get_fna_path(asb, asm):
    asm = asm.replace(' ', '_').replace('#', '_')
    srv = 'ftp://ftp.ncbi.nlm.nih.gov/genomes/all'
    ext = 'genomic.fna.gz'
    return ('%s/%s/%s/%s/%s/%s_%s/%s_%s_%s'
            % (srv, asb[:3], asb[4:7], asb[7:10], asb[10:13],
               asb, asm, asb, asm, ext))


if __name__ == '__main__':
    main()
