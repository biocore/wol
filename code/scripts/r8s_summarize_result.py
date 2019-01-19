# Summarize r8s divergence time estimation results.
# Usage: python me.py r8s.output output_filename_prefix

from sys import argv
import re
import pandas as pd
from skbio import TreeNode

node_dict = {}
curr_node = ''

solutions = []
passed = []

reading_table = False

param2taxon = {}

with open(argv[1], 'r') as f:
    for line in f:
        line = line.rstrip('\r\n')

        m = re.search(r'^\[\*\* The overwritten node is (.*) \*\*\]$', line)
        if m:
            curr_node = m.group(1)
            continue

        m = re.search(r'^Defining clade name: (.*)$', line)
        if m:
            if curr_node != '':
                node_dict[m.group(1)] = curr_node
                curr_node = ''
                continue
            else:
                raise ValueError('Found clade without matching node name.')

        m = re.search(r'Starting optimization \(random starting point (\d+)\)',
                      line)
        if m:
            solutions.append({})
            continue

        if line == '\tParam\tEstimate\tGradient\tActive*\tTaxon':
            reading_table = True
            continue

        if reading_table:
            if line == '':
                reading_table = False
                continue
            param, estimate, gradient, active, taxon = line.strip().split('\t')
            if taxon in node_dict:
                taxon = node_dict[taxon]
            if param in param2taxon:
                if param2taxon[param] != taxon:
                    raise ValueError('Inconsistent param to taxon mapping.')
            else:
                param2taxon[param] = taxon
            solutions[-1][taxon] = estimate
            continue

        if line == '*** Gradient check passed ***':
            passed.append(True)
            continue

        if line == '*** Gradient check FAILED ***':
            passed.append(False)
            continue

        if line == 'MinND returned failure in ConstrOpt (while retrying)':
            passed.append(False)
            continue

        m = re.search(r'Using optimization from starting point (\d+) as best '
                      'estimate', line)
        if m:
            print('Best estimate: %s.' % m.group(1))
            continue

        if line == 'Rates (substitutions per site per unit time)':
            next(f)
            next(f)
            passed_ = [True if x == 'PASSED' else False for x in
                       next(f).rstrip('\r\n').strip().split()]
            if passed != passed_:
                raise ValueError('Inconsistent solution pass status.')
            print('%d out %d replicates passed.'
                  % (passed.count(True), len(passed)))

            solutions = [x for i, x in enumerate(solutions) if passed[i]]
            df = pd.DataFrame(solutions).T
            df.columns = [str(i + 1) for i, x in enumerate(passed) if x]
            df.index.name = 'node'

            node_order = sorted(solutions[0].keys(), key=lambda x: int(x[1:]))
            df = df.reindex(node_order)

            # df['mean'], df['std'] = df.mean(axis=1), df.std(axis=1)

            df.to_csv('%s.tsv' % argv[2], sep='\t')
            continue

        # TODO: Extract substitution rates at nodes and tips.

        if line.startswith('tree '):
            tree = TreeNode.read([line.partition('=')[2].strip()])
            for node in tree.non_tips(include_self=True):
                if node.name in node_dict:
                    node.name = node_dict[node.name]
            tree.write('%s.nwk' % argv[2])
            continue
