#!/usr/bin/env python3
"""Generate a matrix of Hamming distance among sequences, excluding gaps.

Usage:
    align_distmat.py input.fa > output.dm

Notes:
    For each pairwise comparison, sites with one or two gaps are skipped.
    For example, in the following comparision, the distance is 3 / 10 = 0.3.
        GAG-GTC-ATAC
        GAGCCTC-CTAG

    This is a time-consuming operation. It takes 4-6 days to compute distances
    among 10,575 taxa by 38K sites. The code has already been optimized within
    the capability of Python.
"""

import sys
import fileinput
from io import StringIO
import unittest
from unittest.mock import patch, mock_open
from skbio import DistanceMatrix


def main():
    ids, seqs = [], []
    for line in fileinput.input():
        line = line.rstrip('\r\n')
        if line.startswith('>'):
            ids.append(line[1:])
            seqs.append('')
        else:
            seqs[-1] += line
    mat = DistanceMatrix.from_iterable(
        seqs, hamming_no_gap, keys=ids, validate=False)
    mat.write(sys.stdout)


def hamming_no_gap(seq1, seq2):
    """Calculate pairwise Hamming distance, skipping sites with gaps."""
    n, m = 0, 0
    for c1, c2 in zip(seq1, seq2):
        if c1 != '-' and c2 != '-':
            n += 1
            if c1 != c2:
                m += 1
    return m / n


class Tests(unittest.TestCase):
    def test_main(self):
        fasta = ('>seq1\nGAG-GTC-ATAC\n'
                 '>seq2\nGAGCCTC-CTAG\n'
                 '>seq3\nGAC-CTCACTAC\n')
        exp = """	seq1	seq2	seq3
seq1	0.0	0.3	0.3
seq2	0.3	0.0	0.2
seq3	0.3	0.2	0.0
"""
        with patch('builtins.open', mock_open(read_data=fasta)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)

    def test_hamming_no_gap(self):
        obs = hamming_no_gap('GAG-GTC-ATAC',
                             'GAGCCTC-CTAG')
        self.assertEqual(obs, 0.3)


if __name__ == '__main__':
    main()
