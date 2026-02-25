# Minecraft Loot Table Distributions

This project contains the code and result of loot table generation probabilities. 

The primary purpose of this project is to be a reference when attempting to determine
the rarity of a specific loot pool or drop rate. There are already tools out there
have similar functionality, so the goal is to combine all the information and store
it in one place for quick reference. Here are a few resources I used along the way:

- [Minecraft wiki](https://minecraft.fandom.com/wiki/Minecraft_Wiki)
- [Minecraft@Home Discord](https://minecraftathome.com/)
- Official Minecraft loot tables
  - All probability distributions in this repository are computed from the official
    Minecraft loot-table JSON files. The original vanilla data files are not included
    here; only the derived analytical results are provided

## Current Features

- Structure chest loot distribution generator
- Distribution output 
  - **Distribution output will be in the "total-results" folder**
    - This accounts for the fact an item can be in more than one [pool](https://minecraft.fandom.com/wiki/Loot_table#Loot_pool)
  - Example: Ruined Portal Chest Bell Probability
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
    
  - Note: See the precision section for information about Check sum

## Usage

Given a vanilla Minecraft loot table JSON, you can generate per-item count distributions with:

```bash
python3 1.21.11/overworld/structure-loot/loot_distribution.py \
  path/to/loot_table.json \
  path/to/output_directory
```

- The script will **move** the input JSON file into the output directory.
- For each pool in the loot table it creates a `poolN` folder with:
  - `items.txt`: summary of entries, rolls, and weights.
  - `results/ITEM.txt`: probability mass function P(X = k) for the total count of that item from the pool.

Example (ruined portal chest table):

```bash
python3 1.21.11/overworld/structure-loot/loot_distribution.py \
  1.21.11/overworld/structure-loot/chests_ruined_portal.json \
  1.21.11/overworld/structure-loot/ruined-portals
```
  
## Precision

All computations use IEEE-754 double-precision floating point (float in Python).

Because many probabilities (e.g., 1/398, 1/21) cannot be represented exactly in binary floating point, the checksum may differ slightly from 1.0:

`Check sum: 1.00000000000000044409`

This is expected rounding error at machine precision (~10⁻¹⁶) and does not indicate a mathematical error in the model.

Further reading:

- [Wikipedia — Floating-point arithmetic](https://en.wikipedia.org/wiki/Floating-point_arithmetic)
- [University of Illinois — What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)

