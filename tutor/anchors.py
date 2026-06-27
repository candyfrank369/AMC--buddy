"""Anchor registry: maps each catalogued official M1-M6 anchor (year, q) to the
(mechanism, params) that the solver must reproduce. The expected value is read from
content/questions.jsonl (the '(=...)' in stem_summary) by the test — kept separate so
the proof is traceable to the corpus, not to numbers retyped here.

FLAGGED = official M1-M6 anchors deliberately NOT reproduced (answer-key-only sources
with no worked solution + figure/construction rule that cannot be modelled without
guessing). Reported transparently, never faked.
"""
from fractions import Fraction as F

# (year, q) -> (mechanism, params)
REGISTRY = {
    # ---- M1 ----
    (2010, 8):  ("M1", {"type": "digit_extremes", "digits": [2, 7, 5], "groups": [3]}),
    (2013, 5):  ("M1", {"type": "digit_extremes", "digits": [1, 2, 3, 4, 5], "groups": [5]}),
    (2024, 26): ("M1", {"type": "digit_extremes", "digits": [1, 2, 3, 4, 5, 6], "groups": [3, 3]}),

    # ---- M2 ----
    (2009, 16): ("M2", {"type": "int_set_sum_product", "n": 3, "total_sum": 14, "total_product": 70, "want": "max"}),
    (2010, 21): ("M2", {"type": "two_digit_reverse", "target": 132}),
    (2010, 28): ("M2", {"type": "consecutive_product", "k": 3, "product": 12144}),
    (2010, 29): ("M2", {"type": "digit_append", "digit": 2, "increase": 2785}),
    (2011, 21): ("M2", {"type": "cryptarithm_addition",
                         "addends": [["X", 9, "Y"], ["Z", 8, 7]], "result": ["W", 0, "V", 2],
                         "boxes": ["X", "Y", "Z", "W", "V"]}),
    (2011, 26): ("M2", {"type": "constrained_number", "range": [1, 100000], "want": "smallest",
                         "predicates": [["multiple_of", 42], ["num_odd_digits", 2]]}),
    (2011, 27): ("M2", {"type": "two_digit_property"}),
    (2011, 29): ("M2", {"type": "paul_ages", "target": 2011, "parent_gap": 1,
                         "num_kids": 2, "kid_gap": 1, "years_before": 13}),
    (2012, 16): ("M2", {"type": "remove_plus", "sequence": [9, 8, 7, 6, 5, 4, 3, 2, 1], "target": 99}),
    (2012, 23): ("M2", {"type": "crossnumber_reverse"}),
    (2013, 19): ("M2", {"type": "product_bracket", "gap": 1, "bound": 1000}),
    (2013, 22): ("M2", {"type": "harmonic_shares", "combined": 6, "one_class": 10}),
    (2013, 29): ("M2", {"type": "ascending_times", "ndigits": 3, "mult": 5}),
    (2024, 18): ("M2", {"type": "constrained_number", "range": [20, 50], "want": "count",
                         "predicates": ["divisible_by_unit_digit"]}),
    (2025, 16): ("M2", {"type": "not_possible_total", "percentages": [60, 25, 10, 5],
                         "candidates": [240, 100, 40, 25, 20]}),
    (2025, 26): ("M2", {"type": "constrained_number", "range": [100, 999], "want": "smallest",
                         "predicates": ["even", ["multiple_of", 9], ["contains_digit", 5],
                                        ["no_digit", 0], "all_distinct"]}),

    # ---- M3 ----
    (2024, 27): ("M3", {"type": "op_order", "start": 10,
                         "ops": [[1, 10], [2, 0], [F(1, 2), 50], [2, 5]], "objective": "max"}),

    # ---- M4 ----
    (2009, 2):  ("M4", {"type": "affine_chain", "ops": [[2, 7]], "end": 33}),
    (2009, 30): ("M4", {"type": "temples", "temples": 3}),
    (2013, 8):  ("M4", {"type": "affine_chain", "ops": [[2, 2], [F(1, 2), -2]], "end": 6}),
    (2022, 17): ("M4", {"type": "fraction_remainder",
                         "stages": [["take_fraction", F(1, 3)], ["take_fraction", F(1, 2)]],
                         "final": ["count", 8]}),
    (2025, 22): ("M4", {"type": "fraction_remainder",
                         "stages": [["take_fraction", F(3, 5)], ["take_count", 20]],
                         "final": ["fraction", F(3, 20)]}),
    (2025, 23): ("M4", {"type": "consecutive_dates", "count": 7, "sum": 56, "ask": "last_weekday",
                         "start_weekday": "Wed", "target_weekday": "Fri", "days_in_month": 31}),

    # ---- M5 ----
    (2009, 14): ("M5", {"type": "line_arrangement_triangles", "box": [0, 2, 0, 2],
                         "lines": [[1, 0, 0], [1, 0, 1], [1, 0, 2],      # verticals x=0,1,2
                                   [0, 1, 0], [0, 1, 1], [0, 1, 2],      # horizontals y=0,1,2
                                   [1, -1, 0], [1, -1, -1], [1, -1, 1],  # slope +1: y=x, x+1, x-1
                                   [1, 1, 1], [1, 1, 2], [1, 1, 3]]}),   # slope -1: x+y=1,2,3
    (2010, 17): ("M5", {"type": "no_consecutive_labels",
                         "nodes": ["X", "A", "B", "Y", "C"],
                         "edges": [["X", "A"], ["X", "B"], ["A", "B"], ["A", "Y"], ["B", "C"], ["Y", "C"]],
                         "vals": [1, 2, 3, 4, 5], "X": "X", "Y": "Y"}),
    (2010, 30): ("M5", {"type": "cube_2color_orbits", "black": 4}),
    (2011, 23): ("M5", {"type": "perm_divisible", "cards": [2, 3, 5, 6], "divisor": 8}),
    (2011, 25): ("M5", {"type": "stroke_letters", "dots": 4}),
    (2011, 30): ("M5", {"type": "house_renumber_digits", "old_range": [1, 80], "new_range": [65, 144]}),
    (2012, 9):  ("M5", {"type": "sentries", "size": 5, "S": [[2, 5], [4, 3]], "T": [[2, 2]]}),
    (2012, 13): ("M5", {"type": "count_predicate", "range": [1, 14], "predicate": "jillyprime"}),
    (2012, 17): ("M5", {"type": "isosceles_count", "sides": [2, 3, 7, 11]}),
    (2012, 21): ("M5", {"type": "squares_from_points",
                         "points": [[2, 3], [3, 3], [1, 2], [2, 2], [3, 2], [4, 2],
                                    [1, 1], [2, 1], [3, 1], [4, 1], [2, 0], [3, 0]]}),
    (2012, 25): ("M5", {"type": "drilled_cube", "size": 5,
                         "holes": [{"x": [3], "y": [3]},
                                   {"y": [3], "z": [2, 3, 4]},
                                   {"x": [3], "z": [2, 3, 4]}]}),
    (2012, 27): ("M5", {"type": "digit_sum_range", "range": [1, 100]}),
    (2013, 25): ("M5", {"type": "max_subsequence_digitsum", "range": [1, 30], "keep": 6}),
    (2013, 26): ("M5", {"type": "min_bags", "sizes": [1, 3, 8], "costs": [6, 15, 25], "avg": 4}),
    (2013, 27): ("M5", {"type": "choose_sum_divisible", "set": list(range(1, 13)), "choose": 3, "divisor": 3}),
    (2022, 24): ("M5", {"type": "perm_rank", "items": ["p", "q", "r", "s"], "rank": 19}),
    (2022, 28): ("M5", {"type": "distinct_subset_sums", "set": list(range(1, 106, 2)), "choose": 3}),
    (2022, 29): ("M5", {"type": "choose_count", "groups": [[5, 2], [6, 2]]}),
    (2024, 16): ("M5", {"type": "tromino_tiling", "rows": 3, "cols": 5, "piece": 3}),
    (2024, 24): ("M5", {"type": "crt_candidates", "full": 52, "mods": [[4, 3], [6, 1]],
                         "candidates": [2, 10, 11, 17, 21]}),
    (2024, 28): ("M5", {"type": "count_digit_in_list", "start": 5, "step": 5, "count": 300, "digit": 0}),
    (2025, 24): ("M5", {"type": "two_digit_multiples", "cards": [2, 4, 5, 6, 7, 8], "multiple": 3}),
    (2025, 27): ("M5", {"type": "triangular_board_edges", "side": 9}),
    (2025, 28): ("M5", {"type": "sparse_grid", "rows": 4, "cols": 4}),

    # ---- M6 ----
    (2010, 26): ("M6", {"type": "word_cycle_lcm", "lengths": [4, 2, 3, 5, 5, 9]}),
    (2013, 30): ("M6", {"type": "bounded_walk", "length": 12, "low": -2, "high": 2, "start": 0}),
    (2022, 26): ("M6", {"type": "iterate_map", "map": "double_plus4_mod100", "seed": 1, "index": 2022}),
    (2024, 22): ("M6", {"type": "consecutive_sum_threshold", "count": 6, "lower": 100}),
    (2024, 29): ("M6", {"type": "iterate_map", "map": "digit_square_sum", "seed": 2024, "index": 2024}),
    (2024, 30): ("M6", {"type": "stepping_stones", "n": 12}),
    (2025, 20): ("M6", {"type": "repeating_digit_sum", "digits": [2, 0, 2, 5], "target": 2025}),

    # ---- M8 (route inspection / graph) ----  answer = shortest closed route over all fences
    (2018, 24): ("M8", {"type": "route_inspection", "objective": "total",
                         "nodes": ["H", "O", "M", "E", "X"],
                         "edges": [["H", "O", 8], ["M", "E", 8], ["E", "H", 6], ["O", "M", 6],
                                   ["H", "X", 5], ["X", "M", 5], ["E", "X", 5], ["X", "O", 5]],
                         "_dims": [8, 6, 10]}),    # 8x6 field + both diagonals (=10) -> 48 + 12 = 60
    (2018, 27): ("M8", {"type": "cube_opposite_sum", "digits": [0, 1, 2], "length": 3,
                        "visible": [220, 121, 201]}),    # -> 321
}

# Deliberately not reproduced (answer-key-only source, figure/construction rule unknown):
FLAGGED = {
    (2025, 18): "M6 figurate-dot rule: natural reading gives 78 (=trap option E); official 63 unobtainable without the (unavailable) figure rule.",
    (2025, 29): "M6 double-spiral on 45x45: construction rule not modellable from an answer-key-only source.",
    (2012, 29): "M5 free tri-rhomb enumeration on the triangular lattice: shape-equivalence rule too ambiguous to model faithfully.",
}
