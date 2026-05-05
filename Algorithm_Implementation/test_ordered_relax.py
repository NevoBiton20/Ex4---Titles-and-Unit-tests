from ordered_relax import ordered_relax
"""
Pytest tests for ordered_relax.

Run with:
    python -m pytest test_ordered_relax.py -v
"""

from itertools import combinations
import random
import pytest


EPS = 1e-7


def total_cost(projects: set[str], costs: dict[str, float]) -> float:
    return sum(costs[p] for p in projects)


def voter_utility(selected: set[str], voter: set[str], costs: dict[str, float]) -> float:
    return sum(costs[p] for p in selected & voter)


def mpb_value(selected: set[str], voters: list[set[str]], costs: dict[str, float]) -> float:
    if not voters:
        return 0.0
    return min(voter_utility(selected, voter, costs) for voter in voters)


def all_feasible_subsets(projects: list[str], costs: dict[str, float], budget: float):
    for r in range(len(projects) + 1):
        for subset_tuple in combinations(projects, r):
            subset = set(subset_tuple)
            if total_cost(subset, costs) <= budget + EPS:
                yield subset


def brute_force_opt(voters: list[set[str]], costs: dict[str, float], budget: float) -> float:
    """
    Exact OPT by brute force.

    Use only for small / medium instances, because this is O(2^m).
    """
    projects = list(costs.keys())
    best = 0.0

    for subset in all_feasible_subsets(projects, costs, budget):
        best = max(best, mpb_value(subset, voters, costs))

    return best


def assert_valid_output(
    selected: set[str],
    voters: list[set[str]],
    costs: dict[str, float],
    budget: float,
):
    assert isinstance(selected, set)
    assert selected <= set(costs.keys())
    assert total_cost(selected, costs) <= budget + EPS


def lemma_eta(selected: set[str], voters: list[set[str]]) -> float | None:
    """
    Compute eta from Lemma 1.

    j is a worst-off voter under the selected set.
    eta = |A_j \\ S| / |S \\ A_j|

    If |S \\ A_j| = 0, eta is undefined in the formula.
    In that case, the test skips the Lemma 1 numerical check.
    """
    if not voters:
        return None

    utilities_by_index = [
        (len(selected & voter), idx)
        for idx, voter in enumerate(voters)
    ]

    # We choose one worst-off voter by actual cost utility, not by cardinality.
    # This helper does not know costs, so this function is used only after
    # selecting j separately in assert_lemma_guarantee.
    raise NotImplementedError


def assert_lemma_guarantee(
    selected: set[str],
    voters: list[set[str]],
    costs: dict[str, float],
    budget: float,
):
    """
    Checks Lemma 1 guarantee:

        ALG >= OPT - eta * (budget - OPT)

    where:
        ALG = min_i u_i(S)
        OPT = exact MPB optimum
        eta = |A_j \\ S| / |S \\ A_j|
        j = argmin_i u_i(S)

    This requires brute-force OPT, so use it only when the number of projects
    is not too large.
    """
    if not voters:
        return

    alg = mpb_value(selected, voters, costs)
    opt = brute_force_opt(voters, costs, budget)

    utilities = [
        voter_utility(selected, voter, costs)
        for voter in voters
    ]
    worst_value = min(utilities)
    j = utilities.index(worst_value)
    worst_voter = voters[j]

    denominator = len(selected - worst_voter)

    # The Lemma formula uses division by |S \\ A_j|.
    # If denominator is 0, the expression is not numerically usable here.
    if denominator == 0:
        pytest.skip("Lemma eta is undefined because |S \\ A_j| = 0")

    eta = len(worst_voter - selected) / denominator
    lower_bound = opt - eta * (budget - opt)

    assert alg + EPS >= lower_bound


# ---------------------------------------------------------
# Basic examples from your document
# ---------------------------------------------------------


def test_example_1_size_1():
    voters = [
        {"p1"},
    ]
    costs = {
        "p1": 5,
    }
    budget = 5

    selected = ordered_relax(voters, costs, budget)

    assert selected == {"p1"}
    assert_valid_output(selected, voters, costs, budget)
    assert_lemma_guarantee(selected, voters, costs, budget)


