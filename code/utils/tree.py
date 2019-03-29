#!/usr/bin/env python3

from skbio import TreeNode
from math import isclose
from types import MethodType
from skbio.tree import MissingNodeError


def _extract_support(node, strict=False):
    """Extract the support value from a node label, if available.

    Parameters
    ----------
    node : skbio.TreeNode
        node from which the support value is extracted
    strict : bool (optional)
        whether support value must be a number (default: false)

    Returns
    -------
    tuple of
        int, float or None
            The support value extracted from the node label
        str or None
            The node label with the support value stripped
    """
    support, label = None, None
    if node.name:
        # separate support value from node name by the first colon
        left, _, right = node.name.partition(':')
        try:
            support = int(left)
        except ValueError:
            try:
                support = float(left)
            except ValueError:
                if strict:
                    pass
                else:
                    support = left
        # strip support value from node name
        label = right or None if support is not None else node.name
    return support, label


def get_support(node):
    """Return branch support of a node.

    Parameters
    ----------
    skbio.TreeNode
        node to retrive branch support

    Returns
    -------
    str or None
        branch support if any or None

    Notes
    -----
    scikit-bio 0.5.3+'s TreeNode has a `support` method, which conflicts the
    `support` attribute used in this module. This function is a workaround.
    The `support` method should be renamed in the future.
    """
    return node.support if (
        hasattr(node, 'support') and not isinstance(node.support, MethodType)
        and node.support not in (None, '')) else None


def _node_label(node):
    """Generate a node label in the format of "support:name" if both exist,
    or "support" or "name" if either exists.

    Parameters
    ----------
    skbio.TreeNode
        node containing support value or name

    Returns
    -------
    str
        Generated node label
    """
    parts = []
    if get_support(node) is not None:
        parts.append(str(node.support))
    if node.name not in (None, ''):
        parts.append(node.name)
    return ':'.join(parts) or None


def assign_supports(tree):
    """Extract support values from internal node labels of a tree.

    Parameters
    ----------
    skbio.TreeNode
        tree to assign supports

    Notes
    -----
    A "support value" measures the confidence or frequency of the incoming
    branch (the branch from parent to self) of an internal node in a tree.
    Roots and tips do not have support values. To extract a support value
    from a node label, this method reads from left and stops at the first
    ":" (if any), and attempts to convert it to a number.

    For examples: "(a,b)1.0", "(a,b)1.0:2.5", and "(a,b)'1.0:species_A'".
    In these cases the support values are all 1.0.

    For examples: "(a,b):1.0" and "(a,b)species_A". In these cases there
    are no support values.

    If a support value is successfully extracted, it will be stripped from
    the node label and assigned to the `support` property.

    IMPORTANT: mathematically, "support value" is a property of a branch,
    not a node. Because of historical reasons, support values are usually
    attached to nodes in a typical tree file [1].

    [1] Czech, Lucas, Jaime Huerta-Cepas, and Alexandros Stamatakis. "A
        Critical Review on the Use of Support Values in Tree Viewers and
        Bioinformatics Toolkits." Molecular biology and evolution 34.6
        (2017): 1535-1542.

    Examples
    --------
    >>> from skbio import TreeNode
    >>> newick = "((a,b)95,(c,d):1.1,(e,f)'80:Dmel':1.0);"
    >>> tree = TreeNode.read([newick])
    >>> assign_supports(tree)
    >>> tree.lca(['a', 'b']).support
    95
    >>> tree.lca(['c', 'd']).support is None
    True
    >>> tree.lca(['e', 'f']).support
    80
    >>> tree.lca(['e', 'f']).name
    'Dmel'
    """
    for node in tree.traverse():
        if node.is_root() or node.is_tip():
            node.support = None
        else:
            node.support, node.name = _extract_support(node)


def support_to_label(tree, replace=False):
    """Append support values to node labels.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to append support values
    replace : bool (optional)
        whether to replace the original label

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['((a,b)x,((c,d),(e,f))y);'])
    >>> tree.find('x').support = 100
    >>> tree.find('y').support = 95
    >>> tree.lca([tree.find('c'), tree.find('d')]).support = 80
    >>> support_to_label(tree)
    >>> print(str(tree))
    ((a,b)'100:x',((c,d)80,(e,f))'95:y');
    <BLANKLINE>
    """
    for node in tree.non_tips():
        node.name = str(get_support(node)) if replace else _node_label(node)


def walk_copy(node, src):
    """Directionally and recursively copy a tree node and its neighbors.

    Parameters
    ----------
    node : skbio.TreeNode
        node and its neighbors to be copied
    src : skbio.TreeNode
        an upstream node determining the direction of walking (src -> node)

    Returns
    -------
    skbio.TreeNode
        copied node and its neighbors

    Notes
    -----
    After manipulation, `src` will become the parent of `node`, and all other
    neighbors of `node` will become children of it.

    Unlike scikit-bio's `unrooted_copy` function, this function has special
    treatment at root: For an unrooted tree, its "root" will be retained as a
    regular node; for a rooted tree, its root will be deleted, and all basal
    nodes will become immediate children of the basal node where the source is
    located.

    The function determines whether a tree is rooted or unrooted in such way:
    rooted: root has two children; unrooted: root has one or more than two
    children.

    Logic (pseudocode):
    if node is root:
        if tree is rooted:
            raise error
        else:
            if src in node.children:
                append node.other_child
            else:
                raise error
    elif node is basal (i.e., child of root):
        if tree is rooted:
            if src in node.siblings:
                append node.children
            elif src in node.children:
                append node.sibling and node.other_children
            else:
                raise error
        else:
            if src is node.parent (i.e., root):
                append node.children
            elif src in node.children:
                append node.parent and node.other_children
            else:
                raise error
    else: (i.e., node is derived)
        if src is node.parent:
            append node.children
        elif src in node.children:
            append node.parent and node.other_children
        else:
            raise error

    See Also
    --------
    root_above

    Raises
    ------
    ValueError
        if the input node is already a root or if the input node and input
        source node are not neighbors
    """
    parent = node.parent
    children = node.children

    # position of node
    pos = ('root' if node.is_root() else 'basal' if parent.is_root()
           else 'derived')

    # whether tree is rooted
    root = node if pos == 'root' else node.parent if pos == 'basal' else None
    rooted = None if pos == 'derived' else (
        True if len(root.children) == 2 else False)

    if rooted:
        if pos == 'root':
            raise ValueError('Cannot walk from root of a rooted tree.')
        elif pos == 'basal':
            sibling = [x for x in node.siblings()][0]

    # direction of walking
    move = (('bottom' if src is sibling else 'top' if src in children
            else 'n/a') if rooted and pos == 'basal'
            else ('down' if src is parent else 'up' if src in children
            else 'n/a'))
    if move == 'n/a':
        raise ValueError('Source and node are not neighbors.')

    # create a new node
    res = TreeNode(node.name)

    # determine length of the new node
    res.length = (node.length if move == 'down'
                  else (src.length or node.length
                        if None in (src.length, node.length)
                        else src.length + node.length) if move == 'bottom'
                  else src.length)  # up or top

    # determine support of the new node
    if move in ('down', 'bottom'):
        if get_support(node) is not None:
            res.support = node.support
    elif get_support(src) is not None:
        res.support = src.support

    # append children except for src (if applies)
    res.extend([walk_copy(c, node) for c in children if c is not src])

    # append parent if walking up (except at root)
    if move == 'up' and pos != 'root':
        res.append(walk_copy(parent, node))

    # append sibling if walking from one basal node to another
    if move == 'top':
        res.append(walk_copy(sibling, node))

    return res


