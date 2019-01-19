# Convert a distance matrix into the Phylip format (lower triangle) which can
# then be parsed by ClearCut.
# Usage: python me.py input.dm > output.phy

from sys import argv
from os import popen

# get dimension of distance matrix
n = int(popen('cat %s | wc -l' % argv[1]).read().rstrip()) - 1
print(str(n))

# print lower triangle only
i = 1
with open(argv[1], 'r') as f:
    next(f)
    for line in f:
        print('\t'.join(line.rstrip('\r\n').split('\t')[:i]))
        i += 1
