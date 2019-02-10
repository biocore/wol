#!/usr/bin/env python3
"""Generate a core-to-duplicates map for an MSA filtered by RAxML.

Usage:
    raxml_duplicate_map.py input.fa input.reduced.fa > duplicate.map
"""

import sys

import unittest
from os import remove
from io import StringIO
from tempfile import mkstemp
from unittest.mock import patch


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)

    # read original sequences
    seqs = {}
    with open(sys.argv[1], 'r') as f:
        name = ''
        for line in f:
            line = line.rstrip('\r\n')
            if line.startswith('>'):
                name = line[1:]
                seqs[name] = ''
            else:
                seqs[name] += line

    # generate a map of unique sequence to identical sequences
    seqs_rev = {}
    for name, seq in seqs.items():
        seqs_rev.setdefault(seq, set()).add(name)

    # find sequence duplicates
    dups = [names for seq, names in seqs_rev.items() if len(names) > 1]

    # read core sequences from the "reduced" file
    cores = set()
    with open(sys.argv[2], 'r') as f:
        for line in f:
            if line.startswith('>'):
                cores.add(line.rstrip('\r\n')[1:])

    # identify and write duplicate map
    for names in sorted(dups):
        found = set()
        for name in names:
            if name in cores:
                found.add(name)
        if len(found) != 1:
            raise ValueError(
                'Error: Cannot find a core sequence for sequences: %s.'
                % ','.join(sorted(names)))
        print('%s\t%s' % (max(found), ','.join(sorted(names - found))))


class Tests(unittest.TestCase):
    def test_main(self):
        ofd, opath = mkstemp()
        with open(ofd, 'w') as f:
            f.write('>seq1\nATCGA\n'
                    '>seq2\nATCGA\n'
                    '>seq3\nATGGA\n'
                    '>seq4\nACCGA\n'
                    '>seq5\nACCGA\n'
                    '>seq6\nACCGA\n')
        rfd, rpath = mkstemp()
        with open(rfd, 'w') as f:
            f.write('>seq4\nACCGA\n'
                    '>seq3\nATGGA\n'
                    '>seq1\nATCGA\n')
        exp = ('seq1\tseq2\n'
               'seq4\tseq5,seq6\n')
        with patch('sys.argv', [None, opath, rpath]):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)
        remove(opath)
        remove(rpath)


if __name__ == "__main__":
    main()