def root_above(node, name=None):
    """Re-root a tree between a give node and its parent.

    Parameters
    ----------
    node : skbio.TreeNode
        node above which the new root will be placed
    name : str, optional
        name of the new root

    Returns
    -------
    skbio.TreeNode
        resulting rooted tree

    Notes
    -----
    Unlike scikit-bio's `root_at` function which actually generates an
    unrooted tree, this function generates a rooted tree (the root of
    which has exactly two children).

    See Also
    --------
    unroot_at

    Examples
    --------
    >>> from skbio import TreeNode
    >>> newick = ('(((a:1.0,b:0.8)c:2.4,(d:0.8,e:0.6)f:1.2)g:0.4,'
    ...           '(h:0.5,i:0.7)j:1.8)k;')
    >>> tree = TreeNode.read([newick])
    >>> print(tree.ascii_art())
                                  /-a
                        /c-------|
                       |          \\-b
              /g-------|
             |         |          /-d
             |          \\f-------|
    -k-------|                    \\-e
             |
             |          /-h
              \\j-------|
                        \\-i
    >>> rooted = root_above(tree.find('c'))
    >>> print(str(rooted))
    ((a:1.0,b:0.8)c:1.2,((d:0.8,e:0.6)f:1.2,(h:0.5,i:0.7)j:2.2)g:1.2);
    <BLANKLINE>
    >>> print(rooted.ascii_art())
                        /-a
              /c-------|
             |          \\-b
             |
    ---------|                    /-d
             |          /f-------|
             |         |          \\-e
              \\g-------|
                       |          /-h
                        \\j-------|
                                  \\-i
    """
    # walk down from self node
    left = walk_copy(node, node.parent)

    # walk up from parent node
    right = walk_copy(node.parent, node)

    # set basal branch lengths to be half of the original, i.e., midpoint
    if node.length is not None:
        left.length = right.length = node.length / 2

    # create new root
    res = TreeNode(name, children=[left, right])
    return res


def unroot_at(node):
    """Re-arrange a tree so that it is unrooted, with a given node
    placed at the "root" position.

    Parameters
    ----------
    node : skbio.TreeNode
        node that will be placed at "root"

    Returns
    -------
    skbio.TreeNode
        resulting rooted tree

    Notes
    -----
    Works in a behavior comparable (but not exactly identical) to scikit-bio's
    `root_at` function, plus that it handles branch support values correctly.

    See Also
    --------
    root_above

    Examples
    --------
    >>> from skbio import TreeNode
    >>> newick = ('(((a:1.0,b:0.8)c:2.4,(d:0.8,e:0.6)f:1.2)g:0.4,'
    ...           '(h:0.5,i:0.7)j:1.8)k;')
    >>> tree = TreeNode.read([newick])
    >>> print(tree.ascii_art())
                                  /-a
                        /c-------|
                       |          \\-b
              /g-------|
             |         |          /-d
             |          \\f-------|
    -k-------|                    \\-e
             |
             |          /-h
              \\j-------|
                        \\-i
    >>> unrooted = unroot_at(tree.find('c'))
    >>> print(str(unrooted))
    (((d:0.8,e:0.6)f:1.2,(h:0.5,i:0.7)j:2.2)g:2.4,a:1.0,b:0.8)c;
    <BLANKLINE>
    >>> print(unrooted.ascii_art())
                                  /-d
                        /f-------|
                       |          \\-e
              /g-------|
             |         |          /-h
             |          \\j-------|
    -c-------|                    \\-i
             |
             |--a
             |
              \\-b
    """
    clades = []

    # walk up to parent node
    if not node.is_root():
        clades.append(walk_copy(node.parent, node))

    # walk down to child nodes
    for child in node.children:
        clades.append(walk_copy(child, node))

    # create new root
    res = TreeNode(node.name, children=clades)
    return res


def _exact_compare(tree1, tree2):
    """Simultaneously compares the name, length, and support of each node from
    two trees.

    Parameters
    ----------
    tree1: skbio.TreeNode
        first tree to compare
    tree2: skbio.TreeNode
        second tree to compare

    Returns
    -------
    bool
        `True` if name, length, and support of each corresponding node are same
        `False` otherwise
    """
    for n1, n2 in zip(tree1.postorder(), tree2.postorder()):
        if n1.name != n2.name or n1.length != n2.length:
            return False
        if get_support(n1) != get_support(n2):
            return False
    return True


def _compare_length(node1, node2):
    """Private function for compare_branch_lengths. Determines if lengths of the
    two nodes are same.

    Parameters
    ----------
    node1: skbio.TreeNode
        first node to compare
    node2: skbio.TreeNode
        second node to compare

    Returns
    -------
    bool
        `True` if lengths of the two input nodes are None, same, or close
        `False` otherwise

    See Also
    --------
    compare_branch_length

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(["(a:1,b:1)c;"])
    >>> print(_compare_length(tree.find('a'), tree.find('b')))
    True
    >>> print(_compare_length(tree.find('a'), tree.find('c')))
    False

    """
    if node1.length is None and node2.length is None:
        return True
    elif (node1.length is None) ^ (node2.length is None):
        return False
    elif isclose(node1.length, node2.length) is False:
        return False
    return True


def compare_branch_lengths(tree1, tree2):
    """Returns `True` if each corresponding node in 2 trees has same length.

    Parameters
    ----------
    tree1: skbio.TreeNode
        first tree to compare
    tree2: skbio.TreeNode
        second tree to compare

    Returns
    -------
    bool
        `True` if two input trees have same topologies and branch lengths
        `False` otherwise

    Notes
    -----
    This method compares two unordered trees to check if the two given trees
    have same topology and same branch lengths. The topology check is done by
    postorder traversals of the first tree while `find()` the respective nodes
    in tree 2. Topology of tree2 is determined by storing anchoring nodes in
    stack temporarily.

    See Also
    --------
    compare_topology

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree1 = TreeNode.read(['((a:1, c:1):2, b:1);'])
    >>> tree2 = TreeNode.read(['((a:1, c:1):2, b:1);'])
    >>> print(compare_branch_lengths(tree1, tree2))
    True
    >>> tree3 = TreeNode.read(['((a:1, c:1):2, b);'])
    >>> print(compare_branch_lengths(tree3, tree1))
    False
    """
    stack = []  # stack to store nodes in tree2

    for count, node in enumerate(tree1.postorder(include_self=False)):
        if node.is_tip():
            try:
                cur = tree2.find(node.name)
            except MissingNodeError:
                return False
        else:
            if node.id == stack[-1].id:
                cur = stack.pop()
            else:
                return False

        if _compare_length(node, cur) is False:
            return False
        if node.parent.id is None and cur.parent.id is None:
            cur.parent.id = node.parent.id = str(count)
        elif (node.parent.id is not None) ^ (cur.parent.id is not None):
            return False
        if cur.parent not in stack:
            stack.append(cur.parent)
    return True


