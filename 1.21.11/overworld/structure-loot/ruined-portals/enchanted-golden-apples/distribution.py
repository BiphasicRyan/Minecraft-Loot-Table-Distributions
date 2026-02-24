import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from loot_distribution import pmf_total_count, print_pmf

p_hit = 1 / 398 
count_pmf = {1: 1.0}

pmf = pmf_total_count(p_hit=p_hit, count_pmf=count_pmf, n_min=4, n_max=8)
print_pmf(pmf)