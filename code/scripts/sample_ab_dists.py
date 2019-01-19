# Sample pairwise phylogenetic and sequential distances inter- and intra-
# domains (Archaea and Bacteria)
# Usage: python me.py k phy.dm seq.dm archaea.txt result.tsv

from sys import argv
from random import seed, sample
import numpy as np
import pandas as pd
from skbio.stats.distance import DistanceMatrix

seed(42)

k = int(argv[1])  # number of taxa to sample from each domain

phydm = DistanceMatrix.read(argv[2])
seqdm = DistanceMatrix.read(argv[3])

ids = sorted(phydm.ids)
if ids != sorted(seqdm.ids):
    raise ValueError('IDs do not match.')

with open(argv[4], 'r') as f:
    archaea = set(f.read().splitlines())

a_sample = sample([x for x in ids if x in archaea], k)
b_sample = sample([x for x in ids if x not in archaea], k)

ids = sorted(a_sample + b_sample)

phydm = phydm.filter(ids)
seqdm = seqdm.filter(ids)

groups = []
for i, x in enumerate(ids):
    for y in ids[i + 1:]:
        if x in archaea:
            groups.append('AA' if y in archaea else 'AB')
        else:
            groups.append('AB' if y in archaea else 'BB')

phyarr = np.around(phydm.condensed_form(), 5)
seqarr = np.around(seqdm.condensed_form(), 5)

df = pd.DataFrame(np.column_stack([phyarr, seqarr]), columns=['phy', 'seq'])
df['group'] = groups

df.to_csv(argv[5], sep='\t')