def order_nodes(tree, increase=True):
    """Rotate internal nodes of a tree so that child nodes are ordered by the
    number of descendants.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to order
    increase : bool, optional
        order nodes in increasing (True) or decreasing (False) order

    Returns
    -------
    skbio.TreeNode
        resulting ordered tree

    See Also
    --------
    is_ordered

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['(((a,b),(c,d,e)),((f,g),h));'])
    >>> print(tree)
    (((a,b),(c,d,e)),((f,g),h));
    <BLANKLINE>
    >>> ordered = order_nodes(tree, False)
    >>> print(ordered)
    ((h,(f,g)),((a,b),(c,d,e)));
    <BLANKLINE>
    """
    res = tree.copy()
    for node in res.postorder():
        if node.is_tip():
            node.n = 1
        else:
            node.n = sum(x.n for x in node.children)
    for node in res.postorder():
        if not node.is_tip():
            children = node.children
            node.children = []
            for child in sorted(children, key=lambda x: x.n, reverse=increase):
                node.append(child)
    for node in res.postorder():
        delattr(node, 'n')
    return res


def is_ordered(tree, increase=True):
    """Returns `True` if the tree is ordered.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to check ordering
    increase : bool, optional
        check if nodes in increasing (True) or decreasing (False) order

    Returns
    -------
    bool
        `True` if the tree is ordered

    See Also
    --------
    order_nodes

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['((a,b)c,d)e;'])
    >>> print(is_ordered(tree))
    True
    """
    tcopy = tree.copy()
    for node in tcopy.postorder():
        if node.is_tip():
            node.n = 1
        else:
            node.n = sum(x.n for x in node.children)

    p = tcopy.root()
    prev = p.n
    for node in tcopy.levelorder():
        s = [x for x in p.siblings()]
        if node in s:
            cur = node.n
            if prev < cur if increase else prev > cur:
                return False
            prev = cur
        else:
            p = node
            prev = p.n
    return True


def lca2(tree, taxa):
    """Get lowest common ancestor of a taxon set in a tree.

    Parameters
    ----------
    tree : skbio.TreeNode
        query tree
    taxa : set of str
        query taxon set

    Returns
    -------
    skbio.TreeNode
        LCA of query taxon set

    Notes
    -----
    This algorithm achieves the same goal via a different design comparing to
    scikit-bio's `lca` function, which uses a red-black tree strategy. Instead,
    this algorithm relies on pre-assigned taxon sets at each node, and performs
    a preorder recursion from root until it cannot go further. This algorithm
    is significantly more efficient if it is be executed for multiple times.

    For performance consideration, this function does not check whether the
    query taxon set has any invalid taxon. This check, and `assign_taxa`,
    should be done prior to triggering this function.

    Examples
    --------
    >>> from skbio import TreeNode
    >>> newick = '((((a,b)n6,c)n4,(d,e)n5)n2,(f,(g,h)n7)n3,i)n1;'
    >>> tree = TreeNode.read([newick])
    >>> print(tree.ascii_art())
                                            /-a
                                  /n6------|
                        /n4------|          \\-b
                       |         |
              /n2------|          \\-c
             |         |
             |         |          /-d
             |          \\n5------|
             |                    \\-e
             |
    -n1------|          /-f
             |-n3------|
             |         |          /-g
             |          \\n7------|
             |                    \\-h
             |
              \\-i
    >>> assign_taxa(tree)
    >>> lca2(tree, set('ab')).name
    'n6'
    >>> lca2(tree, set('ac')).name
    'n4'
    >>> lca2(tree, set('ae')).name
    'n2'
    >>> lca2(tree, set('ag')).name
    'n1'
    """
    for child in tree.children:
        if taxa.issubset(child.taxa):
            return lca2(child, taxa)
    return tree


def cladistic(tree, taxa):
    """Determines the cladistic property of the given taxon set.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree for taxa comparison
    taxa : iterable of str
        taxon names

    Returns
    -------
    str
        'uni' if input taxon is a single tip in given tree
        'mono' if input taxa are monophyletic in given tree
        'poly' if input taxa are polyphyletic in given tree

    Notes
    -----
    In the following tree example:
                                  /-a
                        /--------|
                       |          \\-b
              /--------|
             |         |          /-c
             |         |         |
             |          \\--------|--d
    ---------|                   |
             |                    \\-e
             |
             |                    /-f
             |          /--------|
              \\--------|          \\-g
                       |
                        \\-h
    ['a'] returns 'uni'
    ['c', 'd', 'e'] returns 'mono'
    ['a', 'c', 'f'] returns 'poly'
    ['f', 'h'] returns 'poly'
    Paraphyly, which is programmably indistinguishable from polyphyly, returns
    poly here.

    Raises
    ------
    ValueError
        if one or more taxon names are not present in the tree

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['((a,b)c,d)e;'])
    >>> print(cladistic(tree, ['a']))
    uni
    >>> print(cladistic(tree, ['a', 'b']))
    mono
    >>> print(cladistic(tree, ['a', 'd']))
    poly
    """
    taxa = set(taxa)
    n = len(taxa)
    if n == 1:
        return 'uni'
    else:
        lca = lca2(tree, taxa) if hasattr(tree, 'taxa') else tree.lca(taxa)
        return 'mono' if lca.count(tips=True) == n else 'poly'


