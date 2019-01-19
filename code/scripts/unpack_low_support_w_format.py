# Remove nodes with low support value and append child nodes to parent.
# Usage: python me.py input.nwk cutoff output.nwk

from sys import argv
from skbio import TreeNode

tree = TreeNode.read(argv[1])
num_tips = tree.count(tips=True)

print('Nodes before unpacking: %d.' % (tree.count() - num_tips))

cutoff = float(argv[2])


def digits(num):
    if not num.replace('.', '').isdigit() or num.count('.') != 1:
        raise ValueError('Not a valid float number: %s' % num)
    return len(num.split('.')[1])


max_f, max_e = 0, 0
for node in tree.traverse():
    if node.length is not None:
        x = str(float(node.length))
        if 'e' in x:
            max_e = max(max_e, digits(str(float(x.split('e')[0]))))
        else:
            max_f = max(max_f, digits(x))


def support(node):
    try:
        return float(node.name.split(':')[0])
    except (ValueError, AttributeError):
        return None


def unpack(node):
    if node.is_root():
        raise ValueError('Cannot unpack root.')
    parent = node.parent
    blen = (node.length or 0.0)
    for child in node.children:
        clen = (child.length or 0.0)
        child.length = (clen + blen or None)
    parent.remove(node)
    parent.extend(node.children)


nodes_to_unpack = []
for node in tree.non_tips():
    sup = support(node)
    if sup is not None and sup < cutoff:
        nodes_to_unpack.append(node)

for node in nodes_to_unpack:
    unpack(node)

print('Nodes after unpacking: %d.' % (tree.count() - num_tips))


with open(argv[3], 'w') as f:
    operators = set(",:_;()[] ")
    current_depth = 0
    nodes_left = [(tree, 0)]
    while len(nodes_left) > 0:
        entry = nodes_left.pop()
        node, node_depth = entry
        if node.children and node_depth >= current_depth:
            f.write('(')
            nodes_left.append(entry)
            nodes_left += ((child, node_depth + 1) for child in
                           reversed(node.children))
            current_depth = node_depth + 1
        else:
            if node_depth < current_depth:
                f.write(')')
                current_depth -= 1
            if node.name:
                escaped = "%s" % node.name.replace("'", "''")
                if any(t in operators for t in node.name):
                    f.write("'")
                    f.write(escaped)
                    f.write("'")
                else:
                    f.write(escaped)
            if node.length is not None:
                f.write(':')
                length = node.length
                if 'e' in str(length):
                    length = '%.*g' % (max_e, length)
                else:
                    length = '%.*g' % (max_f, length)
                f.write(length)
            if nodes_left and nodes_left[-1][1] == current_depth:
                f.write(',')

    f.write(';\n')