def test_example_2_size_2():
    voters = [
        {"p1"},
        {"p2"},
    ]
    costs = {
        "p1": 4,
        "p2": 3,
    }
    budget = 4

    selected = ordered_relax(voters, costs, budget)

    assert selected == {"p1"}
    assert_valid_output(selected, voters, costs, budget)
    assert_lemma_guarantee(selected, voters, costs, budget)


def test_example_3_size_3():
    voters = [
        {"p1", "p2"},
        {"p2"},
        {"p3"},
    ]
    costs = {
        "p1": 3,
        "p2": 3,
        "p3": 2,
    }
    budget = 5

    selected = ordered_relax(voters, costs, budget)

    assert selected == {"p2", "p3"}
    assert_valid_output(selected, voters, costs, budget)
    assert_lemma_guarantee(selected, voters, costs, budget)


def test_example_4_ordered_relax_optimal():
    voters = [
        {"p0", "p1"},
        {"p0", "p2"},
        {"p0", "p3"},
        {"p0", "p4"},
    ]
    costs = {
        "p0": 2,
        "p1": 3,
        "p2": 3,
        "p3": 3,
        "p4": 3,
    }
    budget = 8

    selected = ordered_relax(voters, costs, budget)

    assert selected == {"p0", "p1", "p2"}
    assert_valid_output(selected, voters, costs, budget)
    assert_lemma_guarantee(selected, voters, costs, budget)


def test_example_5_ordered_relax_bad_case():
    voters = [
        {"p4"},
        {"p1", "p2"},
        {"p1", "p3", "p5"},
    ]
    costs = {
        "p0": 23,
        "p1": 68,
        "p2": 198,
        "p3": 189,
        "p4": 146,
        "p5": 38,
    }
    budget = 341

    selected = ordered_relax(voters, costs, budget)

    assert selected == {"p4"}
    assert_valid_output(selected, voters, costs, budget)
    assert_lemma_guarantee(selected, voters, costs, budget)


def test_example_6_large_manual_example():
    voters = [
        {"p0", "p3", "p7"},
        {"p1", "p4", "p6", "p7"},
        {"p0", "p2", "p4", "p5"},
        {"p1", "p6", "p9"},
        {"p1", "p2", "p6", "p7", "p8"},
        {"p1", "p3", "p4", "p6", "p8"},
    ]
    costs = {
        "p0": 18,
        "p1": 45,
        "p2": 43,
        "p3": 32,
        "p4": 28,
        "p5": 32,
        "p6": 5,
        "p7": 37,
        "p8": 43,
        "p9": 17,
    }
    budget = 124

    selected = ordered_relax(voters, costs, budget)

    assert selected == {"p1", "p2"}
    assert_valid_output(selected, voters, costs, budget)
    assert_lemma_guarantee(selected, voters, costs, budget)


# ---------------------------------------------------------
# Edge cases
# ---------------------------------------------------------


def test_empty_voters_and_empty_costs():
    voters = []
    costs = {}
    budget = 10

    selected = ordered_relax(voters, costs, budget)

    assert selected == set()
    assert_valid_output(selected, voters, costs, budget)


def test_no_projects_but_some_voters():
    voters = [
        set(),
        set(),
        set(),
    ]
    costs = {}
    budget = 10

    selected = ordered_relax(voters, costs, budget)

    assert selected == set()
    assert_valid_output(selected, voters, costs, budget)


def test_zero_budget_returns_empty_set():
    voters = [
        {"p1"},
        {"p2"},
    ]
    costs = {
        "p1": 5,
        "p2": 7,
    }
    budget = 0

    selected = ordered_relax(voters, costs, budget)

    assert selected == set()
    assert_valid_output(selected, voters, costs, budget)


def test_project_too_expensive_returns_empty_or_feasible():
    voters = [
        {"p1"},
    ]
    costs = {
        "p1": 100,
    }
    budget = 10

    selected = ordered_relax(voters, costs, budget)

    assert_valid_output(selected, voters, costs, budget)
    assert selected == set()


def test_projects_not_approved_by_anyone_are_allowed_but_output_is_feasible():
    voters = [
        {"p1"},
        {"p2"},
    ]
    costs = {
        "p1": 5,
        "p2": 5,
        "unused": 1,
    }
    budget = 6

    selected = ordered_relax(voters, costs, budget)

    assert_valid_output(selected, voters, costs, budget)


# ---------------------------------------------------------
# Wrong input tests
#
# These assume your implementation validates input and raises ValueError.
# If your current function does not validate input, either add validation
# or remove these tests.
# ---------------------------------------------------------


