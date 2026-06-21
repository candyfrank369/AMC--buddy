"""M6 — Sequence / pattern / recurrence.

Families
--------
- iterate_map             : nth term of a deterministic map with cycle detection.
                            maps: 'digit_square_sum' (2024 Q29=89),
                                  'double_plus4_mod100' (2022 Q26=56)
- consecutive_sum_threshold: run of consecutive ints whose sum first crosses a bound
                            after a +1-each bump (2024 Q22=105)
- stepping_stones         : count orderings visiting 1..n once, steps in {±1,±2},
                            from 1 to n (2024 Q30=41)
- repeating_digit_sum     : repeat a digit block until running total hits target;
                            count numbers written (2025 Q20=900)
- word_cycle_lcm          : LCM of word lengths (2010 Q26=180)
- bounded_walk            : count ±1 walks of given length staying in [low,high]
                            (2013 Q30=972)
"""
import math
import random


def _digit_square_sum(n):
    return sum(int(c) ** 2 for c in str(n))


def _double_plus4_mod100(n):
    n = 2 * n + 4
    return n % 100 if n > 100 else n


_MAPS = {"digit_square_sum": _digit_square_sum, "double_plus4_mod100": _double_plus4_mod100}


def _iterate_map(params):
    f = _MAPS[params["map"]]
    idx = params["index"]                 # 1-based: term 1 = seed
    seq, pos = [], {}
    x = params["seed"]
    while x not in pos:
        pos[x] = len(seq)
        seq.append(x)
        if len(seq) >= idx:
            return seq[idx - 1]
        x = f(x)
    start = pos[x]                        # cycle starts here
    period = len(seq) - start
    return seq[start + (idx - 1 - start) % period]


def _consecutive_sum_threshold(params):
    c, lower = params["count"], params["lower"]
    n = 1
    while True:
        s = sum(range(n, n + c))
        if s < lower and s + c > lower:   # bump each by 1 -> sum + c
            return s + c
        n += 1


def _stepping_stones(params):
    n = params["n"]
    target = n
    count = 0

    def dfs(cur, visited):
        nonlocal count
        if len(visited) == n:
            if cur == target:
                count += 1
            return
        for step in (-2, -1, 1, 2):
            nxt = cur + step
            if 1 <= nxt <= n and nxt not in visited:
                visited.add(nxt)
                dfs(nxt, visited)
                visited.remove(nxt)

    dfs(1, {1})
    return count


def _repeating_digit_sum(params):
    block, target = params["digits"], params["target"]
    total, count, i = 0, 0, 0
    while total < target:
        total += block[i % len(block)]
        count += 1
        i += 1
    return count


def _word_cycle_lcm(params):
    return math.lcm(*params["lengths"])


def _bounded_walk(params):
    low, high, length, start = params["low"], params["high"], params["length"], params["start"]
    dp = {start: 1}
    for _ in range(length):
        nd = {}
        for s, v in dp.items():
            for ns in (s - 1, s + 1):
                if low <= ns <= high:
                    nd[ns] = nd.get(ns, 0) + v
        dp = nd
    return sum(dp.values())


_DISPATCH = {
    "iterate_map": _iterate_map,
    "consecutive_sum_threshold": _consecutive_sum_threshold,
    "stepping_stones": _stepping_stones,
    "repeating_digit_sum": _repeating_digit_sum,
    "word_cycle_lcm": _word_cycle_lcm,
    "bounded_walk": _bounded_walk,
}


def solve(params):
    return _DISPATCH[params["type"]](params)


def difficulty(params):
    t = params["type"]
    if t == "iterate_map":
        return len(str(params["index"]))          # how far out the index is
    if t == "bounded_walk":
        return params["length"]
    if t == "stepping_stones":
        return params["n"]
    if t == "repeating_digit_sum":
        return len(str(params["target"]))
    if t == "word_cycle_lcm":
        return len(params["lengths"])
    return params.get("count", 6)


def generate(seed):
    rng = random.Random(seed)
    return {"type": "iterate_map", "map": "digit_square_sum",
            "seed": rng.randint(1000, 9999), "index": rng.choice([100, 500, 1000])}
