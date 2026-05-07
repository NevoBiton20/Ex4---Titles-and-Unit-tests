'''
An implementation of the algorithm described in:

"Maxmin Participatory Budgeting", by Gogulapati Sreedurga , Mayank Ratan Bhardwaj and Y. Narahari, 2022, https://arxiv.org/pdf/2204.13923

Programmer: Nevo Biton
Date: 2026-04-29
'''

import pulp

"""
Parameters
----------

voters : list[set[str]]
    A list representing the voters. Each element is a set of project names
    approved by one voter.

    Example:
    [
        {"p1", "p2"},
        {"p2", "p3"},
        {"p1"}
    ]

costs : dict[str, float]
    A dictionary mapping each project name to its cost.

    Example:
    {
        "p1": 3,
        "p2": 5,
        "p3": 2
    }

budget : float
    The total available budget. The total cost of the selected projects
    must not exceed this value.

Returns a set[str] containing the names of the selected projects.

Raises ValueError If the budget is negative, if a project has a negative cost, or if a 
voter approves a project that does not appear in the costs dictionary.

The algorithm receives a set of projects, their costs, a budget limit,
and the approval sets of the voters. It first solves a linear relaxation
of the max-min participatory budgeting problem, where each project may be
selected fractionally. Then, it orders the projects according to their
fractional values in the LP solution and greedily selects projects in that
order as long as the budget constraint is not violated.
"""
def ordered_relax(voters: list[set[str]], costs: dict[str, float], budget: float,) -> set[str]:
    
    """
    The input is:
    - voters: list of approval sets, where voters[i] is the approval set of voter i
    - costs: dictionary mapping each project to its cost
    - budget: total available budget

    The output is a feasible set of selected projects.

    Important:
    These doctests assume deterministic tie-breaking according to the insertion
    order of the projects in the `costs` dictionary.

    Example 1: size 1

    >>> voters = [
    ...     {"p1"},
    ... ]
    >>> costs = {
    ...     "p1": 5,
    ... }
    >>> budget = 5
    >>> ordered_relax(voters, costs, budget) == {"p1"}
    True

    Example 2: size 2

    >>> voters = [
    ...     {"p1"},
    ...     {"p2"},
    ... ]
    >>> costs = {
    ...     "p1": 4,
    ...     "p2": 3,
    ... }
    >>> budget = 4
    >>> ordered_relax(voters, costs, budget) == {"p1"}
    True

    Example 3: size 3

    >>> voters = [
    ...     {"p1", "p2"},
    ...     {"p2"},
    ...     {"p3"},
    ... ]
    >>> costs = {
    ...     "p1": 3,
    ...     "p2": 3,
    ...     "p3": 2,
    ... }
    >>> budget = 5
    >>> ordered_relax(voters, costs, budget) == {"p2", "p3"}
    True

    Example 4: ORDERED-RELAX works optimally

    >>> voters = [
    ...     {"p0", "p1"},
    ...     {"p0", "p2"},
    ...     {"p0", "p3"},
    ...     {"p0", "p4"},
    ... ]
    >>> costs = {
    ...     "p0": 2,
    ...     "p1": 3,
    ...     "p2": 3,
    ...     "p3": 3,
    ...     "p4": 3,
    ... }
    >>> budget = 8
    >>> ordered_relax(voters, costs, budget) == {"p0", "p1", "p2"}
    True

    Example 5: ORDERED-RELAX works poorly

    >>> voters = [
    ...     {"p4"},
    ...     {"p1", "p2"},
    ...     {"p1", "p3", "p5"},
    ... ]
    >>> costs = {
    ...     "p0": 23,
    ...     "p1": 68,
    ...     "p2": 198,
    ...     "p3": 189,
    ...     "p4": 146,
    ...     "p5": 38,
    ... }
    >>> budget = 341
    >>> ordered_relax(voters, costs, budget) == {"p4"}
    True

    Example 6: larger ORDERED-RELAX instance

    >>> voters = [
    ...     {"p0", "p3", "p7"},
    ...     {"p1", "p4", "p6", "p7"},
    ...     {"p0", "p2", "p4", "p5"},
    ...     {"p1", "p6", "p9"},
    ...     {"p1", "p2", "p6", "p7", "p8"},
    ...     {"p1", "p3", "p4", "p6", "p8"},
    ... ]
    >>> costs = {
    ...     "p0": 18,
    ...     "p1": 45,
    ...     "p2": 43,
    ...     "p3": 32,
    ...     "p4": 28,
    ...     "p5": 32,
    ...     "p6": 5,
    ...     "p7": 37,
    ...     "p8": 43,
    ...     "p9": 17,
    ... }
    >>> budget = 124
    >>> ordered_relax(voters, costs, budget) == {"p1", "p2"}
    True
    """
    pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
