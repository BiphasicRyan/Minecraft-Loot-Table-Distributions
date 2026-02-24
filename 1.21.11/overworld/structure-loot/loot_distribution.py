from __future__ import annotations

import shutil
import sys
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


# ---------- Math core ----------

PMF = Dict[int, float]


def convolve(pmf_a: PMF, pmf_b: PMF) -> PMF:
    out: Dict[int, float] = defaultdict(float)
    for a, pa in pmf_a.items():
        for b, pb in pmf_b.items():
            out[a + b] += pa * pb
    return dict(out)


def convolve_many(pmfs: list[PMF]) -> PMF:
    out = {0: 1.0}
    for p in pmfs:
        out = convolve(out, p)
    return dict(sorted(out.items()))


def pmf_sum_of_hits(count_pmf: PMF, hits: int) -> PMF:
    if hits == 0:
        return {0: 1.0}
    pmf = dict(count_pmf)
    for _ in range(hits - 1):
        pmf = convolve(pmf, count_pmf)
    return pmf


def pmf_total_count(p_hit: float, count_pmf: PMF, n_min: int, n_max: int) -> PMF:
    if not (0.0 <= p_hit <= 1.0):
        raise ValueError("p_hit must be in [0, 1]")
    mass = sum(count_pmf.values())
    if abs(mass - 1.0) > 1e-9:
        raise ValueError(f"count_pmf must sum to 1, got {mass}")
    if any(k < 0 for k in count_pmf):
        raise ValueError("count_pmf keys must be nonnegative integers")

    out: Dict[int, float] = defaultdict(float)
    n_values = list(range(n_min, n_max + 1))
    w_n = 1.0 / len(n_values)

    sum_pmf_by_hits = {h: pmf_sum_of_hits(count_pmf, h) for h in range(0, n_max + 1)}

    for n in n_values:
        for x in range(0, n + 1):
            px = math.comb(n, x) * (p_hit**x) * ((1 - p_hit) ** (n - x))
            sum_pmf = sum_pmf_by_hits[x]
            for s, ps in sum_pmf.items():
                out[s] += w_n * px * ps

    return dict(sorted(out.items()))


# ---------- Loot-table parsing ----------

def _intish(x: Any) -> int:
    # Mojang uses floats in JSON even for integer counts.
    if isinstance(x, (int, float)):
        return int(round(float(x)))
    raise TypeError(f"Expected number, got {type(x)}")


def parse_rolls(pool: Dict[str, Any]) -> Tuple[int, int]:
    """
    Returns (n_min, n_max) for rolls. Supports:
      - rolls: 4.0
      - rolls: {type: minecraft:uniform, min: 2.0, max: 4.0}
    """
    rolls = pool.get("rolls", 1)
    if isinstance(rolls, (int, float)):
        n = _intish(rolls)
        return n, n
    if isinstance(rolls, dict):
        if rolls.get("type") == "minecraft:uniform":
            n_min = _intish(rolls["min"])
            n_max = _intish(rolls["max"])
            if n_min > n_max:
                n_min, n_max = n_max, n_min
            return n_min, n_max
    raise ValueError(f"Unsupported rolls spec: {rolls!r}")


def parse_count_pmf(entry: Dict[str, Any]) -> PMF:
    """
    Looks for minecraft:set_count in entry.functions.
    Supports:
      - count: 2.0
      - count: {type: minecraft:uniform, min: 1.0, max: 5.0}
    Default: {1: 1.0}
    """
    funcs = entry.get("functions") or []
    for fn in funcs:
        if fn.get("function") != "minecraft:set_count":
            continue
        count = fn.get("count")
        if isinstance(count, (int, float)):
            k = _intish(count)
            return {k: 1.0}
        if isinstance(count, dict) and count.get("type") == "minecraft:uniform":
            a = _intish(count["min"])
            b = _intish(count["max"])
            lo, hi = (a, b) if a <= b else (b, a)
            n = hi - lo + 1
            return {k: 1.0 / n for k in range(lo, hi + 1)}
        raise ValueError(f"Unsupported set_count: {count!r}")

    return {1: 1.0}


def entry_weight(entry: Dict[str, Any]) -> int:
    # Default weight is 1 when omitted.
    w = entry.get("weight", 1)
    return _intish(w)


def entry_name(entry: Dict[str, Any]) -> str:
    t = entry.get("type")
    if t == "minecraft:item":
        return str(entry.get("name", "minecraft:unknown"))
    if t == "minecraft:empty":
        return "minecraft:empty"
    return str(t or "unknown")


def safe_filename(item_name: str) -> str:
    return item_name.replace("minecraft:", "").replace(":", "__")


# ---------- Output ----------

def write_pmf(path: Path, pmf: PMF) -> None:
    keys = sorted(pmf.keys())
    max_s = max(keys) if keys else 0
    with path.open("w", encoding="utf-8") as f:
        for s in range(0, max_s + 1):
            p = pmf.get(s, 0.0)
            f.write(f"P(X={s}) = {p:.20f}\n")
        f.write(f"Check sum: {sum(pmf.values()):.20f}\n")


