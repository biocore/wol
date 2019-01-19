# Summarize the number of hits per marker per genome.
# Usage: python me.py genome.list output.tsv

from sys import argv
from subprocess import run, PIPE, STDOUT

with open(argv[1], 'r') as f:
    gs = f.read().splitlines()

data = {}
markers = set()
for g in gs:
    data[g] = {}
    p = run('tar xOf output/%s.tar.bz2 marker_summary.txt' % g, shell=True,
            stdout=PIPE, stderr=STDOUT)
    for line in p.stdout.decode('utf-8').splitlines():
        x = line.split('\t')
        if x[0] == 'total':
            continue
        if x[0] not in markers:
            markers.add(x[0])
        data[g][x[0]] = int(x[1])
    print(g)

markers = sorted(markers)
print('Markers: %d.' % len(markers))
print('Genomes: %d.' % len(data))

with open(argv[2], 'w') as f:
    f.write('#GenomeID\t%s\n' % '\t'.join(markers))
    for g in sorted(data):
        out = [g]
        for m in markers:
            if m in data[g]:
                out.append(str(data[g][m]))
            else:
                out.append('0')
        f.write('%s\n' % '\t'.join(out))
