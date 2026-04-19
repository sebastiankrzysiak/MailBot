import json
import os
import pytest
import tempfile


def load_cache(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache, path):
    with open(path, "w") as f:
        json.dump(cache, f)


@pytest.fixture
def tmp_cache(tmp_path):
    return str(tmp_path / "cache.json")


def test_cache_miss_returns_empty(tmp_cache):
    cache = load_cache(tmp_cache)
    assert cache == {}


def test_cache_hit_after_write(tmp_cache):
    cache = {}
    cache["msg1"] = "Summary of email 1."
    save_cache(cache, tmp_cache)

    loaded = load_cache(tmp_cache)
    assert loaded["msg1"] == "Summary of email 1."


def test_cache_persists_multiple_entries(tmp_cache):
    cache = {"id1": "Summary 1", "id2": "Summary 2", "id3": "Summary 3"}
    save_cache(cache, tmp_cache)

    loaded = load_cache(tmp_cache)
    assert len(loaded) == 3
    assert loaded["id2"] == "Summary 2"


def test_cache_overwrite(tmp_cache):
    save_cache({"id1": "old"}, tmp_cache)
    save_cache({"id1": "new"}, tmp_cache)

    loaded = load_cache(tmp_cache)
    assert loaded["id1"] == "new"


def test_cache_id_lookup(tmp_cache):
    cache = {"abc123": "Cached summary."}
    save_cache(cache, tmp_cache)

    loaded = load_cache(tmp_cache)
    assert "abc123" in loaded
    assert "missing_id" not in loaded
