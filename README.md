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