def check_monophyly(tree, taxa):
    """Check whether a taxon set is monophyletic in a tree, considering
    that the LCA node may be polytomic.

    Parameters
    ----------
    tree : skbio.TreeNode
        query tree
    taxa : iterable of str
        query taxon set to test monophyly

    Returns
    -------
    str
        'strict' if taxon set is the entire clade
        'relaxed' if taxon set consists of one or more but not all basal clades
            descending from lca
        'rejected' if neither is satisfied, i.e., in at least one basal clade,
            a portion but not all taxa belong to the taxon set
    skbio.TreeNode
        LCA of query taxon set

    Notes
    -----
    This function is useful in testing the significance a taxon set's monopyly
    is supported or rejected by a tree. One frequent instance is that a taxon
    set is not monophyletic in a tree, but after low-support branches are
    unpacked from the tree, the LCA of this taxon set becomes polytomic, at
    which the monophyly of the taxon set can no longer be rejected. In this
    scenario, this taxon set can be considered as "weakly rejected" [1].

    [1] Sayyari E., Whitfield  J. B. and Mirarab S.. DiscoVista: Interpretable
        visualizations of gene tree discordance." Molecular Phylogenetics and
        Evolution. 2018. 122:110-115.

    Examples
    --------
    >>> from skbio import TreeNode
    >>> newick = '(((a,b),(c,d),(e,f)),(g,(h,i)));'
    >>> tree = TreeNode.read([newick])
    >>> print(tree.ascii_art())
                                  /-a
                        /--------|
                       |          \\-b
                       |
                       |          /-c
              /--------|---------|
             |         |          \\-d
             |         |
             |         |          /-e
    ---------|          \\--------|
             |                    \\-f
             |
             |          /-g
              \\--------|
                       |          /-h
                        \\--------|
                                  \\-i
    >>> check_monophyly(tree, 'a')[0]
    'strict'
    >>> check_monophyly(tree, 'ab')[0]
    'strict'
    >>> check_monophyly(tree, 'abc')[0]
    'rejected'
    >>> check_monophyly(tree, 'abcd')[0]
    'relaxed'
    >>> check_monophyly(tree, 'abcde')[0]
    'rejected'
    >>> check_monophyly(tree, 'abcdef')[0]
    'strict'
    """
    if not hasattr(tree, 'taxa'):
        assign_taxa(tree)
    taxa = set(taxa)
    lca = lca2(tree, taxa)
    if lca.taxa == taxa:
        return 'strict', lca

    # iteratively test each child clade: monophyly is violated if part of clade
    # (not all, not none) is covered by the query taxon set
    left = taxa
    n = len(left)
    for child in lca.children:
        left -= child.taxa
        if 0 < n - len(left) < len(child.taxa):
            return 'rejected', lca
        n = len(left)
    return 'relaxed', lca


def support(node):
    """Get support value of a node.

    Parameters
    ----------
    node : skbio.TreeNode
        node to get support value of

    Returns
    -------
    float or None
        support value of the node, or None if not available

    Notes
    -----
    A "support value" is defined as the numeric form of a whole node label
    without ":", or the part preceding the first ":" in the node label.

    - For examples: "(a,b)1.0", "(a,b)1.0:2.5", and "(a,b)'1.0:species_A'". In
    these cases the support values are all 1.0.

    - For examples: "(a,b):1.0" and "(a,b)species_A". In these cases there are
    no support values.

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['((a,b)99,(c,d):1.0);'])
    >>> support(tree.lca(['a', 'b']))
    99.0
    >>> support(tree.lca(['c', 'd'])) is None
    True
    """
    try:
        return float(node.name.split(':')[0])
    except (ValueError, AttributeError):
        return None


def unpack(node):
    """Unpack an internal node of a tree.

    Parameters
    ----------
    node : skbio.TreeNode
        node to unpack

    Notes
    -----
    This function sequentially: 1) elongates child nodes by branch length of
    self (omit if there is no branch length), 2) removes self from parent node,
    and 3) grafts child nodes to parent node.

    Here is an illustration of the "unpack" operation:
                /----a
          /c---|
         |      \\--b
    -----|
         |        /---d
          \f-----|
                  \\-e

    Unpack node "c" and the tree becomes:
          /---------a
         |
    -----|--------b
         |
         |        /---d
          \f-----|
                  \\-e

    Raises
    ------
    ValueError
        if input node is root

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['((c:2.0,d:3.0)a:1.0,(e:2.0,f:1.0)b:2.0);'])
    >>> unpack(tree.find('b'))
    >>> print(tree)
    ((c:2.0,d:3.0)a:1.0,e:4.0,f:3.0);
    <BLANKLINE>
    """
    if node.is_root():
        raise ValueError('Cannot unpack root.')
    parent = node.parent
    blen = (node.length or 0.0)
    for child in node.children:
        clen = (child.length or 0.0)
        child.length = (clen + blen or None)
    parent.remove(node)
    parent.extend(node.children)


def has_duplicates(tree):
    """Test whether there are duplicated taxa (tip names) in a tree.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree for check for duplicates

    Returns
    -------
    bool
        whether there are duplicates

    Raises
    ------
    ValueError
        if taxon is empty
    """
    taxa = [tip.name for tip in tree.tips()]
    if '' in taxa or None in taxa:
        raise ValueError('Empty taxon name(s) found.')
    return len(set(taxa)) < len(taxa)


def compare_topology(tree1, tree2):
    """Test whether the topologies of two trees with all nodes assigned
    unique IDs are identical.

    Parameters
    ----------
    tree1 : skbio.TreeNode
        first tree in comparison
    tree2 : skbio.TreeNode
        second tree in comparison

    Returns
    -------
    bool
        whether the topologies are identical

    Notes
    -----
    Given all nodes (internal nodes or tips) have unique IDs, one just needs
    to check if all node-to-parent pairs are identical.
    Flipping child nodes does not change topology. Branch lengths are ignored
    when comparing topology.
    """
    n2p1, n2p2 = ({node.name: node.parent.name
                  for node in tree.traverse() if not node.is_root()}
                  for tree in (tree1, tree2))
    return n2p1 == n2p2


def intersect_trees(tree1, tree2):
    """Shrink two trees to contain only overlapping taxa.

    Parameters
    ----------
    tree1 : skbio.TreeNode
        first tree to intersect
    tree2 : skbio.TreeNode
        second tree to intersect

    Returns
    -------
    tuple of two TreeNodes
        resulting trees containing only overlapping taxa
    """
    for tree in (tree1, tree2):
        if has_duplicates(tree):
            raise ValueError('Either tree has duplicated taxa.')
    taxa1 = set([tip.name for tip in tree1.tips()])
    taxa2 = set([tip.name for tip in tree2.tips()])
    taxa_lap = taxa1.intersection(taxa2)
    if len(taxa_lap) == 0:
        raise ValueError('Trees have no overlapping taxa.')
    tree1_lap = tree1.shear(taxa_lap)
    tree2_lap = tree2.shear(taxa_lap)
    return (tree1_lap, tree2_lap)


