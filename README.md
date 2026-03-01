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

## Distribution Calculation Explained

### How Structure Chest Loot Works

Each structure chest in Minecraft (e.x. desert pyramids, ruined portals, bastions) has a
**loot table** that defines what items can appear and how likely they are. The loot table
is made up of one or more **pools**, and each pool is rolled independently to contribute
items to the chest.

#### Pools

A loot table contains one or more pools. Each pool is evaluated independently, and the
results of all pools are combined to produce the final chest contents.

#### Rolls

Each pool specifies a number of **rolls** which the number of times the game draws from
that pool. This can be a fixed number (e.x., `1`) or a uniform random range
(e.x., `4` to `8`, where each value in the range is equally likely).

#### Entries and Weights

Each pool has a list of **entries** (possible outcomes). Every entry has a **weight**
that determines its relative probability of being chosen on a single roll. On each roll,
exactly one entry is selected at random, with the probability of picking a given entry
equal to its weight divided by the total weight of all entries in that pool.

For example, if a pool has entries with weights 40, 15, 5, and 1, the total weight is 61
and the entry with weight 5 has a 5/61 chance of being selected on each roll.

#### Item Counts

When an item entry is selected, the game may also apply a **count function** that
determines how many of that item you receive. This can be a fixed number (e.x., always 1)
or a uniform random range (e.x., `4` to `24`, where each integer in the range is equally
likely). If no count function is specified, you receive exactly 1.

#### Putting It Together

For a single chest:

1. For each pool, the game picks how many rolls to perform.
2. On each roll, one entry is selected based on weights.
3. If the selected entry is an item, a count is determined.
4. The total number of a given item in the chest is the sum across all rolls in all pools.

Note: Because pools are independent, an item that appears in multiple pools can accumulate
counts from each one.

### How the Calculation Works

Instead of simulating millions of chests to estimate probabilities, the answer is computed analytically. Here is the general approach:

#### Step 1: Chance of Being Picked

For a single item in a pool, we first figure out its probability of being selected on any
given roll. This is simply the item's weight divided by the total weight of all entries.
For example, a bell with weight 1 in a pool with total weight 398 has a 1/398 chance per
roll.

#### Step 2: How Many Times Does It Get Picked?

A pool performs several rolls. Each roll is an independent chance to pick
the item. The number of times the item gets selected across all those rolls follows a
[binomial distribution](https://en.wikipedia.org/wiki/Binomial_distribution) — the same
math behind "if I flip a coin N times, how many heads do I get?"

When the number of rolls is a range (e.x., 4 to 8), average over every
possible roll count equally.

#### Step 3: How Many Items Per Pick?

Each time the item is picked, you might get a variable number of it (e.x., 4 to 24 gold
nuggets). If the item is picked 3 times and each pick gives a random count, the total is
the sum of 3 random draws. This is handled using
[convolutions](https://en.wikipedia.org/wiki/Convolution) which is a way of combining probability
distributions to find the distribution of their sum.

For example, if each pick gives 1 to 3 items, and you got picked twice, convolution
computes the exact probability of every possible total (2, 3, 4, 5, or 6).

#### Step 4: Combine Across Pools

If an item appears in more than one pool, the results from each pool are combined using convolution again. Since pools are independent, the total count in the chest is
just the sum of the counts from each pool.

#### Technical Summary

The per-pool PMF for a single item is computed as:

```
P(total = s) = (1/|R|) · Σ_n∈R  Σ_{x=0}^{n}  C(n,x) · p^x · (1-p)^(n-x) · P(sum of x draws = s)
```

Where:
- **R** = set of possible roll counts (e.x., {4, 5, 6, 7, 8})
- **p** = weight / total_weight (probability of selecting the item on a single roll)
- **C(n, x)** = binomial coefficient ("n choose x")
- **P(sum of x draws = s)** = x-fold convolution of the item's count distribution

When an item appears in multiple pools, the final distribution is the convolution of all
per-pool PMFs. All computations are exact (no simulation), using IEEE-754 double-precision
floating point.

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
python3 loot_distribution.py \
  path/to/loot_table.json \
  path/to/output_directory
```

- The script will **move** the input JSON file into the output directory.
- For each pool in the loot table it creates a `poolN` folder with:
  - `items.txt`: summary of entries, rolls, and weights.
  - `results/ITEM.txt`: probability mass function P(X = k) for the total count of that item from the pool.

Example (ruined portal chest table):

```bash
python3 loot_distribution.py \
  1.21.11/overworld/structure-loot/chests_ruined_portal.json \
  1.21.11/overworld/structure-loot/ruined-portals
```
  
## Precision

All computations use IEEE-754 double-precision floating point (float in Python).

Because many probabilities (e.x., 1/398, 1/21) cannot be represented exactly in binary floating point, the checksum may differ slightly from 1.0:

`Check sum: 1.00000000000000044409`

This is expected rounding error at machine precision (~10⁻¹⁶) and does not indicate a mathematical error in the model.

Further reading:

- [Wikipedia — Floating-point arithmetic](https://en.wikipedia.org/wiki/Floating-point_arithmetic)
- [University of Illinois — What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)

