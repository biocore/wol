#!/usr/bin/env python3

from unittest import TestCase, main
from shutil import rmtree
from tempfile import mkdtemp
from os.path import join, dirname, realpath
from skbio import TreeNode

from utils.tree import (
    support, unpack, has_duplicates, compare_topology, intersect_trees,
    unpack_by_func, read_taxdump, build_taxdump_tree, order_nodes,
    is_ordered, cladistic, _compare_length, compare_branch_lengths,
    assign_supports, support_to_label, walk_copy, root_above, unroot_at,
    _exact_compare, calc_split_metrics, calc_length_metrics, format_newick,
    root_by_outgroup, restore_rooting, restore_node_labels,
    restore_node_order, get_base, calc_bidi_minlevels, calc_bidi_mindepths)


class TreeTests(TestCase):

    def setUp(self):
        """ Set up working directory and test files
        """
        # test output can be written to this directory
        self.working_dir = mkdtemp()

        # test data directory
        datadir = join(dirname(realpath(__file__)), 'data')

        # test data files
        self.nodes_fp = join(datadir, 'nodes.dmp')
        self.names_fp = join(datadir, 'names.dmp')

    def tearDown(self):
        # there isn't any file to remove at the moment
        # but in the future there will be
        rmtree(self.working_dir)

    def test_support(self):
        """Test getting support value of a node."""
        # test nodes with support alone as label
        tree = TreeNode.read(['((a,b)75,(c,d)90);'])
        node1, node2 = tree.children
        self.assertEqual(support(node1), 75.0)
        self.assertEqual(support(node2), 90.0)

        # test nodes with support and branch length
        tree = TreeNode.read(['((a,b)0.85:1.23,(c,d)0.95:4.56);'])
        node1, node2 = tree.children
        self.assertEqual(support(node1), 0.85)
        self.assertEqual(support(node2), 0.95)

        # test nodes with support and extra label (not a common scenario but
        # can happen)
        tree = TreeNode.read(['((a,b)\'80:X\',(c,d)\'60:Y\');'])
        node1, node2 = tree.children
        self.assertEqual(support(node1), 80.0)
        self.assertEqual(support(node2), 60.0)

        # test nodes without label, with non-numeric label, and with branch
        # length only
        tree = TreeNode.read(['((a,b),(c,d)x,(e,f):1.0);'])
        for node in tree.children:
            self.assertIsNone(support(node))

    def test_unpack(self):
        """Test unpacking an internal node."""
        # test unpacking a node without branch length
        tree = TreeNode.read(['((c,d)a,(e,f)b);'])
        unpack(tree.find('b'))
        exp = '((c,d)a,e,f);\n'
        self.assertEqual(str(tree), exp)

        # test unpacking a node with branch length
        tree = TreeNode.read(['((c:2.0,d:3.0)a:1.0,(e:2.0,f:1.0)b:2.0);'])
        unpack(tree.find('b'))
        exp = '((c:2.0,d:3.0)a:1.0,e:4.0,f:3.0);'
        self.assertEqual(str(tree).rstrip(), exp)

        # test attempting to unpack root
        tree = TreeNode.read(['((d,e)b,(f,g)c)a;'])
        msg = 'Cannot unpack root.'
        with self.assertRaisesRegex(ValueError, msg):
            unpack(tree.find('a'))

    def test_has_duplicates(self):
        """Test checking for duplicated taxa."""
        # test tree without duplicates
        tree = TreeNode.read(['((a,b),(c,d));'])
        obs = has_duplicates(tree)
        self.assertFalse(obs)

        # test tree with duplicates
        tree = TreeNode.read(['((a,a),(c,a));'])
        obs = has_duplicates(tree)
        self.assertTrue(obs)

        tree = TreeNode.read(['((1,(2,x)),4,(5,(6,x,8)));'])
        obs = has_duplicates(tree)
        self.assertTrue(obs)

        # test tree with empty taxon names (not a common scenario but can
        # happen)
        tree = TreeNode.read(['((1,(2,,)),4,(5,(6,,8)));'])
        msg = 'Empty taxon name\(s\) found.'
        with self.assertRaisesRegex(ValueError, msg):
            has_duplicates(tree)

    def test_compare_topology(self):
        """Test comparing topologies of two trees."""
        # test identical Newick strings
        tree1 = TreeNode.read(['(a,b)c;'])
        tree2 = TreeNode.read(['(a,b)c;'])
        obs = compare_topology(tree1, tree2)
        self.assertTrue(obs)

        # test identical topologies with different branch lengths
        tree1 = TreeNode.read(['(a:1,b:2)c:3;'])
        tree2 = TreeNode.read(['(a:3,b:2)c:1;'])
        obs = compare_topology(tree1, tree2)
        self.assertTrue(obs)

        # test identical topologies with flipped child nodes
        tree1 = TreeNode.read(['(a,b)c;'])
        tree2 = TreeNode.read(['(b,a)c;'])
        obs = compare_topology(tree1, tree2)
        self.assertTrue(obs)

        tree1 = TreeNode.read(['((4,5)2,(6,7,8)3)1;'])
        tree2 = TreeNode.read(['((8,7,6)3,(5,4)2)1;'])
        obs = compare_topology(tree1, tree2)
        self.assertTrue(obs)

        tree1 = TreeNode.read(['(((9,10)4,(11,12,13)5)2,((14)6,(15,16,17,18)7,'
                               '(19,20)8)3)1;'])
        tree2 = TreeNode.read(['(((15,16,17,18)7,(14)6,(20,19)8)3,((12,13,11)5'
                               ',(10,9)4)2)1;'])
        obs = compare_topology(tree1, tree2)
        self.assertTrue(obs)

        # test different topologies
        tree1 = TreeNode.read(['(a,b)c;'])
        tree2 = TreeNode.read(['(a,c)b;'])
        obs = compare_topology(tree1, tree2)
        self.assertFalse(obs)

        tree1 = TreeNode.read(['((4,5)2,(6,7,8)3)1;'])
        tree2 = TreeNode.read(['((4,5)3,(6,7,8)2)1;'])
        obs = compare_topology(tree1, tree2)
        self.assertFalse(obs)

        tree1 = TreeNode.read(['((4,5)2,(6,7,8)3)1;'])
        tree2 = TreeNode.read(['(((4,1)8)7,(6,3)2)5;'])
        obs = compare_topology(tree1, tree2)
        self.assertFalse(obs)

    def test_intersect_trees(self):
        """Test intersecting two trees."""
        # test trees with identical taxa
        tree1 = TreeNode.read(['((a,b),(c,d));'])
        tree2 = TreeNode.read(['(a,(b,c,d));'])
        obs = intersect_trees(tree1, tree2)
        exp = (tree1, tree2)
        for i in range(2):
            self.assertEqual(obs[i].compare_subsets(exp[i]), 0.0)

        # test trees with partially different taxa
        tree1 = TreeNode.read(['((a,b),(c,d));'])
        tree2 = TreeNode.read(['((a,b),(c,e));'])
        obs = intersect_trees(tree1, tree2)
        tree1_lap = TreeNode.read(['((a,b),c);'])
        tree2_lap = TreeNode.read(['((a,b),e);'])
        exp = (tree1_lap, tree2_lap)
        for i in range(2):
            self.assertEqual(obs[i].compare_subsets(exp[i]), 0.0)

        tree1 = TreeNode.read(['(((a,b),(c,d)),((e,f,g),h));'])
        tree2 = TreeNode.read(['(a,((b,x),(d,y,(f,g,h))));'])
        obs = intersect_trees(tree1, tree2)
        tree1_lap = TreeNode.read(['(((a,b),d),((f,g),h));'])
        tree2_lap = TreeNode.read(['(a,(b,(d,(f,g,h))));'])
        exp = (tree1_lap, tree2_lap)
        for i in range(2):
            self.assertEqual(obs[i].compare_subsets(exp[i]), 0.0)

        # test trees with completely different taxa
        tree1 = TreeNode.read(['((a,b),(c,d));'])
        tree2 = TreeNode.read(['((e,f),(g,h));'])
        msg = 'Trees have no overlapping taxa.'
        with self.assertRaisesRegex(ValueError, msg):
            intersect_trees(tree1, tree2)

        # test trees with duplicated taxa
        tree1 = TreeNode.read(['((a,b),(c,d));'])
        tree2 = TreeNode.read(['((a,a),(b,c));'])
        msg = 'Either tree has duplicated taxa.'
        with self.assertRaisesRegex(ValueError, msg):
            intersect_trees(tree1, tree2)

    def test_unpack_by_func(self):
        """Test unpacking nodes by function."""
        # unpack internal nodes with branch length <= 1.0
        def func(x):
            return x.length <= 1.0

        # will unpack node 'a', but not tip 'e'
        # will add the branch length of 'a' to its child nodes 'c' and 'd'
        tree = TreeNode.read(['((c:2,d:3)a:1,(e:1,f:2)b:2);'])
        obs = str(unpack_by_func(tree, func)).rstrip()
        exp = '((e:1.0,f:2.0)b:2.0,c:3.0,d:4.0);'
        self.assertEqual(obs, exp)

        # unpack internal nodes with branch length < 2.01
        # will unpack both 'a' and 'b'
        obs = str(unpack_by_func(tree, lambda x: x.length <= 2.0)).rstrip()
        exp = '(c:3.0,d:4.0,e:3.0,f:4.0);'
        self.assertEqual(obs, exp)

        # unpack two nested nodes 'a' and 'c' simultaneously
        tree = TreeNode.read(['(((e:3,f:2)c:1,d:3)a:1,b:4);'])
        obs = str(unpack_by_func(tree, lambda x: x.length <= 2.0)).rstrip()
        exp = '(b:4.0,d:4.0,e:5.0,f:4.0);'
        self.assertEqual(obs, exp)

        # test a complicated scenario (unpacking nodes 'g', 'h' and 'm')
        def func(x):
            return x.length < 2.0
        tree = TreeNode.read(['(((a:1.04,b:2.32,c:1.44)d:3.20,'
                              '(e:3.91,f:2.47)g:1.21)h:1.75,'
                              '(i:4.14,(j:2.06,k:1.58)l:3.32)m:0.77);'])
        obs = str(unpack_by_func(tree, func)).rstrip()
        exp = ('((a:1.04,b:2.32,c:1.44)d:4.95,e:6.87,f:5.43,i:4.91,'
               '(j:2.06,k:1.58)l:4.09);')
        self.assertEqual(obs, exp)

        # unpack nodes with support < 75
        def func(x):
            return support(x) < 75
        tree = TreeNode.read(['(((a,b)85,(c,d)78)75,(e,(f,g)64)80);'])
        obs = str(unpack_by_func(tree, func)).rstrip()
        exp = '(((a,b)85,(c,d)78)75,(e,f,g)80);'
        self.assertEqual(obs, exp)

        # unpack nodes with support < 85
        obs = str(unpack_by_func(tree, lambda x: support(x) < 85)).rstrip()
        exp = '((a,b)85,c,d,e,f,g);'
        self.assertEqual(obs, exp)

        # unpack nodes with support < 0.95
        tree = TreeNode.read(['(((a,b)0.97,(c,d)0.98)1.0,(e,(f,g)0.88)0.96);'])
        obs = str(unpack_by_func(tree, lambda x: support(x) < 0.95)).rstrip()
        exp = '(((a,b)0.97,(c,d)0.98)1.0,(e,f,g)0.96);'
        self.assertEqual(obs, exp)

        # test a case where there are branch lengths, none support values and
        # node labels
        def func(x):
            sup = support(x)
            return sup is not None and sup < 75
        tree = TreeNode.read(['(((a:1.02,b:0.33)85:0.12,(c:0.86,d:2.23)'
                              '70:3.02)75:0.95,(e:1.43,(f:1.69,g:1.92)64:0.20)'
                              'node:0.35)root;'])
        obs = str(unpack_by_func(tree, func)).rstrip()
        exp = ('(((a:1.02,b:0.33)85:0.12,c:3.88,d:5.25)75:0.95,'
               '(e:1.43,f:1.89,g:2.12)node:0.35)root;')
        self.assertEqual(obs, exp)

    def test_read_taxdump(self):
        """Test reading NCBI taxdump."""
        obs = read_taxdump(self.nodes_fp)
        exp = {
            '1': {'parent': '1', 'rank': 'order',
                  'children': set(['2', '3'])},
            '2': {'parent': '1', 'rank': 'family',
                  'children': set(['4', '5'])},
            '3': {'parent': '1', 'rank': 'family',
                  'children': set(['6', '7', '8'])},
            '4': {'parent': '2', 'rank': 'genus',
                  'children': set(['9', '10'])},
            '5': {'parent': '2', 'rank': 'genus',
                  'children': set(['11', '12', '13'])},
            '6': {'parent': '3', 'rank': 'genus',
                  'children': set(['14'])},
            '7': {'parent': '3', 'rank': 'genus',
                  'children': set(['15', '16', '17', '18'])},
            '8': {'parent': '3', 'rank': 'genus',
                  'children': set(['19', '20'])},
            '9': {'parent': '4', 'rank': 'species', 'children': set()},
            '10': {'parent': '4', 'rank': 'species', 'children': set()},
            '11': {'parent': '5', 'rank': 'species', 'children': set()},
            '12': {'parent': '5', 'rank': 'species', 'children': set()},
            '13': {'parent': '5', 'rank': 'species', 'children': set()},
            '14': {'parent': '6', 'rank': 'species', 'children': set()},
            '15': {'parent': '7', 'rank': 'species', 'children': set()},
            '16': {'parent': '7', 'rank': 'species', 'children': set()},
            '17': {'parent': '7', 'rank': 'species', 'children': set()},
            '18': {'parent': '7', 'rank': 'species', 'children': set()},
            '19': {'parent': '8', 'rank': 'species', 'children': set()},
            '20': {'parent': '8', 'rank': 'species', 'children': set()}
        }
        for tid in exp:
            exp[tid]['name'] = ''
        self.assertDictEqual(obs, exp)

        obs = read_taxdump(self.nodes_fp, self.names_fp)
        name_dict = {
            '1': 'root', '2': 'Eukaryota', '3': 'Bacteria', '4': 'Plantae',
            '5': 'Animalia', '6': 'Bacteroidetes', '7': 'Proteobacteria',
            '8': 'Firmicutes', '9': 'Gymnosperms', '10': 'Angiosperms',
            '11': 'Chordata', '12': 'Arthropoda', '13': 'Mollusca',
            '14': 'Prevotella', '15': 'Escherichia', '16': 'Vibrio',
            '17': 'Rhizobium', '18': 'Helicobacter', '19': 'Bacillus',
            '20': 'Clostridia'
        }
        for tid in name_dict:
            exp[tid]['name'] = name_dict[tid]
        self.assertDictEqual(obs, exp)

    def test_build_taxdump_tree(self):
        """Test building NCBI taxdump tree."""
        taxdump = read_taxdump(self.nodes_fp)
        obs = build_taxdump_tree(taxdump)
        exp = TreeNode.read(['(((9,10)4,(11,12,13)5)2,((14)6,(15,16,17,18)7,'
                             '(19,20)8)3)1;'])
        self.assertTrue(compare_topology(obs, exp))

    def test_order_nodes(self):
        """Test order nodes"""
        tree1 = TreeNode.read(['(((a,b),(c,d,i)j),((e,g),h));'])
        # test increase ordering
        tree1_increase = order_nodes(tree1, True)
        self.assertTrue(is_ordered(tree1_increase))

        # test decrease ordering
        tree1_decrease = order_nodes(tree1, False)
        self.assertTrue(is_ordered(tree1_decrease, False))

    def test_is_ordered(self):
        """Test if a tree is ordered"""
        # test tree in increasing order
        tree1 = TreeNode.read(['((i,j)a,b)c;'])
        self.assertTrue(is_ordered(tree1))
        self.assertTrue(is_ordered(tree1, True))
        self.assertFalse(is_ordered(tree1, False))

        # test tree in both increasing and decreasing order
        tree2 = TreeNode.read(['(a, b);'])
        self.assertTrue(is_ordered(tree2))
        self.assertTrue(is_ordered(tree2, False))

        # test an unordered tree
        tree3 = TreeNode.read(['(((a,b),(c,d,x,y,z)),((e,g),h));'])
        self.assertFalse(is_ordered(tree3, True))
        self.assertFalse(is_ordered(tree3, False))

        # test tree in decreasing order
        tree5 = TreeNode.read(['((h,(e,g)),((a,b),(c,d,i)j));'])
        self.assertTrue(is_ordered(tree5, False))

    def test_cladistic(self):
        tree1 = TreeNode.read(['((i,j)a,b)c;'])
        self.assertEqual('uni', cladistic(tree1, ['i']))
        self.assertEqual('mono', cladistic(tree1, ['i', 'j']))
        self.assertEqual('poly', cladistic(tree1, ['i', 'b']))
        msg = 'Taxa not found in the tree.'
        with self.assertRaisesRegex(ValueError, msg):
            cladistic(tree1, ['x', 'b'])

        tree2 = TreeNode.read(['(((a,b),(c,d,x)),((e,g),h));'])
        self.assertEqual('uni', cladistic(tree2, ['a']))
        self.assertEqual('mono', cladistic(tree2, ['a', 'b', 'c', 'd', 'x']))
        self.assertEqual('poly', cladistic(tree2, ['g', 'h']))
        with self.assertRaisesRegex(ValueError, msg):
            cladistic(tree2, ['y', 'b'])

    def test_compare_length(self):
        tree = TreeNode.read(['((a:1.000000001,(b:1.000000002,c:1):1):3,f)g;'])
        self.assertTrue(_compare_length(tree.find('f'), tree.find('g')))
        self.assertTrue(_compare_length(tree.find('a'), tree.find('b')))
        self.assertTrue(_compare_length(tree.find('c'), tree.find('c').parent))
        self.assertFalse(_compare_length(tree.find('c'),
                         tree.find('a').parent))
        self.assertFalse(_compare_length(tree.find('a').parent,
                         tree.find('f')))
        self.assertFalse(_compare_length(tree.find('f'),
                         tree.find('a').parent))

    def test_compare_branch_lengths(self):
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        self.assertTrue(compare_branch_lengths(tree1, tree1))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree2 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        self.assertTrue(compare_branch_lengths(tree1, tree2))

        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree3 = TreeNode.read(['(f:1,((b:1,c:1)d:1,a:1)e:1)g:1;'])
        self.assertTrue(compare_branch_lengths(tree1, tree3))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree3 = TreeNode.read(['(f:1,((b:1,c:1)d:1,a:1)e:1)g:1;'])
        self.assertTrue(compare_branch_lengths(tree3, tree1))

        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree4 = TreeNode.read(['((a:2,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        self.assertFalse(compare_branch_lengths(tree1, tree4))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree4 = TreeNode.read(['((a:2,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        self.assertFalse(compare_branch_lengths(tree4, tree1))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree5 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e,f:1)g:1;'])
        self.assertFalse(compare_branch_lengths(tree1, tree5))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree5 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e,f:1)g:1;'])
        self.assertFalse(compare_branch_lengths(tree5, tree1))

        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree7 = TreeNode.read(['((a:1,(b:1,c:1):1)e:1,f:1)g:1;'])
        self.assertTrue(compare_branch_lengths(tree1, tree7))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree7 = TreeNode.read(['((a:1,(b:1,c:1):1)e:1,f:1)g:1;'])
        self.assertTrue(compare_branch_lengths(tree7, tree1))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree8 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1):1;'])
        self.assertTrue(compare_branch_lengths(tree1, tree8))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree8 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1):1;'])
        self.assertTrue(compare_branch_lengths(tree8, tree1))

        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree6 = TreeNode.read(['(f:1, ((a:1, b:1)c:1 ,d:1)e:1)g:1;'])
        self.assertFalse(compare_branch_lengths(tree1, tree6))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree6 = TreeNode.read(['(f:1, ((a:1, b:1)c:1 ,d:1)e:1)g:1;'])
        self.assertFalse(compare_branch_lengths(tree6, tree1))

        tree9 = TreeNode.read(['(((a:1,b:1)c:1,(d:1,e:1)f:1)g:1,h:1)i:1;'])
        tree10 = TreeNode.read(['(((a:1,b:1)c:1,(d:1,e:1)g:1)f:1,h:1)i:1;'])
        self.assertTrue(compare_branch_lengths(tree9, tree10))
        tree9 = TreeNode.read(['(((a:1,b:1)c:1,(d:1,e:1)f:1)g:1,h:1)i:1;'])
        tree10 = TreeNode.read(['(((a:1,b:1)c:1,(d:1,e:1)g:1)f:1,h:1)i:1;'])
        self.assertTrue(compare_branch_lengths(tree10, tree9))

        tree9 = TreeNode.read(['(((a:1,b:1)c:1,(d:1,e:1)f:1)g:1,h:1)i:1;'])
        tree12 = TreeNode.read(['(((a:1,b:1):1,(h:1,e:1):1):1,d:1):1;'])
        self.assertFalse(compare_branch_lengths(tree9, tree12))
        tree9 = TreeNode.read(['(((a:1,b:1)c:1,(d:1,e:1)f:1)g:1,h:1)i:1;'])
        tree12 = TreeNode.read(['(((a:1,b:1):1,(h:1,e:1):1):1,d:1):1;'])
        self.assertFalse(compare_branch_lengths(tree12, tree9))

        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree11 = TreeNode.read(['((a:1,(x:1,c:1)d:1)e:1,f:1)g:1;'])
        self.assertFalse(compare_branch_lengths(tree1, tree11))
        tree1 = TreeNode.read(['((a:1,(b:1,c:1)d:1)e:1,f:1)g:1;'])
        tree11 = TreeNode.read(['((a:1,(x:1,c:1)d:1)e:1,f:1)g:1;'])
        self.assertFalse(compare_branch_lengths(tree11, tree1))

    def test_assign_supports(self):
        tree = TreeNode.read(["((a,b)95,(c,d):1.1,(e,f)'80:Dmel':1.0);"])
        assign_supports(tree)
        # standalone support value
        self.assertEqual(tree.lca(['a', 'b']).support, 95)
        # no support value
        self.assertIsNone(tree.lca(['c', 'd']).support)
        # support value before node name
        self.assertEqual(tree.lca(['e', 'f']).support, 80)
        # stripped support value from node name
        self.assertEqual(tree.lca(['e', 'f']).name, 'Dmel')

    def test_support_to_label(self):
        # unnamed nodes
        tree = TreeNode.read(['((a,b)100,((c,d)95,(e,f)99)80);'])
        assign_supports(tree)
        self.assertEqual(str(tree), '((a,b),((c,d),(e,f)));\n')
        support_to_label(tree)
        self.assertEqual(str(tree), '((a,b)100,((c,d)95,(e,f)99)80);\n')

        # named nodes
        tree = TreeNode.read(["((a,b)'100:n2',(c,d)'95:n3')n1;"])
        assign_supports(tree)
        self.assertEqual(str(tree), '((a,b)n2,(c,d)n3)n1;\n')
        support_to_label(tree)
        self.assertEqual(str(tree), "((a,b)'100:n2',(c,d)'95:n3')n1;\n")

        # unusual cases
        tree = TreeNode.read(['(((a,b)n2,(c,d)n3)n6,(e,f)n4,(g,h)n5)n1;'])
        tree.find('n2').support = 100
        tree.find('n3').support = 0
        tree.find('n4').support = ''
        tree.find('n5').support = None
        # n6 has no `support` attribute
        tree.find('a').support = 95  # tips shouldn't have support
        support_to_label(tree)
        exp = "(((a,b)'100:n2',(c,d)'0:n3')n6,(e,f)n4,(g,h)n5)n1;\n"
        self.assertEqual(str(tree), exp)

    def test_walk_copy(self):
        tree1 = TreeNode.read(['(((a:1.0,b:0.8)c:2.4,(d:0.8,e:0.6)f:1.2)g:0.4,'
                               '(h:0.5,i:0.7)j:1.8)k;'])

        # test pos = root
        msg = 'Cannot walk from root of a rooted tree.'
        with self.assertRaisesRegex(ValueError, msg):
            walk_copy(tree1.find('k'), tree1.find('j'))
        msg = 'Source and node are not neighbors.'

        # test pos = derived
        with self.assertRaisesRegex(ValueError, msg):
            walk_copy(tree1.find('a'), tree1.find('b'))
        with self.assertRaisesRegex(ValueError, msg):
            walk_copy(tree1.find('c'), tree1.find('f'))
        with self.assertRaisesRegex(ValueError, msg):
            walk_copy(tree1.find('f'), tree1.find('j'))
        with self.assertRaisesRegex(ValueError, msg):
            walk_copy(tree1.find('f'), tree1.find('k'))

        # test pos = basal
        with self.assertRaisesRegex(ValueError, msg):
            walk_copy(tree1.find('g'), tree1.find('a'))
        with self.assertRaisesRegex(ValueError, msg):
            walk_copy(tree1.find('g'), tree1.find('k'))

        # pos = derived, move = up
        exp = TreeNode.read(['(b:0.8,((d:0.8,e:0.6)f:1.2,(h:0.5,i:0.7)j:2.2)'
                             'g:2.4)c:1.0;'])
        obs = walk_copy(tree1.find('c'), tree1.find('a'))
        self.assertTrue(_exact_compare(exp, obs))

        # pos = derived, move = down
        exp = TreeNode.read(['(d:0.8,e:0.6)f:1.2;'])
        obs = walk_copy(tree1.find('f'), tree1.find('g'))
        self.assertTrue(_exact_compare(exp, obs))

        # pos = basal, move = top
        exp = TreeNode.read(['((d:0.8,e:0.6)f:1.2,(h:0.5,i:0.7)j:2.2)g:2.4;'])
        obs = walk_copy(tree1.find('g'), tree1.find('c'))
        self.assertTrue(_exact_compare(exp, obs))

        # pos = basal, move = bottom
        exp = TreeNode.read(['(h:0.5,i:0.7)j:2.2;'])
        obs = walk_copy(tree1.find('j'), tree1.find('g'))
        self.assertTrue(_exact_compare(exp, obs))

        tree2 = TreeNode.read(['(((a:1.0,b:0.8)c:2.4,d:0.8)e:0.6,f:1.2,'
                               'g:0.4)h:0.5;'])

        # pos = basal, move = down
        exp = TreeNode.read(['((a:1.0,b:0.8)c:2.4,d:0.8)e:0.6;'])
        obs = walk_copy(tree2.find('e'), tree2.find('h'))
        self.assertTrue(_exact_compare(exp, obs))

        # pos = basal, move = up
        exp = TreeNode.read(['(d:0.8,(f:1.2,g:0.4)h:0.6)e:2.4;'])
        obs = walk_copy(tree2.find('e'), tree2.find('c'))
        self.assertTrue(_exact_compare(exp, obs))

    def test_root_above(self):
        # test rooted tree
        tree1 = TreeNode.read(['(((a:1.0,b:0.8)c:2.4,(d:0.8,e:0.6)f:1.2)g:0.4,'
                               '(h:0.5,i:0.7)j:1.8)k;'])

        tree1_cg = root_above(tree1.find('c'))
        exp = TreeNode.read(['((a:1.0,b:0.8)c:1.2,((d:0.8,e:0.6)f:1.2,(h:0.5,'
                             'i:0.7)j:2.2)g:1.2);'])
        self.assertTrue(_exact_compare(exp, tree1_cg))

        tree1_ij = root_above(tree1.find('i'))
        exp = TreeNode.read(['(i:0.35,(h:0.5,((a:1.0,b:0.8)c:2.4,(d:0.8,'
                            'e:0.6)f:1.2)g:2.2)j:0.35);'])
        self.assertTrue(_exact_compare(exp, tree1_ij))

        # test unrooted tree
        tree2 = TreeNode.read(['(((a:0.6,b:0.5)g:0.3,c:0.8)h:0.4,(d:0.4,'
                               'e:0.5)i:0.5,f:0.9)j;'])

        tree2_ag = root_above(tree2.find('a'))
        exp = TreeNode.read(['(a:0.3,(b:0.5,(c:0.8,((d:0.4,e:0.5)i:0.5,'
                             'f:0.9)j:0.4)h:0.3)g:0.3);'])
        self.assertTrue(_exact_compare(exp, tree2_ag))

        tree2_gh = root_above(tree2.find('g'))
        exp = TreeNode.read(['((a:0.6,b:0.5)g:0.15,(c:0.8,((d:0.4,e:0.5)i:0.5,'
                             'f:0.9)j:0.4)h:0.15);'])
        self.assertTrue(_exact_compare(exp, tree2_gh))

        # test unrooted tree with 1 basal node
        tree3 = TreeNode.read(['(((a:0.4,b:0.3)e:0.1,(c:0.4,'
                               'd:0.1)f:0.2)g:0.6)h:0.2;'])

        tree3_ae = root_above(tree3.find('a'))
        exp = TreeNode.read(['(a:0.2,(b:0.3,((c:0.4,d:0.1)f:0.2,'
                             'h:0.6)g:0.1)e:0.2);'])
        self.assertTrue(_exact_compare(exp, tree3_ae))

    def test_unroot_at(self):
        # sample example from doctest of scikit-bio's `root_at`
        tree = TreeNode.read(['(((a,b)c,(d,e)f)g,h)i;'])
        obs = unroot_at(tree.find('c'))
        exp = TreeNode.read(['(((d,e)f,h)g,a,b)c;'])
        self.assertTrue(_exact_compare(obs, exp))

        # test branch support handling
        tree.find('c').support = 95
        tree.find('f').support = 99
        obs = unroot_at(tree.find('c'))
        exp = TreeNode.read(["(((d,e)'99:f',h)'95:g',a,b)c;"])
        assign_supports(exp)
        self.assertTrue(_exact_compare(obs, exp))

        # test branch length handling
        tree = TreeNode.read([
            '(((a:1.1,b:2.2)c:1.3,(d:1.4,e:0.8)f:0.6)g:0.4,h:3.1)i;'])
        obs = unroot_at(tree.find('c'))
        exp = TreeNode.read([
            '(((d:1.4,e:0.8)f:0.6,h:3.5)g:1.3,a:1.1,b:2.2)c;'])
        self.assertTrue(_exact_compare(obs, exp))

    def test_exact_compare(self):
        # test name
        tree0 = TreeNode.read(['((e,d)f,(c,(a,b)));'])
        tree1 = TreeNode.read(['(((a,b),c),(d,e)f);'])
        self.assertTrue(_exact_compare(tree1, tree1))
        self.assertFalse(_exact_compare(tree0, tree1))

        # test length
        tree2 = TreeNode.read(['(((a:1,b):2,c:1),(d:1,e:2)f:1);'])
        self.assertTrue(_exact_compare(tree2, tree2))
        self.assertFalse(_exact_compare(tree1, tree2))
        tree3 = TreeNode.read(['(((a:1,b:0.0):2,c:1):0.0,(d:1,e:2)f:1);'])
        self.assertTrue(_exact_compare(tree3, tree3))
        self.assertFalse(_exact_compare(tree2, tree3))

        # test support
        tree4 = TreeNode.read(['(((a:1,b:1)95:2,c:1)98:3,(d:1,e:2)0.0:1);'])
        tree5 = TreeNode.read(['(((a:1,b:1)95:2,c:1)98:3,(d:1,e:2):1);'])
        assign_supports(tree4)
        self.assertTrue(_exact_compare(tree4, tree4))
        self.assertFalse(_exact_compare(tree4, tree5))
        assign_supports(tree5)
        self.assertFalse(_exact_compare(tree4, tree5))

    def test_calc_split_metrics(self):
        """Example from Fig. 9a of Puigbo, et al., 2009, J Biol.
                                                /-A
                                      /n9------|
                            /n8------|          \\-B
                           |         |
                  /n4------|          \\-C
                 |         |
                 |         |          /-D
                 |          \n7------|
                 |                    \\-E
                 |
                 |                    /-F
        -n1------|          /n6------|
                 |         |          \\-G
                 |-n3------|
                 |         |          /-H
                 |          \n5------|
                 |                    \\-I
                 |
                 |          /-J
                  \n2------|
                            \\-K
        """
        tree = TreeNode.read([
            '((((A,B)n9,C)n8,(D,E)n7)n4,((F,G)n6,(H,I)n5)n3,(J,K)n2)n1;'
        ])
        calc_split_metrics(tree)
        obs = {x.name: [getattr(x, y) for y in
                        ('n', 'splits', 'prelevel', 'postlevels')]
               for x in tree.traverse()}
        exp = {
            'n1': [11, 9, 1, [5, 5, 4, 4, 4, 4, 4, 4, 4, 3, 3]],
            'n4': [5, 4, 2, [4, 4, 3, 3, 3]],
            'n3': [4, 3, 2, [3, 3, 3, 3]],
            'n2': [2, 1, 2, [2, 2]],
            'n8': [3, 2, 3, [3, 3, 2]],
            'n7': [2, 1, 3, [2, 2]],
            'n6': [2, 1, 3, [2, 2]],
            'n5': [2, 1, 3, [2, 2]],
            'J': [1, 0, 3, [1]],
            'K': [1, 0, 3, [1]],
            'n9': [2, 1, 4, [2, 2]],
            'C': [1, 0, 4, [1]],
            'D': [1, 0, 4, [1]],
            'E': [1, 0, 4, [1]],
            'F': [1, 0, 4, [1]],
            'G': [1, 0, 4, [1]],
            'H': [1, 0, 4, [1]],
            'I': [1, 0, 4, [1]],
            'A': [1, 0, 5, [1]],
            'B': [1, 0, 5, [1]]
        }
        self.assertDictEqual(obs, exp)

    def test_calc_length_metrics(self):
        """Example from Fig. 1a of Parks et al. (2018):
                                   /--1--A
                          /n3--1--|
                         |         \\--1--B
             /n2----2----|
            |            |             /--1--C
        -n1-|             \n4----2----|
            |                          \\----2----D
            |
             \\------3------E
        """
        tree = TreeNode.read(['(((A:1,B:1)n3:1,(C:1,D:2)n4:2)n2:2,E:3)n1;'])
        calc_length_metrics(tree)
        obs = {x.name: {'height': x.height, 'depths': x.depths,
                        'red': round(x.red, 7)} for x in tree.traverse()}
        exp = {'n1': {'height': 0.0, 'depths': [4.0, 4.0, 5.0, 6.0, 3.0],
                      'red': 0.0},
               'n2': {'height': 2.0, 'depths': [2.0, 2.0, 3.0, 4.0],
                      'red': 0.4210526},
               'n3': {'height': 3.0, 'depths': [1.0, 1.0], 'red': 0.7105263},
               'n4': {'height': 4.0, 'depths': [1.0, 2.0], 'red': 0.7518797},
               'A': {'height': 4.0, 'depths': [0.0], 'red': 1.0},
               'B': {'height': 4.0, 'depths': [0.0], 'red': 1.0},
               'C': {'height': 5.0, 'depths': [0.0], 'red': 1.0},
               'D': {'height': 6.0, 'depths': [0.0], 'red': 1.0},
               'E': {'height': 3.0, 'depths': [0.0], 'red': 1.0}}
        self.assertDictEqual(obs, exp)

    def test_format_newick(self):
        newick = '((A_1:1.05,B_2:1.68):2.24,(C:0.28,D:1.14):1.73e-10);'
        tree = TreeNode.read([newick])

        # default behavior (same as TreeNode.write)
        self.assertEqual(format_newick(tree), newick)

        # keep space
        exp = "(('A 1':1.05,'B 2':1.68):2.24,(C:0.28,D:1.14):1.73e-10);"
        self.assertEqual(format_newick(tree, keep_space=True), exp)

        # specify digits for float point
        exp = '((A_1:1.1,B_2:1.7):2.2,(C:0.28,D:1.1):1.73e-10);'
        self.assertEqual(format_newick(tree, max_f=2), exp)

        # specify digits for scientific notation
        exp = '((A_1:1.05,B_2:1.68):2.24,(C:0.28,D:1.14):1.7e-10);'
        self.assertEqual(format_newick(tree, max_e=2), exp)

        # all options enabled
        exp = "(('A 1':1.1,'B 2':1.7):2.2,(C:0.28,D:1.1):1.7e-10);"
        self.assertEqual(format_newick(tree, True, 2, 2), exp)

    def test_root_by_outgroup(self):
        tree = TreeNode.read(['((((a,b),(c,d)),(e,f)),g);'])

        # outgroup is monophyletic
        obs = root_by_outgroup(tree, outgroup=['a', 'b'])
        exp = TreeNode.read(['((a,b),((c,d),((e,f),g)));'])
        self.assertTrue(_exact_compare(obs, exp))

        # outgroup is monophyletic after rotating
        obs = root_by_outgroup(tree, outgroup=['e', 'f', 'g'])
        exp = TreeNode.read(['(((e,f),g),((c,d),(b,a)));'])
        self.assertTrue(_exact_compare(obs, exp))

        # outgroup is not monophyletic
        msg = 'Outgroup is not monophyletic in tree.'
        with self.assertRaisesRegex(ValueError, msg):
            root_by_outgroup(tree, outgroup=['a', 'c'])

        # outgroup is single taxon
        obs = root_by_outgroup(tree, outgroup=['a'])
        exp = TreeNode.read(['(a,(b,((c,d),((e,f),g))));'])
        self.assertTrue(_exact_compare(obs, exp))

        # outgroup has extra taxa
        obs = root_by_outgroup(tree, outgroup=['a', 'b', 'x'])
        exp = TreeNode.read(['((a,b),((c,d),((e,f),g)));'])
        self.assertTrue(_exact_compare(obs, exp))

        # outgroup has extra taxa but strict mode
        msg = 'Outgroup is not a subset of tree taxa.'
        with self.assertRaisesRegex(ValueError, msg):
            root_by_outgroup(tree, outgroup=['a', 'b', 'x'], strict=True)

        # outgroup is not in tree
        msg = 'None of outgroup taxa are present in tree.'
        with self.assertRaisesRegex(ValueError, msg):
            root_by_outgroup(tree, outgroup=['x', 'y'])

        # outgroup is the whole tree
        msg = 'Outgroup constitutes the entire tree.'
        with self.assertRaisesRegex(ValueError, msg):
            root_by_outgroup(tree, outgroup='abcdefg')

        # generate unrooted tree
        obs = root_by_outgroup(tree, outgroup=['a', 'b'], unroot=True)
        exp = TreeNode.read(['(((e,f),g),(a,b),(c,d));'])
        self.assertTrue(_exact_compare(obs, exp))

    def test_restore_rooting(self):
        # rooted source
        source = TreeNode.read(['(((e,f),g),((c,d),(b,a)));'])
        target = TreeNode.read(['(((a,b),(c,d)),(e,f),g);'])
        rooted = restore_rooting(source, target)
        self.assertTrue(_exact_compare(rooted, source))

        # unrooted source
        source = TreeNode.read(['(((e,f),g),(a,b),(c,d));'])
        unrooted = restore_rooting(source, target)
        self.assertTrue(_exact_compare(unrooted, source))

        # test support handling
        source = TreeNode.read(['(((e,f),g),((c,d),(b,a)));'])
        target = TreeNode.read(['(((a,b)95,(c,d)90)80,(e,f)100,g);'])
        assign_supports(target)
        obs = restore_rooting(source, target)
        exp = TreeNode.read(['(((e,f)100,g)80,((c,d)90,(b,a)95)80);'])
        assign_supports(exp)
        self.assertTrue(_exact_compare(obs, exp))

        # taxa don't match
        msg = 'Source and target trees have different taxa.'
        with self.assertRaisesRegex(ValueError, msg):
            restore_rooting(source, TreeNode.read(['((a,b),(c,d));']))

    def test_restore_node_labels(self):
        # simple case
        source = TreeNode.read(['((a,b)x,(c,d)y);'])
        target = TreeNode.read(['((a:0.5,b:0.6):1.2,(c:1.0,d:1.4):0.4);'])
        obs = restore_node_labels(source, target)
        exp = TreeNode.read(['((a:0.5,b:0.6)x:1.2,(c:1.0,d:1.4)y:0.4);'])
        self.assertTrue(_exact_compare(obs, exp))

        # complex case with missing label, extra taxa, label overwrittern
        source = TreeNode.read(['(((a,b)85,c)90,((d,e)98,(f,g)93));'])
        target = TreeNode.read(['((((g,f),(e,d))x,(c,(a,b))y),h);'])
        obs = restore_node_labels(source, target)
        exp = TreeNode.read(['((((g,f)93,(e,d)98)x,(c,(a,b)85)90),h);'])
        self.assertTrue(_exact_compare(obs, exp))

        # a duplicated node label
        msg = 'Duplicated node label "x" found.'
        with self.assertRaisesRegex(ValueError, msg):
            restore_node_labels(TreeNode.read(['((a,b)x,(c,d)x);']), target)

    def test_restore_node_order(self):
        source = TreeNode.read(['(((a,b),(c,d)),((e,f),g));'])
        target = TreeNode.read(['((g,(e,f)100),((d,c)80,(a,b)90));'])
        obs = restore_node_order(source, target)
        exp = TreeNode.read(['(((a,b)90,(c,d)80),((e,f)100,g));'])
        self.assertTrue(_exact_compare(obs, exp))

        msg = 'Two trees have different sizes.'
        with self.assertRaisesRegex(ValueError, msg):
            restore_node_order(TreeNode.read(['((a,b),(c,d));']), target)

        msg = 'Two trees have different topologies.'
        with self.assertRaisesRegex(ValueError, msg):
            restore_node_order(
                TreeNode.read(['((((a,b),c),d),(e,(f,g)));']), target)

    def test_get_base(self):
        tree = TreeNode.read(['(((a,b)n6,(c,d)n5)n3,((e,f)n4,g)n2)n1;'])
        self.assertEqual(get_base(tree.find('a')).name, 'n3')
        self.assertEqual(get_base(tree.find('e')).name, 'n2')

        obs = get_base(tree.lca([tree.find('a'), tree.find('b')])).name
        self.assertEqual(obs, 'n3')

        msg = 'Root has no base.'
        with self.assertRaisesRegex(ValueError, msg):
            get_base(tree)

    def test_calc_bidi_minlevels(self):
        # an unrooted tree (typical use case)
        tree = TreeNode.read(['(((a,b)n4,(c,d)n5)n2,(((e,f)n8,(g,h)n9)n6,'
                              '((i,j)n10,(k,l)n11)n7)n3,m)n1;'])
        calc_bidi_minlevels(tree)
        # tips should always be 1
        self.assertSetEqual(set(x.minlevel for x in tree.tips()), {1})
        # internal nodes
        obs = {x.name: x.minlevel for x in tree.non_tips(include_self=True)}
        exp = {'n1': 2, 'n2': 3, 'n3': 3, 'n4': 2, 'n5': 2, 'n6': 3, 'n7': 3,
               'n8': 2, 'n9': 2, 'n10': 2, 'n11': 2}
        self.assertDictEqual(obs, exp)

        # a rooted tree (unusual but could happen)
        tree = TreeNode.read(['(((a,b)n3,(c,d)n4)n2,e)n1;'])
        calc_bidi_minlevels(tree)
        obs = {x.name: x.minlevel for x in tree.non_tips(include_self=True)}
        exp = {'n1': 2, 'n2': 2, 'n3': 2, 'n4': 2}
        self.assertDictEqual(obs, exp)

    def test_calc_bidi_mindepths(self):
        tree = TreeNode.read(['(((a:0.5,b:0.7)n5:1.1,c:1.7)n2:0.3,((d:0.8,'
                              'e:0.6)n6:0.9,(f:1.2,g:0.5)n7:0.8)n3:1.3,'
                              '(h:0.4,i:0.3)n4:0.9)n1;'])
        calc_bidi_mindepths(tree)
        # tips should always be 1
        self.assertSetEqual(set(x.mindepth for x in tree.tips()), {0.0})
        # internal nodes
        obs = {x.name: x.mindepth for x in tree.non_tips(include_self=True)}
        exp = {'n1': 1.2, 'n2': 1.5, 'n3': 1.3, 'n4': 0.3, 'n5': 0.5,
               'n6': 0.6, 'n7': 0.5}
        self.assertDictEqual(obs, exp)


if __name__ == '__main__':
    main()