def unpack_by_func(tree, func):
    """Unpack internal nodes that meet certain criteria.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to search for nodes to unpack
    func : function
        a function that accepts a TreeNode and returns `True` or `False`,
        where `True` indicates the node is to be unpacked

    Returns
    -------
    skbio.TreeNode
        resulting tree with nodes meeting criteria unpacked

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['((c:2,d:3)a:1,(e:1,f:2)b:2);'])
    >>> tree_unpacked = unpack_by_func(tree, lambda x: x.length <= 1)
    >>> print(tree_unpacked)
    ((e:1.0,f:2.0)b:2.0,c:3.0,d:4.0);
    <BLANKLINE>
    >>> tree = TreeNode.read(['(((a,b)85,(c,d)78)75,(e,(f,g)64)80);'])
    >>> tree_unpacked = unpack_by_func(tree, lambda x: support(x) < 75)
    >>> print(tree_unpacked)
    (((a,b)85,(c,d)78)75,(e,f,g)80);
    <BLANKLINE>
    """
    tcopy = tree.copy()
    nodes_to_unpack = []
    for node in tcopy.non_tips():
        if func(node):
            nodes_to_unpack.append(node)
    for node in nodes_to_unpack:
        unpack(node)
    return tcopy


def read_taxdump(nodes_fp, names_fp=None):
    """Read NCBI taxdump.

    Parameters
    ----------
    nodes_fp : str
        file path to NCBI nodes.dmp
    names_fp : str, optional
        file path to NCBI names.dmp

    Returns
    -------
    dict of dict
        taxid : {
            'parent' : str
                parent taxid
            'rank' : str
                taxonomic rank
            'name' : str
                taxon name, empty if names_fp is None
            'children' : set of str
                child taxids
        }
    """
    taxdump = {}

    # format of nodes.dmp: taxid | parent taxid | rank | more info...
    with open(nodes_fp, 'r') as f:
        for line in f:
            x = line.rstrip('\r\n').replace('\t|', '').split('\t')
            taxdump[x[0]] = {'parent': x[1], 'rank': x[2], 'name': '',
                             'children': set()}

    # format of names.dmp: taxid | name | unique name | name class |
    if names_fp is not None:
        with open(names_fp, 'r') as f:
            for line in f:
                x = line.rstrip('\r\n').replace('\t|', '').split('\t')
                if x[3] == 'scientific name':
                    taxdump[x[0]]['name'] = x[1]

    # identify children taxids
    for tid in taxdump:
        pid = taxdump[tid]['parent']
        if tid != pid:  # skip root whose taxid equals its parent
            taxdump[pid]['children'].add(tid)

    return taxdump


def build_taxdump_tree(taxdump):
    """Build NCBI taxdump tree.

    Parameters
    ----------
    taxdump : dict of dict
        attributes of each taxid, see read_taxdump

    Returns
    -------
    skbio.TreeNode
        a tree representing taxdump
    """
    # create the tree from root
    tree = TreeNode('1')

    # iteratively attach child nodes to parent node
    def iter_node(node):
        for cid in taxdump[node.name]['children']:
            child = TreeNode(cid)
            node.extend([child])
            iter_node(child)

    iter_node(tree)
    return tree


#
# the following functions are to be further unit-tested
#

def assign_taxa(tree):
    """Append names of descendants to each node as attribute `taxa`.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to assign taxa

    Notes
    -----
    The notion `taxa` is identical to scikit-bio's `subset`, which is already
    used as a function. The current function generates an attribute which can
    be reused.

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['((a,b),(c,d));'])
    >>> assign_taxa(tree)
    >>> print(sorted(tree.taxa))
    ['a', 'b', 'c', 'd']
    >>> node = tree.lca([tree.find('a'), tree.find('b')])
    >>> print(sorted(node.taxa))
    ['a', 'b']
    """
    for node in tree.postorder(include_self=True):
        if node.is_tip():
            node.taxa = set([node.name])
        else:
            node.taxa = set().union(*[x.taxa for x in node.children])


def match_taxa(tree1, tree2):
    """Generate a list of pairs of nodes in two trees with matching taxa.

    Parameters
    ----------
    tree1 : skbio.TreeNode
        tree 1 for comparison
    tree2 : skbio.TreeNode
        tree 2 for comparison

    Returns
    -------
    list of tuple of (skbio.TreeNode, skbio.TreeNode)

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree1 = TreeNode.read(['((a,b),(c,d));'])
    >>> tree2 = TreeNode.read(['(((a,b),c),d);'])
    >>> matches = match_taxa(tree1, tree2)
    >>> len(matches)
    6
    >>> print([sorted(x[0].taxa) for x in matches])
    [['a'], ['a', 'b'], ['a', 'b', 'c', 'd'], ['b'], ['c'], ['d']]
    """
    t2ns = []
    for tree in (tree1, tree2):
        if not hasattr(tree, 'taxa'):
            assign_taxa(tree)
        t2ns.append({','.join(sorted(x.taxa)): x
                     for x in tree.traverse(include_self=True)})
    res = []
    for taxa in sorted(t2ns[0]):
        if taxa in t2ns[1]:
            res.append((t2ns[0][taxa], t2ns[1][taxa]))
    return res


def match_label(tree1, tree2):
    """Generate a list of pairs of nodes in two trees with matching labels.

    Parameters
    ----------
    tree1 : skbio.TreeNode
        tree 1 for comparison
    tree2 : skbio.TreeNode
        tree 2 for comparison

    Returns
    -------
    list of tuple of (skbio.TreeNode, skbio.TreeNode)

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree1 = TreeNode.read(['((a,b)x,(c,d)y);'])
    >>> tree2 = TreeNode.read(['(((a,b)x,c)y,d);'])
    >>> matches = match_label(tree1, tree2)
    >>> len(matches)
    6
    >>> print([' - '.join([','.join(sorted(node.subset())) for node in pair])
    ...        for pair in matches if not any(node.is_tip() for node in pair)])
    ['a,b - a,b', 'c,d - a,b,c']
    """
    l2ns = []
    for tree in (tree1, tree2):
        l2ns.append({})
        for node in tree.traverse(include_self=True):
            label = node.name
            if label not in (None, ''):
                if label in l2ns[-1]:
                    raise ValueError('Duplicated node label "%s" found.'
                                     % label)
                l2ns[-1][label] = node
    res = []
    for label in sorted(l2ns[0]):
        if label in l2ns[1]:
            res.append((l2ns[0][label], l2ns[1][label]))
    return res


