import math

p = 1/398

def prob_exact(x: int) -> float:
    total = 0.0
    for n in range(4, 9):
        if x > n:
            continue
        total += (1/5) * math.comb(n, x) * (p**x) * ((1 - p)**(n - x))
    return total

for x in range(0, 9):
    print(f"P(X={x}) = {prob_exact(x):.12f}")

print("Check sum:", sum(prob_exact(x) for x in range(0, 9)))
