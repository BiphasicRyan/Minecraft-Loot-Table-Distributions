"""Shared loot distribution logic: P(X=x) over n in 4..8 with given per-chest probability p."""
import math


def prob_exact(p: float, x: int) -> float:
    total = 0.0
    for n in range(4, 9):
        if x > n:
            continue
        total += (1 / 5) * math.comb(n, x) * (p**x) * ((1 - p) ** (n - x))
    return total


def run_distribution(p: float) -> None:
    for x in range(0, 9):
        print(f"P(X={x}) = {prob_exact(p, x):.12f}")
    print("Check sum:", sum(prob_exact(p, x) for x in range(0, 9)))
