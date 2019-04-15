## Tree rendering

### What they are

We provide pre-formatted tree with metadata files which can be directly parsed and rendered by [FigTree](http://tree.bio.ed.ac.uk/software/figtree/) and [iTOL](https://itol.embl.de/).

### How to display them

**FigTree**

Simply open `figtree.tre` in FigTree.

- This file is a pre-decorated FigTree Nexus file. It comes with tip and internal node labels (taxonomy and branch supports) and a default collapsing scheme. The "colored" version also has branch colors.

**iTOL**

- Upload `pruned_tree.nwk` and open in the iTOL interface.
  - If iTOL prompts to auto-collapse, click "Reset all".
- Sequentially drag & drop the following files into the iTOL interface. Ignore errors (they are the unused labels). Save changes.
  - `collapse.txt`: Colllapsing scheme.
  - `label.txt`: Node labels, including both tips (genomes) and internal nodes (they now become tips after collapsing).

- (The following are optional "datasets" for iTOL.)
  - `branch_text.txt` - Labels to be shown on branches.
  - `xxx_node_text.txt` - Branch support values as node labels ("xxx" is the type of branch support).
  - `xxx_branch_color.txt` - Branch support values as branch color gradient.

- (The following are only for `astral.e5p50`, which has a pre-defined coloring scheme.)
  - `branch_color.txt`
  - `clade_color.txt`
  - `label_color.txt`

**Moreover**

The file `collapsed_tree.nwk` is a shrinked Newick file with tips representing collapsed clades.


### How they were generated

The workflow starts with a tree and taxonomic annotation ([NCBI](https://www.ncbi.nlm.nih.gov/taxonomy) or [GTDB](http://gtdb.ecogenomic.org/), pre-curated using [tax2tree](https://github.com/biocore/tax2tree)).

It collapses the tree at given rank(s). One can specify multiple ranks and complex criteria for inclusion at each rank. In the current data release, the default criteria are:

- Sequentially collapse at the following ranks:

  - **genus** => **family** => **order** with 50 or more taxa => **class** with 5 or more taxa => **phylum** with at least one taxon => taxonomic units above phylum (if available).

- If a lower-rank clade is already collapsed, its higher-rank ancestors will not be collapsed.

- If a taxonomic unit is polyphyletic, minor clades which have less than 5% taxa of the primary clade will be deleted.

  - e.g., say _Firmicutes_1_ has 1,000 tips. If _Firmicutes_10_ has 45 tips (< 1000 * 5%), it will be deleted.

- Tips that do not belong to any collapsed clades will be deleted.

For a special set of 1k-taxon trees, more relaxed parameters were used:

  - **genus** => **family** with 10 or more taxa => **order** with 5 or more taxa => **class** => **phylum** with at least one taxon

It adds taxonomic labels to branches / nodes. They are the taxonomic units that exclusively describe the corresponding branches. If multiple ranks can describe one branch, only the highest-rank is retained.

Optionally, one can provide additional node metrics (e.g., branch support values), which will be converted into node labels and color gradients.


### How I can generate them

We provided the [source code](../code/notebooks/render_tree.ipynb) for generating the pre-formatted tree files.