def summarize_count_pmf(count_pmf: PMF) -> str:
    if len(count_pmf) == 1:
        (k, p) = next(iter(count_pmf.items()))
        if abs(p - 1.0) < 1e-12:
            return f"count={k}"
    ks = sorted(count_pmf.keys())
    # recognize uniform integer range
    probs = [count_pmf[k] for k in ks]
    if all(abs(probs[i] - probs[0]) < 1e-12 for i in range(1, len(probs))):
        return f"count=uniform[{ks[0]}..{ks[-1]}]"
    return f"count_pmf={count_pmf}"


# ---------- Main driver ----------

def generate_from_loot_table(json_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    dst = out_dir / json_path.name
    shutil.move(str(json_path), str(dst))
    json_path = dst

    data = json.loads(json_path.read_text(encoding="utf-8"))
    pools = data.get("pools", [])

    # Store per-pool PMFs so we can compute whole-chest totals later
    # item_name -> list of (pool_index, pool_pmf_for_item)
    item_pool_pmfs: dict[str, list[tuple[int, PMF]]] = defaultdict(list)

    # Also remember which pools each item appears in (for writing TOTAL into those folders)
    item_pools_present: dict[str, set[int]] = defaultdict(set)

    # First pass: write pool-local outputs (what you already do) AND store PMFs
    for i, pool in enumerate(pools, start=1):
        pool_dir = out_dir / f"pool{i}"
        pool_dir.mkdir(exist_ok=True)

        results_dir = pool_dir / "results"
        results_dir.mkdir(exist_ok=True)

        try:
            n_min, n_max = parse_rolls(pool)
        except Exception as e:
            (pool_dir / "ERROR.txt").write_text(f"Unsupported rolls spec: {e}\n", encoding="utf-8")
            continue

        entries = pool.get("entries", [])
        simple_entries: list[Dict[str, Any]] = []
        skipped: list[str] = []

        for e in entries:
            t = e.get("type")
            if t in ("minecraft:item", "minecraft:empty"):
                simple_entries.append(e)
            else:
                skipped.append(f"- skipped entry type={t} name={e.get('name')}")

        total_weight = sum(entry_weight(e) for e in simple_entries) or 0

        # items.txt
        items_txt = pool_dir / "items.txt"
        with items_txt.open("w", encoding="utf-8") as f:
            f.write(f"Pool {i}\n")
            f.write(f"rolls: {n_min}..{n_max}\n")
            f.write(f"total_weight(simple entries): {total_weight}\n\n")
            f.write("Entries:\n")
            for e in simple_entries:
                name = entry_name(e)
                w = entry_weight(e)
                if e.get("type") == "minecraft:item":
                    cpmf = parse_count_pmf(e)
                    f.write(f"- {name}  weight={w}  {summarize_count_pmf(cpmf)}\n")
                else:
                    f.write(f"- {name}  weight={w}\n")
            if skipped:
                f.write("\nNon-simple entries not processed:\n")
                f.write("\n".join(skipped) + "\n")

        if total_weight == 0:
            continue

        # pool-local PMFs
        for e in simple_entries:
            if e.get("type") != "minecraft:item":
                continue

            name = entry_name(e)
            w = entry_weight(e)
            count_pmf = parse_count_pmf(e)

            p_hit = w / total_weight
            pmf = pmf_total_count(p_hit=p_hit, count_pmf=count_pmf, n_min=n_min, n_max=n_max)

            # Write pool-only PMF (unchanged behavior)
            out_path = results_dir / f"{safe_filename(name)}.txt"
            write_pmf(out_path, pmf)

            # Store for whole-chest totals
            item_pool_pmfs[name].append((i, pmf))
            item_pools_present[name].add(i)

    # Second pass: compute whole-chest PMF per item (convolving across pools)
    total_dir = out_dir / "total-results"
    total_dir.mkdir(exist_ok=True)

    for item_name, pool_list in item_pool_pmfs.items():
        # Convolve all pools where the item appears
        pmfs = [pmf for (_pool_i, pmf) in pool_list]
        total_pmf = convolve_many(pmfs)

        # Write one canonical total file
        write_pmf(total_dir / f"{safe_filename(item_name)}.txt", total_pmf)

        # Also write the SAME total PMF into every pool folder where the item appears
        for pool_i in sorted(item_pools_present[item_name]):
            pool_results_dir = out_dir / f"pool{pool_i}" / "results"
            pool_results_dir.mkdir(exist_ok=True)
            write_pmf(pool_results_dir / f"TOTAL__{safe_filename(item_name)}.txt", total_pmf)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python loot_distribution.py <loot_table.json> <out_dir>")
        raise SystemExit(2)

    generate_from_loot_table(Path(sys.argv[1]), Path(sys.argv[2]))