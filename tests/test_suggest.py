"""Unit tests for matrx_utils.suggest — the shared vocabulary-hint primitive."""
from __future__ import annotations

from matrx_utils import did_you_mean, format_options, suggestion_line


class TestDidYouMean:
    def test_close_match_found(self) -> None:
        assert did_you_mean("databse", ["database", "web", "shell"]) == ["database"]

    def test_no_match_below_cutoff(self) -> None:
        assert did_you_mean("zzzzz", ["database", "web", "shell"]) == []

    def test_best_first_ordering(self) -> None:
        out = did_you_mean("data", ["data_action", "database", "data"])
        assert out[0] == "data"

    def test_n_bounds_result_count(self) -> None:
        options = [f"tool_{i}" for i in range(20)]
        assert len(did_you_mean("tool_x", options, n=3)) <= 3

    def test_empty_wrong_returns_empty(self) -> None:
        assert did_you_mean("", ["a", "b"]) == []

    def test_empty_options_returns_empty(self) -> None:
        assert did_you_mean("anything", []) == []

    def test_cutoff_respected(self) -> None:
        assert did_you_mean("abc", ["abd"], cutoff=0.99) == []
        assert did_you_mean("abc", ["abd"], cutoff=0.5) == ["abd"]


class TestFormatOptions:
    def test_under_cap_lists_all(self) -> None:
        assert format_options(["a", "b", "c"], 5) == "a, b, c"

    def test_at_cap_lists_all(self) -> None:
        assert format_options(["a", "b", "c"], 3) == "a, b, c"

    def test_over_cap_truncates_with_count(self) -> None:
        assert format_options(["a", "b", "c", "d", "e"], 2) == "a, b … (+3 more)"

    def test_empty(self) -> None:
        assert format_options([], 5) == ""


class TestSuggestionLine:
    def test_single_match(self) -> None:
        line = suggestion_line("databse", ["database", "web"], noun="tool")
        assert line == "Did you mean tool 'database'?"

    def test_no_match_returns_none(self) -> None:
        assert suggestion_line("zzzzz", ["database", "web"], noun="tool") is None

    def test_multiple_matches_bounded_list(self) -> None:
        line = suggestion_line("data", ["data_x", "data_y", "data_z"], noun="tool")
        assert line is not None
        assert line.startswith("Did you mean one of these tools:")
        assert "data_x" in line

    def test_default_noun(self) -> None:
        assert suggestion_line("databse", ["database"]) == "Did you mean name 'database'?"
