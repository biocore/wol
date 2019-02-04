#!/usr/bin/env python3

from skbio import TreeNode
from math import isclose
from skbio.tree import MissingNodeError


def _extract_support(node):
    """Extract the support value from a node label, if available.

    Parameters
    ----------
    skbio.TreeNode
        node from which the support value is extracted

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
                pass
        # strip support value from node name
        label = right or None if support is not None else node.name
    return support, label


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
    lblst = []

    if node.support is not None:  # prevents support of NoneType
        lblst.append(str(node.support))
    if node.name:  # prevents name of NoneType
        lblst.append(node.name)

    return ':'.join(lblst)


def assign_supports(tree):
    """Extract support values from internal node labels of a tree.

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
    >>> newick = "((a,b)95,(c,d):1.1,(e,f)'80:speciesA':1.0);"
    >>> tree = TreeNode.read([newick])
    >>> assign_supports(tree)
    >>> tree.lca(['a', 'b']).support
    95
    >>> tree.lca(['c', 'd']).support is None
    True
    >>> tree.lca(['e', 'f']).support
    80
    >>> tree.lca(['e', 'f']).name
    'speciesA'
    """
    for node in tree.traverse():
        if node.is_root() or node.is_tip():
            node.support = None
        else:
            node.support, node.name = _extract_support(node)


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
                  else src.length + node.length if move == 'bottom'
                  else src.length)  # up or top

    # determine support of the new node
    res.support = (node.support if move in ('down', 'bottom')
                   else src.support)

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
    """
    # walk down from self node
    left = walk_copy(node, node.parent)

    # walk up from parent node
    right = walk_copy(node.parent, node)

    # set basal branch lengths to be half of the original, i.e., midpoint
    left.length = right.length = node.length / 2

    # create new root
    res = TreeNode(name, children=[left, right])
    res.support = None
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
    attrs = ['name', 'length', 'support']
    for n1, n2 in zip(tree1.postorder(), tree2.postorder()):
        for attr in attrs:
            if getattr(n1, attr, None) != getattr(n2, attr, None):
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
    >>> tree_ordered = order_nodes(tree, False)
    >>> print(tree_ordered)
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
                       |          \-b
              /--------|
             |         |          /-c
             |         |         |
             |          \--------|--d
    ---------|                   |
             |                    \-e
             |
             |                    /-f
             |          /--------|
              \--------|          \-g
                       |
                        \-h
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
    tips = []
    taxa = set(taxa)
    for tip in tree.tips():
        if tip.name in taxa:
            tips.append(tip)
    n = len(taxa)
    if len(tips) < n:
        raise ValueError('Taxa not found in the tree.')
    return ('uni' if n == 1 else
            ('mono' if len(tree.lca(tips).subset()) == n else
             'poly'))


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
         |      \--b
    -----|
         |        /---d
          \f-----|
                  \-e

    Unpack node "c" and the tree becomes:
          /---------a
         |
    -----|--------b
         |
         |        /---d
          \f-----|
                  \-e

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
