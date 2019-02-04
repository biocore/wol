#!/usr/bin/env python3
"""Filter out low-abundance OTUs within each sample in a BIOM table.

Usage:
    filter_otus_per_sample.py input.biom threshold output.biom

Notes:
    If >= 1, the threshold is an absolute count; if < 1, it is a fraction of
    the sum of counts.

    This is different from QIIME's filter_otus_from_otu_table.py, which
    filters OTUs by the total count.
"""

from sys import argv
from biom import load_table
from biom.util import biom_open


def main():
    th = float(argv[2])

    def filter_otus(data, id_, md):
        bound = th if th > 1 else data.sum() * th
        data[data < bound] = 0
        return data

    table = load_table(argv[1])

    table.transform(filter_otus, axis='sample')
    table.remove_empty(axis='observation')

    with biom_open(argv[3], 'w') as f:
        table.to_hdf5(f, table.generated_by)


if __name__ == '__main__':
    main()
