# Generate a matrix of Hamming distance among sequences, excluding gaps.
# Usage: python me.py input.fa output.dm

# Note: For each pairwise comparison, sites with one or two gaps are skipped.
# For example, in the following comparision, the distance is 3 / 10 = 0.3.
#   GAG-GTC-ATAC
#   GAGCCTC-CTAG

# Note: This is a time-consuming operation. It takes 4-6 days to compute
# distances among 10,575 taxa by 38K sites. The code has already been
# optimized within the capability of Python.

from sys import argv
from skbio import DistanceMatrix


def main():
    ids, seqs = [], []
    with open(argv[1], 'r') as f:
        for line in f:
            line = line.rstrip('\r\n')
            if line.startswith('>'):
                ids.append(line[1:])
                seqs.append('')
            else:
                seqs[-1] += line
    mat = DistanceMatrix.from_iterable(
        seqs, hamming_no_gap, keys=ids, validate=False)
    mat.write(argv[2])


def hamming_no_gap(seq1, seq2):
    n, m = 0, 0
    for c1, c2 in zip(seq1, seq2):
        if c1 != '-' and c2 != '-':
            n += 1
            if c1 != c2:
                m += 1
    return m / n


if __name__ == '__main__':
    main()
