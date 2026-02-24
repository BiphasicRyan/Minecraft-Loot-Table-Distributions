from __future__ import annotations

from pathlib import Path
from typing import Dict, TypedDict

from loot_distribution import pmf_total_count


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "pool1-results"
OUT_DIR.mkdir(exist_ok=True)


class ItemConfig(TypedDict):
    weight: float
    count_pmf: Dict[int, float]


def write_pmf(path: Path, pmf: Dict[int, float]) -> None:
    keys = sorted(pmf.keys())
    max_s = max(keys) if keys else 0
    with path.open("w", encoding="utf-8") as f:
        for s in range(0, max_s + 1):
            p = pmf.get(s, 0.0)
            f.write(f"P(X={s}) = {p:.20f}\n")
        f.write(f"Check sum: {sum(pmf.values())}\n")


def main() -> None:
    # Weights from pool 1 of chests_ruined_portal.json
    # Items without explicit weight are treated as weight 1.
    items: Dict[str, ItemConfig] = {
        "obsidian": {
            "weight": 40,
            "count_pmf": {1: 0.5, 2: 0.5},
        },
        "flint": {
            "weight": 40,
            "count_pmf": {k: 0.25 for k in range(1, 5)},  # 1–4
        },
        "iron_nugget": {
            "weight": 40,
            "count_pmf": {k: 0.1 for k in range(9, 19)},  # 9–18
        },
        "flint_and_steel": {
            "weight": 40,
            "count_pmf": {1: 1.0},
        },
        "fire_charge": {
            "weight": 40,
            "count_pmf": {1: 1.0},
        },
        "golden_apple": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "gold_nugget": {
            "weight": 15,
            "count_pmf": {k: 1 / 21 for k in range(4, 25)},  # 4–24
        },
        "golden_sword": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "golden_axe": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "golden_hoe": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "golden_shovel": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "golden_pickaxe": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "golden_boots": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "golden_chestplate": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "golden_helmet": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "golden_leggings": {
            "weight": 15,
            "count_pmf": {1: 1.0},
        },
        "glistering_melon_slice": {
            "weight": 5,
            "count_pmf": {k: 1 / 9 for k in range(4, 13)},  # 4–12
        },
        "golden_horse_armor": {
            "weight": 5,
            "count_pmf": {1: 1.0},
        },
        "light_weighted_pressure_plate": {
            "weight": 5,
            "count_pmf": {1: 1.0},
        },
        "golden_carrot": {
            "weight": 5,
            "count_pmf": {k: 1 / 9 for k in range(4, 13)},  # 4–12
        },
        "clock": {
            "weight": 5,
            "count_pmf": {1: 1.0},
        },
        "gold_ingot": {
            "weight": 5,
            "count_pmf": {k: 1 / 7 for k in range(2, 9)},  # 2–8
        },
        "bell": {
            "weight": 1,
            "count_pmf": {1: 1.0},
        },
        "enchanted_golden_apple": {
            "weight": 1,
            "count_pmf": {1: 1.0},
        },
        "gold_block": {
            "weight": 1,
            "count_pmf": {1: 0.5, 2: 0.5},
        },
    }

    total_weight = sum(cfg["weight"] for cfg in items.values())  # 398

    for name, cfg in items.items():
        weight = cfg["weight"]
        count_pmf = cfg["count_pmf"]

        p_hit = weight / total_weight
        pmf = pmf_total_count(p_hit=p_hit, count_pmf=count_pmf, n_min=4, n_max=8)
        out_path = OUT_DIR / f"{name}.txt"
        write_pmf(out_path, pmf)


if __name__ == "__main__":
    main()

