# Minecraft Loot Table Distributions

This project contains the code and result of loot table generation probabilities. 

Please raise an issue if any of the numbers, methodology, or code, look incorrect.

## Current Features 
- structure chest loot distribution generator

## Usage

Given a vanilla Minecraft loot table JSON, you can generate per-item count distributions with:

```bash
python 1.21.11/overworld/structure-loot/loot_distribution.py \
  path/to/loot_table.json \
  path/to/output_directory
```

- The script will **move** the input JSON file into the output directory.
- For each pool in the loot table it creates a `poolN` folder with:
  - `items.txt`: summary of entries, rolls, and weights.
  - `results/ITEM.txt`: probability mass function \(P(X = k)\) for the total count of that item from the pool.

Example (ruined portal chest table):

```bash
python 1.21.11/overworld/structure-loot/loot_distribution.py \
  1.21.11/overworld/structure-loot/chests_ruined_portal.json \
  1.21.11/overworld/structure-loot/ruined-portals
```

## Output structure
Example: Ruined Portal Chest Bell Probability
```
P(X=0) = 0.98502523512506257042
P(X=1) = 0.01487454740533164857
P(X=2) = 0.00009982392900320414
P(X=3) = 0.00000039254300285485
P(X=4) = 0.00000000099592689328
P(X=5) = 0.00000000000167141809
P(X=6) = 0.00000000000000180353
P(X=7) = 0.00000000000000000114
P(X=8) = 0.00000000000000000000
Check sum: 1.00000000000000044409
```

## Precision

All computations use IEEE-754 double-precision floating point (float in Python).

Because many probabilities (e.g., 1/398, 1/21) cannot be represented exactly in binary floating point, the checksum may differ slightly from 1.0:

`Check sum: 1.00000000000000044409`

This is expected rounding error at machine precision (~10⁻¹⁶) and does not indicate a mathematical error in the model.

Further reading:
- [Wikipedia — Floating-point arithmetic](https://en.wikipedia.org/wiki/Floating-point_arithmetic)
- [University of Illinois — What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)