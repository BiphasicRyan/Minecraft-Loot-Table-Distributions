import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from loot_distribution import run_distribution

run_distribution(1 / 398)
