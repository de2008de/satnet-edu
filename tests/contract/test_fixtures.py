from pathlib import Path

import pytest

from satnet_edu import load


@pytest.mark.parametrize(
    "path", list((Path(__file__).parents[1] / "fixtures").glob("invalid-*.json"))
)
def test_reject_files(path):
    with pytest.raises(ValueError):
        load(path)


@pytest.mark.parametrize("name", ["minimal-valid.json", "real-engine-route.json"])
def test_valid_files(name):
    load(Path(__file__).parents[1] / "fixtures" / name)
