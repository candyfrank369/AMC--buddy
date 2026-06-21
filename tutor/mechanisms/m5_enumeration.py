"""M5 — Organised enumeration / modular bucketing.

Every family is solved by exhaustive, structured enumeration (the code is the authority
on the count). Dispatched on params['type'] — see each handler's anchor in the comment.
"""
from itertools import combinations, permutations, product as iproduct
from math import comb, isqrt
import random


def _isprime(n):
    if n < 2:
        return False
    for p in range(2, isqrt(n) + 1):
        if n % p == 0:
            return False
    return True


# ---- modular / combinatoric counting ----
def _choose_sum_divisible(p):                       # 2013 Q27 = 76
    return sum(1 for c in combinations(p["set"], p["choose"]) if sum(c) % p["divisor"] == 0)


def _choose_count(p):                               # 2022 Q29 = 150
    r = 1
    for n, k in p["groups"]:
        r *= comb(n, k)
    return r


def _distinct_subset_sums(p):                       # 2022 Q28 = 151
    return len({sum(c) for c in combinations(p["set"], p["choose"])})


def _two_digit_multiples(p):                        # 2025 Q24 = 12
    cards, m = p["cards"], p["multiple"]
    return sum(1 for t, u in permutations(cards, 2) if (10 * t + u) % m == 0)


def _perm_divisible(p):                             # 2011 Q23 = 4
    cnt = 0
    for perm in permutations(p["cards"]):
        v = int("".join(map(str, perm)))
        if v % p["divisor"] == 0:
            cnt += 1
    return cnt


def _perm_rank(p):                                  # 2022 Q24 = 'spqr'
    perms = sorted("".join(x) for x in permutations(p["items"]))
    return perms[p["rank"] - 1]


def _count_predicate(p):                            # 2012 Q13 = 4
    lo, hi = p["range"]
    name = p["predicate"]
    if name == "jillyprime":
        ok = lambda n: _isprime(n) and _isprime(2 * n + 1)
    else:
        raise ValueError(name)
    return sum(1 for n in range(lo, hi + 1) if ok(n))


def _isosceles_count(p):                            # 2012 Q17 = 12
    sides = p["sides"]
    tris = set()
    for a in sides:
        for b in sides:                             # triangle {a,a,b}; b==a -> equilateral
            if 2 * a > b:                           # triangle inequality
                tris.add(tuple(sorted((a, a, b))))
    return len(tris)


def _crt_candidates(p):                             # 2024 Q24 = 21
    full, mods, cands = p["full"], p["mods"], p["candidates"]
    out = [c for c in cands if all((full - c) % m == r for m, r in mods)]
    assert len(out) == 1
    return out[0]


def _count_digit_in_list(p):                        # 2024 Q28 = 199
    vals = [p["start"] + i * p["step"] for i in range(p["count"])]
    d = str(p["digit"])
    return sum(str(v).count(d) for v in vals)


def _max_subsequence_digitsum(p):                   # 2013 Q25 = 38
    s = "".join(str(i) for i in range(p["range"][0], p["range"][1] + 1))
    keep = p["keep"]
    res, start = [], 0
    for slot in range(keep):
        # choose the largest digit in the window that still leaves enough after it
        end = len(s) - (keep - slot - 1)
        best_i = max(range(start, end), key=lambda i: (s[i], -i))
        res.append(s[best_i])
        start = best_i + 1
    return sum(int(c) for c in res)


def _min_bags(p):                                   # 2013 Q26 = 4
    sizes, costs, avg = p["sizes"], p["costs"], p["avg"]
    best = None
    R = 6
    for combo in iproduct(range(R), repeat=len(sizes)):
        if sum(combo) == 0:
            continue
        kg = sum(c * s for c, s in zip(combo, sizes))
        cost = sum(c * x for c, x in zip(combo, costs))
        if cost == avg * kg:
            best = sum(combo) if best is None else min(best, sum(combo))
    return best


