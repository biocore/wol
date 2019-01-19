# Generate a core-to-duplicate map for an MSA filtered by RAxML
# Usage: python me.py input.fa input.reduced.fa > output.txt

from sys import argv

seqs = {}
with open(argv[1], 'r') as f:
    name = ''
    for line in f:
        line = line.rstrip('\r\n')
        if line.startswith('>'):
            name = line[1:]
            seqs[name] = ''
        else:
            seqs[name] += line

seqs_rev = {}
for name, seq in seqs.items():
    seqs_rev.setdefault(seq, set()).add(name)

dups = [names for seq, names in seqs_rev.items() if len(names) > 1]

cores = set()
with open(argv[2], 'r') as f:
    for line in f:
        if line.startswith('>'):
            cores.add(line.rstrip('\r\n')[1:])

for names in dups:
    found = set()
    for name in names:
        if name in cores:
            found.add(name)
    if len(found) != 1:
        raise ValueError(','.join(sorted(names)))
    print('%s\t%s' % (max(found), ','.join(sorted(names - found))))