def calc_split_metrics(tree):
    """Calculate split-related metrics.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to calculate metrics

    Notes
    -----
    The following metrics will be calculated for each node:
    - n : int
        number of descendants (tips)
    - splits : int
        total number of splits from tips
    - prelevel : int
        number of nodes from root
    - postlevels : list of int
        numbers of nodes from tips

    These metrics are related to topology but not branch lengths.

    See Also
    --------
    calc_length_metrics

    Examples
    --------
    >>> # Example from Fig. 9a of Puigbo, et al., 2009, J Biol:
    >>> newick = '((((A,B)n9,C)n8,(D,E)n7)n4,((F,G)n6,(H,I)n5)n3,(J,K)n2)n1;'
    >>> tree = TreeNode.read([newick])
    >>> print(tree.ascii_art())
                                            /-A
                                  /n9------|
                        /n8------|          \\-B
                       |         |
              /n4------|          \\-C
             |         |
             |         |          /-D
             |          \\n7------|
             |                    \\-E
             |
             |                    /-F
    -n1------|          /n6------|
             |         |          \\-G
             |-n3------|
             |         |          /-H
             |          \\n5------|
             |                    \\-I
             |
             |          /-J
              \\n2------|
                        \\-K
    >>> calc_split_metrics(tree)
    >>> tree.find('n3').n
    4
    >>> tree.find('n4').splits
    4
    >>> tree.find('n8').postlevels
    [3, 3, 2]
    >>> tree.find('A').prelevel
    5
    """
    # calculate bottom-up metrics
    for node in tree.postorder(include_self=True):
        if node.is_tip():
            node.n = 1
            node.splits = 0
            node.postlevels = [1]
        else:
            children = node.children
            node.n = sum(x.n for x in children)
            node.splits = sum(x.splits for x in children) + 1
            node.postlevels = [y + 1 for x in node.children for y in
                               x.postlevels]

    # calculate top-down metrics
    for node in tree.preorder(include_self=True):
        if node.is_root():
            node.prelevel = 1
        else:
            node.prelevel = node.parent.prelevel + 1


def calc_length_metrics(tree):
    """Calculate branch length-related metrics.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to calculate metrics

    Notes
    -----
    The following metrics will calculated for each node and appended as extra
    attributes in place:
    - height : float
        sum of branch lengths from the root to the node
    - depths : list of float
        sums of branch lengths from all descendants to current node
    - red : float
        relative evolutionary divergence (RED) [1]:

            RED = p + (d / u) * (1 - p)

        where p = RED of parent, d = length, u = depth_mean of parent

    [1] Parks, D. H. et al. A standardized bacterial taxonomy based on genome
        phylogeny substantially revises the tree of life. Nat. Biotechnol. 36,
        996–1004 (2018).

    See Also
    --------
    calc_split_metrics

    Examples
    --------
    >>> # Example from Fig. 1a of Parks et al., 2018, Nat Biotechnol:
    >>> tree = TreeNode.read(['(((A:1,B:1)n3:1,(C:1,D:2)n4:2)n2:2,E:3)n1;'])
    >>> print(tree.ascii_art())
                                  /-A
                        /n3------|
                       |          \\-B
              /n2------|
             |         |          /-C
    -n1------|          \\n4------|
             |                    \\-D
             |
              \\-E
    >>> calc_length_metrics(tree)
    >>> tree.find('n3').height
    3.0
    >>> tree.find('n2').depths
    [2.0, 2.0, 3.0, 4.0]
    >>> round(tree.find('n4').red, 3)
    0.752
    """
    # calculate depths
    for node in tree.postorder(include_self=True):
        if node.length is None:
            node.length = 0.0
        if node.is_tip():
            node.depths = [0.0]
        else:
            node.depths = [y + x.length for x in node.children for y in
                           x.depths]

    # calculate height and RED
    for node in tree.preorder(include_self=True):
        if node.is_root():
            node.height = 0.0
            node.red = 0.0
        else:
            node.height = node.parent.height + node.length
            if node.is_tip():
                node.red = 1.0
            else:
                node.red = node.parent.red + node.length \
                    / (node.length + sum(node.depths) / len(node.depths)) \
                    * (1 - node.parent.red)


#
# the following functions are to be unit-tested
#

def digits(num):
    """Get number of digits after decimal point.

    Parameters
    ----------
    num : str
        string that represents a number

    Returns
    -------
    int
        number of digits after decimal point
    """
    if not num.replace('.', '').isdigit() or num.count('.') != 1:
        raise ValueError('Not a valid float number: %s' % num)
    return len(num.split('.')[1])


def branch_length_digits(tree):
    """Get maximum number of digits of all branch lengths.

    Parameters
    ----------
    tree : skbio.TreeNode
        input tree

    Returns
    -------
    tuple of (int, int)
        maximum numbers of digits for float point and scientific notation
    """
    max_f, max_e = 0, 0
    for node in tree.traverse():
        if node.length is not None:
            x = str(float(node.length))
            if 'e' in x:
                max_e = max(max_e, digits(str(float(x.split('e')[0]))))
            else:
                max_f = max(max_f, digits(x))
    return (max_f, max_e)


def format_newick(tree, keep_space=False, max_f=None, max_e=None):
    """Generate a Newick string from a tree.

    Parameters
    ----------
    tree : skbio.TreeNode
        input tree
    keep_space : bool
        keep spaces (true) or convert spaces to underscores (false)
    max_f : int or None
        maximum number of digits for float point
    max_e : int or None
        maximum number of digits for scientific notation

    Returns
    -------
    str
        Newick string

    Notes
    -----
    Modified from scikit-bio's `_tree_node_to_newick` function, added some
    flavors.
    """
    res = ''
    operators = set(',:_;()[]')
    if keep_space:
        operators.add(' ')
    current_depth = 0
    nodes_left = [(tree, 0)]
    while len(nodes_left) > 0:
        entry = nodes_left.pop()
        node, node_depth = entry
        if node.children and node_depth >= current_depth:
            res += '('
            nodes_left.append(entry)
            nodes_left += ((child, node_depth + 1) for child in
                           reversed(node.children))
            current_depth = node_depth + 1
        else:
            if node_depth < current_depth:
                res += ')'
                current_depth -= 1
            if node.name:
                escaped = node.name.replace('\'', '\'\'')
                if any(t in operators for t in node.name):
                    res += '\'%s\'' % escaped
                else:
                    res += (escaped if keep_space
                            else escaped.replace(' ', '_'))
            if node.length is not None:
                length = node.length
                if 'e' in str(length):
                    if max_e is not None:
                        length = '%.*g' % (max_e, length)
                elif max_f is not None:
                    length = '%.*g' % (max_f, length)
                res += ':%s' % length
            if nodes_left and nodes_left[-1][1] == current_depth:
                res += ','
    res += ';'
    return res