def test_negative_budget_raises_value_error():
    voters = [
        {"p1"},
    ]
    costs = {
        "p1": 5,
    }

    with pytest.raises(ValueError):
        ordered_relax(voters, costs, -1)


def test_negative_cost_raises_value_error():
    voters = [
        {"p1"},
    ]
    costs = {
        "p1": -5,
    }
    budget = 10

    with pytest.raises(ValueError):
        ordered_relax(voters, costs, budget)


def test_voter_approves_unknown_project_raises_value_error():
    voters = [
        {"p1", "unknown_project"},
    ]
    costs = {
        "p1": 5,
    }
    budget = 10

    with pytest.raises(ValueError):
        ordered_relax(voters, costs, budget)


def test_non_set_voter_raises_value_error():
    voters = [
        ["p1"],  # wrong: should be {"p1"}
    ]
    costs = {
        "p1": 5,
    }
    budget = 10

    with pytest.raises(ValueError):
        ordered_relax(voters, costs, budget)


# ---------------------------------------------------------
# Random small tests with exact OPT
# ---------------------------------------------------------


def generate_random_instance(
    *,
    seed: int,
    num_voters: int,
    num_projects: int,
    min_cost: int = 1,
    max_cost: int = 20,
    approval_probability: float = 0.35,
):
    rng = random.Random(seed)

    projects = [f"p{i}" for i in range(num_projects)]

    costs = {
        p: rng.randint(min_cost, max_cost)
        for p in projects
    }

    total = sum(costs.values())
    budget = rng.randint(max(1, total // 4), max(1, total // 2))

    voters = []
    for _ in range(num_voters):
        approval_set = {
            p for p in projects
            if rng.random() < approval_probability
        }

        # Avoid empty approval sets in most random tests.
        if not approval_set:
            approval_set.add(rng.choice(projects))

        voters.append(approval_set)

    return voters, costs, budget


@pytest.mark.parametrize("seed", range(20))
def test_random_small_instances_satisfy_feasibility_and_lemma(seed):
    voters, costs, budget = generate_random_instance(
        seed=seed,
        num_voters=4,
        num_projects=10,
        min_cost=1,
        max_cost=25,
        approval_probability=0.4,
    )

    selected = ordered_relax(voters, costs, budget)

    assert_valid_output(selected, voters, costs, budget)
    assert_lemma_guarantee(selected, voters, costs, budget)


@pytest.mark.parametrize("seed", range(20, 30))
def test_random_medium_instances_satisfy_feasibility_and_lemma(seed):
    """
    15 projects means brute force checks 2^15 = 32768 subsets,
    which is still usually fine for pytest.
    """
    voters, costs, budget = generate_random_instance(
        seed=seed,
        num_voters=6,
        num_projects=15,
        min_cost=1,
        max_cost=40,
        approval_probability=0.35,
    )

    selected = ordered_relax(voters, costs, budget)

    assert_valid_output(selected, voters, costs, budget)
    assert_lemma_guarantee(selected, voters, costs, budget)


# ---------------------------------------------------------
# Big tests
#
# For truly big inputs, exact OPT is expensive.
# Therefore these tests check validity, feasibility, and stability.
# ---------------------------------------------------------


@pytest.mark.parametrize("seed", range(100, 110))
def test_big_random_inputs_are_feasible(seed):
    voters, costs, budget = generate_random_instance(
        seed=seed,
        num_voters=50,
        num_projects=100,
        min_cost=1,
        max_cost=100,
        approval_probability=0.15,
    )

    selected = ordered_relax(voters, costs, budget)

    assert_valid_output(selected, voters, costs, budget)


def test_large_dense_input_is_feasible():
    voters, costs, budget = generate_random_instance(
        seed=999,
        num_voters=100,
        num_projects=150,
        min_cost=1,
        max_cost=50,
        approval_probability=0.5,
    )

    selected = ordered_relax(voters, costs, budget)

    assert_valid_output(selected, voters, costs, budget)


def test_large_sparse_input_is_feasible():
    voters, costs, budget = generate_random_instance(
        seed=1000,
        num_voters=100,
        num_projects=150,
        min_cost=1,
        max_cost=50,
        approval_probability=0.05,
    )

    selected = ordered_relax(voters, costs, budget)

    assert_valid_output(selected, voters, costs, budget)