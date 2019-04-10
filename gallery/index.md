---
title: "Gallery"
row1:
  - title: "Interactive visualization"
    url: empress.html
    image_path: gallery/headers/empress.png
    excerpt: "Zoom, color, collapse and export in one window. Powered by our new massive tree renderer: **Empress**."
    btn_label: " "
row2:
  - title: "PDF images"
    url: gallery/static
    image_path: gallery/headers/pdf.png
    excerpt: "Pre-rendered high-resolution vector images in multiple layouts and collapsing schemes."
    btn_label: " "
  - title: "iTOL pack"
    url: gallery/itol_pack.tar.bz2
    image_path: gallery/headers/itol.png
    excerpt: "Tree and data files ready for iTOL."
    btn_label: " "
  - title: "FigTree pack"
    url: gallery/figtree.tre.bz2
    image_path: gallery/headers/figtree.png
    excerpt: "Pre-formatted FigTree Nexus file."
    btn_label: " "
---


## Reference tree

ASTRAL tree, with low-support branches contracted. See [details](../data/trees/astral).<br />

{% include feature_row id="row1" type="left" %}

{% include feature_row id="row2" %}


## Alternative trees

Rendering packages (iTOL and FigTree) for [alternative trees](alter) are provided.


## Protocol & code

We provide the [protocol](../protocols/tree_rendering.md) and [source code](../code/notebooks/render_tree.ipynb) for generating and using the rendering packages.

Also check out [Empress](https://github.com/biocore/empress), currently under development.
