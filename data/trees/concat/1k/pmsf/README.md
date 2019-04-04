# PMSF trees

These trees were built using the posterior mean site frequency (**PMSF**) method ([Wang et al., 2018](https://academic.oup.com/sysbio/article/67/2/216/4076233)) implemented in [IQ-TREE](http://www.iqtree.org/). It uses the empirical profile mixture model C60 ([Quang et al., 2008](https://academic.oup.com/bioinformatics/article/24/20/2317/260174)) to account for amino acid substitution rate heterogeneity across sites. It is more robust to long-branch attraction (LBA) than site homogeneous models.

Branch supports were generated using ultrafast bootstrap (**ufboot**) ([Hoang et al., 2018](https://academic.oup.com/mbe/article/35/2/518/4565479)), with 1000 replicates (downscaled to integers between 0-100).

Also comes in **cons** (using up to 100 conserved sites per gene), **rand** (using 100 randomly selected sites per gene) and **rpls** (using 30 ribosomal proteins) variants.

Go to [GitHub directory](https://github.com/biocore/wol/tree/master/data/trees/concat/1k/pmsf).
