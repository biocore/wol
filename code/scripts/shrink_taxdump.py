# Shrink the standard NCBI taxdump files nodes.dmp and names.dmp so that
# they only contain given TaxIDs and their ancestors
# usage: python me.py taxid_list taxdump_dir
# output: nodes.dmp and names.dmp

from sys import argv
from os.path import join

# read TaxIDs to be included
with open(argv[1], 'r') as f:
    tids = set(f.read().splitlines())

# read the NCBI taxonomy tree
with open(join(argv[2], 'nodes.dmp'), 'r') as f:
    tid2pid = dict(x.replace('\t|', '').split('\t')[:2]
                   for x in f.read().splitlines())

# identify all ancestral TaxIDs
ancs = set()
for tid in tids:
    cid = tid
    while True:
        pid = tid2pid[cid]
        if cid == pid or pid in ancs:
            break
        ancs.add(pid)
        cid = pid
tids.update(ancs)

# shrink taxdump files
for stem in ('nodes', 'names'):
    fo = open('%s.dmp' % stem, 'w')
    fi = open(join(argv[2], '%s.dmp' % stem), 'r')
    for line in fi:
        x = line.rstrip('\r\n').replace('\t|', '').split('\t')
        if x[0] in tids:
            if stem == 'nodes' or 'scientific name' in x:
                fo.write(line)
    fi.close()
    fo.close()
