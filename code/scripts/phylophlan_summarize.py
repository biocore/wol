# Summarize marker gene to genome matches identified by PhyloPhlAn.
# Usage: python me.py

import lzma

p2prots = {}  # marker gene to protein IDs
prot2p = {}  # protein ID to marker gene

# read and parse marker to proteins maps
# due to computational expense, PhyloPhlAn was run on 20 subsets of genomes
for i in range(20):
    print(str(i))
    with lzma.open('%s/up2prots.txt.xz' % str(i).zfill(2), 'rt') as f:
        for line in f:
            l = line.rstrip('\r\n').split('\t')
            # format: marker ID <tab> protein1 ID <tab> protein2 ID <tab> ...
            p, prots = l[0], l[1:]
            if p not in p2prots:
                p2prots[p] = set()
            for prot in prots:
                if prot in p2prots[p]:
                    raise ValueError('%s: %s already exists!' % (p, prot))
                p2prots[p].add(prot)
                if prot in prot2p:
                    raise ValueError('%s already exists!' % p)
                prot2p[prot] = p

# write protein to marker map
with open('prot2p.txt', 'w') as f:
    for prot in sorted(prot2p):
        f.write('%s\t%s\n' % (prot, prot2p[prot]))

# write marker to proteins map
with open('p2prots.txt', 'w') as f:
    for p in sorted(p2prots):
        f.write('%s\t%s\n' % (p, ','.join(sorted(p2prots[p]))))

# read genome list
# note: some genomes may receive zero marker gene
with open('gs.txt', 'r') as f:
    gs = f.read().splitlines()

# read nucleotid to genome map
with lzma.open('nucl2g.txt.xz', 'rt') as f:
    nucl2g = dict(x.split('\t') for x in f.read().splitlines())

# generate genome to marker(s) map
g2ps = {x: set() for x in gs}
for prot, p in prot2p.items():
    g = nucl2g['_'.join(prot.split('_')[:-1])]
    if p in g2ps[g]:
        raise ValueError('Genome %s has more than one copy of %s.' % (g, p))
    g2ps[g].add(p)

# write phyletics
ps = sorted(p2prots)
with open('phyletics.tsv', 'w') as f:
    f.write('#ID\t%s\n' % '\t'.join(ps))
    for g in sorted(gs):
        out = ['1' if x in g2ps[g] else '0' for x in ps]
        f.write('%s\t%s\n' % (g, '\t'.join(out)))
