#!/usr/bin/env python3
"""Convert GTDB taxonomy into NCBI style.

Usage:
    gtdb_to_taxdump.py gtdb_taxonomy.tsv
    gtdb_to_taxdump.py bac120_taxonomy_r89.tsv ar122_taxonomy_r89.tsv

Output:
    nodes.dmp: NCBI-style nodes file.
    names.dmp: NCBI-style names file.
    taxid.map: genome ID to taxonomy ID map.

Notes:
    This script converts GTDB lineage strings (Greengenes-style) into an NCBI-
    style taxonomy database (taxdump), in which each taxonomic unit is given
    a unique numeric ID (a.k.a. TaxID). This ID is incremental, starting from 1
    at the root, and increasing from higher ranks to lower ranks.

    This script is generally applicable to Greengenes-style lineage strings.
    However the following criteria must suffice: 1) All lineages have exactly
    seven ranks, from domain (d) to species (s). 2) All ranks are filled (i.e.,
    there are no gaps like "g__;". 3) At the same rank, all taxon names are
    unique.

    If you plan to use this script on custom lineage strings, you may need to
    consider these criteria and modify the code accordingly.
"""

import fileinput

__author__ = 'Qiyun Zhu'
__license__ = 'BSD-3-Clause'
__version__ = '0.0.1-dev'
__email__ = 'qiyunzhu@gmail.com'

ranks = ('domain', 'phylum', 'class', 'order', 'family', 'genus', 'species')


def main():
    """Reformat GTDB taxonomy into NCBI taxdump.
    """
    # genome to species map
    g2species = {}

    # taxon to parent map
    taxon2parent = {x: {} for x in ranks}

    # parse records
    for line in fileinput.input():
        g, lineage = line.rstrip().split('\t')

        # start with root
        parent = 'root'

        # parse taxa in order
        for i, taxon in enumerate(lineage.split(';')):
            code, taxon = taxon.split('__')

            # validate order of ranks
            rank = ranks[i]
            if code != rank[0]:
                raise ValueError(f'Invalid rank code: {code}.')

            # validate consistency with existing record
            if taxon in taxon2parent[rank]:
                if taxon2parent[rank][taxon] != parent:
                    raise ValueError(f'Inconsistent parent: {taxon}.')

            # add taxon to records
            else:
                taxon2parent[rank][taxon] = parent

            # update parent
            parent = taxon

        # last taxon is species
        if rank != 'species':
            raise ValueError(f'Incomplete record: {parent}.')
        g2species[g] = parent

    # build taxonomy tree
    taxdump = {'1': {'parent': '1', 'rank': 'no rank', 'name': 'root'}}

    # current taxId (incremental)
    cid = 1

    # assign taxIds to taxa
    parent2id = {'root': 1}
    for rank in ranks:
        taxon2id = {}
        for taxon, parent in taxon2parent[rank].items():
            cid += 1
            taxdump[str(cid)] = {
                'parent': str(parent2id[parent]), 'rank': rank, 'name': taxon}
            taxon2id[taxon] = cid
        parent2id = {k: v for k, v in taxon2id.items()}

    # write genome to species taxId map
    with open('taxid.map', 'w') as f:
        for g, species in sorted(g2species.items()):
            f.write(f'{g}\t{parent2id[species]}\n')

    # write nodes.dmp and names.dmp
    fo = open('nodes.dmp', 'w')
    fa = open('names.dmp', 'w')
    for id_, rec in sorted(taxdump.items(), key=lambda x: int(x[0])):
        fo.write(f"{id_}\t|\t{rec['parent']}\t|\t{rec['rank']}\t|\n")
        fa.write(f"{id_}\t|\t{rec['name']}\t|\t\t|\tscientific name\t|\n")
    fo.close()
    fa.close()


if __name__ == '__main__':
    main()
