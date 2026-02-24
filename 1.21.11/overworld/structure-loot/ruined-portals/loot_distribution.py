import math
from collections import defaultdict
from typing import Dict

def convolve(pmf_a: Dict[int, float], pmf_b: Dict[int, float]) -> Dict[int, float]:
    """Discrete convolution of two PMFs over nonnegative integers."""
    out = defaultdict(float)
    for a, pa in pmf_a.items():
        for b, pb in pmf_b.items():
            out[a + b] += pa * pb
    return dict(out)

def pmf_sum_of_hits(count_pmf: Dict[int, float], hits: int) -> Dict[int, float]:
    """
    PMF of sum of 'hits' iid draws from count_pmf.
    For hits=0, sum is 0 with prob 1.
    """
    if hits == 0:
        return {0: 1.0}
    # Repeated convolution; fast enough for small hits (<= 8 in your case)
    pmf = dict(count_pmf)
    for _ in range(hits - 1):
        pmf = convolve(pmf, count_pmf)
    return pmf

def pmf_total_count(p_hit: float, count_pmf: Dict[int, float], n_min: int = 4, n_max: int = 8) -> Dict[int, float]:
    """
    Returns PMF of S = total item count, where:
      n ~ Uniform{n_min..n_max}
      X | n ~ Binomial(n, p_hit)
      S | X=x = sum_{i=1..x} Yi, with Yi ~ count_pmf iid
    """
    # sanity checks
    if not (0.0 <= p_hit <= 1.0):
        raise ValueError("p_hit must be in [0, 1]")
    mass = sum(count_pmf.values())
    if abs(mass - 1.0) > 1e-9:
        raise ValueError(f"count_pmf must sum to 1, got {mass}")
    if any(k < 0 for k in count_pmf):
        raise ValueError("count_pmf keys must be nonnegative integers")

    out = defaultdict(float)
    n_values = list(range(n_min, n_max + 1))
    w_n = 1.0 / len(n_values)

    # Precompute per-hit-sum PMFs for hits up to max n
    sum_pmf_by_hits = {h: pmf_sum_of_hits(count_pmf, h) for h in range(0, n_max + 1)}

    for n in n_values:
        for x in range(0, n + 1):
            # P(X=x | n)
            px = math.comb(n, x) * (p_hit ** x) * ((1 - p_hit) ** (n - x))
            # P(S=s | X=x)
            sum_pmf = sum_pmf_by_hits[x]
            for s, ps in sum_pmf.items():
                out[s] += w_n * px * ps

    return dict(sorted(out.items()))

def print_pmf(pmf: Dict[int, float], max_s: int | None = None) -> None:
    keys = list(pmf.keys())
    if max_s is None:
        max_s = max(keys) if keys else 0
    total = 0.0
    for s in range(0, max_s + 1):
        p = pmf.get(s, 0.0)
        total += p
        print(f"P(S={s}) = {p:.12f}")
    print("Check sum:", sum(pmf.values()))
    if max_s < (max(keys) if keys else 0):
        print(f"(Truncated print at S={max_s}; full PMF max S={max(keys)})")
        