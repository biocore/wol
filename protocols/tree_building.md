## Tree building

Core protocol of this project. Phylogentic reconstruction of evolutionary relationships of individual gene families and whole genomes.


### 1. Tools

- [**FastTree**](http://www.microbesonline.org/fasttree/) 2.1.9
- [**RAxML**](https://cme.h-its.org/exelixis/web/software/raxml/) 8.2.10
- [**IQ-TREE**](http://www.iqtree.org/) 1.6.1
- [**ASTRAL**](https://github.com/smirarab/ASTRAL) 5.12.6a
- [**UPP**](https://github.com/smirarab/sepp) 2.0
- [**PhyloPhlAn**](http://huttenhower.sph.harvard.edu/phylophlan) commit 2c0e61a
- [**TreeShrink**](https://github.com/uym2/TreeShrink)

Note: the commands listed below have ignored multi-threading parameters and filename-specific parameters.


### 2. Sequence alignment

#### 2.1. Per-gene alignment
UPP was run with all sequences but fragments are used for the backbone. Sequences with length L < 0.34\*M or L > 1.33\*M, where M is the median length of all the sequences, are detected as fragments and not included in the backbone.


```
run_upp.py -s seqfile.fa -B 100000 -M -1 -T 0.66 -m amino
```

After aligned the sequences by UPP, we filter out the gappy **sites** with more than 95% gaps, then filter out the low quality sequences with  more than 66% gaps.

#### 2.2 Gene filtering

We dropped marker genes with more than 75% gaps in the alignment matrix.

This left **381** out of 400 marker genes, and left **10,575** out of 11,079 genomes.


### 3. Gene trees

#### 3.1. Model selection

We used [`ProteinModelSelection.pl`](https://github.com/stamatak/standard-RAxML/blob/master/usefulScripts/ProteinModelSelection.pl) as bundled in RAxML.

#### 3.2. Tree building

Build a starting tree using FastTree:

```
FastTree -lg -gamma -seed 12345 align.fa > fasttree.nwk
```

Remove outliers (low quality sequences, contaminations, etc.) presented as long branches in the tree using TreeShrink:

```
run_treeshrink.py -i input_directory -t fasttree.nwk -a align.fa -o output_directory
```

Infer gene tree topology using CAT in RAxML. Three runs were performed, one with the FastTree tree as the starting tree; the other two with random seeds:

```
raxmlHPC -m PROTCATLG -F -f D -D -s align.fa -t fasttree.nwk
raxmlHPC -m PROTCATLG -F -f D -D -s align.fa -p 12345
raxmlHPC -m PROTCATLG -F -f D -D -s align.fa -p 23456
```

- The amino acid substitution matrix `LG` can be replaced with other gene-specific matrices.

Optimize branch lengths and compute likelihood score using Gamma in RAxML:

```
raxmlHPC -m PROTGAMMALG -f e -s align.fa -t cat.nwk
```

If one or more of the three runs fail due to computational limitation, use IQ-TREE instead for all three:

```
iqtree -m LG+G4 -s align.fa -te cat.nwk
```

Among the three trees, keep one with the highest likelihood score.


### 4. Species tree by concatenation

#### 4.1. Site sampling

The 381 gene alignments were concatenated into a supermatrix. To reduce computational cost, and to improve alignment reliability, we performed two types of site sampling:

1. Select up to _k_ most conserved sites per gene, using the **Trident** algorithm implemented in PhyloPhlAn.

2. Randomly select _k_ sites per gene, from sites with less than 50% gaps.

In the current release, _k_ = 100.

#### 4.2. Tree building

The procedures are overall similar to those used for generating individual gene trees.

Generate a starting tree using FastTree:

```
FastTree -lg -gamma -seed 12345 concat.phy > fasttree.nwk
```

Infer topology using CAT in RAxML:

```
raxmlHPC -m PROTCATLG -F -f D -s concat.phy -t fasttree.nwk
raxmlHPC -m PROTCATLG -F -f D -s concat.phy -p 12345
raxmlHPC -m PROTCATLG -F -f D -s concat.phy -p 23456
```

Optimize branch lengths and compute likelihood score using Gamma in IQ-TREE:

```
iqtree -m LG+G4 -s concat.phy -te raxml.nwk
```

#### 4.3. Branch supports

Branch support values were provided by 100 rapid bootstraps using RAxML:

```
raxmlHPC -m PROTCATLG -s concat.phy -p 12345 -x 12345 -N 100
raxmlHPC -m PROTGAMMALG -f b -z xboot.nwk -t iqtree.nwk
```


### 5. Species tree by summary

We use ASTRAL, which infers the optimal species tree topolgy by summarizing multiple gene trees.

#### 5.1. Tree building

```
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

```
iqtree -s align.fa -te tree.nwk -keep-ident -m LG+G4 -pre [] -nt 24
```

Please also see [tree manipulation](tree_manipulation).
