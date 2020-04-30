#!/usr/bin/env python3
"""Generate a single Fasta file from multiple genome sequences.
"""

from os import listdir
from os.path import join, splitext
import re
import gzip
import bz2
import lzma
import argparse

__author__ = 'Qiyun Zhu'
__license__ = 'BSD-3-Clause'
__version__ = '0.0.1-dev'
__email__ = 'qiyunzhu@gmail.com'

usage = """%(prog)s -i INPUT_DIR -o OUTPUT_FILE [options]"""

description = """example:
  %(prog)s -i multi_fna.gz_dir -o output.fna --concat --gap N*20
"""


def parse_args():
    parser = argparse.ArgumentParser(
        usage=usage, description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    arg = parser.add_argument
    arg('-i', '--input', required=True,
        help='input directory containing genome sequences (fna)')
    arg('-o', '--output', required=True,
        help='output multi-Fasta filename')
    arg('-c', '--concat', action='store_true',
        help='concatenate sequences of each genome')
    arg('-g', '--gap', default='',
        help=('fill sequence gaps with string, use "*" to indicate repeats, '
              'e.g., "N*20"'))
    arg('-e', '--ext',
        help='filename extension following genome ID')
    arg('-f', '--filt',
        help=('exclude sequences with any of comma-delimited words in title, '
              'e.g., "plasmid,phage"'))
    arg('-n', '--ncbi', action='store_true',
        help=('parse NCBI-style genome filenames, e.g., "GCF_123456789.1_'
              'ASM123v1_genomic.fna.gz" will be given ID "G123456789"'))
    for arg in parser._actions:
        arg.metavar = '\b'
    return parser.parse_args()


def main():
    # parser arguments
    args = parse_args()

    # generate gap string
    gap = ''
    if args.gap:
        gap = args.gap
        if '*' in gap:
            str_, n_ = gap.rsplit('*', 1)
            if n_.isdigit():
                gap = str_ * int(n_)

    # compressed filename pattern
    zipdic = {'.gz': gzip, '.bz2': bz2, '.xz': lzma, '.lz': lzma}

    # read input genome list
    gs = {}
    if args.ncbi:
        ptn = re.compile(r'GC[FA]_([0-9]{9})\.[0-9]+_.*')
    for fname in listdir(args.input):
        g = ''

        # custom extension
        if args.ext:
            if not fname.endswith(args.ext):
                continue
            g = fname[:-len(args.ext)].rstrip('.')

        # auto-recognize
        else:
            g, ext = splitext(fname)
            if len(ext) > 1 and ext in zipdic:
                g, ext = splitext(g)
        if g in gs:
            raise ValueError('Duplicate genome ID "%s".' % g)

        # parse NCBI filename
        if args.ncbi:
            m = ptn.match(g)
            if m:
                g = 'G%s' % m.group(1)

        gs[g] = fname
    print('Found %d genomes.' % len(gs))

    # summary
    nseq = 0
    nchar = 0

    # helper to read compressed files
    def read(fname):
        ext = splitext(fname)[1]
        zipfunc = getattr(zipdic[ext], 'open') if ext in zipdic else open
        return zipfunc(fname, 'rt')

    # sequence title filter
    if args.filt:
        ptn = re.compile(
            r'[^a-zA-Z0-9](%s)[^a-zA-Z0-9]' % args.filt.replace(',', '|'))

        def filtseq(title):
            return ptn.search(title, re.IGNORECASE) is not None

    # output file
    fo = open(args.output, 'w')

    # store or write a sequence when finishing reading
    def finseq():
        nonlocal seq, nseq, nchar
        if seq:
            if not todel:
                if args.concat:
                    seqs.append(seq)
                else:
                    fo.write('%s\n' % seq)
                nseq += 1
                nchar += len(seq)
            seq = ''

    # parse input genome sequences
    for g, fname in sorted(gs.items(), key=lambda x: x[0]):
        if args.concat:
            fo.write('>%s\n' % g)
        fi = read(join(args.input, fname))
        seqs = []
        seq = ''
        todel = False
        for line in fi:
            line = line.rstrip('\r\n')
            if line.startswith('>'):
                finseq()
                todel = filtseq(line) if args.filt else False
                if not args.concat and not todel:
                    fo.write('%s\n' % line.split()[0])
            else:
                seq += line
        fi.close()
        finseq()
        if args.concat:
            fo.write('%s\n' % gap.join(seqs))
    print('Parsed %d sequences (%d characters in total).'
          % (nseq, nchar))

    # finish writing
    fo.close()
    print('Output file %s written.' % args.output)


if __name__ == "__main__":
    main()
