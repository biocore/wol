#!/usr/bin/env python3
"""Export node labels of a tree to a table.

Usage:
    export_supports.py input.nwk > output.tsv

Notes:
    Nodes must have IDs:
        i.e., "N1" is the ID of `(a,b)'100:N1'`.
    Supported node label formats:
     - single number: `100`, `0.99`
     - multiple numbers split by slash: `100/0.99`
     - multiple key-value pairs in brackets: `[bs=100;rell=0.95;alrt=0.99]`
     - more complex format: `[&taxon="Ecoli",support=95,range={91,98}]`
"""

import sys
import fileinput
import re
from skbio import TreeNode

import unittest
from io import StringIO
from unittest.mock import patch, mock_open


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with fileinput.input() as f:
        tree = TreeNode.read(f)

    # check node support format
    is_simple = True
    for node in tree.non_tips(include_self=False):
        if node.name is not None and ':' in node.name:
            if '[' in node.name.rsplit(':', 1)[0]:
                is_simple = False
            break

    # extract support values
    data = []
    for node in tree.levelorder(include_self=False):
        if node.is_tip():
            continue
        if node.name is not None and ':' in node.name:
            sup, nid = node.name.rsplit(':', 1)
            if is_simple:
                print('%s\t%s' % (nid, sup.replace('/', '\t')))
            else:
                # remove boundaries
                sup = sup.lstrip('[').rstrip(']').lstrip('&')

                # uniformly use comma as delimiter
                sup = sup.replace(';', ',').rstrip(',')

                # temporarily replace commas within braces
                sup = re.sub(r',(?=[^{]*})', '\t', sup)

                # split into key-value pairs
                supd = dict(x.replace('\t', ',').split('=') for x in
                            sup.split(','))

                data.append((nid, supd))

    # export complex node labels
    if not is_simple:
        fields = sorted(set().union(*[x[1].keys() for x in data]))
        print('node\t%s' % '\t'.join(fields))
        for nid, supd in data:
            out = [nid]
            for field in fields:
                out.append(supd[field] if field in supd else '')
            print('\t'.join(out))


class Tests(unittest.TestCase):
    def test_main(self):
        # single numerical support value
        nwk = "((a,b)'100:n2',(c,d)'95:n3')root;"
        exp = 'n2\t100\nn3\t95\n'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)

        # multiple numerical support values separated by slash
        nwk = ("((a:1.5,b:2.2)'0.99/95:n2':0.35,"
               "(c:0.5,d:0.9)'0.97/85:n3':2.0)'0.5:root';")
        exp = 'n2\t0.99\t95\nn3\t0.97\t85\n'
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)

        # complex node label structure 1
        nwk = ("((a,b)'[bs=90;rell=0.95;alrt=0.99]:n2',"
               "(c,d)'[bs=80;rell=0.90;alrt=0.95]:n3');")
        exp = ('node\talrt\tbs\trell\n'
               'n2\t0.99\t90\t0.95\n'
               'n3\t0.95\t80\t0.90\n')
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)

        # complex node label structure 2
        nwk = ("((a,b)'[&taxon=Ecoli,support=95;range={91,98}]:n2',"
               "(c,d)'[&taxon=Cdiff,support=80;range={65,85}]:n3');")
        exp = ('node\trange\tsupport\ttaxon\n'
               'n2\t{91,98}\t95\tEcoli\n'
               'n3\t{65,85}\t80\tCdiff\n')
        with patch('builtins.open', mock_open(read_data=nwk)):
            with patch('sys.stdout', new=StringIO()) as m:
                main()
                self.assertEqual(m.getvalue(), exp)


if __name__ == "__main__":
    main()
