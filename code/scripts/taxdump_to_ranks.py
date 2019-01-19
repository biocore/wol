# Extract taxon names and IDs at given ranks for each genome.
# Usage: python me.py g2tid.txt taxdump_dir
# Output: rank_tids.tsv and rank_names.tsv

from sys import argv

# ranks to extract
ranks = ['superkingdom', 'kingdom', 'phylum', 'class', 'order', 'family',
         'genus', 'species']

rank_dic = {x: x for x in ranks}

# uncomment this line to merge superkingdom into kingdom
# rank_dic['superkingdom'] = 'kingdom'

# one can do it later using Bash:
# cat rank_names.tsv | head -n1 | cut -f1,3- > output.tsv
# cat rank_names.tsv | tail -n+2 | cut -f1,2,4- >> output.tsv

# read genome to TaxID map
with open(argv[1], 'r') as f:
    g2tid = dict(x.split('\t') for x in f.read().splitlines())

tids = set(g2tid.values())

# read NCBI taxonomy
taxdump = {}

# format of nodes.dmp: taxid | parent taxid | rank | more info...
with open('%s/nodes.dmp' % argv[2], 'r') as f:
    for line in f:
        x = line.rstrip('\r\n').replace('\t|', '').split('\t')
        taxdump[x[0]] = {'parent': x[1], 'rank': x[2], 'name': '',
                         'children': set()}

# format of names.dmp: taxid | name | unique name | name class |
with open('%s/names.dmp' % argv[2], 'r') as f:
    for line in f:
        x = line.rstrip('\r\n').replace('\t|', '').split('\t')
        if x[3] == 'scientific name':
            taxdump[x[0]]['name'] = x[1]

rank_tids = {}
rank_names = {}
for tid in tids:
    rank_tids[tid] = {x: '0' for x in ranks}
    rank_names[tid] = {x: '' for x in ranks}
    cid = tid
    while True:
        rank = taxdump[cid]['rank']
        if rank in rank_dic:
            rankx = rank_dic[rank]
            if rank_tids[tid][rankx] != '0':
                print('taxon %s has duplicated definition of rank %s'
                      % (tid, rankx))
            rank_tids[tid][rankx] = cid
            name = taxdump[cid]['name']
            if ';' in name:
                raise ValueError('taxon name of %s has ;.' % cid)
            if name[0] == ' ':
                raise ValueError('taxon name of %s has leading space.' % cid)
            if name[-1] == ' ':
                raise ValueError('taxon name of %s has trailing space.' % cid)
            rank_names[tid][rankx] = name
        pid = taxdump[cid]['parent']
        if cid == pid:
            break
        cid = pid

f1 = open('rank_tids.tsv', 'w')
f2 = open('rank_names.tsv', 'w')

for f in (f1, f2):
    f.write('genome\t%s\n' % '\t'.join(ranks))

for g in sorted(g2tid):
    f1.write('%s\t%s\n' % (g, '\t'.join([rank_tids[g2tid[g]][x]
                                         for x in ranks])))
    f2.write('%s\t%s\n' % (g, '\t'.join([rank_names[g2tid[g]][x]
                                         for x in ranks])))

f1.close()
f2.close()
