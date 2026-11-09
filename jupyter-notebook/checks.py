"""Public acceptance checks appended by the notebook checker."""
import math


def check_summary(summarize):
    cases = [
        ([], {"count": 0, "minimum": None, "maximum": None, "mean": None}),
        ([2, 4, 6], {"count": 3, "minimum": 2, "maximum": 6, "mean": 4.0}),
        ([-4, 0, 1], {"count": 3, "minimum": -4, "maximum": 1, "mean": -1.0}),
        ([3, 3], {"count": 2, "minimum": 3, "maximum": 3, "mean": 3.0}),
        ([0.1, 0.2], {"count": 2, "minimum": 0.1, "maximum": 0.2, "mean": 0.15}),
    ]
    for values, expected in cases:
        original = list(values)
        actual = summarize(values)
        assert values == original, "input must remain unchanged"
        assert isinstance(actual, dict), "expected a dict"
        assert actual.keys() == expected.keys(), "unexpected result fields"
        for key in ["count", "minimum", "maximum"]:
            assert actual[key] == expected[key], f"incorrect {key} for {values}"
        if expected["mean"] is None:
            assert actual["mean"] is None, "empty input must have mean=None"
        else:
            assert math.isclose(actual["mean"], expected["mean"], rel_tol=1e-9, abs_tol=1e-12), f"incorrect mean for {values}"
    print("All 5 public checks passed")
