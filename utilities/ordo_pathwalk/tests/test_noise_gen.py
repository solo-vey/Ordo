from utilities.ordo_pathwalk.generator.maze_gen import generate_tree, END_SENTINEL
from utilities.ordo_pathwalk.generator.noise_gen import generate_script


def test_ground_truth_length_matches_depth():
    tree = generate_tree(seed=10, depth=5, branching_range=(2, 3))
    script = generate_script(tree, script_seed=20, num_confusion_episodes=(2, 3))
    assert len(script.ground_truth) == tree.depth


def test_expected_node_after_values_exist_or_end():
    tree = generate_tree(seed=11, depth=4, branching_range=(2, 3))
    script = generate_script(tree, script_seed=21, num_confusion_episodes=(1, 2))
    valid = set(tree.nodes) | {END_SENTINEL}
    assert all(turn.expected_node_after in valid for turn in script.turns)


def test_script_to_dict_is_stable_shape():
    tree = generate_tree(seed=12, depth=3, branching_range=(2, 2))
    data = generate_script(tree, script_seed=22, num_confusion_episodes=(0, 0)).to_dict()
    assert sorted(data) == ["ground_truth", "script_seed", "tree_seed", "turns"]
    assert all("expected_node_after" in t for t in data["turns"])
