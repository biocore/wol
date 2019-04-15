## Genome sampling

### Summary

**Goal**: Select a subset of genomes for phylogenetic inference from all available genomes from NCBI. The selected genomes should contain largest-possible biodiversity.

The biodiversity was estimated using the [MinHash](https://en.wikipedia.org/wiki/MinHash) signatures of genome sequences. The maximization of biodiversity was achieved by using a new algorithm developed by our team to efficiently solve the **prototype selection** problem.

Meanwhile, a series of additional criteria were applied to ensure the quality of selected genomes.

By the time of sampling, there were **86,200** bacterial and archaeal genomes in total. Considering computational efficiency, our goal was to select **~10k** genomes.


### MinHash distance

The MinHash distance between two genomes is defined as the [Jaccard index](https://en.wikipedia.org/wiki/Jaccard_index) of the MinHash sketches of the genome sequences. Simply speaking, it is the **fraction of shared _k_-mers** between the two DNA sequences.

We used [Mash](https://github.com/marbl/mash) 1.1.1 ([Ondov et al., 2016](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-016-0997-x)) with its default setting (_k_ = 21) to compute the MinHash sketch of each genome:

```bash
mash sketch $id.fna
```

Merge sketches and generate a table of pairwise distances:

```bash
mash paste -l all.msh ids.txt
mash dist -p $cpus all.msh all.msh > all.dist
```

We wrote a Python script mash_pair_to_mat.py to convert this file into a distance matrix:

```bash
mash_pair_to_mat.py all.dist > all.dm
```

### Prototype selection

**Prototype selection** is a statistical problem which aims to select a fixed number of elements from a larger population, such that the sum of distances among those elements is maximized.

We designed and implemented a new heuristic solution: `destructive_maxdist`, to this problem. This algorithm is efficient with ~100k's data points, achieves high scores comparing to other (slower) solutions

We provide the Python implementation of this as well as several previous solutions in [code/prototypeSelection](../code/prototypeSelection), with more detailed help information. Here is the example usage:

```python
from skbio.stats.distance import DistanceMatrix
dm = DistanceMatrix.read('all.dm')
k = 10000
prototypes = prototype_selection_destructive_maxdist(dm, k)
```

In addition, our algorithm allows inclusion of "seed" elements (e.g., pre-selected taxa), without losing performance:

```python
seeds = ['G000123456', 'G000654321', ...]
prototypes = prototype_selection_destructive_maxdist(dm, k, seeds)
```

Finally, one can obtain the sum of distances by:

```python
distsum = distance_sum(prototypes, dm)
```

### Full workflow

The following procedures (including prototype selection) were sequentially applied to the original genome pool.

1. Exclude genomes with contamination > 10% or marker gene count < 100.
2. Include NCBI reference and representative genomes.
3. Include only representatives of each phylum to genus.
4. Include only representatives of each species without defined lineage.
5. Run prototype selection based on the MinHash distance matrix, with already included genomes as seeds, to obtain a total of 11000 genomes.
6. For each phylum to genus, and species without defined lineage, select one with highest marker gene count.

This process was automated by [genome_sampling.ipynb](../code/notebooks/genome_sampling.ipynb). It selected 11,079 genomes out of 86,200.