def root_by_outgroup(tree, outgroup, strict=False, unroot=False):
    """Root a tree with a given set of taxa as outgroup.

    Parameters
    ----------
    tree : skbio.TreeNode
        tree to root
    outgroup : list of str
        list of taxa to be set as outgroup
    strict : bool (optional)
        outgroup must be a subset of tree taxa (default: false)
    unroot : bool (optional)
        result is an unrooted tree (thus "root" has three child clades)
        (default: false)

    Returns
    -------
    skbio.TreeNode
        resulting rooted tree

    See Also
    --------
    root_above

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['((((a,b),(c,d)),(e,f)),g);'])
    >>> print(tree.ascii_art())
                                            /-a
                                  /--------|
                                 |          \\-b
                        /--------|
                       |         |          /-c
                       |          \\--------|
              /--------|                    \\-d
             |         |
             |         |          /-e
    ---------|          \\--------|
             |                    \\-f
             |
              \\-g
    >>> rooted = root_by_outgroup(tree, outgroup=['a', 'b'])
    >>> print(rooted.ascii_art())
                        /-a
              /--------|
             |          \\-b
             |
    ---------|                    /-c
             |          /--------|
             |         |          \\-d
              \\--------|
                       |                    /-e
                       |          /--------|
                        \\--------|          \\-f
                                 |
                                  \\-g
    >>> rooted = root_by_outgroup(tree, outgroup=['e', 'f', 'g'])
    >>> print(rooted.ascii_art())
                                  /-e
                        /--------|
              /--------|          \\-f
             |         |
             |          \\-g
    ---------|
             |                    /-c
             |          /--------|
             |         |          \\-d
              \\--------|
                       |          /-b
                        \\--------|
                                  \\-a
    >>> unrooted = root_by_outgroup(tree, outgroup=['a', 'b'], unroot=True)
    >>> print(unrooted.ascii_art())
                                  /-e
                        /--------|
              /--------|          \\-f
             |         |
             |          \\-g
             |
    ---------|          /-a
             |---------|
             |          \\-b
             |
             |          /-c
              \\--------|
                        \\-d
    """
    # select taxa that are present in tree
    og = set(outgroup).intersection(tree.subset())

    n = len(og)
    if strict and n < len(outgroup):
        raise ValueError('Outgroup is not a subset of tree taxa.')
    if n == 0:
        raise ValueError('None of outgroup taxa are present in tree.')
    if n == tree.count(tips=True):
        raise ValueError('Outgroup constitutes the entire tree.')

    # create new tree
    res = tree.copy()

    # locate lowest common ancestor (LCA) of outgroup in the target tree
    lca = res.lca(og) if n > 1 else res.find(max(og))

    # if LCA is root rather than derived (i.e., outgroup is split across basal
    # clades), swap the tree and locate LCA again
    if lca is res:
        for tip in tree.tips():
            if tip.name not in og:
                res = unroot_at(tip.parent) if unroot else root_above(tip)
                break
        lca = res.lca(og)

    # test monophyly
    if lca.count(tips=True) > n:
        raise ValueError('Outgroup is not monophyletic in tree.')

    # re-root target tree between LCA of outgroup and LCA of ingroup
    return unroot_at(lca.parent) if unroot else root_above(lca)


def restore_rooting(source, target):
    """Restore rooting scenario in an unrooted tree based on a rooted tree.

    Parameters
    ----------
    source : skbio.TreeNode
        source tree from which rooting to be read
    target : skbio.TreeNode
        target tree to which rooting to be set

    Returns
    -------
    skbio.TreeNode
        tree with rooting scenario restored

    Notes
    -----
    Source tree can be rooted ("root" has two children) or unrooted ("root")
    has three children. In either case the rooting scenario will be restored.

    Examples
    --------
    >>> from skbio import TreeNode
    >>> source = TreeNode.read(['(((e,f),g),((c,d),(b,a)));'])
    >>> print(source.ascii_art())
                                  /-e
                        /--------|
              /--------|          \\-f
             |         |
             |          \\-g
    ---------|
             |                    /-c
             |          /--------|
             |         |          \\-d
              \\--------|
                       |          /-b
                        \\--------|
                                  \\-a
    >>> target = TreeNode.read(['(((a,b)95,(c,d)90)80,(e,f)100,g);'])
    >>> print(target.ascii_art())
                                  /-a
                        /95------|
                       |          \\-b
              /80------|
             |         |          /-c
             |          \\90------|
             |                    \\-d
    ---------|
             |          /-e
             |-100-----|
             |          \\-f
             |
              \\-g
    >>> assign_supports(target)
    >>> rooted = restore_rooting(source, target)
    >>> support_to_label(rooted)
    >>> print(rooted.ascii_art())
                                  /-e
                        /100-----|
              /80------|          \\-f
             |         |
             |          \\-g
    ---------|
             |                    /-c
             |          /90------|
             |         |          \\-d
              \\80------|
                       |          /-b
                        \\95------|
                                  \\-a
    """
    if source.subset() != target.subset():
        raise ValueError('Source and target trees have different taxa.')
    counts = {x: x.count(tips=True) for x in source.children}
    fewer = min(counts, key=counts.get)
    outgroup = (set([fewer.name]) if fewer.is_tip()
                else set(x.name for x in fewer.tips()))
    return root_by_outgroup(target, outgroup, strict=True,
                            unroot=(len(counts) > 2))


def restore_node_labels(source, target):
    """Restore internal node labels in one tree based on another tree.

    Parameters
    ----------
    source : skbio.TreeNode
        source tree from which internal node labels to be read
    target : skbio.TreeNode
        target tree to which internal node labels to be written

    Returns
    -------
    skbio.TreeNode
        resulting tree with internal node labels added

    Notes
    -----
    Labels are assigned based on exact match of all descending taxa. Taxa in
    the source and target trees do not have to be identical. Original labels
    in the target tree, if any, will be overwritten.

    Examples
    --------
    >>> from skbio import TreeNode
    >>> source = TreeNode.read(['(((a,b)85,c)90,((d,e)98,(f,g)93));'])
    >>> target = TreeNode.read(['((((g,f),(e,d))x,(c,(a,b))y),h);'])
    >>> labeled = restore_node_labels(source, target)
    >>> print(str(labeled))
    ((((g,f)93,(e,d)98)x,(c,(a,b)85)90),h);
    <BLANKLINE>
    """
    # assign taxa to internal nodes
    for tree in (source, target):
        if not hasattr(tree, 'taxa'):
            assign_taxa(tree)

    # read descendants under each node label in source tree
    label2taxa = {}
    for node in source.non_tips(include_self=True):
        label = node.name
        if label is not None and label != '':
            if label in label2taxa:
                raise ValueError('Duplicated node label "%s" found.' % label)
            label2taxa[label] = ','.join(sorted(node.taxa))
    taxa2label = {v: k for k, v in label2taxa.items()}

    # identify and mark matching nodes per node label in target tree
    res = target.copy()
    for node in res.non_tips(include_self=True):
        taxa = ','.join(sorted(node.taxa))
        if taxa in taxa2label:
            node.name = taxa2label[taxa]

    return res


