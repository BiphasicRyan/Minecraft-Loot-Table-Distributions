from __future__ import annotations

from pathlib import Path
from typing import Dict

from loot_distribution import pmf_total_count


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "pool2-results"
OUT_DIR.mkdir(exist_ok=True)


def write_pmf(path: Path, pmf: Dict[int, float]) -> None:
    keys = sorted(pmf.keys())
    max_s = max(keys) if keys else 0
    with path.open("w", encoding="utf-8") as f:
        for s in range(0, max_s + 1):
            p = pmf.get(s, 0.0)
            f.write(f"P(X={s}) = {p:.12f}\n")
        f.write(f"Check sum: {sum(pmf.values())}\n")


def main() -> None:
    # Pool 2 of chests_ruined_portal.json:
    weight_empty = 1.0
    weight_lodestone = 2.0

    p_hit = weight_lodestone / (weight_empty + weight_lodestone)  # 2/3

    count_pmf = {1: 0.5, 2: 0.5}

    pmf = pmf_total_count(p_hit=p_hit, count_pmf=count_pmf, n_min=1, n_max=1)

    out_path = OUT_DIR / "lodestone.txt"
    write_pmf(out_path, pmf)


if __name__ == "__main__":
    main()

