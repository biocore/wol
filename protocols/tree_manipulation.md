## Tree manipulation

We wrote and made publicly available multiple [Python scripts](../code/scripts) that facilitates tree manipulation. They depend on the `TreeNode` object in [scikit-bio](http://scikit-bio.org/). Here we describe some of them.


### Duplication treatment

We removed identical sequences from an alignment were removed prior to tree-building, and added them back as **polytomies** to the resulting tree.

Note: Different tree-building programs treat sequence duplicates in different ways. For example, **FastTree** places them as multifurcating branches (which is good); whereas **RAxML** and **IQ-TREE** force them into bifurcating branches, with branch length = 1e-6 (RAxML) or 0.0 (IQ-TREE). That's why we wanted to override them in a constant behavior.
{: .notice}

De-duplication can be done using RAxML:

```bash
raxmlHPC -m PROTCATLG -s align.fa -p 12345
```

- A new alignment file `align.fa.reduced` will be generated, which contains only unique sequences.

We provide [raxml_duplicate_map.py](../code/scripts/raxml_duplicate_map.py) to generate a representative-to-duplicates map from the RAxML output files:

```bash
raxml_duplicate_map.py align.fa align.reduced.fa > duplicate.map
```

After tree building, we use [append_taxa.py](../code/scripts/append_taxa.py) to add duplicate taxa back to the tree:

```bash
append_taxa.py input.nwk duplicate.map > output.nwk
```

In the resulting tree, duplicates form a polytomic clade with zero branch lengths. For example:

- Before appending: `(a:0.2,b1:0.1);`
- After appending: `(a:0.2,(b1,b2,b3):0.1);`


### Tree rooting

We provide [root_by_outgroup.py](../code/scripts/root_by_outgroup.py) to root a tree based on a given taxon set as outgroup:

```bash
root_by_outgroup.py input.nwk outgroup.list > output.nwk
```

- This script allows incomplete taxon list: the tree may contain less taxa (e.g., a subsampled tree).

We also have [restore_rooting.py](../code/scripts/restore_rooting.py) to root one tree based on another.

```bash
restore_rooting.py source.nwk target.nwk > output.nwk
```

- Example usage: root a RAxML bootstrapped tree (which loses original rooting) based on the original tree.

These scripts can treat both rooted (i.e., "root" has two children) and unrooted (i.e., "root" has three children) trees.

In some cases the input tree is arbitrarily rooted (e.g., the ASTRAL output tree) and one wants to make it unrooted. Here is [trifurcate_tree.py](../code/scripts/trifurcate_tree.py):

```bash
trifurcate_tree.py input.nwk > output.nwk
```


### Node ordering

One can rearrange nodes in decreasing order using [decrease_node_order.py](../code/scripts/decrease_node_order.py):

```bash
decrease_node_order.py input.nwk > output.nwk
```

- This "decreasing order" is identical to FigTree's same command.
- In the original `order_nodes` function in [tree.py](../code/utils/tree.py), it also allows increasing node order.

One can restore node ordering of one tree based on another, using [restore_node_order.py](../code/scripts/restore_node_order.py):

```bash
restore_node_order.py source.nwk target.nwk > output.nwk
```

As a bonus, the script [trianglize_tree.py](../code/scripts/trianglize_tree.py) rearranges nodes so that the two basal clades are in increasing and
decreasing node order, respectively. If the input tree is already midpoint-
rooted, the output tree will shape like a triangle:

```bash
trianglize_tree.py input.nwk > output.nwk
```
