Code
====

The programs developed during the project are hosted in this project. Each program file contains instruction for users and/or developers. Use cases of individual programs are introduced in **Protocols**.

No installation is required. The scripts and notebooks should work out-of-the-box, with or without a few common dependencies. To simplify usage, we recommend using **conda** to create a virtual Python environment to host dependencies:

```
conda create -n wol -c conda-forge python=3 scikit-bio scikit-learn seaborn
source activate wol
```

- [**scripts**](scripts): Python scripts.

- [**notebooks**](notebooks): Jupyter Notebooks.

- [**utils**](utils): Python modules used by scripts and notebooks.

- [**prototypeSelection**](prototypeSelection): Algorithms for "prototype selection", a statistical process that is central to the genome sampling process of this project.

Some utilities developed during this work have been merged into the latest releases of [scikit-bio](http://scikit-bio.org/), an integrated Python package for bioinformatics.
