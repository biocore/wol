---
title: "PDF images"
row1:
  - title: "Main image"
    url: gallery/main.pdf
    image_path: gallery/logo/logo_s.png
row2:
  - url: gallery/ranks/order.pdf
    image_path: gallery/ranks/order.jpg
  - url: gallery/ranks/family.pdf
    image_path: gallery/ranks/family.jpg
  - url: gallery/ranks/genus.pdf
    image_path: gallery/ranks/genus.jpg
row3:
  - url: gallery/layouts/unrooted.shadow.pdf
    image_path: gallery/layouts/unrooted.shadow.jpg
  - url: gallery/layouts/unrooted.branch.pdf
    image_path: gallery/layouts/unrooted.branch.jpg
  - url: gallery/layouts/collapsed.unrooted.isotriangle.pdf
    image_path: gallery/layouts/collapsed.unrooted.isotriangle.jpg
  - url: gallery/layouts/collapsed.circular.branch.pdf
    image_path: gallery/layouts/collapsed.circular.branch.jpg
  - url: gallery/layouts/circular.shadow.pdf
    image_path: gallery/layouts/circular.shadow.jpg
  - url: gallery/layouts/collapsed.circular.shadow.pdf
    image_path: gallery/layouts/collapsed.circular.shadow.jpg
---

## Main figure

{% include gallery id="row1" layout="" %}

**Technical details**: ASTRAL tree (`astral`) with branch lengths estimated using the conserved alignment (`cons`), and with low-support branches contracted (`e5p50`), collapsed to classes with 10 or more taxa, or phyla with at least one taxon, following NCBI taxonomy curated using tax2tree. [More details...](../../protocols/tree_rendering)



## More ranks 

{% include gallery id="row2" layout="third" %}


## More layouts

{% include gallery id="row3" layout="third" %}

These are alternative renderings of the reference tree. You may see value in them for scientific observations. But above all, we provided them for aethetics.
