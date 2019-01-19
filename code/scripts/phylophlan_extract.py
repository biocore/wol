# Read protein sequences from a master file, match them with marker gene
# families (p0000-p0400), and write to individual faa files.
# Sequence IDs are converted into the genome IDs, assuming that they are all
# single-copy marker genes.
# Usage: python me.py

import bz2
import lzma

# nucleotide accession to genome ID dictionary
with lzma.open('nucl2g.txt.xz', 'rt') as f:
    nucl2g = dict(x.split('\t') for x in f.read().splitlines())

# protein ID to marker gene family ID dictionary
with bz2.open('prot2p.txt.bz2', 'rt') as f:
    prot2p = dict(x.split('\t') for x in f.read().splitlines())

# record used genome-to-marker matches
used = {'p%s' % str(i).zfill(4): set() for i in range(400)}

# read protein sequences and extract those that are marker genes
with bz2.open('prodigal/prots/all.faa.bz2', 'rt') as fi:
    fo = open('seqs/p0000.faa', 'w')
    fo.close()
    for line in fi:
        line = line.rstrip('\r\n')
        if line.startswith('>'):
            if not fo.closed:
                fo.close()
            prot = line[1:].split()[0]
            if prot in prot2p:
                p = prot2p[prot]
                # protein ID = nucleotide accession _underline_ number
                nucl = '_'.join(prot.split('_')[:-1])
                g = nucl2g[nucl]
                if g in used[p]:
                    raise ValueError('%s: %s already exists.' % (p, g))
                used[p].add(g)
                fo = open('seqs/%s.faa' % p, 'a')
                # protein ID is replaced by genome ID
                fo.write('>%s\n' % g)
        elif not fo.closed:
            fo.write('%s\n' % line)
    if not fo.closed:
        fo.close()