def restore_node_order(source, target):
    """Restore ordering of nodes in one tree based on another tree.

    Parameters
    ----------
    source : skbio.TreeNode
        source tree from which node ordering to be read
    target : skbio.TreeNode
        target tree to which nodes to be re-ordered accordingly

    Returns
    -------
    skbio.TreeNode
        resulting tree with nodes re-ordered

    Examples
    --------
    >>> from skbio import TreeNode
    >>> source = TreeNode.read(['(((a,b),(c,d)),((e,f),g));'])
    >>> target = TreeNode.read(['((g,(e,f)100),((d,c)80,(a,b)90));'])
    >>> ordered = restore_node_order(source, target)
    >>> print(str(ordered))
    (((a,b)90,(c,d)80),((e,f)100,g));
    <BLANKLINE>
    """
    n = source.count()
    if n != target.count():
        raise ValueError('Two trees have different sizes.')

    # find matching nodes
    matches = match_taxa(source, target)
    if n != len(matches):
        raise ValueError('Two trees have different topologies.')

    def taxastr(node):
        return ','.join(sorted(node.taxa))

    taxa2src = {taxastr(x[0]): x[0] for x in matches
                if not x[0].is_tip()}

    # re-order child nodes under each internal node
    res = target.copy()
    for node in res.non_tips(include_self=True):
        src_node = taxa2src[taxastr(node)]
        taxa2child = {}
        for child in node.children:
            taxa2child[taxastr(child)] = child
        node.children = []
        for child in src_node.children:
            node.append(taxa2child[taxastr(child)])

    return res


def get_base(node):
    """Return current node's basal node in tree

    Parameters
    ----------
    node : skbio.TreeNode
        query node

    Returns
    -------
    skbio.TreeNode
        basal node of query node

    Notes
    -----
    A "basal" node is defined as a child node of root.

    See Also
    --------
    scikit-bio's `root` function

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['(((a,b)n6,(c,d)n5)n3,((e,f)n4,g)n2)n1;'])
    >>> node = tree.find('a')
    >>> print(get_base(node).name)
    n3
    """
    if node.is_root():
        raise ValueError('Root has no base.')
    cnode = node
    while True:
        pnode = cnode.parent
        if pnode.is_root():
            break
        cnode = pnode
    return cnode


def calc_bidi_minlevels(tree):
    """Calculate minimum levels of nodes to tree's surface from both
    post- and pre-directions.

    Parameters
    ----------
    node : skbio.TreeNode
        query node

    Notes
    -----
    A new attribute will be appended to each internal node:
    - minlevel : int
        minimum level of current node to tree's surface

    Will execute calc_split_metrics if not already.

    See Also
    --------
    calc_split_metrics

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['(((a,b)n4,(c,d)n5)n2,(((e,f)n8,(g,h)n9)n6,'
    ...                       '((i,j)n10,(k,l)n11)n7)n3,m)n1;'])
    >>> print(tree.ascii_art())
                                  /-a
                        /n4------|
                       |          \\-b
              /n2------|
             |         |          /-c
             |          \\n5------|
             |                    \\-d
             |
             |                              /-e
             |                    /n8------|
             |                   |          \\-f
             |          /n6------|
             |         |         |          /-g
    -n1------|         |          \\n9------|
             |         |                    \\-h
             |-n3------|
             |         |                    /-i
             |         |          /n10-----|
             |         |         |          \\-j
             |          \\n7------|
             |                   |          /-k
             |                    \\n11-----|
             |                              \\-l
             |
              \\-m
    >>> calc_bidi_minlevels(tree)
    >>> # minlevel of n4 is 2 (a-n4)
    >>> tree.find('n4').minlevel
    2
    >>> # minlevel of n6 is 3 (e-n8-n6)
    >>> tree.find('n6').minlevel
    3
    >>> # minlevel of n3 is 3 (m-n1-n3) rather than 4 (e-n8-n6-n3)
    >>> tree.find('n3').minlevel
    3
    """
    # check if tree is unrooted (if yes, "root" accounts for one node)
    unrooted = int(len(tree.children) != 2)

    # execute calc_split_metrics if not yet
    if not hasattr(tree, 'postlevels'):
        calc_split_metrics(tree)

    # root's minlevel is the min of all descendants (single direction)
    tree.minlevel = min(tree.postlevels)

    # internal node's minlevel is the min of post- and pre-direction
    for node in tree.preorder(include_self=False):

        # tips are already at surface, so minlevel = 1
        if node.is_tip():
            node.minlevel = 1
            continue

        # basal nodes: compare siblings, consider (un)rooting
        if node.parent.is_root():
            node.minlevel_above = 1 + unrooted + \
                min(min(x.postlevels) for x in tree.children if x is not node)

        # derived nodes: increment from parent
        else:
            node.minlevel_above = node.parent.minlevel_above + 1

        # minimum level of post- and pre-direction levels
        node.minlevel = min(node.minlevel_above, min(node.postlevels))

    # clean up
    for node in tree.non_tips(include_self=False):
        delattr(node, 'minlevel_above')


def calc_bidi_mindepths(tree):
    """Calculate minimum depths of nodes to tree's surface from both
    post- and pre-directions.

    Parameters
    ----------
    node : skbio.TreeNode
        query node

    Notes
    -----
    A new attribute will be appended to each internal node:
    - mindepth : float
        minimum depth of current node to tree's surface

    Will execute calc_length_metrics if not already.

    See Also
    --------
    calc_length_metrics

    Examples
    --------
    >>> from skbio import TreeNode
    >>> tree = TreeNode.read(['(((a:0.5,b:0.7)n5:1.1,c:1.7)n2:0.3,((d:0.8,'
    ...                       'e:0.6)n6:0.9,(f:1.2,g:0.5)n7:0.8)n3:1.3,'
    ...                       '(h:0.4,i:0.3)n4:0.9)n1;'])
    >>> print(tree.ascii_art())
                                  /-a
                        /n5------|
              /n2------|          \\-b
             |         |
             |          \\-c
             |
             |                    /-d
             |          /n6------|
    -n1------|         |          \\-e
             |-n3------|
             |         |          /-f
             |          \\n7------|
             |                    \\-g
             |
             |          /-h
              \\n4------|
                        \\-i
    >>> calc_bidi_mindepths(tree)
    >>> # mindepth of n5 is 0.5 (a-0.5-n5)
    >>> tree.find('n5').mindepth
    0.5
    >>> # mindepth of n3 is 1.3 (g-0.5-n7-0.8-n3)
    >>> tree.find('n3').mindepth
    1.3
    >>> # mindepth of n2 is 1.5 (i-0.3-n4-0.9-n1-0.3-n2) instead of
    >>> # 1.7 (c-1.7-n2)
    >>> tree.find('n2').mindepth
    1.5
    """
    if not hasattr(tree, 'depths'):
        calc_length_metrics(tree)
    tree.mindepth = min(tree.depths)
    for node in tree.preorder(include_self=False):
        if node.is_tip():
            node.mindepth = 0.0
            continue
        if node.parent.is_root():
            node.mindepth_above = node.length + \
                min(min(x.depths) + x.length for x in tree.children
                    if x is not node)
        else:
            node.mindepth_above = node.parent.mindepth_above + node.length
        node.mindepth = min(node.mindepth_above, min(node.depths))
    for base in tree.non_tips(include_self=False):
        delattr(base, 'mindepth_above')
