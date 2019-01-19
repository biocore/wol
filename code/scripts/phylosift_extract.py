# Extract marker gene sequences from search result.
# Usage: python me.py marker_gene.list genome.list output_dir

from sys import argv
from subprocess import run, PIPE, STDOUT
import pandas as pd

# read marker gene list
with open(argv[1], 'r') as f:
    ms = f.read().splitlines()

# read genome list
with open(argv[2], 'r') as f:
    gs = f.read().splitlines()

# read summary table
df = pd.read_table('matrices/all.tsv', index_col=0)

for g in gs:
    p = run('tar tf output/%s.tar.bz2' % g,
            shell=True, stdout=PIPE, stderr=STDOUT)
    flist = p.stdout.decode('utf-8').splitlines()
    for m in ms:
        if df[m][g] != 1:
            continue
        fnames = []
        for fname in flist:
            if fname.startswith('%s.lastal.candidate.aa.1.' % m):
                fnames.append(fname)
        if len(fnames) != 1:
            raise ValueError('Exception of file number at %s: %s' % (g, m))
        fname = fnames[0]
        p = run('tar xOf output/%s.tar.bz2 %s' % (g, fname),
                shell=True, stdout=PIPE, stderr=STDOUT)
        lines = p.stdout.decode('utf-8').splitlines()
        if len(lines) != 2:
            raise ValueError('Exception of line number at %s: %s' % (g, m))
        if not lines[0].startswith('>'):
            raise ValueError('Exception of line format at %s: %s' % (g, m))
        with open('%s/%s.faa' % (argv[3], m), 'a') as f:
            f.write('>%s\n%s\n' % (g, lines[1]))
