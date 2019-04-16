## Tree building

Core protocol of this project. Phylogentic reconstruction of evolutionary relationships of individual gene families and whole genomes.

This protocol is fully programmed, _without the need for any manual curation_. Although in the actual analysis one needs to manually kick-start individual computational tasks, since they are so heavy with this amount of data and have to be scheduled with care on a super cluster (in our case, [SDSC Comet](https://www.sdsc.edu/support/user_guides/comet.html)).


### 1. Tools

- [**UPP**](https://github.com/smirarab/sepp) 2.0
- [**FastTree**](http://www.microbesonline.org/fasttree/) 2.1.9
- [**RAxML**](https://cme.h-its.org/exelixis/web/software/raxml/) 8.2.10
- [**IQ-TREE**](http://www.iqtree.org/) 1.6.1
- [**PhyloPhlAn**](http://huttenhower.sph.harvard.edu/phylophlan) 2c0e61a
- [**TreeShrink**](https://github.com/uym2/TreeShrink) 1.1
- [**ASTRAL**](https://github.com/smirarab/ASTRAL) 5.12.6a

Note: the commands listed below have ignored multi-threading parameters and filename-specific parameters.


### 2. Sequence alignment

#### 2.1. Per-gene alignment

Align amino acid sequences using UPP.

```bash
run_upp.py -s seqfile.fa -B 100000 -M -1 -T 0.66 -m amino
```

- UPP was run with all sequences but fragments are used for the backbone. Sequences with length _L_ < 0.34\*_M_ or _L_ > 1.33\*_M_, where _M_ is the median length of all the sequences, were detected as fragments and not included in the backbone.

After aligned the sequences by UPP, we filtered out **sites** with more than 95% gaps, then filtered out **sequences** with more than 66% gaps.

#### 2.2 Gene filtering

Drop marker genes with more than 75% gaps in the alignment matrix.

This left **381** out of 400 marker genes, and left **10,575** out of 11,079 genomes.


### 3. Gene trees

#### 3.1. Model selection

We used [`ProteinModelSelection.pl`](https://github.com/stamatak/standard-RAxML/blob/master/usefulScripts/ProteinModelSelection.pl) as bundled in RAxML:

```bash
perl ProteinModelSelection.pl align.fa > best_model.txt
```


#### 3.2. Tree building

Build a starting tree using FastTree:

```bash
FastTree -lg -gamma -seed 12345 align.fa > fasttree.nwk
```

Remove outliers (low quality sequences, contaminations, etc.) presented as unproportionally long branches in the FastTree trees using TreeShrink:

```bash
run_treeshrink.py -i input_dir -t fasttree.nwk -a align.fa -o output_dir
```

Infer gene tree topology using CAT in RAxML. Three runs were performed, one with the FastTree tree as the starting tree; the other two with random seeds:

```bash
raxmlHPC -m PROTCATLG -F -f D -D -s align.fa -t fasttree.nwk
raxmlHPC -m PROTCATLG -F -f D -D -s align.fa -p 12345
raxmlHPC -m PROTCATLG -F -f D -D -s align.fa -p 23456
```

- The amino acid substitution matrix `LG` can be replaced with other gene-specific matrices.

Optimize branch lengths and compute likelihood score using Gamma in RAxML:

```bash
raxmlHPC -m PROTGAMMALG -f e -s align.fa -t cat.nwk
```

If one or more of the three runs fail due to computational limitation, use IQ-TREE instead for all three:

```bash
iqtree -m LG+G4 -s align.fa -te cat.nwk
```

Among the three trees, keep one with the highest likelihood score.


### 4. Species tree by concatenation

#### 4.1. Site sampling

The 381 gene alignments were concatenated into a supermatrix. To reduce computational cost, and to improve alignment reliability, we performed two types of site sampling:

1. Select up to _k_ most conserved sites per gene, using the [**Trident**](https://doi.org/10.1002/prot.10146) scoring function implemented in PhyloPhlAn.

```python
import phylophlan as ppa
ppa.subsample('path/to/input/folder',
              'path/to/output/folder',
              ppa.onehundred,
              ppa.trident,
              'substitution_matrices/pfasum60.pkl',
              unknown_fraction=0.3)
```

2. Randomly select _k_ sites per gene, from sites with less than 50% gaps.

```python
import phylophlan as ppa
ppa.subsample('path/to/input/folder',
              'path/to/output/folder',
              ppa.onehundred,
              ppa.random_score,
              'substitution_matrices/pfasum60.pkl',
              unknown_fraction=0.3)
```

In the current release, _k_ = 100.


#### 4.2. Tree building

The procedures are overall similar to those used for generating individual gene trees.

Generate a starting tree using FastTree:

```bash
FastTree -lg -gamma -seed 12345 concat.phy > fasttree.nwk
```

Infer topology using CAT in RAxML:

```bash
raxmlHPC -m PROTCATLG -F -f D -s concat.phy -t fasttree.nwk
raxmlHPC -m PROTCATLG -F -f D -s concat.phy -p 12345
raxmlHPC -m PROTCATLG -F -f D -s concat.phy -p 23456
```

Optimize branch lengths and compute likelihood score using Gamma in IQ-TREE:

```bash
iqtree -m LG+G4 -s concat.phy -te raxml.nwk
```

Keep the highest-score tree of the three.


#### 4.3. Branch supports

Branch support values were provided by 100 rapid bootstraps using RAxML:

```bash
raxmlHPC -m PROTCATLG -s concat.phy -p 12345 -x 12345 -N 100
raxmlHPC -m PROTCATLG -f b -z xboot.nwk -t iqtree.nwk
```


### 5. Species tree by summary

We use ASTRAL, which infers the optimal species tree topolgy by summarizing multiple gene trees.


#### 5.1. Tree building

```bash
java -jar astral.jar -i gene.trees -o astral.tre
```


#### 5.2. Branch supports

The output file `astral.tre` reports the following branch support values:

- EN, QC, f1, f2, f3, pp1, pp2, pp3, q1, q2, q3

In which three are cared:

- EN: **Effective number (en): number of gene trees that provided information.
- q1: Quartet score (qts): proportion of gene trees that support this branch.
- pp1: Local posterior probability (lpp): computed based on the quartet score.


#### 5.3. Branch lengths

The branch lengths in `astral.tre` are in units of coalescence. To obtain "conventional" branch lengths, i.e., number of mutations per site, we used the concatenated alignments:

```bash
iqtree -s align.fa -te tree.nwk -keep-ident -m LG+G4 -pre [] -nt 24
```

Please also see [tree manipulation](tree_manipulation).
