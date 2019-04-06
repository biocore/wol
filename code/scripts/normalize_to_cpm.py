#!/usr/bin/env python3
"""Normalize a BIOM table of counts to copies per million sequences (cpm).

Usage:
    normalize_to_cpm.py input.biom output.biom

Notes:
    This is a pure BIOM solution, in contrast to the more complicated and
    slower Pandas solution.
"""

from sys import argv
from biom import load_table
from biom.util import biom_open

n = 1000000

table = load_table(argv[1])
table.transform(
    lambda data, id_, md: (data / data.sum() * n).round(), axis='sample')
with biom_open(argv[2], 'w') as f:
    table.to_hdf5(f, table.generated_by)
