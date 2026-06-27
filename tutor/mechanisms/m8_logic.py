"""M8 — Logic / invariant / graph reasoning.

Families (dispatched on params['type']):
  route_inspection   walk every edge of a weighted graph and return to start; shortest total
                     distance = sum(edges) + min extra (Chinese-postman: pair the odd-degree
                     vertices and re-walk the cheapest shortest paths).  (2018 Q24 = 60)

Code is the authority: solve() computes the answer exactly (all-pairs shortest paths via
Floyd-Warshall + minimum-weight perfect matching of the odd-degree vertices by brute force,
which is exact for the small vertex counts AMC uses).
"""
from itertools import product

INF = float("inf")


def _shortest_paths(nodes, edges):
    idx = {n: i for i, n in enumerate(nodes)}
    N = len(nodes)
    D = [[INF] * N for _ in range(N)]
    for i in range(N):
        D[i][i] = 0
    for u, v, w in edges:
        i, j = idx[u], idx[v]
        D[i][j] = min(D[i][j], w)
        D[j][i] = min(D[j][i], w)
    for k in range(N):
        Dk = D[k]
        for i in range(N):
            dik = D[i][k]
            if dik == INF:
                continue
            Di = D[i]
            for j in range(N):
                if dik + Dk[j] < Di[j]:
                    Di[j] = dik + Dk[j]
    return D, idx


def _min_matching(odd, D, idx):
    """Minimum-weight perfect matching of the odd-degree vertices (brute force)."""
    if not odd:
        return 0
    a = odd[0]
    best = INF
    for k in range(1, len(odd)):
        b = odd[k]
        rest = odd[1:k] + odd[k + 1:]
        cost = D[idx[a]][idx[b]] + _min_matching(rest, D, idx)
        best = min(best, cost)
    return best


def _route_inspection(p):
    nodes, edges = p["nodes"], p["edges"]
    total = sum(w for _, _, w in edges)
    deg = {n: 0 for n in nodes}
    for u, v, w in edges:
        deg[u] += 1
        deg[v] += 1
    odd = [n for n in nodes if deg[n] % 2 == 1]
    D, idx = _shortest_paths(nodes, edges)
    extra = _min_matching(odd, D, idx)
    if extra == INF:                       # disconnected odd vertices: no closed route
        return None
    ans = total + extra if p.get("objective", "total") == "total" else extra
    return int(ans)


def _valid_faces(digits, length):
    out = set()
    for combo in product(sorted(set(digits)), repeat=length):
        if combo[0] == 0:                       # no leading zero
            continue
        out.add(int("".join(map(str, combo))))
    return out


def _cube_opposite_sum(p):
    """Cube faces are distinct k-digit numbers using only `digits`; 3 faces meeting at a corner
    are `visible`; opposite faces share one total T. Return the largest achievable T."""
    digits, length, vis = p["digits"], p["length"], p["visible"]
    V = _valid_faces(digits, length)
    if not all(v in V for v in vis) or len(set(vis)) != len(vis):
        return None
    for T in range(min(vis) + max(V), -1, -1):
        opp = [T - v for v in vis]
        if all(o in V for o in opp) and len(set(opp + list(vis))) == 2 * len(vis):
            return T
    return None


_DISPATCH = {"route_inspection": _route_inspection, "cube_opposite_sum": _cube_opposite_sum}


def solve(params):
    return _DISPATCH[params["type"]](params)


def solution_count(params):
    a = solve(params)
    return 1 if a is not None else 0


def difficulty(params):
    if params["type"] == "route_inspection":
        return len(params["edges"])          # work proxy; topology size
    if params["type"] == "cube_opposite_sum":
        return params["length"] * len(set(params["digits"]))
    return 5