def _tromino_tiling(p):                             # 2024 Q16 = 4
    R, C, L = p["rows"], p["cols"], p["piece"]
    cells = [(r, c) for r in range(R) for c in range(C)]
    idx = {cell: i for i, cell in enumerate(cells)}

    def place(grid):
        try:
            i = grid.index(False)
        except ValueError:
            return 1
        r, c = cells[i]
        total = 0
        # horizontal piece
        if c + L <= C and all(not grid[idx[(r, c + k)]] for k in range(L)):
            g = grid[:]
            for k in range(L):
                g[idx[(r, c + k)]] = True
            total += place(g)
        # vertical piece
        if r + L <= R and all(not grid[idx[(r + k, c)]] for k in range(L)):
            g = grid[:]
            for k in range(L):
                g[idx[(r + k, c)]] = True
            total += place(g)
        return total

    return place([False] * len(cells))


def _squares_from_points(p):                        # 2012 Q21 = 11
    pts = [tuple(q) for q in p["points"]]
    cnt = 0
    for four in combinations(pts, 4):
        d2 = sorted((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
                    for a, b in combinations(four, 2))
        # square: 4 equal sides s, 2 equal diagonals 2s, s>0
        if d2[0] > 0 and d2[0] == d2[1] == d2[2] == d2[3] and d2[4] == d2[5] == 2 * d2[0]:
            cnt += 1
    return cnt


def _cube_rotations():
    # 8 corners as bits; centred coords in {-1,1}
    corners = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    cidx = {c: i for i, c in enumerate(corners)}

    def det(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

    rots = []
    for perm in permutations(range(3)):
        for signs in iproduct((-1, 1), repeat=3):
            m = [[0, 0, 0] for _ in range(3)]
            for row in range(3):
                m[row][perm[row]] = signs[row]
            if det(m) != 1:
                continue
            perm8 = []
            for c in corners:
                cc = [2 * v - 1 for v in c]                       # to {-1,1}
                nc = [sum(m[r][k] * cc[k] for k in range(3)) for r in range(3)]
                nb = tuple((v + 1) // 2 for v in nc)              # back to {0,1}
                perm8.append(cidx[nb])
            rots.append(tuple(perm8))
    return rots


def _cube_2color_orbits(p):                         # 2010 Q30 = 7
    rots = _cube_rotations()
    seen, count = set(), 0
    for black in combinations(range(8), p["black"]):
        bset = frozenset(black)
        if bset in seen:
            continue
        orbit = {frozenset(r[i] for i in bset) for r in rots}
        seen |= orbit
        count += 1
    return count


def _line_arrangement_triangles(p):                 # 2009 Q14 = 44
    lines = [tuple(l) for l in p["lines"]]
    x0, x1, y0, y1 = p["box"]
    eps = 1e-9

    def inter(L1, L2):
        a1, b1, c1 = L1
        a2, b2, c2 = L2
        d = a1 * b2 - a2 * b1
        if abs(d) < eps:
            return None
        x = (c1 * b2 - c2 * b1) / d
        y = (a1 * c2 - a2 * c1) / d
        if x0 - eps <= x <= x1 + eps and y0 - eps <= y <= y1 + eps:
            return (round(x, 6), round(y, 6))
        return None

    cnt = 0
    for L1, L2, L3 in combinations(lines, 3):
        p12, p13, p23 = inter(L1, L2), inter(L1, L3), inter(L2, L3)
        if not (p12 and p13 and p23):
            continue
        if len({p12, p13, p23}) != 3:               # concurrent / coincident -> no triangle
            continue
        cnt += 1
    return cnt


def _stroke_letters(p):                             # 2011 Q25 = 16 (spanning trees of K4)
    n = p["dots"]
    edges = list(combinations(range(n), 2))
    cnt = 0
    for tree in combinations(edges, n - 1):
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        ok = True
        for a, b in tree:
            ra, rb = find(a), find(b)
            if ra == rb:
                ok = False
                break
            parent[ra] = rb
        if ok and len({find(i) for i in range(n)}) == 1:
            cnt += 1
    return cnt


def _drilled_cube(p):                               # 2012 Q25 = 29
    n = p["size"]
    rng = range(1, n + 1)
    removed = set()
    for hole in p["holes"]:
        xs = hole.get("x", list(rng))
        ys = hole.get("y", list(rng))
        zs = hole.get("z", list(rng))
        for x in xs:
            for y in ys:
                for z in zs:
                    removed.add((x, y, z))
    return len(removed)


def _sentries(p):                                   # 2012 Q9 = 7
    n = p["size"]
    guarded = set()
    for cc, rr in p["S"]:
        for k in range(1, n + 1):
            guarded.add((cc, k))
            guarded.add((k, rr))
    for tc, tr in p["T"]:
        for c in range(1, n + 1):
            for r in range(1, n + 1):
                if abs(c - tc) == abs(r - tr):
                    guarded.add((c, r))
    return n * n - len(guarded)


def _no_consecutive_labels(p):                      # 2010 Q17 -> {5,7} (anchor checks 7)
    nodes, edges, vals = p["nodes"], p["edges"], p["vals"]
    out = set()
    for perm in permutations(vals):
        a = dict(zip(nodes, perm))
        if all(abs(a[u] - a[v]) != 1 for u, v in edges):
            out.add(a[p["X"]] + a[p["Y"]])
    return sorted(out)


def _sparse_grid(p):                                # 2025 Q28 = 12
    R, C = p["rows"], p["cols"]
    n = R * C
    cnt = 0
    for mask in range(1 << n):
        ok = True
        for r in range(R - 1):
            for c in range(C - 1):
                cells = [r * C + c, r * C + c + 1, (r + 1) * C + c, (r + 1) * C + c + 1]
                if sum((mask >> i) & 1 for i in cells) != 1:
                    ok = False
                    break
            if not ok:
                break
        cnt += ok
    return cnt


def _triangular_board_edges(p):                     # 2025 Q27 = 108
    n = p["side"]
    down = (n - 1) * n // 2
    return 3 * down                                 # each down-triangle borders 3 up-triangles


def _digit_sum_range(p):                            # 2012 Q27 = 901
    return sum(int(c) for n in range(p["range"][0], p["range"][1] + 1) for c in str(n))


def _tens_hundreds_tally(lo, hi):
    from collections import Counter
    t = Counter()
    for n in range(lo, hi + 1):
        for c in str(n)[:-1]:                       # all digits except units
            t[int(c)] += 1
    return t


def _house_renumber_digits(p):                      # 2011 Q30 = 69
    from collections import Counter
    supply = _tens_hundreds_tally(*p["old_range"])
    demand = _tens_hundreds_tally(*p["new_range"])
    need = Counter({d: max(0, demand[d] - supply[d]) for d in range(10)})
    spare = {d: max(0, supply[d] - demand[d]) for d in range(10)}
    # 6 <-> 9 interchangeable
    swap = min(need[9], spare[6]); need[9] -= swap; spare[6] -= swap
    swap = min(need[6], spare[9]); need[6] -= swap; spare[9] -= swap
    return sum(need.values())


_DISPATCH = {
    "choose_sum_divisible": _choose_sum_divisible,
    "choose_count": _choose_count,
    "distinct_subset_sums": _distinct_subset_sums,
    "two_digit_multiples": _two_digit_multiples,
    "perm_divisible": _perm_divisible,
    "perm_rank": _perm_rank,
    "count_predicate": _count_predicate,
    "isosceles_count": _isosceles_count,
    "crt_candidates": _crt_candidates,
    "count_digit_in_list": _count_digit_in_list,
    "max_subsequence_digitsum": _max_subsequence_digitsum,
    "min_bags": _min_bags,
    "tromino_tiling": _tromino_tiling,
    "squares_from_points": _squares_from_points,
    "cube_2color_orbits": _cube_2color_orbits,
    "line_arrangement_triangles": _line_arrangement_triangles,
    "stroke_letters": _stroke_letters,
    "drilled_cube": _drilled_cube,
    "sentries": _sentries,
    "no_consecutive_labels": _no_consecutive_labels,
    "sparse_grid": _sparse_grid,
    "triangular_board_edges": _triangular_board_edges,
    "digit_sum_range": _digit_sum_range,
    "house_renumber_digits": _house_renumber_digits,
}


def solve(params):
    return _DISPATCH[params["type"]](params)


def difficulty(params):
    """Generic proxy = log10 of the naive search space where meaningful, else a count."""
    t = params["type"]
    if t in ("choose_sum_divisible", "distinct_subset_sums"):
        return len(params["set"])
    if t == "sparse_grid":
        return params["rows"] * params["cols"]
    return 5


def generate(seed):
    rng = random.Random(seed)
    n = rng.choice([9, 12, 15])
    return {"type": "choose_sum_divisible", "set": list(range(1, n + 1)),
            "choose": 3, "divisor": 3}
