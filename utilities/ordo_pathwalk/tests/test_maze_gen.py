from utilities.ordo_pathwalk.generator.maze_gen import generate_tree, END_SENTINEL


def test_same_seed_same_tree():
    a = generate_tree(seed=42, depth=4, branching_range=(2, 3)).to_dict()
    b = generate_tree(seed=42, depth=4, branching_range=(2, 3)).to_dict()
    assert a == b


def test_leaf_children_end_at_exact_depth():
    tree = generate_tree(seed=7, depth=3, branching_range=(2, 2))
    assert all(node.depth < tree.depth for node in tree.nodes.values())
    for node in tree.nodes.values():
        if node.depth == tree.depth - 1:
            assert set(node.children.values()) == {END_SENTINEL}


def test_branching_in_range():
    tree = generate_tree(seed=8, depth=4, branching_range=(2, 4))
    for node in tree.nodes.values():
        assert 2 <= len(node.options) <= 4
        assert set(node.options) == set(node.children)
